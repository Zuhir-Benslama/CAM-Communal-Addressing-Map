"""Tests for layer/refresh.py."""
import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from .helpers import setup_mocks, make_mock_iface, make_mock_layer


class TestLayerRefresh(unittest.TestCase):
    """Test layer refresh and style functions."""

    @classmethod
    def setUpClass(cls):
        setup_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.layer.refresh', 'layer/refresh.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.layer.refresh'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.iface = make_mock_iface()
        self.layer = make_mock_layer()

    @patch('plans_adressage.layer.refresh.QgsProject')
    def test_apply_categorized_style(self, mock_project):
        mock_project.instance.return_value.mapLayersByName.return_value = [self.layer]
        feature = MagicMock()
        self.layer.getFeatures.return_value = [feature]
        self.mod.apply_categorized_style(self.iface, 'test_layer', ['type'])
        self.layer.setRenderer.assert_called_once()

    @patch('plans_adressage.layer.refresh.QgsProject')
    def test_apply_categorized_style_no_layer(self, mock_project):
        mock_project.instance.return_value.mapLayersByName.return_value = []
        self.mod.apply_categorized_style(self.iface, 'nonexistent', ['type'])
        self.layer.setRenderer.assert_not_called()

    @patch('plans_adressage.layer.refresh.QgsProject')
    def test_remove_categorized_style(self, mock_project):
        mock_project.instance.return_value.mapLayersByName.return_value = [self.layer]
        self.mod.remove_categorized_style(self.iface, 'test_layer')
        self.layer.setRenderer.assert_called_once()

    @patch('plans_adressage.layer.refresh.QgsProject')
    def test_remove_categorized_style_no_layer(self, mock_project):
        mock_project.instance.return_value.mapLayersByName.return_value = []
        self.mod.remove_categorized_style(self.iface, 'nonexistent')
        self.layer.setRenderer.assert_not_called()

    @patch('plans_adressage.layer.refresh.qgis_config')
    def test_refresh_all_layers(self, mock_qgis_config):
        mock_qgis_config.return_value = {
            'mapper': [],
            'other_layers': [],
        }
        self.mod.refresh_all_layers(self.iface)

    @patch('plans_adressage.layer.refresh.qgis_config')
    def test_apply_all_categorized_styles(self, mock_qgis_config):
        mock_qgis_config.return_value = {
            'categorize': [],
        }
        self.mod.apply_all_categorized_styles(self.iface)

    @patch('plans_adressage.layer.refresh.qgis_config')
    def test_remove_all_categorized_styles(self, mock_qgis_config):
        mock_qgis_config.return_value = {
            'other_layers': [],
        }
        self.mod.remove_all_categorized_styles(self.iface)

    @patch('plans_adressage.layer.refresh.QgsProject')
    def test_add_feature_to_layer_with_wkt(self, mock_project):
        model_instance = MagicMock(spec=[])
        table_mock = MagicMock()
        table_mock.columns = []
        type(model_instance).__table__ = table_mock

        self.mod.add_feature_to_layer(self.layer, model_instance, 'POINT(1 2)')
        self.layer.dataProvider().addFeature.assert_called_once()
        self.layer.commitChanges.assert_called_once()

    def test_add_feature_to_layer_no_wkt_no_geometry(self):
        model_instance = MagicMock()
        model_instance.geometry = None
        self.mod.add_feature_to_layer(self.layer, model_instance, None)
        self.layer.dataProvider().addFeature.assert_not_called()


if __name__ == '__main__':
    unittest.main()
