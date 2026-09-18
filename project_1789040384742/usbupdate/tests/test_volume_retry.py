import ctypes
from ctypes import wintypes
import unittest
from unittest.mock import Mock, patch
from volume import lock_volume


class LockTests(unittest.TestCase):
    def test_busy_lock_retries_then_succeeds(self):
        kernel = Mock()
        kernel.DeviceIoControl.side_effect = [0, 1]
        with patch('volume.ctypes.get_last_error', return_value=5), patch('volume.time.sleep') as sleep:
            lock_volume(kernel, 1, wintypes.DWORD())
        sleep.assert_called_once_with(2)
        self.assertEqual(kernel.DeviceIoControl.call_count, 2)

    def test_lock_timeout_does_not_dismount(self):
        kernel = Mock()
        kernel.DeviceIoControl.return_value = 0
        with patch('volume.ctypes.get_last_error', return_value=5), self.assertRaisesRegex(RuntimeError, '未强制'):
            lock_volume(kernel, 1, wintypes.DWORD(), timeout=0)
        self.assertEqual(kernel.DeviceIoControl.call_args.args[1], 0x90018)
