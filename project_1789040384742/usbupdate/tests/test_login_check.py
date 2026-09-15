import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

from cloud_download import ensure_cloud_login
from usb_update import Upgrade


class LoginCheckTests(unittest.TestCase):
    def setup_browser(self, initial_errors=(), probe_error=None):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / 'cloud.json'
        cfg = {'cloud': {'url': 'https://pan.thundersoft.com/web/index.html', 'auth_state': str(path)}}
        browser = Mock()
        context, probe = Mock(), Mock()
        browser.new_context.side_effect = [context, probe]
        context.storage_state.return_value = {'cookies': [], 'origins': []}
        if initial_errors:
            context.new_page.return_value.get_by_text.return_value.first.wait_for.side_effect = initial_errors
        if probe_error:
            probe.new_page.return_value.get_by_text.return_value.first.wait_for.side_effect = probe_error
        runtime = Mock()
        runtime.chromium.launch.return_value = browser
        manager = Mock()
        manager.__enter__ = Mock(return_value=runtime)
        manager.__exit__ = Mock(return_value=False)
        module = types.ModuleType('playwright.sync_api')
        module.sync_playwright = Mock(return_value=manager)
        module.TimeoutError = TimeoutError
        return cfg, path, browser, context, module

    def test_valid_saved_session_reused_without_scan(self):
        cfg, path, browser, context, module = self.setup_browser()
        saved = {'cookies': [], 'origins': []}
        path.write_text(json.dumps(saved), encoding='utf8')
        event = Mock()
        with patch.dict('sys.modules', {'playwright.sync_api': module}):
            ensure_cloud_login(cfg, event)
        self.assertEqual(browser.new_context.call_args_list[0].kwargs, {'storage_state': saved})
        self.assertNotIn('CLOUD_LOGIN_REQUIRED', [call.args[0] for call in event.call_args_list])
        self.assertEqual(event.call_args_list[-1].args, ('CLOUD_LOGIN_READY',))
        browser.close.assert_called_once()

    def test_expired_session_scanned_and_verified(self):
        cfg, path, browser, context, module = self.setup_browser([TimeoutError(), None])
        event = Mock()
        with patch.dict('sys.modules', {'playwright.sync_api': module}):
            ensure_cloud_login(cfg, event)
        self.assertTrue(path.is_file())
        self.assertEqual([c.args[0] for c in event.call_args_list],
                         ['CLOUD_LOGIN_CHECK', 'CLOUD_LOGIN_REQUIRED', 'CLOUD_LOGIN_READY'])
        self.assertEqual(browser.new_context.call_count, 2)

    def test_fresh_context_failure_never_saves_session(self):
        cfg, path, browser, context, module = self.setup_browser(probe_error=TimeoutError())
        event = Mock()
        with patch.dict('sys.modules', {'playwright.sync_api': module}), self.assertRaises(RuntimeError):
            ensure_cloud_login(cfg, event)
        self.assertFalse(path.exists())
        self.assertNotIn('CLOUD_LOGIN_READY', [c.args[0] for c in event.call_args_list])
        browser.close.assert_called_once()

    def test_check_never_passes_when_login_fails(self):
        runner = Upgrade.__new__(Upgrade)
        runner.cfg = {}
        runner.adb = 'adb'
        runner.serial = '3696ade'
        runner.command = Mock()
        runner.event = Mock()
        with patch('importlib.util.find_spec', return_value=object()), \
             patch('cloud_download.ensure_cloud_login', side_effect=RuntimeError('login failed')), \
             self.assertRaises(RuntimeError):
            runner.check()
        self.assertNotIn('ENVIRONMENT_CHECK_PASSED', [c.args[0] for c in runner.event.call_args_list])
