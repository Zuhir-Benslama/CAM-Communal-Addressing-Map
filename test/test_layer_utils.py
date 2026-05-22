"""Tests for layer/utils.py."""
import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from .helpers import setup_mocks, wire_module_attributes, make_mock_iface, make_mock_layer


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
                {'label': 'test_layer', 'style': 'test.qml', 'url': '?query=select 1'},
            ],
            'mapper': [
                {'layer': 'test_layer', 'model': 'Road'},
            ],
        }
        self.mod.create_other_layers(self.iface)
        mock_project.instance.return_value.addMapLayer.assert_called_once_with(layer)

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
        mock_project.instance.return_value.mapLayersByName.return_value = [MagicMock()]
        mock_qgis_config.return_value = {
            'other_layers': [
                {'label': 'test_layer', 'style': 'test.qml', 'url': '?query=select 1'},
            ],
            'mapper': [],
        }
        self.mod.create_other_layers(self.iface)
        mock_project.instance.return_value.addMapLayer.assert_not_called()

    @patch('plans_adressage.layer.utils.open')
    @patch('plans_adressage.layer.utils.toml.load')
    @patch('plans_adressage.layer.utils.get_session')
    @patch('plans_adressage.layer.utils.QgsProject')
    @patch('plans_adressage.layer.utils.qgis_config')
    def test_init_allowed_zone_with_cookie(
        self, mock_qgis_config, mock_project, mock_get_session, mock_toml_load, mock_open,
    ):
        mock_qgis_config.return_value = {'other_layers': [], 'mapper': []}
        mock_toml_load.return_value = {
            'Session': {'cookie': 'test_cookie', 'uid': 'test_uid'},
        }
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        user = MagicMock()
        user.affectation_id = 'loc1'
        mock_session.query.return_value.filter.return_value.first.side_effect = [user, None]
        mock_project.instance.return_value.mapLayersByName.return_value = []
        self.mod.init_allowed_zone(self.iface)

    @patch('plans_adressage.layer.utils.open')
    @patch('plans_adressage.layer.utils.toml.load')
    def test_init_allowed_zone_no_cookie(self, mock_toml_load, mock_open):
        mock_toml_load.return_value = {'Session': {}}
        self.mod.init_allowed_zone(self.iface)


if __name__ == '__main__':
    unittest.main()
