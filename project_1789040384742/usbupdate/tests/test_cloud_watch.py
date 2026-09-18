import datetime as dt
import tempfile
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from cloud_download import pending_build, wait_for_today
from error_evidence import capture


class WatchTests(unittest.TestCase):
    def test_ci_wait_has_deadline(self):
        scan = Mock(return_value=None)
        cfg = {'variant': 'gas', 'cloud': {}, '_cloud_wait_timeout_seconds': 1}
        with patch('cloud_download.time.monotonic', side_effect=[0, 0, 0, 2]), \
                patch('cloud_download.time.sleep'), self.assertRaisesRegex(RuntimeError, '超时'):
            wait_for_today(scan, cfg, Mock())
        scan.assert_called_once()

    def test_waits_then_returns_without_downloading_old_category(self):
        scan = Mock(side_effect=[None, None, ('today', {'name': 'pkg'})])
        with patch('cloud_download.time.sleep') as sleep:
            result = wait_for_today(scan, {'variant': 'gas', 'cloud': {}}, Mock())
        self.assertEqual(result[0], 'today')
        self.assertEqual(sleep.call_count, 2)

    def test_only_today_latest_for_selected_variant(self):
        today = dt.date.today().strftime('%Y%m%d')
        yesterday = (dt.date.today() - dt.timedelta(days=1)).strftime('%Y%m%d')
        self.assertIsNone(pending_build([yesterday + '_230000_full_userdebug', today + '_120000_userdebug'], 'gas'))
        latest = today + '_130000_full_userdebug'
        self.assertEqual(pending_build([latest, today + '_120000_full_userdebug'], 'gas'), latest)

    def test_network_error_is_not_silently_retried(self):
        with patch('cloud_download.time.sleep') as sleep:
            with self.assertRaisesRegex(RuntimeError, 'login'):
                wait_for_today(Mock(side_effect=RuntimeError('login')), {'variant': 'gas', 'cloud': {}}, Mock())
            sleep.assert_not_called()

    def test_smoke_failure_does_not_capture(self):
        with patch('error_evidence.subprocess.run') as command:
            capture(Mock(_smoke_started=True), RuntimeError('smoke'))
            command.assert_not_called()

    def test_failed_screenshot_keeps_exception_and_logcat(self):
        with tempfile.TemporaryDirectory() as folder:
            runner = Mock(logs=Path(folder), adb='adb', serial='device', _smoke_started=False)
            results = [Mock(returncode=1, stdout=b'', stderr=b'offline'),
                       Mock(returncode=0, stdout=b'logcat', stderr=b''),
                       Mock(returncode=0, stdout=b'devices', stderr=b'')]
            with patch('error_evidence.subprocess.run', side_effect=results):
                capture(runner, RuntimeError('upgrade failed'))
            self.assertIn('upgrade failed', (Path(folder) / 'error/exception.txt').read_text())
            self.assertEqual((Path(folder) / 'error/logcat.txt').read_bytes(), b'logcat')
            self.assertIn('offline', (Path(folder) / 'error/capture_status.txt').read_text())
