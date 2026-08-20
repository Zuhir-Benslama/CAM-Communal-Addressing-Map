"""Extended tests for layer/utils.py — covers uncovered functions."""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from test.helpers import setup_mocks, wire_module_attributes, make_mock_iface

# Capture real SQLAlchemy types before setup_mocks() replaces sys.modules.
try:
    from sqlalchemy import Boolean as _RealBoolean
    from sqlalchemy import Float as _RealFloat
    from sqlalchemy import Integer as _RealInteger
    from sqlalchemy import SmallInteger as _RealSmallInteger
    from sqlalchemy import String as _RealString
    from sqlalchemy import Text as _RealText

    _HAS_REAL_SA = True
except ImportError:
    _HAS_REAL_SA = False


def _load_module():
    setup_mocks()
    spec = importlib.util.spec_from_file_location(
        'plans_adressage.layer.utils',
        'layer/utils.py',
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules['plans_adressage.layer.utils'] = mod
    spec.loader.exec_module(mod)
    wire_module_attributes()
    return mod


class TestSaTypeToQVariant(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def _patch_type_map(self):
        """Replace the module's _TYPE_MAP with one using real SQLAlchemy types."""
        if not _HAS_REAL_SA:
            self.skipTest('sqlalchemy not installed')
        real_map = [
            ((_RealInteger, _RealSmallInteger), self.mod.QVariant.Int),
            ((_RealFloat,), self.mod.QVariant.Double),
            ((_RealString, _RealText), self.mod.QVariant.String),
            ((_RealBoolean,), self.mod.QVariant.Bool),
        ]
        return patch.object(self.mod, '_TYPE_MAP', real_map)

    def _make_sa_instance(self, type_class):
        """Create an instance of a real SQLAlchemy type."""
        return type_class()

    def test_integer_type(self):
        if not _HAS_REAL_SA:
            self.skipTest('sqlalchemy not installed')
        with self._patch_type_map():
            result = self.mod._sa_type_to_qvariant(self._make_sa_instance(_RealInteger))
        self.assertEqual(result, self.mod.QVariant.Int)

    def test_small_integer_type(self):
        if not _HAS_REAL_SA:
            self.skipTest('sqlalchemy not installed')
        with self._patch_type_map():
            result = self.mod._sa_type_to_qvariant(
                self._make_sa_instance(_RealSmallInteger)
            )
        self.assertEqual(result, self.mod.QVariant.Int)

    def test_float_type(self):
        if not _HAS_REAL_SA:
            self.skipTest('sqlalchemy not installed')
        with self._patch_type_map():
            result = self.mod._sa_type_to_qvariant(self._make_sa_instance(_RealFloat))
        self.assertEqual(result, self.mod.QVariant.Double)

    def test_string_type(self):
        if not _HAS_REAL_SA:
            self.skipTest('sqlalchemy not installed')
        with self._patch_type_map():
            result = self.mod._sa_type_to_qvariant(self._make_sa_instance(_RealString))
        self.assertEqual(result, self.mod.QVariant.String)

    def test_text_type(self):
        if not _HAS_REAL_SA:
            self.skipTest('sqlalchemy not installed')
        with self._patch_type_map():
            result = self.mod._sa_type_to_qvariant(self._make_sa_instance(_RealText))
        self.assertEqual(result, self.mod.QVariant.String)

    def test_boolean_type(self):
        if not _HAS_REAL_SA:
            self.skipTest('sqlalchemy not installed')
        with self._patch_type_map():
            result = self.mod._sa_type_to_qvariant(self._make_sa_instance(_RealBoolean))
        self.assertEqual(result, self.mod.QVariant.Bool)

    def test_unknown_type_returns_string(self):
        unknown = MagicMock()
        with self._patch_type_map():
            result = self.mod._sa_type_to_qvariant(unknown)
        self.assertEqual(result, self.mod.QVariant.String)


class TestCreateOtherLayers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def setUp(self):
        self.iface = make_mock_iface()

    @patch('plans_adressage.layer.utils.qgis_config')
    def test_create_other_layers_no_config(self, mock_qgis_config):
        mock_qgis_config.return_value = {'other_layers': [], 'mapper': []}
        self.mod.create_other_layers(self.iface)

    @patch('plans_adressage.layer.utils.qgis_config')
    @patch('plans_adressage.layer.utils.QgsVectorLayer')
    @patch('plans_adressage.layer.utils.QgsProject')
    def test_create_other_layers_with_layer(
        self, mock_project, mock_vector_layer, mock_qgis_config
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
            'mapper': [],
        }
        self.mod.create_other_layers(self.iface)
        mock_project.instance.return_value.addMapLayer.assert_called_once_with(layer)

    @patch('plans_adressage.layer.utils.qgis_config')
    @patch('plans_adressage.layer.utils.QgsVectorLayer')
    @patch('plans_adressage.layer.utils.QgsProject')
    def test_create_other_layers_skips_existing(
        self, mock_project, mock_vector_layer, mock_qgis_config
    ):
        layer = MagicMock()
        layer.isValid.return_value = True
        mock_vector_layer.return_value = layer
        mock_project.instance.return_value.mapLayersByName.return_value = [MagicMock()]
        mock_qgis_config.return_value = {
            'other_layers': [{'label': 'x', 'url': '?'}],
            'mapper': [],
        }
        self.mod.create_other_layers(self.iface)
        mock_project.instance.return_value.addMapLayer.assert_not_called()

    @patch('plans_adressage.layer.utils.qgis_config')
    @patch('plans_adressage.layer.utils.QgsVectorLayer')
    def test_create_other_layers_invalid_layer(
        self, mock_vector_layer, mock_qgis_config
    ):
        layer = MagicMock()
        layer.isValid.return_value = False
        mock_vector_layer.return_value = layer
        mock_qgis_config.return_value = {
            'other_layers': [{'label': 'x', 'url': '?'}],
            'mapper': [],
        }
        self.mod.create_other_layers(self.iface)

    @patch('plans_adressage.layer.utils._sa_type_to_qvariant', return_value=None)
    @patch('plans_adressage.layer.utils.qgis_config')
    @patch('plans_adressage.layer.utils.QgsVectorLayer')
    @patch('plans_adressage.layer.utils.QgsProject')
    def test_create_other_layers_with_mapper_and_model(
        self, mock_project, mock_vector_layer, mock_qgis_config, mock_sa
    ):
        layer = MagicMock()
        layer.isValid.return_value = True
        layer.name.return_value = 'basemap'
        mock_vector_layer.return_value = layer
        mock_project.instance.return_value.mapLayersByName.return_value = []

        geoalchemy2 = sys.modules.get('geoalchemy2')
        Geometry = geoalchemy2.Geometry if geoalchemy2 else type('Geometry', (), {})

        col_ok = MagicMock()
        col_ok.type = MagicMock(spec=[])  # not a Geometry instance
        col_geo = MagicMock()
        col_geo.type = Geometry()  # IS a Geometry instance

        model_cls = MagicMock()
        model_cls.__table__ = MagicMock()
        model_cls.__table__.columns = {'field': col_ok, 'geom': col_geo}

        import plans_adressage.app.orders.models as _models

        setattr(_models, 'Road', model_cls)

        mock_qgis_config.return_value = {
            'other_layers': [{'label': 'basemap', 'url': '?'}],
            'mapper': [{'layer': 'basemap', 'model': 'Road'}],
        }
        self.mod.create_other_layers(self.iface)
        layer.dataProvider.return_value.addAttributes.assert_called()


class TestCommuneIdFromCode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    @patch('plans_adressage.layer.utils.COMMUNES_JSON', '/fake/communes.json')
    @patch('plans_adressage.layer.utils.Path')
    def test_found(self, mock_path_cls):
        data = {'1': {'commune_code': '4112', 'commune_id': 99}}
        mock_path_cls.return_value.open.return_value.__enter__ = MagicMock(
            return_value=MagicMock()
        )
        mock_path_cls.return_value.open.return_value.__exit__ = MagicMock(
            return_value=False
        )
        with patch.object(self.mod.json, 'load', return_value=data):
            result = self.mod._commune_id_from_code('4112')
        self.assertEqual(result, 99)

    @patch('plans_adressage.layer.utils.COMMUNES_JSON', '/fake/communes.json')
    @patch('plans_adressage.layer.utils.Path')
    def test_not_found(self, mock_path_cls):
        data = {'1': {'commune_code': '9999', 'commune_id': 1}}
        mock_path_cls.return_value.open.return_value.__enter__ = MagicMock(
            return_value=MagicMock()
        )
        mock_path_cls.return_value.open.return_value.__exit__ = MagicMock(
            return_value=False
        )
        with patch.object(self.mod.json, 'load', return_value=data):
            result = self.mod._commune_id_from_code('4112')
        self.assertIsNone(result)

    @patch('plans_adressage.layer.utils.COMMUNES_JSON', '/fake/communes.json')
    @patch('plans_adressage.layer.utils.Path')
    def test_file_not_found(self, mock_path_cls):
        mock_path_cls.return_value.open.side_effect = FileNotFoundError
        result = self.mod._commune_id_from_code('4112')
        self.assertIsNone(result)


class TestWktFromCommuneId(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    @patch('plans_adressage.layer.utils.COMMUNES_DB', '/fake/communes.db')
    @patch('plans_adressage.layer.utils.sqlite3')
    def test_found(self, mock_sqlite):
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = ('MULTIPOLYGON(...)',)
        mock_sqlite.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_sqlite.connect.return_value.__exit__ = MagicMock(return_value=False)
        result = self.mod._wkt_from_commune_id(42)
        self.assertEqual(result, 'MULTIPOLYGON(...)')

    @patch('plans_adressage.layer.utils.COMMUNES_DB', '/fake/communes.db')
    @patch('plans_adressage.layer.utils.sqlite3')
    def test_not_found(self, mock_sqlite):
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = None
        mock_sqlite.connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_sqlite.connect.return_value.__exit__ = MagicMock(return_value=False)
        result = self.mod._wkt_from_commune_id(999)
        self.assertIsNone(result)

    @patch('plans_adressage.layer.utils.COMMUNES_DB', '/fake/communes.db')
    @patch('plans_adressage.layer.utils.sqlite3')
    def test_sql_error(self, mock_sqlite):
        mock_sqlite.Error = Exception
        mock_sqlite.connect.side_effect = mock_sqlite.Error('db error')
        result = self.mod._wkt_from_commune_id(1)
        self.assertIsNone(result)


class TestResolveCommuneGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    @patch('plans_adressage.layer.utils.get_current_user')
    def test_no_user(self, mock_get_user):
        mock_get_user.return_value = None
        geom = self.mod._resolve_commune_geometry()
        self.assertIsNotNone(geom)

    @patch('plans_adressage.layer.utils.get_current_user')
    def test_no_commune_code(self, mock_get_user):
        mock_get_user.return_value = {'commune_code': None}
        geom = self.mod._resolve_commune_geometry()
        self.assertIsNotNone(geom)

    @patch('plans_adressage.layer.utils._wkt_from_commune_id', return_value=None)
    @patch('plans_adressage.layer.utils._commune_id_from_code', return_value=42)
    @patch('plans_adressage.layer.utils.get_current_user')
    def test_no_wkt(self, mock_get_user, mock_id, mock_wkt):
        mock_get_user.return_value = {'commune_code': '1234'}
        geom = self.mod._resolve_commune_geometry()
        self.assertIsNotNone(geom)

    @patch('plans_adressage.layer.utils.QgsGeometry')
    @patch(
        'plans_adressage.layer.utils._wkt_from_commune_id',
        return_value='MULTIPOLYGON(...)',
    )
    @patch('plans_adressage.layer.utils._commune_id_from_code', return_value=42)
    @patch('plans_adressage.layer.utils.get_current_user')
    def test_success(self, mock_get_user, mock_id, mock_wkt, mock_geom_cls):
        mock_get_user.return_value = {'commune_code': '1234'}
        mock_geom_cls.fromWkt.return_value = MagicMock()
        geom = self.mod._resolve_commune_geometry()
        self.assertIsNotNone(geom)

    @patch('plans_adressage.layer.utils._commune_id_from_code', return_value=None)
    @patch('plans_adressage.layer.utils.get_current_user')
    def test_commune_id_none(self, mock_get_user, mock_id):
        mock_get_user.return_value = {'commune_code': '1234'}
        geom = self.mod._resolve_commune_geometry()
        self.assertIsNotNone(geom)


class TestSetLayerGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_with_geometry(self):
        layer = MagicMock()
        layer.getFeatures.return_value = []
        multipolygon = MagicMock()
        multipolygon.isEmpty.return_value = False
        self.mod._set_layer_geometry(layer, multipolygon)
        layer.startEditing.assert_called_once()
        layer.commitChanges.assert_called_once()
        layer.triggerRepaint.assert_called_once()

    def test_with_empty_geometry(self):
        layer = MagicMock()
        layer.getFeatures.return_value = []
        multipolygon = MagicMock()
        multipolygon.isEmpty.return_value = True
        self.mod._set_layer_geometry(layer, multipolygon)
        layer.startEditing.assert_called_once()
        layer.commitChanges.assert_called_once()

    def test_with_none_geometry(self):
        layer = MagicMock()
        layer.getFeatures.return_value = [MagicMock()]
        self.mod._set_layer_geometry(layer, None)
        layer.startEditing.assert_called_once()


class TestCreateMunicipalityLayer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    @patch('plans_adressage.layer.utils.QgsFillSymbol')
    @patch('plans_adressage.layer.utils.QgsProject')
    @patch('plans_adressage.layer.utils.QgsVectorLayer')
    def test_with_geometry(self, mock_vl, mock_proj, mock_symbol):
        layer = MagicMock()
        mock_vl.return_value = layer
        multipolygon = MagicMock()
        multipolygon.isEmpty.return_value = False
        self.mod._create_municipality_layer(multipolygon)
        mock_proj.instance.return_value.addMapLayer.assert_called_once_with(layer)
        layer.dataProvider.return_value.addFeature.assert_called_once()

    @patch('plans_adressage.layer.utils.QgsFillSymbol')
    @patch('plans_adressage.layer.utils.QgsProject')
    @patch('plans_adressage.layer.utils.QgsVectorLayer')
    def test_with_empty_geometry(self, mock_vl, mock_proj, mock_symbol):
        layer = MagicMock()
        mock_vl.return_value = layer
        multipolygon = MagicMock()
        multipolygon.isEmpty.return_value = True
        self.mod._create_municipality_layer(multipolygon)
        layer.dataProvider.return_value.addFeature.assert_not_called()

    @patch('plans_adressage.layer.utils.QgsFillSymbol')
    @patch('plans_adressage.layer.utils.QgsProject')
    @patch('plans_adressage.layer.utils.QgsVectorLayer')
    def test_with_none_geometry(self, mock_vl, mock_proj, mock_symbol):
        layer = MagicMock()
        mock_vl.return_value = layer
        self.mod._create_municipality_layer(None)
        layer.dataProvider.return_value.addFeature.assert_not_called()


class TestLogMunicipalityDiagnostics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    @patch('plans_adressage.layer.utils.QgsProject')
    def test_with_layers(self, mock_proj):
        layer = MagicMock()
        layer.featureCount.return_value = 5
        layer.extent.return_value.toString.return_value = '0,0 1,1'
        mock_proj.instance.return_value.mapLayersByName.return_value = [layer]
        mock_proj.instance.return_value.layerTreeRoot.return_value.children.return_value = []
        self.mod._log_municipality_diagnostics()

    @patch('plans_adressage.layer.utils.QgsProject')
    def test_without_layers(self, mock_proj):
        mock_proj.instance.return_value.mapLayersByName.return_value = []
        mock_proj.instance.return_value.layerTreeRoot.return_value.children.return_value = []
        self.mod._log_municipality_diagnostics()


class TestInitAllowedZone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    @patch('plans_adressage.layer.utils.create_other_layers')
    @patch('plans_adressage.layer.utils._log_municipality_diagnostics')
    @patch('plans_adressage.layer.utils.QgsProject')
    def test_existing_layer(self, mock_proj, mock_diag, mock_other):
        mock_proj.instance.return_value.mapLayersByName.return_value = [MagicMock()]
        with patch.object(
            self.mod, '_resolve_commune_geometry', return_value=MagicMock()
        ):
            iface = make_mock_iface()
            self.mod.init_allowed_zone(iface)

    @patch('plans_adressage.layer.utils.create_other_layers')
    @patch('plans_adressage.layer.utils._log_municipality_diagnostics')
    @patch('plans_adressage.layer.utils._create_municipality_layer')
    @patch('plans_adressage.layer.utils.QgsProject')
    def test_new_layer(self, mock_proj, mock_create, mock_diag, mock_other):
        mock_proj.instance.return_value.mapLayersByName.return_value = []
        with patch.object(
            self.mod, '_resolve_commune_geometry', return_value=MagicMock()
        ):
            iface = make_mock_iface()
            self.mod.init_allowed_zone(iface)
            mock_create.assert_called_once()

    @patch('plans_adressage.layer.utils.create_other_layers')
    @patch('plans_adressage.layer.utils._log_municipality_diagnostics')
    @patch('plans_adressage.layer.utils.QgsProject')
    def test_zooms_to_extent(self, mock_proj, mock_diag, mock_other):
        geom = MagicMock()
        geom.isEmpty.return_value = False
        geom.boundingBox.return_value = MagicMock()
        mock_proj.instance.return_value.mapLayersByName.return_value = []
        with (
            patch.object(self.mod, '_resolve_commune_geometry', return_value=geom),
            patch.object(self.mod, '_create_municipality_layer'),
        ):
            iface = make_mock_iface()
            self.mod.init_allowed_zone(iface)
            iface.mapCanvas().zoomToFeatureExtent.assert_called_once()

    @patch('plans_adressage.layer.utils.create_other_layers')
    @patch('plans_adressage.layer.utils._log_municipality_diagnostics')
    @patch('plans_adressage.layer.utils.QgsProject')
    def test_no_zoom_when_empty(self, mock_proj, mock_diag, mock_other):
        geom = MagicMock()
        geom.isEmpty.return_value = True
        mock_proj.instance.return_value.mapLayersByName.return_value = []
        with (
            patch.object(self.mod, '_resolve_commune_geometry', return_value=geom),
            patch.object(self.mod, '_create_municipality_layer'),
        ):
            iface = make_mock_iface()
            self.mod.init_allowed_zone(iface)
            iface.mapCanvas().zoomToFeatureExtent.assert_not_called()


if __name__ == '__main__':
    unittest.main()
