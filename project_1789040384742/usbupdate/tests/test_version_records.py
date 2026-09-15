import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
from version_records import resolve_expected, explicit_versions


class VersionRecordTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.original = Path.cwd()
        os.chdir(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(os.chdir, self.original)
        self.folder = '/group/branch/20260914_080544_thundergod_full_userdebug'
        self.receipt = {'folder': self.folder, 'sha256': 'a' * 64, 'expected_qnx': ''}
        Path('prepared_package.json').write_text(json.dumps(self.receipt))
        self.cfg = {'cloud': {'expected_qnx_by_build': {}}}

    def test_uses_matching_sha_not_other_package(self):
        Path('packages.json').write_text(json.dumps([
            dict(self.receipt, expected_qnx='correct'),
            dict(self.receipt, sha256='b' * 64, expected_qnx='wrong')]))
        self.assertEqual(resolve_expected(self.cfg, Mock()), 'correct')

    def test_exact_build_release_and_cached_second_check(self):
        with patch('cloud_download.fetch_release_version', return_value='qnx-target') as fetch:
            self.assertEqual(resolve_expected(self.cfg, Mock()), 'qnx-target')
            fetch.assert_called_once()
            self.assertEqual(fetch.call_args.args[1], self.folder)
        with patch('cloud_download.fetch_release_version') as fetch:
            self.assertEqual(resolve_expected(self.cfg, Mock()), 'qnx-target')
            fetch.assert_not_called()

    def test_conflicting_records_fail(self):
        Path('packages.json').write_text(json.dumps([dict(self.receipt, expected_qnx='one')]))
        self.cfg['cloud']['expected_qnx_by_build'][self.folder.rsplit('/', 1)[-1]] = 'two'
        with self.assertRaisesRegex(RuntimeError, '冲突'):
            resolve_expected(self.cfg, Mock())

    def test_missing_release_version_does_not_guess_date(self):
        with patch('cloud_download.fetch_release_version', return_value=''):
            with self.assertRaisesRegex(RuntimeError, '未提供明确'):
                resolve_expected(self.cfg, Mock())

    def test_release_text_explicit_keys_only(self):
        self.assertEqual(explicit_versions('Build date: 20260914\nQNX system version: 1.01.05.61-260911_023700'),
                         {'1.01.05.61-260911_023700'})
        self.assertEqual(explicit_versions('{"qnx_version":"exact"}'), {'exact'})
        self.assertEqual(explicit_versions('Build date: 20260914'), set())
