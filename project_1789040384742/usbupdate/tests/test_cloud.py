import datetime as dt
import unittest

from cloud_download import select_build, select_file


class CloudTests(unittest.TestCase):
    def test_today_no_gas_does_not_allow_yesterday_gas(self):
        today = dt.date.today().strftime('%Y%m%d')
        yesterday = (dt.date.today() - dt.timedelta(days=1)).strftime('%Y%m%d')
        names = [yesterday + '_080544_thundergod_full_userdebug',
                 today + '_022746_thundergod_userdebug']
        with self.assertRaisesRegex(RuntimeError, 'gas.*最新日期'):
            select_build(names, 'gas', today_only=True)
        self.assertEqual(select_build(names, 'no_gas', today_only=True), names[1])
    def test_no_gas_excludes_newer_gas(self):
        day = dt.date.today().strftime('%Y%m%d')
        expected = day + '_120000_thundergod_userdebug'
        self.assertEqual(select_build([day + '_230000_thundergod_full_userdebug',
                                       day + '_010000_thundergod_userdebug', expected],
                                      'no_gas'), expected)

    def test_latest_timestamp_not_list_position(self):
        day = dt.date.today().strftime('%Y%m%d')
        newest = day + '_174415_thundergod_full_userdebug'
        self.assertEqual(select_build([newest, day + '_023550_thundergod_full_userdebug',
                                       day + '_190000_thundergod_userdebug'], 'gas'), newest)

    def test_incomplete_latest_never_uses_cdc_package(self):
        with self.assertRaises(RuntimeError):
            select_file([{'name': 'build_update_all_cdc_package.zip', 'size': 123}])

    def test_actual_renault_zip_selected(self):
        expected = {'name': 'build_update_all_renault.zip', 'size': 123}
        self.assertIs(select_file([expected, {'name': 'build_update_target.zip', 'size': 123}]), expected)

    def test_old_build_blocked(self):
        yesterday = (dt.date.today() - dt.timedelta(days=1)).strftime('%Y%m%d')
        with self.assertRaises(RuntimeError):
            select_build([yesterday + '_174415_thundergod_full_userdebug'], 'gas', today_only=True)

    def test_latest_available_date_when_today_missing(self):
        yesterday = (dt.date.today() - dt.timedelta(days=1)).strftime('%Y%m%d')
        older = (dt.date.today() - dt.timedelta(days=3)).strftime('%Y%m%d')
        newest = yesterday + '_174415_thundergod_full_userdebug'
        self.assertEqual(select_build([newest, older + '_235959_thundergod_full_userdebug',
                                       yesterday + '_023550_thundergod_full_userdebug'], 'gas'), newest)

    def test_ambiguous_file_blocked(self):
        with self.assertRaises(RuntimeError):
            select_file([{'name': 'a_update_all_renault.zip', 'size': 1}, {'name': 'b_update_all_renault.zip', 'size': 1}])


if __name__ == '__main__':
    unittest.main()
