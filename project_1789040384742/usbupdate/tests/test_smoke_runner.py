import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from smoke_runner import discover, run_pytest
from auto_update import AutomaticUpgrade


class SmokeTests(unittest.TestCase):
    def test_numeric_order_and_backup_exclusion(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            cases = root / 'tests_scripts'
            cases.mkdir()
            names = ['test_smoke_test_10.py', 'test_smoke_test_2.py', 'test_smoke_test_7.1.py',
                     'test_smoke_test_7_row6.py', 'test_smoke_test_7.py', 'test_smoke_test_7_row5.py',
                     'test_smoke_test_50 copy.py', 'test.py']
            for name in names:
                (cases / name).touch()
            _, files = discover({'smoke': {'project_root': folder}})
            self.assertEqual([p.name for p in files], ['test_smoke_test_2.py', 'test_smoke_test_7.py',
                             'test_smoke_test_7_row5.py', 'test_smoke_test_7_row6.py',
                             'test_smoke_test_7.1.py', 'test_smoke_test_10.py'])

    def test_failed_version_prevents_smoke(self):
        runner = AutomaticUpgrade.__new__(AutomaticUpgrade)
        runner.verify = Mock(side_effect=RuntimeError('wrong date'))
        with patch('smoke_runner.run_smoke') as run:
            with self.assertRaises(RuntimeError):
                runner.verify_and_smoke()
            run.assert_not_called()

    def test_successful_verification_runs_smoke(self):
        runner = AutomaticUpgrade.__new__(AutomaticUpgrade)
        runner.cfg, runner.logs, runner.event = {}, Path('.'), Mock()
        runner.verify = Mock()
        with patch('smoke_runner.run_smoke') as run:
            runner.verify_and_smoke()
            runner.verify.assert_called_once_with('', date_only=True)
            run.assert_called_once_with(runner.cfg, runner.logs, runner.event)

    def test_serial_execution_continues_after_failure_and_reports(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'tests_scripts').mkdir()
            for n in (2, 10):
                (root / 'tests_scripts' / f'test_smoke_test_{n}.py').touch()
            calls = []
            def execute(args, **kwargs):
                calls.append(args)
                junit = Path(next(arg.split('=', 1)[1] for arg in args if arg.startswith('--junitxml=')))
                failure = int(len(calls) == 1)
                junit.write_text(f'<testsuites><testsuite tests="1" failures="{failure}" errors="0" skipped="0"/></testsuites>')
                self.assertEqual(kwargs['cwd'], root)
                return Mock(returncode=failure)
            with patch('smoke_runner.subprocess.run', side_effect=execute):
                with self.assertRaisesRegex(RuntimeError, '1/2'):
                    run_pytest({'smoke': {'project_root': folder}}, root / 'logs', Mock())
            self.assertEqual(len(calls), 2)
            report = json.loads((root / 'logs/smoke/summary.json').read_text())
            self.assertEqual([r['passed'] for r in report], [False, True])
