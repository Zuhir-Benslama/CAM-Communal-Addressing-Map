"""Tests for layer/utils.py."""
import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from .helpers import make_mock_iface, setup_mocks, wire_module_attributes


class TestLayerUtils(unittest.TestCase):
    """Test layer utility functions."""

    @classmethod
    def setUpClass(cls):
        setup_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.layer.utils', 'layer/utils.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.layer.utils'] = cls.mod
        spec.loader.exec_module(cls.mod)
        wire_module_attributes()

    def setUp(self):
        self.iface = make_mock_iface()

    @patch('plans_adressage.layer.utils.qgis_config')
    def test_create_other_layers_no_config(self, mock_qgis_config):
        mock_qgis_config.return_value = {
            'other_layers': [],
            'mapper': [],
        }
        self.mod.create_other_layers(self.iface)

    @patch('plans_adressage.layer.utils.qgis_config')
    @patch('plans_adressage.layer.utils.QgsVectorLayer')
    @patch('plans_adressage.layer.utils.QgsProject')
    def test_create_other_layers_with_layer(
        self, mock_project, mock_vector_layer, mock_qgis_config,
    ):
        layer = MagicMock()
        layer.isValid.return_value = True
        layer.name.return_value = 'test_layer'
        mock_vector_layer.return_value = layer
        mock_project.instance.return_value.mapLayersByName.return_value = []
        mock_qgis_config.return_value = {
            'other_layers': [
                {'label': 'test_layer', 'style': 'test.qml',
                 'url': '?query=select 1'},
            ],
            'mapper': [
                {'layer': 'test_layer', 'model': 'Road'},
            ],
        }
        self.mod.create_other_layers(self.iface)
        (mock_project.instance.return_value.addMapLayer
         .assert_called_once_with(layer))

    @patch('plans_adressage.layer.utils.qgis_config')
    @patch('plans_adressage.layer.utils.QgsVectorLayer')
    @patch('plans_adressage.layer.utils.QgsProject')
    def test_create_other_layers_skips_existing(
        self, mock_project, mock_vector_layer, mock_qgis_config,
    ):
        existing_layer = MagicMock()
        mock_vector_layer.return_value = existing_layer
        existing_layer.isValid.return_value = True
        existing_layer.name.return_value = 'test_layer'
        (mock_project.instance.return_value
         .mapLayersByName.return_value) = [MagicMock()]
        mock_qgis_config.return_value = {
            'other_layers': [
                {'label': 'test_layer', 'style': 'test.qml',
                 'url': '?query=select 1'},
            ],
            'mapper': [],
        }
        self.mod.create_other_layers(self.iface)
        mock_project.instance.return_value.addMapLayer.assert_not_called()

    @patch('plans_adressage.layer.utils.get_current_user')
    @patch('plans_adressage.layer.utils.QgsProject')
    @patch('plans_adressage.layer.utils.qgis_config')
    def test_init_allowed_zone_with_commune(
        self, mock_qgis_config, mock_project, mock_get_user,
    ):
        mock_get_user.return_value = {
            'commune_code': '4112',
            'wilaya_code': 41,
            'wilaya': 'Wilaya',
            'commune': 'Commune',
        }
        mock_qgis_config.return_value = {'other_layers': [], 'mapper': []}
        mock_project.instance.return_value.mapLayersByName.return_value = []
        # Mock commune lookup + GeoJSON loading (no geometry found)
        with patch('plans_adressage.layer.utils.open'), \
             patch('plans_adressage.layer.utils.json.load') as mock_json_load:
            mock_json_load.side_effect = [
                {'1': {'commune_code': 4112, 'commune_id': 1}},
                {"type": "FeatureCollection", "features": []},
            ]
            self.mod.init_allowed_zone(self.iface)

    @patch('plans_adressage.layer.utils.get_current_user')
    def test_init_allowed_zone_no_user(self, mock_get_user):
        mock_get_user.return_value = None
        self.mod.init_allowed_zone(self.iface)


if __name__ == '__main__':
    unittest.main()
