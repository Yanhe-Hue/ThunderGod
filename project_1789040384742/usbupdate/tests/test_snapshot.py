import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from usb_update import Upgrade


class SnapshotTests(unittest.TestCase):
    def test_occupied_cli_uses_u2_and_reuses_reader(self):
        with tempfile.TemporaryDirectory() as folder:
            runner = Upgrade.__new__(Upgrade)
            runner.logs, runner.serial, runner.event = Path(folder), '3696ade', Mock()
            runner.adb_run = Mock(side_effect=RuntimeError('dump failed'))
            sdk = Mock()
            sdk.connect_usb.return_value.dump_hierarchy.return_value = '<hierarchy><node text="USB Upgrade"/></hierarchy>'
            with patch.dict('sys.modules', {'uiautomator2': sdk}):
                self.assertEqual(runner.snapshot().find('node').get('text'), 'USB Upgrade')
                runner.snapshot()
            runner.adb_run.assert_called_once()
            sdk.connect_usb.assert_called_once_with('3696ade')
            self.assertTrue((Path(folder) / 'last_ui.xml').exists())

    def test_empty_stderr_reports_command_and_exit_code(self):
        runner = Upgrade.__new__(Upgrade)
        runner.event = Mock()
        with patch('usb_update.subprocess.run', return_value=Mock(returncode=1, stdout=b'', stderr=b'')):
            with self.assertRaisesRegex(RuntimeError, '退出码 1.*uiautomator'):
                runner.command(['adb', 'shell', 'uiautomator', 'dump'])

    def test_empty_u2_tree_is_not_success(self):
        runner = Upgrade.__new__(Upgrade)
        runner._ui_reader = Mock()
        runner._ui_reader.dump_hierarchy.return_value = '<hierarchy/>'
        with self.assertRaisesRegex(RuntimeError, '页面树为空'):
            runner.snapshot()
