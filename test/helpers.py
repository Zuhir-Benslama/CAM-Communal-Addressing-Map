"""Test helpers for mocking QGIS and project dependencies."""
import sys
import types
from unittest.mock import MagicMock, PropertyMock


def setup_mocks():
    """Set up mock modules for QGIS and project dependencies in sys.modules.

    Must be called before importing any module that depends on ``qgis``
    or uses relative imports from a ``plans_adressage`` package context.
    """
    # Always re-setup mocks to ensure they are in place

    _pkg = types.ModuleType('plans_adressage')
    _pkg.__path__ = ['.']
    _pkg.__package__ = 'plans_adressage'
    sys.modules['plans_adressage'] = _pkg

    _layer_pkg = types.ModuleType('plans_adressage.layer')
    _layer_pkg.__path__ = ['layer']
    _layer_pkg.__package__ = 'plans_adressage.layer'
    sys.modules['plans_adressage.layer'] = _layer_pkg

    _app_pkg = types.ModuleType('plans_adressage.app')
    _app_pkg.__path__ = ['app']
    _app_pkg.__package__ = 'plans_adressage.app'
    sys.modules['plans_adressage.app'] = _app_pkg

    for subpkg in ('app.core', 'app.orders', 'app.users', 'app.shared'):
        _sp = types.ModuleType(f'plans_adressage.{subpkg}')
        _sp.__path__ = [subpkg.replace('.', '/')]
        _sp.__package__ = f'plans_adressage.{subpkg}'
        sys.modules[f'plans_adressage.{subpkg}'] = _sp

    _shared_utils = MagicMock()
    _shared_utils.get_all_fields_and_labels = MagicMock(return_value=(
        ['valeur', 'etat'], {'valeur': 'Value', 'etat': 'State'},
    ))
    sys.modules['plans_adressage.app.shared.utils'] = _shared_utils

    _constants = MagicMock()
    _constants.NOTIFY_DURATION = 5
    _constants.current_locale = lambda: 'en'
    _constants.CRS = 'EPSG:4326'
    _constants.COOKIE_FILE = '/tmp/test_cookie.toml'
    _constants.LAYER_MUNICIPALITY = 'My Municipality'
    _constants.MEMORY_PROVIDER = 'memory'
    _constants.DEFAULT_STYLE_DIR = '/tmp/styles'
    _constants.STYLE_QML = '/tmp/style.qml'
    sys.modules['plans_adressage.constants'] = _constants

    _scripts_pkg = types.ModuleType('plans_adressage.scripts')
    _scripts_pkg.__path__ = ['scripts']
    _scripts_pkg.__package__ = 'plans_adressage.scripts'
    sys.modules['plans_adressage.scripts'] = _scripts_pkg

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
        'categorize': [
            {'layer': 'roads', 'by': ['type']},
        ],
    })
    _users_repo.get_current_user = MagicMock()
    sys.modules['plans_adressage.app.users.repository'] = _users_repo

    _orders_repo = MagicMock()
    _orders_repo.export_model = MagicMock()
    _orders_repo.count_numberings = MagicMock()
    _orders_repo.count_panels = MagicMock()
    _orders_repo.query_missing_pan = MagicMock()
    _orders_repo.query_missing_num = MagicMock()
    _orders_repo.query_missing_rep = MagicMock()
    sys.modules['plans_adressage.app.orders.repository'] = _orders_repo

    _database = MagicMock()
    _database.get_session = MagicMock()
    sys.modules['plans_adressage.app.core.database'] = _database

    _orders_models = MagicMock()
    for name in ('Road', 'Zone', 'Localite', 'Organization', 'Subdivision', 'PanelSign', 'Numbering'):
        m = MagicMock()
        object.__setattr__(m, '__table__', MagicMock())
        m.__table__.columns = {}
        setattr(_orders_models, name, m)
    sys.modules['plans_adressage.app.orders.models'] = _orders_models

    _users_models = MagicMock()
    _user = MagicMock()
    object.__setattr__(_user, '__table__', MagicMock())
    _user.__table__.columns = {}
    _users_models.User = _user
    sys.modules['plans_adressage.app.users.models'] = _users_models

    _qgis = MagicMock()
    _qgis.__path__ = ['/fake/qgis']
    _qgis.__name__ = 'qgis'
    sys.modules['qgis'] = _qgis

    _core = MagicMock()
    _core.QgsProject = MagicMock()
    _core.QgsProject.instance = MagicMock(return_value=MagicMock())
    _core.QgsMapLayer = MagicMock()
    _core.QgsMapLayer.VectorLayer = 0
    _core.QgsMapLayer.RasterLayer = 1
    _core.QgsWkbTypes = MagicMock()
    _core.QgsWkbTypes.PointGeometry = 0
    _core.QgsWkbTypes.LineGeometry = 1
    _core.QgsWkbTypes.PolygonGeometry = 2
    _core.Qgis = MagicMock()
    _core.Qgis.Info = 0
    _core.Qgis.Critical = 1
    _core.Qgis.Warning = 2
    _core.QgsFeature = MagicMock()
    _core.QgsGeometry = MagicMock()
    _core.QgsGeometry.fromWkt = MagicMock(return_value=MagicMock())
    _core.QgsField = MagicMock()
    _core.QgsSymbol = MagicMock()
    _core.QgsSymbol.defaultSymbol = MagicMock(return_value=MagicMock())
    type(_core.QgsSymbol.defaultSymbol).__name__ = 'builtin_function_or_method'
    _core.QgsExpression = MagicMock()
    _core.QgsExpressionContext = MagicMock()
    _core.QgsExpressionContext().setFeature = MagicMock()
    _core.QgsCategorizedSymbolRenderer = MagicMock()
    _core.QgsSingleSymbolRenderer = MagicMock()
    _core.QgsRendererCategory = MagicMock()
    _core.QgsFillSymbol = MagicMock()
    _core.QgsFillSymbol.createSimple = MagicMock(return_value=MagicMock())
    _core.QgsVectorLayer = MagicMock()
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

    # Mirror 'plans_adressage.app.*' under 'app.*' so that
    # code using direct top-level 'app' imports works in tests.
    for key in list(sys.modules.keys()):
        if key.startswith('plans_adressage.app'):
            app_key = key[len('plans_adressage.'):]
            if app_key not in sys.modules:
                sys.modules[app_key] = sys.modules[key]

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

    for sub in ('gui', 'scripts', 'layer', 'i18n'):
        _sub = types.ModuleType(f'plans_adressage.{sub}')
        _sub.__path__ = [sub]
        _sub.__package__ = f'plans_adressage.{sub}'
        sys.modules[f'plans_adressage.{sub}'] = _sub

    # Mock app packages to prevent real SQLAlchemy-dependent imports
    for pkg in ('app', 'app.core', 'app.users', 'app.orders', 'app.shared',
                'app.core.database', 'app.orders.models', 'app.orders.repository',
                'app.users.models', 'app.users.repository', 'app.users.service',
                'app.shared.utils'):
        _mock = MagicMock()
        _mock.__path__ = [pkg.replace('.', '/')]
        _mock.__package__ = f'plans_adressage.{pkg}'
        _mock.__spec__ = None
        sys.modules[f'plans_adressage.{pkg}'] = _mock

    _constants = MagicMock()
    _constants.current_theme = lambda: 'dark'
    _constants.get_theme_qss = lambda t: ''
    _constants.current_locale = lambda: 'ar'
    _constants.locale_value = lambda v, f, l=None: getattr(v, f)
    _constants.validate_text = lambda t, f, l: (True, t)
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
    _lookup.apply_widget_texts = lambda w, l: None
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
        m = MagicMock()
        object.__setattr__(m, '__table__', MagicMock())
        m.__table__.columns = {}
        setattr(_orders_models, name, m)
    sys.modules['plans_adressage.app.orders.models'] = _orders_models

    _users_models = MagicMock()
    _users_models.User = MagicMock()
    object.__setattr__(_users_models.User, '__table__', MagicMock())
    _users_models.User.__table__.columns = {}
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
               'fill_subdivision_type', 'fill_type_zone', 'fill_type_org',
               'fill_type_act'):
        setattr(_ui_fillers, fn, MagicMock())
    sys.modules['plans_adressage.gui.ui_fillers'] = _ui_fillers

    # Mock qgis.core and qgis.gui — their C extensions (qgis._core / qgis._gui)
    # depend on Qt5Quick which has a missing symbol on this system.
    _qgis = types.ModuleType('qgis')
    _qgis.__path__ = ['/fake/qgis']
    sys.modules['qgis'] = _qgis

    _core = MagicMock()
    _core.QgsProject = MagicMock()
    _core.QgsSymbol = MagicMock()
    _core.QgsWkbTypes = MagicMock()
    _core.QgsFeatureRequest = MagicMock()
    _core.QgsExpression = MagicMock()
    _core.QgsMapLayer = MagicMock()
    _core.QgsApplication = MagicMock()
    _core.QgsField = MagicMock()
    _core.QgsFeature = MagicMock()
    _core.QgsGeometry = MagicMock()
    _core.QgsDistanceArea = MagicMock()
    _core.QgsPointXY = MagicMock()
    sys.modules['qgis.core'] = _core

    class _FakeMapTool:
        """Minimal stub that accepts canvas arg in __init__."""
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
        """Stub IdentifyTool base class."""
        MODE_FORM = "form"
        MODE_REF = "ref"

    _gui = MagicMock()
    _gui.QgsMapToolIdentify = _FakeIdentifyTool
    _gui.QgsMapToolEmitPoint = _FakeMapTool
    _gui.QgsRubberBand = MagicMock()
    _gui.QgsVertexMarker = MagicMock()
    sys.modules['qgis.gui'] = _gui

    _qgis_pyqt = types.ModuleType('qgis.PyQt')
    _qgis_pyqt.__path__ = ['/fake/qgis/PyQt']
    sys.modules['qgis.PyQt'] = _qgis_pyqt

    # Common QWidget methods needed by PopupDialog
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
        'layout': property(lambda self: MagicMock()),
    }
    _FakeDialog = type('QDialog', (), _qwidget_attrs)
    _FakeFormClass = type('FORM_CLASS', (), _qwidget_attrs)

    # SetupUi must create all UI widget attributes referenced by PopupDialog
    def _setupUi(instance):
        uiwidgets = (
            'cat_org', 'type_voie', 'dyn_ref3', 'dyn_ref4',
            'cat_act_3', 'num_etat', 'etat_mont', 'type_city',
            'type_zone', 'type_org', 'type_act_3',
            'submit_voie', 'submit_zone', 'submit_city',
            'submit_org', 'submit_num', 'submit_pan',
            'select_ref3', 'select_ref4',
            'nom_voie', 'dec_voie', 'nom_org', 'nom_city',
            'nom_zone', 'num_val', 'repetition',
            'ref_name3', 'ref_name4',
            'router', 'frame_12', 'frame_10', 'frame_9',
            'table', 'list_title',
        )
        for w in uiwidgets:
            setattr(instance, w, MagicMock())
        instance.router.findChild = MagicMock(return_value=MagicMock())
        instance.router.setCurrentWidget = MagicMock()
        instance.findChildren = MagicMock(return_value=[])

    class _FakeFormWithSetup:
        def setupUi(self, w):
            _setupUi(w)

    _FakePopupDialogType = type('PopupDialog', (_FakeFormClass, _FakeFormWithSetup), {})

    _qgis_uic = MagicMock()
    _qgis_uic.loadUiType = MagicMock(return_value=(_FakePopupDialogType, MagicMock))
    sys.modules['qgis.PyQt.uic'] = _qgis_uic

    _qgis_qtcore = MagicMock()
    _qgis_qtcore.Qt = MagicMock()
    _qgis_qtcore.QVariant = MagicMock()
    _qgis_qtcore.QSize = MagicMock()
    _qgis_qtcore.pyqtSignal = MagicMock()
    _qgis_qtcore.pyqtSlot = MagicMock(lambda x: lambda f: f)
    _qgis_qtcore.QObject = MagicMock()
    sys.modules['qgis.PyQt.QtCore'] = _qgis_qtcore

    _qgis_qtgui = MagicMock()
    _qgis_qtgui.QIcon = MagicMock()
    sys.modules['qgis.PyQt.QtGui'] = _qgis_qtgui

    class _FakeQPushButton:
        """QPushButton stub that properly connects and emits signals."""
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
    sys.modules['qgis.PyQt.QtWidgets'] = _qgis_qtwidgets

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
