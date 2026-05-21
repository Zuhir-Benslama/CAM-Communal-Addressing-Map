"""Tests for mixins/report_mixin.py."""
import importlib
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from .helpers import setup_gui_mocks


class TestReportMixin(unittest.TestCase):
    """Test ReportMixin statistical report and purchase order generation."""

    @classmethod
    def setUpClass(cls):
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.mixins.report_mixin',
            'mixins/report_mixin.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.mixins.report_mixin'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.mod.TMP_JSON = os.path.join(self.tmpdir, 'report.json')
        self.mod.REPORTING_SCRIPT = '/fake/report.py'
        self.mod._SUBPROCESS_FLAGS = {}

        host = type('Host', (), {'_tr': lambda self, s: s})()
        self.mixin = self.mod.ReportMixin()
        self.mixin._tr = lambda s: s
        self.mixin.current_user = {'wilaya': '16', 'commune': 'Algiers'}

        self.mod.count_numberings = MagicMock(return_value=5)
        self.mod.count_panels = MagicMock(return_value=3)
        self.mod.query_missing_pan = MagicMock(return_value=[{'id': 1}])
        self.mod.query_missing_num = MagicMock(return_value=[{'id': 2}])
        self.mod.query_missing_rep = MagicMock(return_value=[{'id': 3}])

        sub_run = MagicMock()
        sub_run.return_value = MagicMock()
        self._subprocess_patch = patch.object(self.mod, 'subprocess')
        self.mock_subprocess = self._subprocess_patch.start()
        self.mock_subprocess.run = sub_run
        self.mock_subprocess.CalledProcessError = type('CalledProcessError', (Exception,), {})
        self.mock_subprocess.run.side_effect = None

        msgbox = MagicMock()
        msgbox.return_value = msgbox
        self._qmsg_patch = patch.object(self.mod, 'QMessageBox')
        self.mock_qmsg = self._qmsg_patch.start()
        self.mock_qmsg.Information = 1
        self.mock_qmsg.Critical = 2
        self.mock_qmsg.return_value = MagicMock()

    def tearDown(self):
        self._subprocess_patch.stop()
        self._qmsg_patch.stop()
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_gen_report_success(self):
        result = self.mixin.gen_report()
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.mod.TMP_JSON))
        import json
        with open(self.mod.TMP_JSON) as f:
            data = json.load(f)
        self.assertEqual(data['wilaya'], '16')
        self.assertEqual(data['commune'], 'Algiers')

    def test_gen_report_json_write_failure(self):
        self.mod.TMP_JSON = '/nonexistent/dir/report.json'
        result = self.mixin.gen_report()
        self.assertFalse(result)

    def test_gen_report_subprocess_failure(self):
        self.mock_subprocess.run.side_effect = self.mock_subprocess.CalledProcessError
        result = self.mixin.gen_report()
        self.assertFalse(result)
        self.assertTrue(os.path.exists(self.mod.TMP_JSON))

    def test_gen_report_unexpected_exception(self):
        self.mock_subprocess.run.side_effect = RuntimeError('unexpected')
        result = self.mixin.gen_report()
        self.assertFalse(result)

    def test_bon_commande_success(self):
        result = self.mixin.bon_commande()
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.mod.TMP_JSON))
        import json
        with open(self.mod.TMP_JSON) as f:
            data = json.load(f)
        self.assertEqual(data['wilaya'], '16')

    def test_bon_commande_json_write_failure(self):
        self.mod.TMP_JSON = '/nonexistent/dir/report.json'
        result = self.mixin.bon_commande()
        self.assertFalse(result)

    def test_bon_commande_subprocess_failure(self):
        self.mock_subprocess.run.side_effect = self.mock_subprocess.CalledProcessError
        result = self.mixin.bon_commande()
        self.assertFalse(result)

    def test_bon_commande_unexpected_exception(self):
        self.mock_subprocess.run.side_effect = RuntimeError('unexpected')
        result = self.mixin.bon_commande()
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
