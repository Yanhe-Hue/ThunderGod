import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from daily_update import run_daily, wait_next_day


class DailyTests(unittest.TestCase):
    def test_ci_once_returns_after_success_and_does_not_repeat(self):
        with tempfile.TemporaryDirectory() as folder:
            cfg = {'daily_state_file': str(Path(folder) / 'state.json'), 'variant': 'gas',
                   'smoke': {'enabled': True}, 'cloud': {'url': 'url', 'path': []}}
            runner = Mock(logs=folder, entry={'build_date': '2026-09-16', 'sha256': 'sha'})
            runner.run.return_value = True
            with patch('daily_update.now', return_value=dt.datetime(2026, 9, 16, 1)), \
                    patch('daily_update.AutomaticUpgrade', return_value=runner) as factory, \
                    patch('daily_update.wait_next_day') as wait:
                run_daily(cfg, Mock(), once=True)
                run_daily(cfg, Mock(), once=True)
                self.assertEqual(factory.call_count, 1)
                self.assertEqual(factory.call_args.args[0]['_cloud_wait_timeout_seconds'], 7200)
                wait.assert_not_called()

    def test_midnight_wait_uses_bounded_sleeps(self):
        before = dt.datetime(2026, 9, 16, 23, 59, 30)
        after = dt.datetime(2026, 9, 17)
        with patch('daily_update.now', side_effect=[before, before, after]), patch('daily_update.time.sleep') as sleep:
            wait_next_day(before.date(), Mock())
        sleep.assert_called_once_with(30)

    def test_success_waits_and_restart_does_not_repeat_completed_day(self):
        with tempfile.TemporaryDirectory() as folder:
            state = Path(folder) / 'state.json'
            cfg = {'daily_state_file': str(state), 'variant': 'gas', 'usb_serial': 'device',
                   'cloud': {'url': 'url', 'path': ['builds']}}
            runner = Mock(logs=Path(folder), entry={'build_date': '2026-09-16', 'sha256': 'sha'})
            runner.run.return_value = True
            with patch('daily_update.now', return_value=dt.datetime(2026, 9, 16, 22)), \
                    patch('daily_update.AutomaticUpgrade', return_value=runner) as factory, \
                    patch('daily_update.wait_next_day', side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    run_daily(cfg, Mock())
                self.assertEqual(factory.call_count, 1)
                factory.reset_mock()
                with self.assertRaises(KeyboardInterrupt):
                    run_daily(cfg, Mock())
                factory.assert_not_called()
            self.assertEqual(next(iter(json.loads(state.read_text()).values()))['completed_build_date'], '2026-09-16')

    def test_cross_midnight_completion_immediately_checks_next_date(self):
        with tempfile.TemporaryDirectory() as folder:
            cfg = {'daily_state_file': str(Path(folder) / 'state.json'), 'variant': 'gas',
                   'cloud': {'url': 'url', 'path': []}}
            first = Mock(logs=folder, entry={'build_date': '2026-09-16', 'sha256': 'a'})
            first.run.return_value = True
            second = Mock(logs=folder)
            second.run.side_effect = KeyboardInterrupt()
            with patch('daily_update.now', return_value=dt.datetime(2026, 9, 17, 1)), \
                    patch('daily_update.AutomaticUpgrade', side_effect=[first, second]) as factory, \
                    patch('daily_update.wait_next_day') as wait:
                with self.assertRaises(KeyboardInterrupt):
                    run_daily(cfg, Mock())
                wait.assert_not_called()
                self.assertEqual(factory.call_count, 2)

    def test_failure_never_marks_day_complete(self):
        with tempfile.TemporaryDirectory() as folder:
            state = Path(folder) / 'state.json'
            cfg = {'daily_state_file': str(state), 'variant': 'gas', 'cloud': {'url': 'url', 'path': []}}
            runner = Mock(logs=folder)
            runner.run.side_effect = RuntimeError('smoke failed')
            with patch('daily_update.AutomaticUpgrade', return_value=runner), self.assertRaises(RuntimeError):
                run_daily(cfg, Mock())
            self.assertFalse(state.exists())
