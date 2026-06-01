"""Popup dialog for viewing and editing feature attributes — QML version."""
import logging
import os
from typing import TYPE_CHECKING

from qgis.PyQt.QtCore import QObject, QUrl, pyqtSlot
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QVBoxLayout
from qgis.core import QgsProject

try:
    from qgis.PyQt.QtQuickWidgets import QQuickWidget
    _HAS_QML = True
except ImportError:
    QQuickWidget = None  # type: ignore[assignment]
    _HAS_QML = False

from ..app.core.config import get_theme_qss
from ..app.core.database import get_session
from ..app.orders import models as _models
from ..app.users.repository import qgis_config
from ..constants import current_locale, current_theme
from ..scripts.lookup_data import get_string, locale_label
from .popup_handlers import (
    POPULATE_DISPATCH,
    update_numbering as _update_numbering,
    update_organization as _update_organization,
    update_panel as _update_panel,
    update_road as _update_road,
    update_subdivision as _update_subdivision,
    update_zone as _update_zone,
)
from .ui_fillers import (
    get_activity_category_options,
    get_activity_type_options,
    get_mounting_status_options,
    get_numbering_state_options,
    get_org_category_options,
    get_org_type_options,
    get_panel_reference_options,
    get_road_reference_options,
    get_road_type_options,
    get_subdivision_type_options,
    get_zone_type_options,
)

if TYPE_CHECKING:
    from .identify_tool import IdentifyTool

logger = logging.getLogger(__name__)

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QML_DIR = os.path.join(PLUGIN_DIR, 'qml')


class PopupBridge(QObject):
    """Bridge object exposed to QML for Python ↔ QML communication."""

    def __init__(self, dialog: 'PopupDialog') -> None:
        super().__init__()
        self.dialog = dialog

    # ------------------------------------------------------------------
    # Called from QML when the user clicks Save
    # ------------------------------------------------------------------
    @pyqtSlot(str, 'QVariantMap')
    def saveForm(self, pageKey: str, data: dict) -> None:
        self.dialog._current_form_data = data
        dispatch = {
            'zone': _update_zone,
            'roads': _update_road,
            'org': _update_organization,
            'city': _update_subdivision,
            'num': _update_numbering,
            'pan': _update_panel,
        }
        handler = dispatch.get(pageKey)
        if handler:
            handler(self.dialog)

    # ------------------------------------------------------------------
    # Called from QML when the user clicks "Select Reference"
    # ------------------------------------------------------------------
    @pyqtSlot(str, str)
    def selectReference(self, pageKey: str, layerName: str) -> None:
        if pageKey == 'num':
            self.dialog.select_numbering_reference(layerName)
        elif pageKey == 'pan':
            self.dialog.select_panel_reference(layerName)

    # ------------------------------------------------------------------
    # Called from QML when the org category combo changes
    # ------------------------------------------------------------------
    @pyqtSlot(str)
    def onOrgCatChanged(self, catValue: str) -> None:
        self.dialog._update_org_type_options(catValue)

    # ------------------------------------------------------------------
    # Called from QML when the activity category combo changes
    # ------------------------------------------------------------------
    @pyqtSlot(str)
    def onActivityCatChanged(self, catValue: str) -> None:
        self.dialog._update_activity_type_options(catValue)

    # ------------------------------------------------------------------
    # Accessors for existing handler code (reads QML form data)
    # ------------------------------------------------------------------
    def get(self, field: str, default=None):
        return self.dialog._current_form_data.get(field, default)

    def get_field_text(self, field: str) -> str:
        return str(self.dialog._current_form_data.get(field, ''))

    def get_field_index(self, field: str) -> int:
        return int(self.dialog._current_form_data.get(field, -1))


_COMBO_GETTERS = {
    'zone': {'zoneTypes': get_zone_type_options},
    'roads': {'roadTypes': get_road_type_options},
    'org': {
        'orgCats': get_org_category_options,
        'orgTypes': get_org_type_options,
    },
    'city': {'subdTypes': get_subdivision_type_options},
    'num': {
        'refTypes': get_road_reference_options,
        'states': get_numbering_state_options,
        'activityCats': get_activity_category_options,
        'activityTypes': get_activity_type_options,
    },
    'pan': {
        'mountStatuses': get_mounting_status_options,
        'refTypes': get_panel_reference_options,
    },
}


class PopupDialog(QDialog):
    """Dialog for updating attributes of a selected feature (QML-backed)."""

    def __init__(self, layer_name_value, layer_name_key, attribute, iface, *,
                 parent=None) -> None:
        super().__init__(parent)
        self._tr_locale = current_locale()

        self.layer_name_value = layer_name_value
        self.layer_name_key = layer_name_key
        self.attribute = str(attribute)
        self.iface = iface

        self._current_form_data: dict = {}
        self.ref_identify_tool: 'IdentifyTool | None' = None
        self._ref_layer: str = ''
        self._ref_id: str = ''

        # Build UI with QQuickWidget instead of uic.loadUi
        self._init_qml()

        # Apply theme QSS to the dialog shell
        self.setStyleSheet(get_theme_qss(current_theme()))
        self.setWindowTitle(self.layer_name_key)

    # ------------------------------------------------------------------
    # QML setup
    # ------------------------------------------------------------------
    def _init_qml(self) -> None:
        if not _HAS_QML or QQuickWidget is None:
            raise ImportError(
                "Qt Quick Widgets (QtQml) is not available.\n"
                "Please install the Qt Quick / QML package for your system\n"
                "(e.g., python3-pyqt6.qml or qml6 on Debian/Ubuntu)."
            )
        self.setObjectName('rnaPopupDialog')
        self.setMinimumSize(700, 500)
        self.resize(760, 560)
        self.setSizeGripEnabled(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._quick_widget = QQuickWidget()
        self._quick_widget.setResizeMode(QQuickWidget.SizeRootObjectToView)

        # Add our QML directory to the import path
        engine = self._quick_widget.engine()
        engine.addImportPath(QML_DIR)
        for p in ('/usr/lib64/qt5/qml', '/usr/lib/qt5/qml',
                  '/usr/local/lib/python3.14/site-packages/PyQt5/Qt5/qml'):
            if os.path.isdir(p):
                engine.addImportPath(p)

        # Bridge for QML → Python calls
        self._bridge = PopupBridge(self)
        context = self._quick_widget.rootContext()
        context.setContextProperty('pluginBridge', self._bridge)
        context.setContextProperty('layerNameValue', self.layer_name_value)
        context.setContextProperty('layerNameKey', self.layer_name_key)
        context.setContextProperty('isDark', current_theme() == 'dark')

        # Load the main QML file
        qml_path = os.path.join(QML_DIR, 'popup', 'PopupDialog.qml')
        self._quick_widget.setSource(QUrl.fromLocalFile(qml_path))

        layout.addWidget(self._quick_widget)

        # Populate combos and form data after QML is loaded
        self._qml_root = self._quick_widget.rootObject()
        self._populate_combos()
        self.set_form()

    # ------------------------------------------------------------------
    # Combo population
    # ------------------------------------------------------------------
    def _populate_combos(self) -> None:
        """Push combo options for the current page to QML."""
        getters = _COMBO_GETTERS.get(self.layer_name_value, {})
        options = {}
        for key, getter in getters.items():
            try:
                options[key] = getter(self._tr_locale)
            except Exception:
                logger.exception('Failed to get options for %s', key)
                options[key] = []
        self._qml_root.setComboOptions(options)

    def _update_org_type_options(self, cat_value: str) -> None:
        """Re-populate org type options when category changes."""
        try:
            options = get_org_type_options(self._tr_locale, cat_value)
        except Exception:
            logger.exception('Failed to get org type options')
            options = []
        self._qml_root.setComboOptions({'orgTypes': options})

    def _update_activity_type_options(self, cat_value: str) -> None:
        """Re-populate activity type options when category changes."""
        try:
            options = get_activity_type_options(self._tr_locale, cat_value)
        except Exception:
            logger.exception('Failed to get activity type options')
            options = []
        self._qml_root.setComboOptions({'activityTypes': options})

    # ------------------------------------------------------------------
    # Form population (DB → QML)
    # ------------------------------------------------------------------
    def set_form(self) -> None:
        """Load feature data from DB and push to QML form."""
        data_list = qgis_config().get('mapper') or []
        for data in data_list:
            if data.get('layer') == self.layer_name_key:
                session = get_session()
                try:
                    model_name = data.get('model')
                    model = getattr(_models, model_name, None)
                    if model is None:
                        logger.warning("Unknown model: %s", model_name)
                        continue

                    query = session.query(model).filter(
                        model.id == self.attribute,
                    ).first()
                    if query:
                        handler = POPULATE_DISPATCH.get(
                            self.layer_name_key)
                        if handler:
                            form_data = handler(
                                self, query, self._tr_locale)
                            self._current_form_data.update(form_data)
                            self._qml_root.setFormData(form_data)
                finally:
                    session.close()

    # ------------------------------------------------------------------
    # Reference selection (map tool)
    # ------------------------------------------------------------------
    def select_numbering_reference(self, layer_name: str = '') -> None:
        """Activate map tool to select a reference for numbering."""
        from .identify_tool import (  # pylint: disable=import-outside-toplevel
            IdentifyTool,
        )
        self._qml_root.setReferenceName('')
        project = QgsProject.instance()

        if layer_name:
            layer = project.mapLayersByName(layer_name)
            if layer:
                self.iface.setActiveLayer(layer[0])
                canvas = self.iface.mapCanvas()
                self.ref_identify_tool = IdentifyTool(
                    canvas, mode=IdentifyTool.MODE_REF,
                )
                self.ref_identify_tool.set_iface(self.iface)
                self.ref_identify_tool.ref_selected.connect(
                    self._on_reference_selected)
                self.ref_identify_tool.set_active_layer(layer[0])
                canvas.setMapTool(self.ref_identify_tool)
        else:
            QMessageBox.critical(
                self,
                get_string("Error", self._tr_locale),
                get_string("Reference type not specified", self._tr_locale),
            )

        layer = project.mapLayersByName(self.layer_name_key)
        if layer:
            self.iface.setActiveLayer(layer[0])

    def select_panel_reference(self, layer_name: str = '') -> None:
        """Activate map tool to select a reference for panel."""
        from .identify_tool import (  # pylint: disable=import-outside-toplevel
            IdentifyTool,
        )
        self._qml_root.setReferenceName('')
        project = QgsProject.instance()

        if layer_name:
            layer = project.mapLayersByName(layer_name)
            if layer:
                self.iface.setActiveLayer(layer[0])
                canvas = self.iface.mapCanvas()
                self.ref_identify_tool = IdentifyTool(
                    canvas, mode=IdentifyTool.MODE_REF,
                )
                self.ref_identify_tool.set_iface(self.iface)
                self.ref_identify_tool.ref_selected.connect(
                    self._on_reference_selected)
                self.ref_identify_tool.set_active_layer(layer[0])
                canvas.setMapTool(self.ref_identify_tool)
        else:
            QMessageBox.critical(
                self,
                get_string("Error", self._tr_locale),
                get_string("Reference type not specified", self._tr_locale),
            )

        layer = project.mapLayersByName(self.layer_name_key)
        if layer:
            self.iface.setActiveLayer(layer[0])

    def _on_reference_selected(self, feature_id, layer_name) -> None:
        """Called when the user selects a reference feature on the map."""
        self._ref_id = str(feature_id)
        self._ref_layer = layer_name
        display_name = f'{layer_name} [{feature_id}]'
        self._qml_root.setReferenceName(display_name)

    # ------------------------------------------------------------------
    # Public API used by popup_handlers
    # ------------------------------------------------------------------
    @property
    def bridge(self) -> PopupBridge:
        return self._bridge

    def _set_combo_value(self, combo_name: str, value: str) -> None:
        """Set a combo by value (stored for populate handlers)."""
        self._current_form_data[combo_name] = value

    def route(self, page_index) -> None:
        """Switch the stacked widget to the given page (compat wrapper)."""
        self._qml_root.switchToPage(page_index)
