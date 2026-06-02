"""Tests for layer/refresh.py."""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from .helpers import (
    make_mock_iface,
    make_mock_layer,
    setup_mocks,
    wire_module_attributes,
)


class TestLayerRefresh(unittest.TestCase):
    """Test layer refresh and style functions."""

    @classmethod
    def setUpClass(cls):
        setup_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.layer.refresh',
            'layer/refresh.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.layer.refresh'] = cls.mod
        spec.loader.exec_module(cls.mod)
        wire_module_attributes()

    def setUp(self):
        self.iface = make_mock_iface()
        self.layer = make_mock_layer()

    @patch('plans_adressage.layer.refresh.QgsProject')
    def test_apply_categorized_style(self, mock_project):
        (mock_project.instance.return_value.mapLayersByName.return_value) = [self.layer]
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
        (mock_project.instance.return_value.mapLayersByName.return_value) = [self.layer]
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
    def test_add_feature_to_layer_with_wkt(self, _mock_project):
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

    @patch('plans_adressage.layer.refresh._models', MagicMock(spec=[]))
    @patch('plans_adressage.layer.refresh.get_session')
    @patch('plans_adressage.layer.refresh.QgsProject')
    def test_refresh_from_db_unknown_model(
        self,
        _mock_project,
        mock_get_session,
    ):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        self.mod.refresh_layer_from_db(self.iface, 'test_layer', 'NonExistentModel')
        mock_session.close.assert_called_once()

    def _make_mock_model(self, columns=None):
        mock_model = MagicMock(spec=[])
        table_mock = MagicMock()
        table_mock.columns = columns or []
        type(mock_model).__table__ = table_mock
        return mock_model

    @patch('plans_adressage.layer.refresh._models')
    @patch('plans_adressage.layer.refresh.get_session')
    @patch('plans_adressage.layer.refresh.QgsProject')
    def test_refresh_from_db_no_results(
        self,
        _mock_project,
        mock_get_session,
        mock_models,
    ):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_session.query.return_value.all.return_value = []
        model = self._make_mock_model()
        mock_models.Road = model
        self.mod.refresh_layer_from_db(self.iface, 'test_layer', 'Road')
        mock_session.close.assert_called_once()

    @patch('plans_adressage.layer.refresh._models')
    @patch('plans_adressage.layer.refresh.get_session')
    @patch('plans_adressage.layer.refresh.QgsProject')
    def test_refresh_from_db_layer_not_found(
        self,
        mock_project,
        mock_get_session,
        mock_models,
    ):
        mock_project.instance.return_value.mapLayersByName.return_value = []
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_session.query.return_value.all.return_value = [(MagicMock(), 'POINT(1 2)')]
        model = self._make_mock_model()
        mock_models.Road = model
        self.mod.refresh_layer_from_db(self.iface, 'nonexistent', 'Road')
        mock_session.close.assert_called_once()

    @patch('plans_adressage.layer.refresh._models')
    @patch('plans_adressage.layer.refresh.get_session')
    @patch('plans_adressage.layer.refresh.QgsProject')
    def test_refresh_from_db_with_geometry(
        self,
        mock_project,
        mock_get_session,
        mock_models,
    ):
        (mock_project.instance.return_value.mapLayersByName.return_value) = [self.layer]
        self.layer.fields.return_value = []
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_geom_col = MagicMock()
        mock_geom_col.name = 'geometry'
        mock_geom_col.type = object()
        mock_text_col = MagicMock()
        mock_text_col.name = 'name'
        mock_text_col.type = object()
        model = self._make_mock_model([mock_geom_col, mock_text_col])
        mock_models.Road = model
        result_row = MagicMock()
        result_row.name = 'Test Road'
        mock_session.query.return_value.all.return_value = [
            (result_row, 'LINESTRING(0 0, 1 1)')
        ]
        self.mod.refresh_layer_from_db(self.iface, 'test_layer', 'Road')
        self.layer.dataProvider().deleteFeatures.assert_called_once()
        self.layer.commitChanges.assert_called_once()
        mock_session.close.assert_called_once()

    @patch('plans_adressage.layer.refresh._models')
    @patch('plans_adressage.layer.refresh.get_session')
    @patch('plans_adressage.layer.refresh.QgsProject')
    def test_refresh_from_db_no_geometry_column(
        self,
        mock_project,
        mock_get_session,
        mock_models,
    ):
        (mock_project.instance.return_value.mapLayersByName.return_value) = [self.layer]
        self.layer.fields.return_value = []
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_session.query.return_value.all.return_value = [(MagicMock(), None)]
        mock_text_col = MagicMock()
        mock_text_col.name = 'name'
        mock_text_col.type = object()
        model = self._make_mock_model([mock_text_col])
        mock_models.Road = model
        self.mod.refresh_layer_from_db(self.iface, 'test_layer', 'Road')
        self.layer.dataProvider().deleteFeatures.assert_called_once()
        self.layer.commitChanges.assert_called_once()
        mock_session.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
