"""Tests for mixins.report_mixin."""

import importlib
import sys
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
            patch.object(self.mod, 'get_qgis_python', return_value='python3'),
            patch.object(self.mod, 'REPORTING_SCRIPT', '/tmp/script.py'),
            patch('builtins.open', MagicMock()),
            patch('json.dump'),
            patch.object(self.mod, 'subprocess') as mock_sub,
            patch.object(self.mod, 'QMessageBox'),
        ):
            mock_sub.run.return_value = MagicMock(returncode=0)
            mock_sub.CalledProcessError = type('CalledProcessError', (Exception,), {})
            result = self.mixin.generate_report()
            self.assertTrue(result)

    def test_purchase_order_success(self):
        with (
            patch.object(self.mod, 'TMP_JSON', '/tmp/test_order.json'),
            patch.object(self.mod, 'get_qgis_python', return_value='python3'),
            patch.object(self.mod, 'REPORTING_SCRIPT', '/tmp/script.py'),
            patch('builtins.open', MagicMock()),
            patch('json.dump'),
            patch.object(self.mod, 'subprocess') as mock_sub,
            patch.object(self.mod, 'QMessageBox'),
        ):
            mock_sub.run.return_value = MagicMock(returncode=0)
            mock_sub.CalledProcessError = type('CalledProcessError', (Exception,), {})
            result = self.mixin.purchase_order()
            self.assertTrue(result)

    def test_json_write_error_returns_false(self):
        with (
            patch.object(self.mod, 'TMP_JSON', '/tmp/opencode'),
            patch.object(self.mod, 'get_qgis_python', return_value='python3'),
        ):
            result = self.mixin.generate_report()
        self.assertFalse(result)

    def test_generate_report_process_error(self):
        with (
            patch.object(self.mod, 'TMP_JSON', '/tmp/test_report_err.json'),
            patch.object(self.mod, 'get_qgis_python', return_value='python3'),
            patch.object(self.mod, 'REPORTING_SCRIPT', '/tmp/script.py'),
            patch('json.dump'),
            patch.object(self.mod, 'subprocess') as mock_sub,
            patch.object(self.mod, 'QMessageBox') as mock_box,
        ):
            err_cls = type('CalledProcessError', (Exception,), {})
            mock_sub.CalledProcessError = err_cls
            mock_sub.run.side_effect = err_cls(1, 'cmd')
            result = self.mixin.generate_report()
            self.assertFalse(result)
            self.assertEqual(mock_box.return_value.setIcon.call_count, 1)

    def test_generate_report_oserror(self):
        with (
            patch.object(self.mod, 'TMP_JSON', '/tmp/test_report_err2.json'),
            patch.object(self.mod, 'get_qgis_python', return_value='python3'),
            patch.object(self.mod, 'REPORTING_SCRIPT', '/tmp/script.py'),
            patch('json.dump'),
            patch.object(self.mod, 'subprocess') as mock_sub,
            patch.object(self.mod, 'QMessageBox'),
        ):
            mock_sub.CalledProcessError = type('CalledProcessError', (Exception,), {})
            mock_sub.run.side_effect = OSError('spawn failed')
            result = self.mixin.generate_report()
            self.assertFalse(result)

    def test_purchase_order_process_error(self):
        with (
            patch.object(self.mod, 'TMP_JSON', '/tmp/test_order_err.json'),
            patch.object(self.mod, 'get_qgis_python', return_value='python3'),
            patch.object(self.mod, 'REPORTING_SCRIPT', '/tmp/script.py'),
            patch('json.dump'),
            patch.object(self.mod, 'subprocess') as mock_sub,
            patch.object(self.mod, 'QMessageBox') as mock_box,
        ):
            err_cls = type('CalledProcessError', (Exception,), {})
            mock_sub.CalledProcessError = err_cls
            mock_sub.run.side_effect = err_cls(1, 'cmd')
            result = self.mixin.purchase_order()
            self.assertFalse(result)
            self.assertEqual(mock_box.return_value.setIcon.call_count, 1)
