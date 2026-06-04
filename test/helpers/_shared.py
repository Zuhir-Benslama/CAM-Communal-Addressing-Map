"""Shared utility functions used by both core and GUI mock modules."""

import importlib
import os
import sys
import types
from unittest.mock import MagicMock


def _setup_package_tree(packages):
    """Register a list of dotted package names in sys.modules."""
    for name in packages:
        mod = types.ModuleType(name)
        parts = name.split('.')
        if len(parts) == 1:
            mod.__path__ = ['.']
        else:
            mod.__path__ = ['/'.join(parts[1:])]
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


def _mirror_app_modules():
    """Mirror ``plans_adressage.app.*`` under ``app.*`` for direct imports."""
    for key in list(sys.modules.keys()):
        if key.startswith('plans_adressage.app'):
            app_key = key[len('plans_adressage.') :]
            if app_key not in sys.modules:
                sys.modules[app_key] = sys.modules[key]


def wire_module_attributes():
    """Ensure all ``plans_adressage.*`` submodules are set as parent attrs.

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
                    parent_mod = sys.modules[parent_key]
                    setattr(parent_mod, attr_name, sys.modules[key])
                except (TypeError, AttributeError):
                    pass


def _qt_widgets_module():
    """Return the preferred QtWidgets module for GUI tests."""
    for module_name in (
        'PyQt6.QtWidgets',
        'qgis.PyQt.QtWidgets',
    ):
        try:
            return importlib.import_module(module_name)
        except ImportError:
            continue
    return None


def get_qt_widget_class(name):
    """Return a QtWidgets class by name from the active test binding."""
    module = _qt_widgets_module()
    return getattr(module, name) if module is not None else None


def get_qapp():
    """Return a QApplication instance, creating one if needed.

    Works in headless environments when ``QT_QPA_PLATFORM=offscreen`` is set.
    Returns ``None`` if no supported Qt binding is installed.
    """
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    module = _qt_widgets_module()
    if module is None:
        return None
    QApplication = module.QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


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
