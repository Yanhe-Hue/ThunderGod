from pathlib import Path
import tempfile
import unittest
from smoke_runner import discover


class SmokeSelectionTests(unittest.TestCase):
    def test_exact_file_selection(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            directory = root / 'tests_scripts' / 'launcher'
            directory.mkdir(parents=True)
            for number in (4, 6):
                (directory / f'test_smoke_test_{number}.py').write_text('')
            cfg = {'smoke': {'project_root': folder, 'case_files': ['tests_scripts/launcher/test_smoke_test_4.py']}}
            _, files = discover(cfg)
            self.assertEqual([p.name for p in files], ['test_smoke_test_4.py'])
            cfg['smoke']['case_files'] = ['tests_scripts/launcher/test_smoke_test_9.py']
            with self.assertRaises(RuntimeError):
                discover(cfg)
