"""Test helpers for mocking QGIS and project dependencies."""
import sys
import types
from unittest.mock import MagicMock, PropertyMock


def _setup_package_tree(packages):
    """Register a list of dotted package names in sys.modules."""
    for name in packages:
        mod = types.ModuleType(name)
        mod.__path__ = name.replace('.', '/')
        mod.__package__ = name
        sys.modules[name] = mod


def _mock_model_table(model, columns=None):
    """Attach a fake ``__table__`` with ``.columns`` to a MagicMock model."""
    object.__setattr__(model, '__table__', MagicMock())
    model.__table__.columns = columns or {}
    return model


def _mock_constants_base():
    """Return a MagicMock constants module with test defaults."""
    c = MagicMock()
    c.NOTIFY_DURATION = 5
    c.current_locale = lambda: 'en'
    c.CRS = 'EPSG:4326'
    c.COOKIE_FILE = '/tmp/test_cookie.toml'
    c.LAYER_MUNICIPALITY = 'My Municipality'
    c.MEMORY_PROVIDER = 'memory'
    c.DEFAULT_STYLE_DIR = '/tmp/styles'
    c.STYLE_QML = '/tmp/style.qml'
    return c


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
    return core


def _mock_orders_models(names):
    """Return a MagicMock orders.models module with named model stubs."""
    m = MagicMock()
    for name in names:
        setattr(m, name, _mock_model_table(MagicMock()))
    return m


def _mirror_app_modules():
    """Mirror ``plans_adressage.app.*`` under ``app.*`` for direct imports."""
    for key in list(sys.modules.keys()):
        if key.startswith('plans_adressage.app'):
            app_key = key[len('plans_adressage.'):]
            if app_key not in sys.modules:
                sys.modules[app_key] = sys.modules[key]


def setup_mocks():
    """Set up mock modules for QGIS and project dependencies in sys.modules.

    Must be called before importing any module that depends on ``qgis``
    or uses relative imports from a ``plans_adressage`` package context.
    """
    _setup_package_tree([
        'plans_adressage', 'plans_adressage.layer', 'plans_adressage.app',
        'plans_adressage.app.core', 'plans_adressage.app.orders',
        'plans_adressage.app.users', 'plans_adressage.app.shared',
    ])

    _shared_utils = MagicMock()
    _shared_utils.get_all_fields_and_labels = MagicMock(return_value=(
        ['valeur', 'etat'], {'valeur': 'Value', 'etat': 'State'},
    ))
    sys.modules['plans_adressage.app.shared.utils'] = _shared_utils

    _constants = _mock_constants_base()
    sys.modules['plans_adressage.constants'] = _constants

    _setup_package_tree(['plans_adressage.scripts'])
    _lookup = MagicMock()
    _lookup.get_string = lambda s, loc=None: s
    sys.modules['plans_adressage.scripts.lookup_data'] = _lookup

    _users_repo = MagicMock()
    _users_repo.qgis_config = MagicMock(return_value={
        'mapper': [
            {'layer': 'roads', 'model': 'Road'},
            {'layer': 'zones', 'model': 'Zone'},
        ],
        'other_layers': [
            {'label': 'basemap', 'style': 'basemap.qml', 'url': '?query=select 1'},
        ],
        'categorize': [{'layer': 'roads', 'by': ['type']}],
    })
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
        ['Road', 'Zone', 'Localite', 'Organization', 'Subdivision', 'PanelSign', 'Numbering'],
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
    _QtCore.QVariant = MagicMock()
    _QtCore.QVariant.Int = 2
    _QtCore.QVariant.Double = 3
    _QtCore.QVariant.String = 4
    _QtCore.QVariant.Bool = 5
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


def _make_gui_qgis_core():
    """Return a lighter ``qgis.core`` mock for GUI tests."""
    core = MagicMock()
    for attr in ('QgsProject', 'QgsSymbol', 'QgsWkbTypes', 'QgsFeatureRequest',
                 'QgsExpression', 'QgsMapLayer', 'QgsApplication', 'QgsField',
                 'QgsFeature', 'QgsGeometry', 'QgsDistanceArea', 'QgsPointXY'):
        setattr(core, attr, MagicMock())
    return core


def _make_gui_pyqt_mocks():
    """Return a dict of PyQt subsystem mocks for GUI tests.

    Contains keys: qgis.PyQt, QtCore, QtGui, QtWidgets, uic
    """
    _qgis_pyqt = types.ModuleType('qgis.PyQt')
    _qgis_pyqt.__path__ = ['/fake/qgis/PyQt']

    _qwidget_attrs = {
        '__init__': lambda self, parent=None: None,
        'setObjectName': lambda self, name: None,
        'setSizeGripEnabled': lambda self, enabled: None,
        'setMinimumSize': lambda self, w, h: None,
        'setMaximumSize': lambda self, w, h: None,
        'setWindowTitle': lambda self, title: None,
        'setStyleSheet': lambda self, ss: None,
        'close': lambda self: None,
        'resize': lambda self, w, h: None,
        'width': lambda self: 800,
        'height': lambda self: 600,
        'layout': property(lambda _self: MagicMock()),
    }
    _FakeDialog = type('QDialog', (), _qwidget_attrs)
    _FakeFormClass = type('FORM_CLASS', (), _qwidget_attrs)

    def _setupUi(instance):
        for w in (
            'org_cat', 'type_road', 'dyn_ref3', 'dyn_ref4',
            'cat_act_3', 'num_state', 'mount_status', 'subd_type',
            'zone_type', 'org_type', 'activity_type_3',
            'submit_road', 'submit_zone', 'submit_subd',
            'submit_org', 'submit_num', 'submit_pan',
            'select_ref3', 'select_ref4',
            'road_name', 'road_decision', 'org_name', 'subd_name',
            'nom_zone', 'num_val', 'repetition',
            'ref_name3', 'ref_name4',
            'router', 'frame_12', 'frame_10', 'frame_9',
            'table', 'list_title',
        ):
            setattr(instance, w, MagicMock())
        instance.router.findChild = MagicMock(return_value=MagicMock())
        instance.router.setCurrentWidget = MagicMock()
        instance.findChildren = MagicMock(return_value=[])

    class _FakeFormWithSetup:
        def setupUi(self, w):
            _setupUi(w)

    class _FakePopupDialogType(_FakeFormClass, _FakeFormWithSetup):
        pass

    _qgis_uic = MagicMock()
    _qgis_uic.loadUiType = MagicMock(return_value=(_FakePopupDialogType, MagicMock))

    _qgis_qtcore = MagicMock()
    _qgis_qtcore.Qt = MagicMock()
    _qgis_qtcore.QVariant = MagicMock()
    _qgis_qtcore.QSize = MagicMock()
    _qgis_qtcore.pyqtSignal = MagicMock()
    _qgis_qtcore.pyqtSlot = MagicMock(lambda x: lambda f: f)
    _qgis_qtcore.QObject = MagicMock()

    _qgis_qtgui = MagicMock()
    _qgis_qtgui.QIcon = MagicMock()

    class _FakeQPushButton:
        def __init__(self, text=''):
            self.text = text
            self._slots = []
            self.clicked = MagicMock()
            self.clicked.connect = self._connect_clicked
        def _connect_clicked(self, slot):
            self._slots.append(slot)
            self.clicked.connect = lambda s: self._slots.append(s)
        def click(self):
            for slot in self._slots:
                slot()

    _qgis_qtwidgets = MagicMock()
    _qgis_qtwidgets.QComboBox = MagicMock()
    for w in ('QDateEdit', 'QFormLayout', 'QLayout', 'QLineEdit', 'QSizePolicy',
              'QDialogButtonBox', 'QApplication'):
        setattr(_qgis_qtwidgets, w, MagicMock())
    _qgis_qtwidgets.QMessageBox = MagicMock()
    _qgis_qtwidgets.QPushButton = _FakeQPushButton
    _qgis_qtwidgets.QWidget = MagicMock()
    _qgis_qtwidgets.QDialog = _FakeDialog

    return {
        'qgis.PyQt': _qgis_pyqt,
        'qgis.PyQt.QtCore': _qgis_qtcore,
        'qgis.PyQt.QtGui': _qgis_qtgui,
        'qgis.PyQt.QtWidgets': _qgis_qtwidgets,
        'qgis.PyQt.uic': _qgis_uic,
    }


def _setup_gui_app_packages():
    """Register MagicMock stubs for ``app.*`` subpackages in sys.modules."""
    for pkg in ('app', 'app.core', 'app.users', 'app.orders', 'app.shared',
                'app.core.database', 'app.orders.models', 'app.orders.repository',
                'app.users.models', 'app.users.repository', 'app.users.service',
                'app.shared.utils'):
        _mock = MagicMock()
        _mock.__path__ = [pkg.replace('.', '/')]
        _mock.__package__ = f'plans_adressage.{pkg}'
        _mock.__spec__ = None
        sys.modules[f'plans_adressage.{pkg}'] = _mock


def _setup_gui_domain_mocks():
    """Register constants, scripts, i18n, database, models, and repo mocks."""
    _constants = MagicMock()
    _constants.current_theme = lambda: 'dark'
    _constants.get_theme_qss = lambda t: ''
    _constants.current_locale = lambda: 'ar'
    _constants.locale_value = lambda v, f, loc=None: getattr(v, f)
    _constants.validate_text = lambda t, f, loc: (True, t)
    _constants.LAYER_KEY = 'key'
    _constants.LAYER_ROADS = 'roads'
    _constants.LAYER_FACILITIES = 'facilities'
    _constants.LAYER_SUBDIVISIONS = 'subdivisions'
    _constants.LAYER_ZONES = 'zones'
    _constants.LAYER_NUMBERING = 'numbering'
    _constants.LAYER_PANELS = 'panels'
    _constants.NOTIFY_DURATION = 5
    _constants.SRID = 4326
    _constants.DEFAULT_PANEL_DIM = '60x80'
    sys.modules['plans_adressage.constants'] = _constants

    _lookup = MagicMock()
    _lookup.get_string = lambda s, loc=None: s if isinstance(s, str) else 'test'
    _lookup.apply_widget_texts = lambda w, loc: None
    sys.modules['plans_adressage.scripts.lookup_data'] = _lookup

    _i18n = MagicMock()
    _i18n.tr = lambda s, loc=None: s
    sys.modules['plans_adressage.i18n'] = _i18n

    _shared_utils = MagicMock()
    _shared_utils.get_all_fields_and_labels = MagicMock(return_value=(
        ['valeur', 'etat'], {'valeur': 'Value', 'etat': 'State'},
    ))
    sys.modules['plans_adressage.app.shared.utils'] = _shared_utils

    _database = MagicMock()
    _database.get_session = MagicMock()
    _database.get_session.return_value.query.return_value.count.return_value = 0
    sys.modules['plans_adressage.app.core.database'] = _database

    _orders_models = MagicMock()
    _orders_models.get_all_fields_and_labels = MagicMock(return_value=(
        ['id', 'name'], {'id': 'ID', 'name': 'Name'},
    ))
    for name in ('Road', 'Zone', 'Localite', 'Organization', 'Subdivision', 'PanelSign', 'Numbering'):
        setattr(_orders_models, name, _mock_model_table(MagicMock()))
    sys.modules['plans_adressage.app.orders.models'] = _orders_models

    _users_models = MagicMock()
    _users_models.User = _mock_model_table(MagicMock())
    sys.modules['plans_adressage.app.users.models'] = _users_models

    _users_repo = MagicMock()
    _users_repo.qgis_config = MagicMock(return_value={
        'mapper': [], 'other_layers': [], 'categorize': [],
    })
    sys.modules['plans_adressage.app.users.repository'] = _users_repo

    _orders_repo = MagicMock()
    sys.modules['plans_adressage.app.orders.repository'] = _orders_repo

    _refresh = MagicMock()
    _refresh.refresh_all_layers = MagicMock()
    sys.modules['plans_adressage.layer.refresh'] = _refresh

    _ui_fillers = MagicMock()
    for fn in ('fill_org_category', 'fill_road_type', 'fill_road_reference',
               'fill_panel_reference', 'fill_activity_category',
               'fill_numbering_state', 'fill_mounting_status',
               'fill_subdivision_type', 'fill_zone_type', 'fill_org_type',
               'fill_activity_type'):
        setattr(_ui_fillers, fn, MagicMock())
    sys.modules['plans_adressage.gui.ui_fillers'] = _ui_fillers


def _setup_gui_qgis_mocks():
    """Register qgis, qgis.core, and qgis.gui mocks in sys.modules."""
    _qgis = types.ModuleType('qgis')
    _qgis.__path__ = ['/fake/qgis']
    sys.modules['qgis'] = _qgis
    sys.modules['qgis.core'] = _make_gui_qgis_core()

    class _FakeMapTool:
        def __init__(self, canvas):
            self.canvas = canvas
            self.paused = False
        def reset(self):
            self.points = []
            self.markers = []
            self.labels = []
        def deactivate(self):
            self.reset()

    class _FakeIdentifyTool(_FakeMapTool):
        MODE_FORM = "form"
        MODE_REF = "ref"

    _gui = MagicMock()
    _gui.QgsMapToolIdentify = _FakeIdentifyTool
    _gui.QgsMapToolEmitPoint = _FakeMapTool
    _gui.QgsRubberBand = MagicMock()
    _gui.QgsVertexMarker = MagicMock()
    sys.modules['qgis.gui'] = _gui

    for name, mock in _make_gui_pyqt_mocks().items():
        sys.modules[name] = mock


def setup_gui_mocks():
    """Set up ``plans_adressage`` package hierarchy for GUI module tests.

    Must be called before ``importlib``-loading any ``gui/`` module that
    uses relative imports (``from ..models import ...``).
    """
    if 'plans_adressage' in sys.modules and hasattr(sys.modules['plans_adressage'], '_gui_mocks_ready'):
        return

    _pkg = types.ModuleType('plans_adressage')
    _pkg.__path__ = ['.']
    _pkg.__package__ = 'plans_adressage'
    _pkg._gui_mocks_ready = True
    sys.modules['plans_adressage'] = _pkg

    _setup_package_tree([f'plans_adressage.{sub}' for sub in ('gui', 'scripts', 'layer', 'i18n')])
    _setup_gui_app_packages()
    _setup_gui_domain_mocks()
    _setup_gui_qgis_mocks()

    wire_module_attributes()


def wire_module_attributes():
    """Ensure all ``plans_adressage.*`` submodules are set as parent attributes.

    Python 3.10's ``unittest.mock._importer`` resolves dotted ``@patch``
    targets (e.g. ``'plans_adressage.layer.utils.open'``) by calling
    ``getattr(parent, submodule)`` rather than checking ``sys.modules``.
    This helper ensures every submodule in ``sys.modules`` is also an
    attribute of its parent module.
    """
    for key in list(sys.modules.keys()):
        if key.startswith('plans_adressage.') and '.' in key:
            parts = key.split('.')
            parent_key = '.'.join(parts[:-1])
            attr_name = parts[-1]
            if parent_key in sys.modules:
                try:
                    setattr(sys.modules[parent_key], attr_name, sys.modules[key])
                except (TypeError, AttributeError):
                    pass


def get_qapp():
    """Return a QApplication instance, creating one if needed.

    Works in headless environments when ``QT_QPA_PLATFORM=offscreen`` is set.
    Returns ``None`` if PyQt5 is not installed.
    """
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            import sys
            app = QApplication(sys.argv)
        return app
    except ImportError:
        return None


def make_mock_iface():
    """Create a mock QGIS ``iface`` object."""
    iface = MagicMock()
    iface.messageBar = MagicMock(return_value=MagicMock())
    iface.messageBar().pushMessage = MagicMock()
    iface.activeLayer = MagicMock(return_value=None)
    iface.setActiveLayer = MagicMock()
    iface.mapCanvas = MagicMock(return_value=MagicMock())
    iface.mapCanvas().refresh = MagicMock()
    iface.mapCanvas().refreshAllLayers = MagicMock()
    iface.actionAddFeature = MagicMock(return_value=MagicMock())
    iface.actionVertexTool = MagicMock(return_value=MagicMock())
    iface.actionAddFeature().trigger = MagicMock()
    return iface


def make_mock_layer(layer_type=0, name='test_layer'):
    """Create a mock QGIS vector layer."""
    layer = MagicMock()
    layer.type = MagicMock(return_value=0)
    layer.geometryType = MagicMock(return_value=layer_type)
    layer.name = MagicMock(return_value=name)
    layer.isEditable = MagicMock(return_value=False)
    layer.startEditing = MagicMock()
    layer.commitChanges = MagicMock(return_value=True)
    layer.dataProvider = MagicMock(return_value=MagicMock())
    layer.dataProvider().deleteFeatures = MagicMock()
    layer.dataProvider().addAttributes = MagicMock()
    layer.dataProvider().addFeature = MagicMock()
    layer.updateFields = MagicMock()
    layer.triggerRepaint = MagicMock()
    layer.setRenderer = MagicMock()
    layer.fields = MagicMock(return_value=[])
    layer.getFeatures = MagicMock(return_value=[])
    layer.loadNamedStyle = MagicMock()
    return layer
