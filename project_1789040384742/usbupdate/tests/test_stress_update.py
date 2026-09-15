import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
import xml.etree.ElementTree as ET

from stress_update import run_stress
from auto_update import AutomaticUpgrade


class StressTests(unittest.TestCase):
    def test_reuses_package_and_never_enables_smoke(self):
        with tempfile.TemporaryDirectory() as folder:
            controller = Mock(logs=Path(folder))
            rounds = []
            entry = {'sha256': 'a' * 64, 'source': 'F:/USB_UPDATE/Update.zip'}
            def create(cfg, reusable):
                runner = Mock(logs=Path(folder), entry=entry)
                runner.run.return_value = True
                rounds.append((copy.deepcopy(cfg), reusable, runner))
                if len(rounds) == 4:
                    runner.run.side_effect = KeyboardInterrupt()
                return runner
            with patch('stress_update.Upgrade', return_value=controller), patch('stress_update.StressRound', side_effect=create):
                with self.assertRaises(KeyboardInterrupt):
                    run_stress({'smoke': {'enabled': True}})
            self.assertEqual(len(rounds), 4)
            self.assertIsNone(rounds[0][1])
            self.assertEqual(rounds[1][1], entry)
            for cfg, _, runner in rounds:
                self.assertFalse(cfg['smoke']['enabled'])
                runner.run.assert_called_once_with(local=True)
            report = json.loads((Path(folder) / 'stress_summary.json').read_text())
            self.assertEqual(report['status'], 'cancelled')
            self.assertEqual([r['status'] for r in report['rounds']], ['passed'] * 3 + ['cancelled'])
            self.assertIsNone(report['requested_rounds'])

    def test_failure_stops_later_rounds(self):
        with tempfile.TemporaryDirectory() as folder:
            controller = Mock(logs=Path(folder))
            first = Mock(logs=Path(folder), entry={'sha256': 'a' * 64})
            first.run.return_value = True
            second = Mock(logs=Path(folder))
            second.run.side_effect = RuntimeError('installation failed')
            with patch('stress_update.Upgrade', return_value=controller), \
                    patch('stress_update.StressRound', side_effect=[first, second]) as factory:
                with self.assertRaisesRegex(RuntimeError, 'installation failed'):
                    run_stress({})
            self.assertEqual(factory.call_count, 2)
            report = json.loads((Path(folder) / 'stress_summary.json').read_text())
            self.assertEqual(report['status'], 'stopped')

    def test_stale_installation_cannot_count_as_new_round(self):
        runner = AutomaticUpgrade.__new__(AutomaticUpgrade)
        runner.cfg = {'_stress_round': 2, 'ui': {
            'validation_done': {'text': 'verified'}, 'flash_done': {'text': 'installed'},
            'start': {'text': 'Start'}}}
        runner.snapshot = Mock(return_value=ET.fromstring('<hierarchy><node text="installed"/></hierarchy>'))
        runner.click = Mock()
        with self.assertRaisesRegex(RuntimeError, '每轮实际重新安装'):
            runner.phase('start', 'validation_done', 'done', 1)
        runner.click.assert_not_called()
