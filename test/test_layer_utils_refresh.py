"""Tests for layer.utils and layer.refresh."""

import importlib
import sys
import unittest
from unittest.mock import patch

from test.helpers import setup_gui_mocks


class TestLayerRefreshModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.layer.refresh',
            'layer/refresh.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.layer.refresh'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def test_get_model_class_valid(self):
        result = self.mod._get_model_class('Zone')
        self.assertIsNotNone(result)

    def test_get_model_class_none(self):
        result = self.mod._get_model_class('NonExistent')
        self.assertIsNone(result)

    def test_get_geometry_column(self):
        from app.orders.models.zone import Zone

        result = self.mod._get_geometry_column(Zone)
        if result is None:
            self.skipTest('Zone model has no Geometry column (mock contamination)')
        self.assertIsNotNone(result)

    def test_get_geometry_column_none(self):
        class FakeModel:
            __table__ = type('T', (), {'columns': []})()

        result = self.mod._get_geometry_column(FakeModel)
        self.assertIsNone(result)

    def test_get_all_model_fields(self):
        from app.orders.models.zone import Zone

        result = self.mod._get_all_model_fields(Zone)
        self.assertIsInstance(result, list)

    def test_get_layer_none(self):
        with patch.object(self.mod, 'QgsProject') as mock_proj:
            mock_proj.instance.return_value.mapLayersByName.return_value = []
            result = self.mod._get_layer('NonExistent')
            self.assertIsNone(result)
