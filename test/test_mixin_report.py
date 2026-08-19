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
