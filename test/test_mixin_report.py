"""Tests for mixins.report_mixin."""

import importlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from test.helpers import setup_gui_mocks


class TestReportMixin(unittest.TestCase):
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
        self.mixin = self.mod.ReportMixin()
        self.mixin._tr = lambda s: s
        self.mixin._tr_locale = 'ar'
        self.mixin.current_user = {'wilaya': '16', 'commune': 'test'}
        self.mixin._output_dir = '/tmp'

    def test_generate_report_no_user(self):
        self.mixin.current_user = None
        result = self.mixin.generate_report()
        self.assertFalse(result)

    def test_purchase_order_no_user(self):
        self.mixin.current_user = None
        result = self.mixin.purchase_order()
        self.assertFalse(result)

    def test_generate_report_success(self):
        with (
            patch.object(self.mod, 'TMP_JSON', '/tmp/test_report.json'),
            patch.object(self.mod, 'run_reporting_script') as mock_run,
            patch('builtins.open', MagicMock()),
            patch('json.dump'),
            patch.object(self.mod, 'QMessageBox'),
        ):
            result = self.mixin.generate_report()
            self.assertTrue(result)
            mock_run.assert_called_once_with('2')

    def test_purchase_order_success(self):
        with (
            patch.object(self.mod, 'TMP_JSON', '/tmp/test_order.json'),
            patch.object(self.mod, 'run_reporting_script'),
            patch('builtins.open', MagicMock()),
            patch('json.dump'),
            patch.object(self.mod, 'QMessageBox'),
        ):
            result = self.mixin.purchase_order()
            self.assertTrue(result)

    def test_json_write_error_returns_false(self):
        # The system temp dir always exists and is a directory, so opening
        # it for writing raises IsADirectoryError (an OSError) everywhere.
        with patch.object(self.mod, 'TMP_JSON', tempfile.gettempdir()):
            result = self.mixin.generate_report()
        self.assertFalse(result)

    def test_generate_report_process_error(self):
        with (
            patch.object(self.mod, 'TMP_JSON', '/tmp/test_report_err.json'),
            patch('json.dump'),
            patch.object(self.mod, 'run_reporting_script') as mock_run,
            patch.object(self.mod, 'QMessageBox') as mock_box,
        ):
            mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')
            result = self.mixin.generate_report()
            self.assertFalse(result)
            self.assertEqual(mock_box.return_value.setIcon.call_count, 1)

    def test_generate_report_oserror(self):
        with (
            patch.object(self.mod, 'TMP_JSON', '/tmp/test_report_err2.json'),
            patch('json.dump'),
            patch.object(self.mod, 'run_reporting_script') as mock_run,
            patch.object(self.mod, 'QMessageBox'),
        ):
            mock_run.side_effect = OSError('spawn failed')
            result = self.mixin.generate_report()
            self.assertFalse(result)

    def test_purchase_order_process_error(self):
        with (
            patch.object(self.mod, 'TMP_JSON', '/tmp/test_order_err.json'),
            patch('json.dump'),
            patch.object(self.mod, 'run_reporting_script') as mock_run,
            patch.object(self.mod, 'QMessageBox') as mock_box,
        ):
            mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')
            result = self.mixin.purchase_order()
            self.assertFalse(result)
            self.assertEqual(mock_box.return_value.setIcon.call_count, 1)
