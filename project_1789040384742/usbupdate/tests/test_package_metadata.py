import json
import tempfile
import unittest
from pathlib import Path
import zipfile
from package_metadata import qnx_version

class MetadataTests(unittest.TestCase):
    def archive(self, files):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / 'Update.zip'
        with zipfile.ZipFile(path,'w') as archive:
            for name, data in files.items(): archive.writestr(name,data)
        return path

    def test_explicit_property(self):
        path = self.archive({'build.prop':'ro.vendor.version.qnx.full.name=1.01-test'})
        self.assertEqual(qnx_version(path),'1.01-test')

    def test_nested_json(self):
        path = self.archive({'manifest.json': json.dumps({'build':{'qnx_version':'1.02'}})})
        self.assertEqual(qnx_version(path),'1.02')

    def test_date_is_not_version(self):
        path = self.archive({'manifest.json':'{"build_date":"2026-09-14"}'})
        with self.assertRaises(RuntimeError): qnx_version(path)

    def test_conflicting_versions_fail(self):
        path = self.archive({'a.prop':'qnx_version=1', 'b.prop':'qnx_version=2'})
        with self.assertRaises(RuntimeError): qnx_version(path)
