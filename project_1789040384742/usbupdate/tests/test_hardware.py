import unittest
from unittest.mock import Mock, call, patch

from hardware import AutoCarHardware
from usb_update import Upgrade


class HardwareTests(unittest.TestCase):
    def adapter(self):
        at = Mock()
        at.usb_switch.return_value = {'success': True, 'response_port': 2}
        at.power_open.return_value.set_output.return_value = True
        cfg = {'usb_switch': {'port': 'COM14', 'pc_usb_port': 3, 'car_usb_port': 2},
               'power': {'resource': 'ASRL13::INSTR', 'off_seconds': 5}}
        return AutoCarHardware(cfg, Mock(), at), at

    def test_usb_correct_route(self):
        hw, at = self.adapter()
        hw.switch_usb('car')
        at.usb_switch.assert_called_once_with(port='COM14', usb_port=2)

    def test_pc_uses_usb3(self):
        hw, at = self.adapter()
        at.usb_switch.return_value = {'success': True, 'response_port': 3}
        hw.switch_usb('pc')
        at.usb_switch.assert_called_once_with(port='COM14', usb_port=3)

    def test_drive_timeout_reports_actual_drives(self):
        runner = Upgrade.__new__(Upgrade)
        runner.cfg = {'usb_root': 'E:/', 'usb_switch': {'enumeration_timeout': 0}}
        runner.hardware = Mock()
        runner.event = Mock()
        with patch('volume.removable_roots', return_value=['F:/']), self.assertRaisesRegex(RuntimeError, 'E:/.*F:/'):
            runner.switch_to_pc()
        runner.hardware.return_value.switch_usb.assert_called_once_with('pc')

    def test_unknown_channels_do_not_touch_hardware(self):
        for channels in [(None, 2), (1, 1), (0, 2), (True, 2)]:
            hw, at = self.adapter()
            hw.config['usb_switch'].update(pc_usb_port=channels[0], car_usb_port=channels[1])
            with self.subTest(channels=channels), self.assertRaises(RuntimeError):
                hw.switch_usb('car')
            at.usb_switch.assert_not_called()

    def test_usb_wrong_ack_stops(self):
        hw, at = self.adapter()
        at.usb_switch.return_value = {'success': True, 'response_port': 1}
        with self.assertRaises(RuntimeError):
            hw.switch_usb('car')

    def test_power_off_wait_on_in_order(self):
        hw, at = self.adapter()
        trace = Mock()
        trace.attach_mock(at, 'at')
        with patch('hardware.time.sleep') as sleep:
            trace.attach_mock(sleep, 'sleep')
            hw.power_cycle()
        self.assertEqual(trace.mock_calls, [call.at.power_open('ASRL13::INSTR'),
                         call.at.power_open().set_output(on=False), call.sleep(5),
                         call.at.power_open().set_output(on=True)])

    def test_failed_off_never_sends_on(self):
        hw, at = self.adapter()
        at.power_open.return_value.set_output.return_value = False
        with patch('hardware.time.sleep') as sleep, self.assertRaises(RuntimeError):
            hw.power_cycle()
        sleep.assert_not_called()
        at.power_open.return_value.set_output.assert_called_once_with(on=False)

    def test_failed_on_reported(self):
        hw, at = self.adapter()
        at.power_open.return_value.set_output.side_effect = [True, False]
        with patch('hardware.time.sleep'), self.assertRaises(RuntimeError):
            hw.power_cycle()

    def test_cancel_does_not_implicitly_power_on(self):
        hw, at = self.adapter()
        with patch('hardware.time.sleep', side_effect=KeyboardInterrupt), self.assertRaises(KeyboardInterrupt):
            hw.power_cycle()
        at.power_open.return_value.set_output.assert_called_once_with(on=False)

    def test_wired_connect_never_uses_tcpip(self):
        runner = Upgrade.__new__(Upgrade)
        runner.serial = 'TESTUSB123'
        runner.cfg = {}
        runner.adb_run = Mock(side_effect=['device', '1000'])
        runner.command = Mock()
        runner.event = Mock()
        with patch('usb_update.time.time', return_value=1000):
            runner.connect()
        runner.command.assert_not_called()
        self.assertEqual(runner.adb_run.call_args_list, [call('get-state'), call('shell', 'date', '+%s')])


if __name__ == '__main__':
    unittest.main()
