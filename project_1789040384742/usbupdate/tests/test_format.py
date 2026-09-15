import unittest
from unittest.mock import Mock, patch

from auto_update import AutomaticUpgrade
from volume import format_exfat


class FormatTests(unittest.TestCase):
    def test_invalid_targets_never_launch_formatter(self):
        with patch('volume.subprocess.run') as run:
            for root in ('C:/', 'F:/USB_UPDATE', 'F:', '//server/share', 'F:/../C:/'):
                with self.subTest(root=root), self.assertRaises(RuntimeError):
                    format_exfat(root)
            run.assert_not_called()

    def test_formatter_failure_is_not_success(self):
        with patch('volume.subprocess.run', return_value=Mock(returncode=1, stdout='', stderr='denied')):
            with self.assertRaisesRegex(RuntimeError, 'denied'):
                format_exfat('F:/')

    def runner(self):
        runner = AutomaticUpgrade.__new__(AutomaticUpgrade)
        runner.cfg = {'usb_root': 'F:/'}
        for name in ('preflight', 'connect', 'switch_to_pc', 'event', 'flash'):
            setattr(runner, name, Mock())
        return runner

    def test_local_never_formats_or_downloads(self):
        runner = self.runner()
        runner.local_package = Mock(return_value=None)
        with patch('auto_update.ctypes.windll.kernel32.GetDriveTypeW', return_value=2), \
                patch('auto_update.format_exfat') as formatter, \
                patch('cloud_download.download_latest') as download:
            runner.run(local=True)
        formatter.assert_not_called()
        download.assert_not_called()
        runner.flash.assert_not_called()

    def test_format_failure_stops_download_and_flash(self):
        runner = self.runner()
        with patch('auto_update.ctypes.windll.kernel32.GetDriveTypeW', return_value=2), \
                patch('auto_update.format_exfat', side_effect=RuntimeError('format failed')), \
                patch('cloud_download.download_latest', side_effect=lambda *args, **kwargs: kwargs['prepare_destination']()) as download:
            with self.assertRaisesRegex(RuntimeError, 'format failed'):
                runner.run()
        download.assert_called_once()
        runner.flash.assert_not_called()

    def test_missing_today_package_never_formats(self):
        runner = self.runner()
        with patch('auto_update.ctypes.windll.kernel32.GetDriveTypeW', return_value=2), \
                patch('auto_update.format_exfat') as formatter, \
                patch('cloud_download.download_latest', side_effect=RuntimeError('no today build')):
            with self.assertRaisesRegex(RuntimeError, 'no today build'):
                runner.run()
        formatter.assert_not_called()
        runner.flash.assert_not_called()
