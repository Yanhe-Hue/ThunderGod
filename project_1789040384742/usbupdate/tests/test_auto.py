import unittest
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch
from auto_update import AutomaticUpgrade, qnx_build_date
import datetime as dt
import xml.etree.ElementTree as ET


class AutoTests(unittest.TestCase):
    def test_verify_adb_starts_without_power_on_delay(self):
        runner = self.runner()
        runner.cfg['verify_expected_qnx'] = 'target'
        runner.wait_after_power_on = Mock()
        runner.connect = Mock()
        runner.verify = Mock()
        runner.verify_installed_version(wait_before_adb=False)
        runner.wait_after_power_on.assert_not_called()
        runner.connect.assert_called_once_with()
        runner.verify.assert_called_once_with('', date_only=True)

    def test_power_on_waits_120_seconds_before_adb(self):
        runner = self.runner()
        runner.cfg.update(automation={'upgrade_navigation': [{}]}, validation_timeout=1,
                          flash_timeout=1, activation_timeout=1, boot_timeout=10)
        runner.cfg['ui']['reboot_prompt'] = {'text': 'reboot'}
        runner.navigate = Mock()
        runner.phase = Mock()
        runner.wait_new_state = Mock()
        calls = []
        responses = iter(['old-boot', 'new-boot', '1'])
        def adb(*args, **kwargs):
            calls.append('adb')
            return next(responses)
        runner.adb_run = Mock(side_effect=adb)
        power = Mock()
        power.power_cycle.side_effect = lambda: calls.append('power_on')
        runner.hardware = Mock(return_value=power)
        with patch('usb_update.time.sleep', side_effect=lambda seconds: calls.append(('sleep', seconds))):
            runner.flash(package_ready=True)
        self.assertEqual(calls, ['adb', 'power_on', ('sleep', 120), 'adb', 'adb'])

    def test_standalone_version_check_waits_then_connects_and_compares(self):
        runner = self.runner()
        runner.cfg['verify_expected_qnx'] = 'target-version'
        order = Mock()
        runner.wait_after_power_on = order.wait
        runner.connect = order.connect
        runner.verify = order.verify
        runner.verify_installed_version()
        self.assertEqual([item[0] for item in order.mock_calls], ['wait', 'connect', 'verify'])
        runner.verify.assert_called_once_with('', date_only=True)

    def test_date_verification_needs_no_package_records(self):
        runner = self.runner()
        runner.connect = Mock()
        runner.verify = Mock()
        with patch('version_records.resolve_expected', side_effect=AssertionError('must not read records')):
            runner.verify_installed_version(wait_before_adb=False)
        runner.connect.assert_called_once_with()

    def test_qnx_date_formats_and_invalid_dates(self):
        for value in ('1.01.05.61-260914_023700', '1.01.05.61-20260914_023700'):
            self.assertEqual(qnx_build_date(value), dt.date(2026, 9, 14))
        for value in ('1.01.05.61', '1.01.05.61-260230_023700'):
            with self.assertRaises(RuntimeError):
                qnx_build_date(value)

    def test_date_check_pass_and_mismatch(self):
        runner = self.runner()
        runner.cfg['automation'] = {'version_navigation': []}
        runner.cfg['ui']['qnx_value'] = {'resource-id': 'version'}
        runner.navigate = Mock()
        for delta in (0, -1):
            date = dt.date.today() + dt.timedelta(days=delta)
            version = '1.01.05.61-' + date.strftime('%y%m%d') + '_023700'
            runner.snapshot = Mock(return_value=ET.fromstring(f'<hierarchy><node resource-id="version" text="{version}"/></hierarchy>'))
            if delta:
                with self.assertRaisesRegex(RuntimeError, '日期不符'):
                    runner.verify('', date_only=True)
            else:
                runner.verify('', date_only=True)
                self.assertEqual(runner.event.call_args.args[0], 'VERSION_DATE_VERIFIED')

    def test_resume_skips_package_preparation(self):
        runner = self.runner()
        runner.preflight = Mock()
        runner.connect = Mock()
        runner.flash = Mock()
        runner.verify = Mock()
        runner.switch_to_pc = Mock()
        runner.prepare = Mock()
        runner.resume()
        runner.preflight.assert_called_once_with(local=True)
        runner.flash.assert_called_once_with(package_ready=True)
        runner.verify.assert_called_once_with('', date_only=True)
        runner.switch_to_pc.assert_not_called()
        runner.prepare.assert_not_called()

    def test_resume_flash_does_not_switch_or_hash_usb(self):
        runner = self.runner()
        runner.cfg.update(automation={'upgrade_navigation': [{}]}, validation_timeout=1,
                          flash_timeout=1, activation_timeout=1)
        runner.switch_to_car = Mock()
        runner.navigate = Mock()
        runner.phase = Mock(side_effect=RuntimeError('stop at phase'))
        runner.hardware = Mock()
        with self.assertRaisesRegex(RuntimeError, 'stop at phase'):
            runner.flash(package_ready=True)
        runner.switch_to_car.assert_not_called()
        runner.hardware.assert_not_called()

    def upgrade_route(self, runner):
        steps = [{'component': 'com.alliance.engineering.fota/.UsbUpdateBtnActivity',
                  'arrived': {'text': 'System Update'}},
                 {'selector': {'text': 'USB Upgrade'}, 'arrived': {'text': 'USB Upgrade'}}]
        runner.cfg['automation'] = {'upgrade_navigation': steps}
        return steps

    def upgrade_screen(self):
        return ET.fromstring('<hierarchy><node text="USB Upgrade"/><node text="Upgrade package verified" resource-id="com.alliance.engineering.fota:id/usb_tv_title"/></hierarchy>')

    def test_navigation_already_at_upgrade_skips_entry(self):
        runner = self.runner()
        steps = self.upgrade_route(runner)
        runner.snapshot = Mock(return_value=self.upgrade_screen())
        runner.adb_run = Mock()
        runner.click = Mock()
        runner.navigate(steps)
        runner.adb_run.assert_not_called()
        runner.click.assert_not_called()

    def test_activity_restores_upgrade_page_without_menu(self):
        runner = self.runner()
        steps = self.upgrade_route(runner)
        runner.snapshot = Mock(side_effect=[ET.fromstring('<hierarchy/>'), self.upgrade_screen()])
        runner.adb_run = Mock()
        runner.click = Mock()
        runner.navigate(steps)
        runner.adb_run.assert_called_once_with('shell', 'am', 'start', '-n', steps[0]['component'])
        runner.click.assert_not_called()

    def test_menu_entry_text_is_not_upgrade_destination(self):
        runner = self.runner()
        root = ET.fromstring('<hierarchy><node text="System Update"/><node text="USB Upgrade"/></hierarchy>')
        self.assertFalse(runner.on_upgrade_page(root))

    def test_custom_usb_mount_is_discovered(self):
        runner = self.runner()
        runner.adb_run = Mock(side_effect=['emulated\nself', 'usb0'])
        self.assertEqual(runner.car_package_paths(), ['/mnt/media_rw/usb0/USB_UPDATE/Update.zip'])

    def test_standard_usb_mount_is_still_discovered(self):
        runner = self.runner()
        runner.adb_run = Mock(side_effect=['emulated\n7AFB-27F6', ''])
        self.assertEqual(runner.car_package_paths(), ['/storage/7AFB-27F6/USB_UPDATE/Update.zip'])

    def test_missing_target_records_version_without_claiming_match(self):
        runner = self.runner()
        runner.cfg['automation'] = {'version_navigation': [{}]}
        runner.cfg['ui']['qnx_value'] = {'resource-id': 'version'}
        runner.navigate = Mock()
        runner.snapshot = Mock(return_value=ET.fromstring('<hierarchy><node resource-id="version" text="actual"/></hierarchy>'))
        runner.verify('')
        runner.event.assert_called_once_with('VERSION_RECORDED_NOT_VERIFIED', actual='actual', evidence='ui')

    def test_local_existing_target_needs_no_copy_or_cloud(self):
        runner = self.runner()
        runner.prepare = Mock()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / 'USB_UPDATE' / 'Update.zip'
            target.parent.mkdir()
            with zipfile.ZipFile(target, 'w') as archive:
                archive.writestr('payload.bin', b'example')
            with patch('tkinter.Tk'), patch('tkinter.filedialog.askopenfilename', return_value=str(target)):
                entry = runner.local_package(root)
            self.assertEqual(entry['expected_qnx'], '')
            self.assertEqual(entry['source'], str(target))
            runner.prepare.assert_not_called()

    def test_local_cancel_does_not_prepare(self):
        runner = self.runner()
        runner.prepare = Mock()
        with patch('tkinter.Tk'), patch('tkinter.filedialog.askopenfilename', return_value=''):
            self.assertIsNone(runner.local_package(Path('.')))
        runner.prepare.assert_not_called()

    def test_local_incomplete_download_rejected(self):
        runner = self.runner()
        runner.prepare = Mock()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'Update.part'
            source.write_bytes(b'incomplete')
            with patch('tkinter.Tk'), patch('tkinter.filedialog.askopenfilename', return_value=str(source)):
                with self.assertRaises(RuntimeError):
                    runner.local_package(Path(directory))
        runner.prepare.assert_not_called()

    def test_known_notice_dismissed_with_back_only(self):
        runner = self.runner()
        runner.adb_run = Mock()
        notice = ET.fromstring('<hierarchy><node resource-id="com.google.android.gms:id/auth_uncertified_notification_description"/></hierarchy>')
        menu = ET.fromstring('<hierarchy><node text="System Update"/></hierarchy>')
        with patch('usb_update.Upgrade.snapshot', side_effect=[notice, menu]):
            self.assertIs(runner.snapshot(), menu)
        runner.adb_run.assert_called_once_with('shell', 'input', 'keyevent', '4')

    def runner(self):
        runner = AutomaticUpgrade.__new__(AutomaticUpgrade)
        runner.cfg = {'ui': {}, 'cloud': {}, 'smoke': {'enabled': False}}
        runner.logs = Path('.')
        runner.event = Mock()
        return runner

    def test_missing_evidence_stops_before_download_or_hardware(self):
        runner = self.runner()
        runner.connect = Mock()
        runner.hardware = Mock()
        with patch('builtins.input', side_effect=AssertionError('禁止交互')), self.assertRaises(RuntimeError):
            runner.run()
        runner.connect.assert_not_called()
        runner.hardware.assert_not_called()

    def test_existing_completion_continues_without_click(self):
        runner = self.runner()
        runner.cfg['ui'] = {'validation_done': {'text':'done'}, 'start':{'text':'Start Update'}}
        runner.snapshot = Mock(return_value=ET.fromstring('<hierarchy><node text="done"/></hierarchy>'))
        runner.click = Mock()
        runner.phase('start','validation_done','done',1)
        runner.click.assert_not_called()
        runner.event.assert_called_once_with('PHASE_ALREADY_COMPLETE', action='start',
                                            completion='validation_done', observed='validation_done',
                                            evidence='current_ui')

    def test_later_completion_skips_earlier_phase(self):
        runner = self.runner()
        runner.cfg['ui'] = {'validation_done': {'text': 'verified'},
                            'flash_done': {'text': 'installed'}, 'start': {'text': 'Start'}}
        runner.snapshot = Mock(return_value=ET.fromstring('<hierarchy><node text="installed"/></hierarchy>'))
        runner.click = Mock()
        runner.phase('start', 'validation_done', 'done', 1)
        runner.click.assert_not_called()
        self.assertEqual(runner.event.call_args.kwargs['observed'], 'flash_done')

    def test_failure_overrides_completion(self):
        runner = self.runner()
        runner.cfg['ui'] = {'validation_done': {'text': 'done'}, 'start': {'text': 'Start'},
                            'failure_selectors': [{'text': 'failed'}]}
        runner.snapshot = Mock(return_value=ET.fromstring('<hierarchy><node text="done"/><node text="failed"/></hierarchy>'))
        runner.click = Mock()
        with self.assertRaisesRegex(RuntimeError, '失败'):
            runner.phase('start', 'validation_done', 'done', 1)
        runner.click.assert_not_called()

    def test_unfinished_phase_still_clicks_and_waits(self):
        runner = self.runner()
        runner.cfg['ui'] = {'validation_done': {'text': 'done'}, 'start': {'text': 'Start'}}
        runner.snapshot = Mock(return_value=ET.fromstring('<hierarchy><node text="Start" enabled="true"/></hierarchy>'))
        runner.click = Mock()
        runner.wait_new_state = Mock()
        runner.phase('start', 'validation_done', 'done', 10)
        runner.click.assert_called_once_with({'text': 'Start'})
        runner.wait_new_state.assert_called_once_with({'text': 'done'}, 10, 'done')

    def test_eject_failure_never_switches_usb(self):
        runner = self.runner()
        runner.cfg['usb_root'] = 'E:/'
        runner.hardware = Mock()
        with patch('auto_update.eject', side_effect=OSError('busy')), self.assertRaises(OSError):
            runner.switch_to_car()
        runner.hardware.assert_not_called()

    def test_wrong_version_cannot_pass(self):
        runner = self.runner()
        runner.cfg['automation'] = {'version_navigation':[{}]}
        runner.cfg['ui']['qnx_value'] = {'resource-id':'version'}
        runner.navigate = Mock()
        runner.snapshot = Mock(return_value=ET.fromstring('<hierarchy><node resource-id="version" text="wrong"/></hierarchy>'))
        with self.assertRaises(RuntimeError):
            runner.verify('expected')

    def test_activation_failure_never_powers_off(self):
        runner = self.runner()
        runner.cfg.update(automation={'upgrade_navigation':[{}]}, validation_timeout=1,
                          flash_timeout=1, activation_timeout=1)
        runner.switch_to_car = Mock()
        runner.navigate = Mock()
        runner.phase = Mock(side_effect=[None, None, RuntimeError('activation failed')])
        runner.hardware = Mock()
        with self.assertRaises(RuntimeError):
            runner.flash()
        runner.hardware.assert_not_called()
