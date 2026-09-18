import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from usb_stress import expected_date, validate_settings, run, usb_package, PackageRound
import zipfile


class IndependentStressTests(unittest.TestCase):
    def test_modified_source_cannot_replace_active_package(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'USB_UPDATE').mkdir()
            active = root / 'USB_UPDATE/Update.zip'
            active.write_bytes(b'previous')
            source = root / 'B.zip'
            source.write_bytes(b'changed')
            runner = PackageRound.__new__(PackageRound)
            runner.cfg = {'_stress_replace': True}
            runner.package = {'source': str(source), 'sha256': '0' * 64, 'expected_date': '2026-09-16'}
            runner.event = Mock()
            with self.assertRaisesRegex(RuntimeError, '原始安装包被修改'):
                runner.local_package(root)
            self.assertEqual(active.read_bytes(), b'previous')

    def test_usb_originals_preserved_when_replacing_active_package(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            originals = root / 'versions'
            originals.mkdir()
            entries = []
            for name in ('A', 'B'):
                source = originals / (name + '.zip')
                with zipfile.ZipFile(source, 'w') as archive:
                    archive.writestr('payload', name)
                entries.append(usb_package({'path': str(source), 'expected_date': '2026-09-16'}, root))
            for entry in entries + entries[:1]:
                runner = PackageRound.__new__(PackageRound)
                runner.package = entry
                runner.event = Mock()
                runner.local_package(root)
                self.assertEqual((root / 'USB_UPDATE/Update.zip').read_bytes(), Path(entry['source']).read_bytes())
            self.assertTrue(all(Path(entry['source']).is_file() for entry in entries))
            with self.assertRaisesRegex(RuntimeError, '目录外'):
                usb_package({'path': str(root / 'USB_UPDATE/Update.zip')}, root)

    def test_usb_smoke_mode_enables_cases_and_alternates(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            cfg = {'usb_root': folder, 'smoke': {'enabled': False}, 'stress': {
                'mode': 'usb_pair_smoke', 'packages': [{'path': 'A'}, {'path': 'B'}]}}
            entries = [{'sha256': 'A', 'expected_date': '2026-09-14', 'expected_qnx': ''},
                       {'sha256': 'B', 'expected_date': '2026-09-15', 'expected_qnx': ''}]
            seen = []
            def create(config, package):
                self.assertTrue(config['smoke']['enabled'])
                self.assertEqual(config['smoke']['case_directory'], 'usbupdate/smoke_cases')
                seen.append(package['sha256'])
                runner = Mock(logs=root)
                runner.run.return_value = True
                if len(seen) == 3:
                    runner.run.side_effect = KeyboardInterrupt()
                return runner
            with patch('smoke_runner.discover'), patch('usb_stress.AutomaticUpgrade', return_value=Mock(logs=root)), \
                    patch('usb_stress.usb_package', side_effect=entries), patch('usb_stress.PackageRound', side_effect=create), \
                    patch('usb_stress.cache_package') as cache:
                with self.assertRaises(KeyboardInterrupt):
                    run(cfg)
                cache.assert_not_called()
            self.assertEqual(seen, ['A', 'B', 'A'])

    def test_cloud_downloads_once_and_reuses(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            log = root / 'logs'
            log.mkdir()
            cfg = {'usb_root': str(root / 'usb'), 'stress': {'mode': 'cloud',
                   'cache_dir': str(root / 'cache')}}
            runner = Mock(logs=log)
            runner.run.side_effect = [True, True, KeyboardInterrupt()]
            entry = {'source': 'download.zip', 'build_date': '2026-09-15'}
            def download(*args, **kwargs):
                kwargs['prepare_destination']()
                return entry
            with patch('usb_stress.AutomaticUpgrade', return_value=Mock(logs=log)), \
                    patch('cloud_download.download_latest', side_effect=download) as fetch, \
                    patch('volume.format_exfat') as format_usb, \
                    patch('usb_stress.cache_package', return_value={'sha256': 'a', 'expected_date': '2026-09-15'}) as cache, \
                    patch('usb_stress.PackageRound', return_value=runner):
                with self.assertRaises(KeyboardInterrupt):
                    run(cfg)
            self.assertEqual(fetch.call_count, 1)
            format_usb.assert_called_once_with(cfg['usb_root'])
            self.assertEqual(cache.call_args.args[-1], '2026-09-15')
            self.assertEqual(runner.run.call_count, 3)

    def test_dates_use_package_not_today(self):
        with patch('usb_stress.qnx_version', return_value='1.2-260914_123000'):
            self.assertEqual(expected_date('unused'), '2026-09-14')
        with patch('usb_stress.qnx_version', side_effect=RuntimeError()):
            self.assertEqual(expected_date('unused', fallback='2026-09-13'), '2026-09-13')
            with self.assertRaises(RuntimeError):
                expected_date('unused')
        self.assertEqual(expected_date('unused', '2026-09-12'), '2026-09-12')

    def test_pair_requires_two_packages(self):
        with self.assertRaises(RuntimeError):
            validate_settings({'mode': 'local_pair', 'packages': [{'path': 'a.zip'}]})

    def test_pair_alternates_and_stops_without_smoke(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            log = root / 'logs'
            log.mkdir()
            cfg = {'usb_root': str(root / 'usb'), 'smoke': {'enabled': True},
                   'stress': {'mode': 'local_pair', 'cache_dir': str(root / 'cache'),
                              'packages': [{'path': 'a.zip'}, {'path': 'b.zip'}]}}
            packages = [{'sha256': 'a', 'expected_date': '2026-09-14'},
                        {'sha256': 'b', 'expected_date': '2026-09-15'}]
            seen = []
            def make_round(config, package):
                self.assertFalse(config['smoke']['enabled'])
                self.assertEqual(config['_stress_expected_date'], package['expected_date'])
                seen.append(package['sha256'])
                runner = Mock(logs=log)
                runner.run.return_value = True
                if len(seen) == 4:
                    runner.run.side_effect = KeyboardInterrupt()
                return runner
            with patch('usb_stress.AutomaticUpgrade', return_value=Mock(logs=log)), \
                    patch('usb_stress.cache_package', side_effect=packages), \
                    patch('usb_stress.PackageRound', side_effect=make_round):
                with self.assertRaises(KeyboardInterrupt):
                    run(cfg)
            self.assertEqual(seen, ['a', 'b', 'a', 'b'])
            report = json.loads((log / 'stress_summary.json').read_text())
            self.assertEqual(report['status'], 'cancelled')
            self.assertEqual([r['status'] for r in report['rounds']], ['passed'] * 3 + ['cancelled'])

    def test_failed_round_does_not_continue(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            log = root / 'logs'
            log.mkdir()
            cfg = {'usb_root': str(root / 'usb'), 'stress': {'mode': 'local_single',
                   'cache_dir': str(root / 'cache'), 'packages': [{'path': 'a.zip'}]}}
            runner = Mock(logs=log)
            runner.run.side_effect = RuntimeError('flash failure')
            with patch('usb_stress.AutomaticUpgrade', return_value=Mock(logs=log)), \
                    patch('usb_stress.cache_package', return_value={'sha256': 'a', 'expected_date': '2026-09-14'}), \
                    patch('usb_stress.PackageRound', return_value=runner) as factory:
                with self.assertRaisesRegex(RuntimeError, 'flash failure'):
                    run(cfg)
            self.assertEqual(factory.call_count, 1)
