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
    """Test layer refresh functions."""

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

    @patch('plans_adressage.layer.refresh.qgis_config')
    def test_refresh_all_layers(self, mock_qgis_config):
        mock_qgis_config.return_value = {
            'mapper': [],
            'other_layers': [],
        }
        self.mod.refresh_all_layers(self.iface)

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


class TestRefreshHelpers(unittest.TestCase):
    """Test the private helper functions in layer/refresh.py."""

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

    def test_get_model_class_returns_class(self):
        mock_model = MagicMock()
        with patch.object(self.mod._models, 'Road', mock_model):
            self.assertIs(self.mod._get_model_class('Road'), mock_model)

    def test_get_model_class_unknown_returns_none(self):
        with patch.object(self.mod, '_models', MagicMock(spec=[])):
            self.assertIsNone(self.mod._get_model_class('NonExistent'))

    def _make_geom_type(self):
        return self.mod.Geometry()

    def _make_model(self, columns):
        model = MagicMock(spec=[])
        table_mock = MagicMock()
        table_mock.columns = columns
        type(model).__table__ = table_mock
        return model

    def test_get_geometry_column_returns_geometry(self):
        geom_col = MagicMock()
        geom_col.type = self._make_geom_type()
        text_col = MagicMock()
        text_col.type = object()
        model = self._make_model([geom_col, text_col])
        self.assertEqual(self.mod._get_geometry_column(model), geom_col)

    def test_get_geometry_column_none_when_absent(self):
        text_col = MagicMock()
        text_col.type = object()
        model = self._make_model([text_col])
        self.assertIsNone(self.mod._get_geometry_column(model))

    def test_get_all_model_fields_excludes_geometry(self):
        geom_col = MagicMock()
        geom_col.name = 'geometry'
        geom_col.type = self._make_geom_type()
        text_col = MagicMock()
        text_col.name = 'name'
        text_col.type = object()
        model = self._make_model([geom_col, text_col])
        fields = self.mod._get_all_model_fields(model)
        self.assertIn('name', fields)
        self.assertNotIn('geometry', fields)

    def test_get_all_model_fields_includes_properties(self):
        class FakeModel:
            @property
            def derived(self):
                return 1

        table_mock = MagicMock()
        text_col = MagicMock()
        text_col.name = 'name'
        text_col.type = object()
        table_mock.columns = [text_col]
        FakeModel.__table__ = table_mock
        fields = self.mod._get_all_model_fields(FakeModel)
        self.assertIn('name', fields)
        self.assertIn('derived', fields)

    def test_query_all_records_with_geometry(self):
        session = MagicMock()
        session.query.return_value.all.return_value = [
            (object(), 'POINT(1 2)'),
            (object(), 'POINT(3 4)'),
        ]
        result = self.mod._query_all_records(session, MagicMock(), MagicMock())
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][1], 'POINT(1 2)')

    def test_query_all_records_without_geometry(self):
        session = MagicMock()
        session.query.return_value.all.return_value = [object(), object()]
        result = self.mod._query_all_records(session, MagicMock(), None)
        self.assertEqual(len(result), 2)
        self.assertIsNone(result[0][1])

    def test_build_feature_sets_attributes(self):
        result = MagicMock()
        result.geom = 'x'
        result.name = 'Main St'
        import datetime

        result.dt = datetime.datetime(2024, 1, 1, 12, 0, 0)
        feature = MagicMock()
        with (
            patch.object(self.mod, 'QgsFeature', return_value=feature),
            patch.object(self.mod.QgsGeometry, 'fromWkt', return_value=MagicMock()),
        ):
            built = self.mod._build_feature(
                result, 'POINT(0 0)', ['geom', 'name', 'dt'], ['geom', 'name', 'dt']
            )
        self.assertIs(built, feature)
        feature.setGeometry.assert_called_once()
        attrs = feature.setAttributes.call_args.args[0]
        self.assertEqual(attrs[0], 'x')
        self.assertEqual(attrs[1], 'Main St')
        self.assertEqual(attrs[2], '2024-01-01T12:00:00')

    def test_build_feature_returns_none_without_geometry(self):
        self.assertIsNone(self.mod._build_feature(MagicMock(), None, [], []))

    def test_build_feature_handles_missing_attribute(self):
        result = MagicMock(spec=[])
        result.name = 'Main St'
        feature = MagicMock()
        with (
            patch.object(self.mod, 'QgsFeature', return_value=feature),
            patch.object(self.mod.QgsGeometry, 'fromWkt', return_value=MagicMock()),
        ):
            built = self.mod._build_feature(
                result, 'POINT(0 0)', ['name', 'missing'], ['name', 'missing']
            )
        attrs = built.setAttributes.call_args.args[0]
        self.assertEqual(attrs[0], 'Main St')
        self.assertIsNone(attrs[1])

    def test_build_feature_skips_non_all_fields(self):
        result = MagicMock(spec=[])
        feature = MagicMock()
        with (
            patch.object(self.mod, 'QgsFeature', return_value=feature),
            patch.object(self.mod.QgsGeometry, 'fromWkt', return_value=MagicMock()),
        ):
            built = self.mod._build_feature(result, 'POINT(0 0)', ['other'], ['other'])
        attrs = built.setAttributes.call_args.args[0]
        self.assertEqual(attrs[0], None)

    def test_get_new_layer_fields_skips_existing(self):
        field = MagicMock()
        field.name.return_value = 'a'
        layer = MagicMock()
        layer.fields.return_value = [field]
        captured = []
        with patch.object(
            self.mod,
            'QgsField',
            side_effect=lambda name, t: captured.append(name) or name,
        ):
            result = self.mod._get_new_layer_fields(layer, ['a', 'b'])
        self.assertEqual(captured, ['b'])
        self.assertEqual([r for r in result], ['b'])


class TestRefreshFailurePaths(unittest.TestCase):
    """Test exception and failure handling in refresh flows."""

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

    def test_provider_error_rolls_back(self):
        iface = make_mock_iface()
        layer = make_mock_layer()
        mock_session = MagicMock()

        # Model with a geometry column so results carry WKT and the loop runs.
        geom_col = MagicMock()
        geom_col.type = self.mod.Geometry()
        model = MagicMock(spec=[])
        table_mock = MagicMock()
        table_mock.columns = [geom_col]
        type(model).__table__ = table_mock

        with (
            patch('plans_adressage.layer.refresh._models') as mock_models,
            patch('plans_adressage.layer.refresh.get_session') as mock_get_session,
            patch('plans_adressage.layer.refresh.QgsProject') as mock_project,
        ):
            mock_project.instance.return_value.mapLayersByName.return_value = [layer]
            mock_get_session.return_value = mock_session
            mock_session.query.return_value.all.return_value = [
                (MagicMock(), 'POINT(0 0)')
            ]
            mock_models.Road = model
            layer.dataProvider().addFeature.side_effect = RuntimeError('boom')
            with self.assertRaises(RuntimeError):
                self.mod.refresh_layer_from_db(iface, 'test_layer', 'Road')
            layer.rollBack.assert_called_once()
        mock_session.close.assert_called_once()

    def test_commit_failure_logs_and_rolls_back(self):
        iface = make_mock_iface()
        layer = make_mock_layer()
        layer.commitChanges.return_value = False
        layer.commitErrors.return_value = ['err1']
        model = MagicMock(spec=[])
        table_mock = MagicMock()
        table_mock.columns = []
        type(model).__table__ = table_mock

        with (
            patch('plans_adressage.layer.refresh._models') as mock_models,
            patch('plans_adressage.layer.refresh.get_session') as mock_get_session,
            patch('plans_adressage.layer.refresh.QgsProject') as mock_project,
            patch('plans_adressage.layer.refresh.logger') as mock_logger,
        ):
            mock_project.instance.return_value.mapLayersByName.return_value = [layer]
            mock_get_session.return_value = MagicMock()
            mock_session = mock_get_session.return_value
            mock_session.query.return_value.all.return_value = []
            mock_models.Road = model
            self.mod.refresh_layer_from_db(iface, 'test_layer', 'Road')
        layer.commitChanges.assert_called_once()
        layer.rollBack.assert_called_once()
        mock_logger.error.assert_called()

    def test_refresh_all_layers_with_mapper(self):
        iface = make_mock_iface()
        mapper = [{'layer': 'roads', 'model': 'Road'}]
        with (
            patch('plans_adressage.layer.refresh.get_session'),
            patch('plans_adressage.layer.refresh.qgis_config') as mock_cfg,
            patch('plans_adressage.layer.refresh.QgsProject'),
            patch(
                'plans_adressage.layer.refresh.refresh_layer_from_db'
            ) as mock_refresh,
        ):
            mock_cfg.return_value = {'mapper': mapper, 'other_layers': []}
            self.mod.refresh_all_layers(iface)
        mock_refresh.assert_called_once_with(iface, 'roads', 'Road')

    def test_refresh_all_layers_continues_on_error(self):
        iface = make_mock_iface()
        mapper = [
            {'layer': 'roads', 'model': 'Road'},
            {'layer': 'zones', 'model': 'Zone'},
        ]
        with (
            patch('plans_adressage.layer.refresh.get_session'),
            patch('plans_adressage.layer.refresh.qgis_config') as mock_cfg,
            patch('plans_adressage.layer.refresh.QgsProject'),
            patch('plans_adressage.layer.refresh.logger') as mock_logger,
            patch(
                'plans_adressage.layer.refresh.refresh_layer_from_db'
            ) as mock_refresh,
        ):
            mock_refresh.side_effect = [
                RuntimeError('bad'),
                None,
            ]
            mock_cfg.return_value = {'mapper': mapper, 'other_layers': []}
            self.mod.refresh_all_layers(iface)
        self.assertEqual(mock_refresh.call_count, 2)
        mock_logger.exception.assert_called()

    def test_refresh_all_layers_applies_styles(self):
        iface = make_mock_iface()
        layer = make_mock_layer()
        layer_cfg = {'label': 'basemap', 'style': 'basemap.qml'}
        with (
            patch('plans_adressage.layer.refresh.get_session'),
            patch('plans_adressage.layer.refresh.qgis_config') as mock_cfg,
            patch('plans_adressage.layer.refresh.QgsProject') as mock_project,
        ):
            mock_project.instance.return_value.mapLayersByName.return_value = [layer]
            mock_cfg.return_value = {
                'mapper': [],
                'other_layers': [layer_cfg],
            }
            with patch.object(
                self.mod,
                'DEFAULT_STYLE_DIR',
                MagicMock(__truediv__=MagicMock(return_value=MagicMock())),
            ):
                self.mod.refresh_all_layers(iface)
        layer.loadNamedStyle.assert_called_once()


if __name__ == '__main__':
    unittest.main()
