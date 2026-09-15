import datetime as dt
import unittest
from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET

from usb_update import Upgrade, choose_package


def package(folder='build_full_userdebug', days=0, **changes):
    value = dict(folder=folder, name='x_update_all_renault',
                 build_date=(dt.date.today() + dt.timedelta(days=days)).isoformat(),
                 expected_qnx='QNX-TEST', sha256='a' * 64, source='unused')
    value.update(changes)
    return value


class PackageTests(unittest.TestCase):
    def test_gas_and_no_gas_are_separate(self):
        gas, no_gas = package(), package('build_userdebug')
        self.assertIs(choose_package([no_gas, gas], 'gas'), gas)
        self.assertIs(choose_package([gas, no_gas], 'no_gas'), no_gas)

    def test_latest_date_and_future_exclusion(self):
        today = package()
        self.assertIs(choose_package([package(days=-1), package(days=1), today], 'gas'), today)

    def test_latest_available_default_and_optional_today_policy(self):
        old = package(days=-1)
        with self.assertRaises(RuntimeError):
            choose_package([old], 'gas', True)
        self.assertIs(choose_package([old], 'gas'), old)

    def test_ambiguous_daily_build_rejected(self):
        with self.assertRaises(RuntimeError):
            choose_package([package(), package('other_full_userdebug')], 'gas')

    def test_invalid_package_metadata_rejected(self):
        for changes in ({'sha256': ''}, {'expected_qnx': ''}, {'name': 'x_update_all_cdc_package.zip'}):
            with self.subTest(changes=changes), self.assertRaises(RuntimeError):
                choose_package([package(**changes)], 'gas')

    def test_invalid_variant_rejected(self):
        with self.assertRaises(RuntimeError):
            choose_package([package()], 'typo')

    def test_actual_zip_suffix_and_latest_build_time(self):
        date = dt.date.today().strftime('%Y%m%d')
        morning = package(date + '_023550_thundergod_full_userdebug', name='x_update_all_renault.zip')
        evening = package(date + '_174415_thundergod_full_userdebug', name='x_update_all_renault.zip')
        self.assertIs(choose_package([morning, evening], 'gas'), evening)


class StateTests(unittest.TestCase):
    def runner(self):
        runner = Upgrade.__new__(Upgrade)
        runner.cfg = {'ui': {'start': {'text': 'Start Update'},
                             'validation_done': {'text': 'Validated'},
                             'failure_selectors': [{'text': 'Error'}]}}
        runner.click = Mock()
        runner.event = Mock()
        return runner

    def test_stale_success_must_not_trigger_click(self):
        runner = self.runner()
        runner.snapshot = Mock(return_value=ET.fromstring('<hierarchy><node text="Validated"/></hierarchy>'))
        with self.assertRaises(RuntimeError):
            runner.phase('start', 'validation_done', 'done', 1)
        runner.click.assert_not_called()

    def test_error_stops_waiting_even_with_success_present(self):
        runner = self.runner()
        runner.snapshot = Mock(return_value=ET.fromstring('<hierarchy><node text="Error"/><node text="Validated"/></hierarchy>'))
        with self.assertRaises(RuntimeError):
            runner.wait_new_state({'text': 'Validated'}, 1, 'done')
        runner.event.assert_not_called()

    def test_click_then_wait_for_new_completion(self):
        runner = self.runner()
        runner.snapshot = Mock(side_effect=[ET.fromstring('<hierarchy/>'),
                                           ET.fromstring('<hierarchy><node text="Validated"/></hierarchy>')])
        runner.phase('start', 'validation_done', 'done', 1)
        runner.click.assert_called_once_with({'text': 'Start Update'})
        runner.event.assert_called_once_with('done')

    def test_cancel_manual_completion_stops_phase(self):
        runner = self.runner()
        runner.cfg['ui']['validation_done'] = None
        with patch('builtins.input', return_value='NO'), self.assertRaises(RuntimeError):
            runner.phase('start', 'validation_done', 'done', 1)
        runner.event.assert_not_called()


if __name__ == '__main__':
    unittest.main()
