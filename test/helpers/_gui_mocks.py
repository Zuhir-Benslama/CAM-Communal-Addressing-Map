"""GUI mock setup for ``setup_gui_mocks()``."""

import sys
import types
from unittest.mock import MagicMock

from ._shared import _mock_model_table, _setup_package_tree, wire_module_attributes


def _make_gui_qgis_core():
    """Return a lighter ``qgis.core`` mock for GUI tests."""
    core = MagicMock()
    for attr in (
        'QgsProject',
        'QgsSymbol',
        'QgsWkbTypes',
        'QgsFeatureRequest',
        'QgsExpression',
        'QgsMapLayer',
        'QgsApplication',
        'QgsField',
        'QgsFeature',
        'QgsGeometry',
        'QgsDistanceArea',
        'QgsPointXY',
    ):
        setattr(core, attr, MagicMock())
    core.QVariant = types.SimpleNamespace(
        Bool=1,
        Int=2,
        Double=6,
        String=10,
    )
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
        'setWindowTitle': lambda self, title: setattr(
            self,
            '_window_title',
            title,
        ),
        'windowTitle': lambda self: getattr(self, '_window_title', ''),
        'setStyleSheet': lambda self, ss: None,
        'findChild': lambda self, cls, name='': MagicMock(),
        'close': lambda self: None,
        'resize': lambda self, w, h: None,
        'width': lambda self: 800,
        'height': lambda self: 600,
        'layout': property(lambda _self: MagicMock()),
    }
    _FakeDialog = type('QDialog', (), _qwidget_attrs)
    _FakeFormClass = type('FORM_CLASS', (), _qwidget_attrs)

    class _FakeLabel:
        def __init__(self, text=''):
            self._text = text
            self._enabled = True

        def setAlignment(self, _alignment):
            return None

        def setProperty(self, _name, _value):
            return None

        def setSizePolicy(self, *_args):
            return None

        def setText(self, text):
            self._text = text

        def text(self):
            return self._text

    class _FakeTable:
        def __init__(self):
            self._rows = 0
            self._columns = 0
            self._items = {}
            self._sorting_enabled = False
            self._vertical_header = MagicMock()

        def isSortingEnabled(self):
            return self._sorting_enabled

        def setSortingEnabled(self, enabled):
            self._sorting_enabled = enabled

        def setAlternatingRowColors(self, _enabled):
            return None

        def setSelectionBehavior(self, _behavior):
            return None

        def setSelectionMode(self, _mode):
            return None

        def verticalHeader(self):
            return self._vertical_header

        def setRowCount(self, rows):
            self._rows = rows

        def rowCount(self):
            return self._rows

        def setColumnCount(self, columns):
            self._columns = columns

        def columnCount(self):
            return self._columns

        def setHorizontalHeaderLabels(self, _labels):
            return None

        def setItem(self, row, column, item):
            self._items[(row, column)] = item

        def item(self, row, column):
            return self._items.get((row, column))

    class _FakeTableWidgetItem:
        def __init__(self, text=''):
            self._text = text

        def text(self):
            return self._text

    def _setupUi(instance):
        for w in (
            'org_cat',
            'type_road',
            'dyn_ref3',
            'dyn_ref4',
            'cat_act_3',
            'num_state',
            'mount_status',
            'subd_type',
            'zone_type',
            'org_type',
            'activity_type_3',
            'submit_road',
            'submit_zone',
            'submit_subd',
            'submit_org',
            'submit_num',
            'submit_pan',
            'select_ref3',
            'select_ref4',
            'road_name',
            'road_decision',
            'org_name',
            'subd_name',
            'nom_zone',
            'num_val',
            'repetition',
            'ref_name3',
            'ref_name4',
            'router',
            'frame_2',
            'frame_12',
            'frame_10',
            'frame_9',
            'table',
            'label',
            'label_24',
            'list_title',
        ):
            setattr(instance, w, MagicMock())
        instance.label = _FakeLabel()
        instance.label_24 = _FakeLabel()
        instance.list_title = _FakeLabel()
        instance.table = _FakeTable()
        instance.router.findChild = MagicMock(return_value=MagicMock())
        instance.router.setCurrentWidget = MagicMock()
        instance.findChildren = MagicMock(return_value=[])
        instance.findChild = MagicMock(return_value=MagicMock())

    class _FakeFormWithSetup:
        def setupUi(self, w):
            _setupUi(w)

    class _FakePopupDialogType(_FakeFormClass, _FakeFormWithSetup):
        pass

    _qgis_uic = MagicMock()
    _qgis_uic.loadUiType = MagicMock(return_value=(_FakePopupDialogType, MagicMock))

    _qgis_qtcore = MagicMock()
    _qgis_qtcore.Qt = types.SimpleNamespace(
        AlignmentFlag=types.SimpleNamespace(
            AlignCenter=132,
            AlignHCenter=4,
            AlignLeft=1,
            AlignVCenter=128,
        ),
        ContextMenuPolicy=types.SimpleNamespace(
            CustomContextMenu=3,
            DefaultContextMenu=1,
        ),
        CursorShape=types.SimpleNamespace(ArrowCursor=0),
        DockWidgetArea=types.SimpleNamespace(LeftDockWidgetArea=1),
        Key=types.SimpleNamespace(
            Key_E=69,
            Key_P=80,
            Key_R=82,
            Key_Return=16777220,
        ),
        LayoutDirection=types.SimpleNamespace(
            LeftToRight=0,
            RightToLeft=1,
        ),
        MouseButton=types.SimpleNamespace(LeftButton=1, RightButton=2),
    )
    _qgis_qtcore.QVariant = MagicMock()
    _qgis_qtcore.QSize = MagicMock()
    _qgis_qtcore.pyqtSignal = MagicMock()
    _qgis_qtcore.pyqtSlot = lambda *types, **kw: lambda f: f
    _qgis_qtcore.QObject = type(
        'QObject',
        (),
        {
            '__init__': lambda self, parent=None: None,
        },
    )

    _qgis_qtgui = MagicMock()
    _qgis_qtgui.QIcon = MagicMock()

    class _FakeQPushButton:
        def __init__(self, text=''):
            self.text = text
            self._slots = []
            self._enabled = True
            self.clicked = MagicMock()
            self.clicked.connect = self._connect_clicked

        def _connect_clicked(self, slot):
            self._slots.append(slot)
            self.clicked.connect = self._slots.append

        def setEnabled(self, enabled):
            self._enabled = enabled

        def isEnabled(self):
            return self._enabled

        def setIconSize(self, _size):
            return None

        def setMinimumHeight(self, _height):
            return None

        def setProperty(self, _name, _value):
            return None

        def setSizePolicy(self, *_args):
            return None

        def setMaximumWidth(self, _width):
            return None

        def click(self):
            for slot in self._slots:
                slot()

    _qgis_qtwidgets = MagicMock()
    _qgis_qtwidgets.QComboBox = MagicMock()
    for w in (
        'QDateEdit',
        'QFormLayout',
        'QLayout',
        'QLineEdit',
        'QSizePolicy',
        'QDialogButtonBox',
        'QApplication',
    ):
        setattr(_qgis_qtwidgets, w, MagicMock())
    _qgis_qtwidgets.QMessageBox = MagicMock()
    _qgis_qtwidgets.QPushButton = _FakeQPushButton
    _qgis_qtwidgets.QLabel = _FakeLabel
    _qgis_qtwidgets.QTableWidgetItem = _FakeTableWidgetItem
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
    for pkg in (
        'app',
        'app.core',
        'app.users',
        'app.orders',
        'app.shared',
        'app.core.database',
        'app.orders.models',
        'app.orders.repository',
        'app.users.models',
        'app.users.repository',
        'app.users.service',
        'app.shared.utils',
    ):
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

    _widget_texts = MagicMock()
    _widget_texts.get_string = lambda s, loc=None: s if isinstance(s, str) else 'test'
    _widget_texts.apply_widget_texts = lambda w, loc: None
    sys.modules['plans_adressage.scripts.widget_texts'] = _widget_texts

    _i18n = MagicMock()
    _i18n.tr = lambda s, loc=None: s
    sys.modules['plans_adressage.i18n'] = _i18n

    _shared_utils = MagicMock()
    _shared_utils.get_all_fields_and_labels = MagicMock(
        return_value=(
            ['value', 'state'],
            {'value': 'Value', 'state': 'State'},
        )
    )
    sys.modules['plans_adressage.app.shared.utils'] = _shared_utils

    _database = MagicMock()
    _database.get_session = MagicMock()
    sess_q = _database.get_session.return_value.query.return_value
    sess_q.count.return_value = 0
    sys.modules['plans_adressage.app.core.database'] = _database

    _orders_models = MagicMock(spec=[])
    _orders_models.get_all_fields_and_labels = MagicMock(
        return_value=(
            ['id', 'name'],
            {'id': 'ID', 'name': 'Name'},
        )
    )
    for name in (
        'Road',
        'Zone',
        'Organization',
        'Subdivision',
        'PanelSign',
        'Numbering',
    ):
        setattr(_orders_models, name, _mock_model_table(MagicMock()))
    sys.modules['plans_adressage.app.orders.models'] = _orders_models

    _users_models = MagicMock()
    _users_models.User = _mock_model_table(MagicMock())
    sys.modules['plans_adressage.app.users.models'] = _users_models

    _users_repo = MagicMock()
    _users_repo.qgis_config = MagicMock(
        return_value={
            'mapper': [],
            'other_layers': [],
            'categorize': [],
        }
    )
    sys.modules['plans_adressage.app.users.repository'] = _users_repo

    _orders_repo = MagicMock()
    sys.modules['plans_adressage.app.orders.repository'] = _orders_repo

    _refresh = MagicMock()
    _refresh.refresh_all_layers = MagicMock()
    sys.modules['plans_adressage.layer.refresh'] = _refresh

    _ui_fillers = MagicMock()
    for fn in (
        'fill_org_category',
        'fill_road_type',
        'fill_road_reference',
        'fill_panel_reference',
        'fill_activity_category',
        'fill_numbering_state',
        'fill_mounting_status',
        'fill_subdivision_type',
        'fill_zone_type',
        'fill_org_type',
        'fill_activity_type',
    ):
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
        MODE_FORM = 'form'
        MODE_REF = 'ref'

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
    if 'plans_adressage' in sys.modules and hasattr(
        sys.modules['plans_adressage'], '_gui_mocks_ready'
    ):
        return

    _pkg = types.ModuleType('plans_adressage')
    _pkg.__path__ = ['.']
    _pkg.__package__ = 'plans_adressage'
    _pkg._gui_mocks_ready = True
    sys.modules['plans_adressage'] = _pkg

    _setup_package_tree(
        [f'plans_adressage.{sub}' for sub in ('gui', 'scripts', 'layer', 'i18n')]
    )
    _setup_gui_app_packages()
    _setup_gui_domain_mocks()
    _setup_gui_qgis_mocks()

    wire_module_attributes()
