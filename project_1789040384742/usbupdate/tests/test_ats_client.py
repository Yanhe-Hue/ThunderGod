import json
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch
from ats_client import run_ats


class AtsTests(TestCase):
    def test_submits_ats_uri_and_uses_ats_result(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            logs = root / 'usbupdate/logs/test'
            def launch(uri):
                self.assertIn('vscode://local-usbupdate.usbupdate-ats-bridge/run?', uri)
                (logs / 'smoke/ats-result.json').write_text(json.dumps({'status': 'complete', 'result': {'total': 1, 'passed': 1}}))
            with patch('ats_client.os.startfile', side_effect=launch):
                run_ats({'usb_serial': '3696ade'}, root, [root / 'tests_scripts/test_smoke_test_3.py'], logs, Mock())
            request = json.loads((logs / 'smoke/ats-request.json').read_text())
            self.assertEqual(request['deviceId'], '3696ade')

    def test_ats_abort_is_not_success(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            logs = root / 'usbupdate/logs/test'
            def launch(uri):
                (logs / 'smoke/ats-result.json').write_text('{"status":"aborted"}')
            with patch('ats_client.os.startfile', side_effect=launch), self.assertRaisesRegex(RuntimeError, '未全部通过'):
                run_ats({}, root, [root / 'tests_scripts/test_smoke_test_3.py'], logs, Mock())
