"""Core (non-GUI) mock setup for ``setup_mocks()``."""

import sys
import types
from unittest.mock import MagicMock

from ._shared import (
    _mirror_app_modules,
    _mock_constants_base,
    _mock_model_table,
    _setup_package_tree,
    wire_module_attributes,
)


def _mock_qgis_core():
    """Return a MagicMock ``qgis.core`` module."""
    core = MagicMock()
    core.QgsProject = MagicMock()
    core.QgsProject.instance = MagicMock(return_value=MagicMock())
    core.QgsMapLayer = MagicMock()
    core.QgsMapLayer.VectorLayer = 0
    core.QgsMapLayer.RasterLayer = 1
    core.QgsWkbTypes = MagicMock()
    core.QgsWkbTypes.PointGeometry = 0
    core.QgsWkbTypes.LineGeometry = 1
    core.QgsWkbTypes.PolygonGeometry = 2
    core.Qgis = MagicMock()
    core.Qgis.Info = 0
    core.Qgis.Critical = 1
    core.Qgis.Warning = 2
    core.QgsFeature = MagicMock()
    core.QgsGeometry = MagicMock()
    core.QgsGeometry.fromWkt = MagicMock(return_value=MagicMock())
    core.QgsField = MagicMock()
    core.QgsSymbol = MagicMock()
    core.QgsSymbol.defaultSymbol = MagicMock(return_value=MagicMock())
    type(core.QgsSymbol.defaultSymbol).__name__ = 'builtin_function_or_method'
    core.QgsExpression = MagicMock()
    core.QgsExpressionContext = MagicMock()
    core.QgsExpressionContext().setFeature = MagicMock()
    core.QgsCategorizedSymbolRenderer = MagicMock()
    core.QgsSingleSymbolRenderer = MagicMock()
    core.QgsRendererCategory = MagicMock()
    core.QgsFillSymbol = MagicMock()
    core.QgsFillSymbol.createSimple = MagicMock(return_value=MagicMock())
    core.QgsVectorLayer = MagicMock()
    core.QVariant = types.SimpleNamespace(
        Bool=1,
        Int=2,
        Double=6,
        String=10,
    )
    return core


def _mock_orders_models(names):
    """Return a MagicMock orders.models module with named model stubs."""
    m = MagicMock()
    for name in names:
        setattr(m, name, _mock_model_table(MagicMock()))
    return m


def setup_mocks():
    """Set up mock modules for QGIS and project dependencies in sys.modules.

    Must be called before importing any module that depends on ``qgis``
    or uses relative imports from a ``plans_adressage`` package context.
    """
    _setup_package_tree(
        [
            'plans_adressage',
            'plans_adressage.layer',
            'plans_adressage.app',
            'plans_adressage.app.core',
            'plans_adressage.app.orders',
            'plans_adressage.app.users',
            'plans_adressage.app.shared',
        ]
    )

    _shared_utils = MagicMock()
    _shared_utils.get_all_fields_and_labels = MagicMock(
        return_value=(
            ['value', 'state'],
            {'value': 'Value', 'state': 'State'},
        )
    )
    sys.modules['plans_adressage.app.shared.utils'] = _shared_utils

    _constants = _mock_constants_base()
    sys.modules['plans_adressage.constants'] = _constants

    _setup_package_tree(['plans_adressage.scripts'])
    _lookup = MagicMock()
    _lookup.get_string = lambda s, loc=None: s
    sys.modules['plans_adressage.scripts.lookup_data'] = _lookup
    _widget_texts = MagicMock()
    _widget_texts.get_string = lambda s, loc=None: s
    sys.modules['plans_adressage.scripts.widget_texts'] = _widget_texts

    _users_repo = MagicMock()
    _users_repo.qgis_config = MagicMock(
        return_value={
            'mapper': [
                {'layer': 'roads', 'model': 'Road'},
                {'layer': 'zones', 'model': 'Zone'},
            ],
            'other_layers': [
                {'label': 'basemap', 'style': 'basemap.qml', 'url': '?query=select 1'},
            ],
            'categorize': [{'layer': 'roads', 'by': ['type']}],
        }
    )
    _users_repo.get_current_user = MagicMock()
    sys.modules['plans_adressage.app.users.repository'] = _users_repo

    _orders_repo = MagicMock()
    _orders_repo.export_model = MagicMock()
    _orders_repo.count_numberings = MagicMock()
    _orders_repo.count_panels = MagicMock()
    for fn in ('query_missing_pan', 'query_missing_num', 'query_missing_rep'):
        setattr(_orders_repo, fn, MagicMock())
    sys.modules['plans_adressage.app.orders.repository'] = _orders_repo

    _database = MagicMock()
    _database.get_session = MagicMock()
    sys.modules['plans_adressage.app.core.database'] = _database

    sys.modules['plans_adressage.app.orders.models'] = _mock_orders_models(
        ['Road', 'Zone', 'Organization', 'Subdivision', 'PanelSign', 'Numbering'],
    )

    _users_models = MagicMock()
    _users_models.User = _mock_model_table(MagicMock())
    sys.modules['plans_adressage.app.users.models'] = _users_models

    _qgis = MagicMock()
    _qgis.__path__ = ['/fake/qgis']
    _qgis.__name__ = 'qgis'
    sys.modules['qgis'] = _qgis

    _core = _mock_qgis_core()
    sys.modules['qgis.core'] = _core

    _PyQt = MagicMock()
    _PyQt.__path__ = ['/fake/qgis/PyQt']
    _PyQt.__name__ = 'qgis.PyQt'
    sys.modules['qgis.PyQt'] = _PyQt
    _QtCore = MagicMock()
    sys.modules['qgis.PyQt.QtCore'] = _QtCore

    _mirror_app_modules()

    _gda2 = types.ModuleType('geoalchemy2')
    sys.modules['geoalchemy2'] = _gda2

    class _FakeGeometryType:
        """Fake Geometry type for isinstance() checks in tests."""

    _gda2.Geometry = _FakeGeometryType
    sys.modules['geoalchemy2.Geometry'] = _FakeGeometryType
    sys.modules['geoalchemy2.elements'] = MagicMock()

    _sa = MagicMock()
    _sa.func = MagicMock()
    _sa.func.ST_AsText = MagicMock()
    sys.modules['sqlalchemy'] = _sa

    wire_module_attributes()

    return _core, _constants
