"""Popup dialog for viewing and editing feature attributes — Qt Widgets version."""

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QMessageBox,
    QStackedWidget,
    QVBoxLayout,
)

from ..app.core.config import get_theme_qss
from ..app.core.database import get_session
from ..app.orders import models as _models
from ..app.users.repository import qgis_config
from ..constants import current_locale, current_theme
from ..scripts.widget_texts import get_string
from .popup_handlers import (
    POPULATE_DISPATCH,
)
from .popup_handlers import (
    update_numbering as _update_numbering,
)
from .popup_handlers import (
    update_organization as _update_organization,
)
from .popup_handlers import (
    update_panel as _update_panel,
)
from .popup_handlers import (
    update_road as _update_road,
)
from .popup_handlers import (
    update_subdivision as _update_subdivision,
)
from .popup_handlers import (
    update_zone as _update_zone,
)
from .popup_pages import (
    build_city_page,
    build_num_page,
    build_org_page,
    build_pan_page,
    build_road_page,
    build_zone_page,
)
from .ui_fillers import (
    fill_activity_category,
    fill_activity_type,
    fill_mounting_status,
    fill_numbering_state,
    fill_org_category,
    fill_org_type,
    fill_panel_reference,
    fill_road_reference,
    fill_road_type,
    fill_subdivision_type,
    fill_zone_type,
)

if TYPE_CHECKING:
    from .identify_tool import IdentifyTool

logger = logging.getLogger(__name__)

_PAGE_MAP = {
    'zone': 0,
    'roads': 1,
    'org': 2,
    'city': 3,
    'num': 4,
    'pan': 5,
}

# ---------------------------------------------------------------------------
# Form-value dispatch helpers (module-level so they stay readable & testable)
# ---------------------------------------------------------------------------


def _set_zone_values(dialog: 'PopupDialog', data: dict) -> None:
    dialog._set_combo_by_data(dialog._combo_zone_type, data.get('type'))
    if data.get('name'):
        dialog._field_zone_name.setText(str(data['name']))


def _set_road_values(dialog: 'PopupDialog', data: dict) -> None:
    dialog._set_combo_by_data(dialog._combo_road_type, data.get('type'))
    if data.get('name'):
        dialog._field_road_name.setText(str(data['name']))


def _set_org_values(dialog: 'PopupDialog', data: dict) -> None:
    dialog._set_combo_by_data(dialog._combo_org_cat, data.get('category'))
    dialog._set_combo_by_data(dialog._combo_org_type, data.get('type'))
    if data.get('name'):
        dialog._field_org_name.setText(str(data['name']))


def _set_city_values(dialog: 'PopupDialog', data: dict) -> None:
    dialog._set_combo_by_data(dialog._combo_subd_type, data.get('type'))
    if data.get('name'):
        dialog._field_subd_name.setText(str(data['name']))


def _set_num_values(dialog: 'PopupDialog', data: dict) -> None:
    dialog._set_combo_by_data(dialog._combo_road_ref, data.get('refType'))
    if data.get('number'):
        dialog._field_num_val.setText(str(data['number']))
    if data.get('repetition'):
        dialog._field_repetition.setText(str(data['repetition']))
    dialog._set_combo_by_data(dialog._combo_num_state, data.get('state'))
    dialog._set_combo_by_data(dialog._combo_activity_cat, data.get('activityCat'))
    dialog._set_combo_by_data(dialog._combo_activity_type, data.get('activityType'))


def _set_pan_values(dialog: 'PopupDialog', data: dict) -> None:
    dialog._set_combo_by_data(dialog._combo_mount_status, data.get('mountStatus'))
    dialog._set_combo_by_data(dialog._combo_panel_ref, data.get('refType'))


_SET_FORM_DISPATCH: dict[str, Callable] = {
    'zone': _set_zone_values,
    'roads': _set_road_values,
    'org': _set_org_values,
    'city': _set_city_values,
    'num': _set_num_values,
    'pan': _set_pan_values,
}


def _collect_zone_data(dialog: 'PopupDialog') -> dict:
    return {
        'type': dialog._combo_zone_type.currentData(),
        'name': dialog._field_zone_name.text(),
    }


def _collect_road_data(dialog: 'PopupDialog') -> dict:
    return {
        'type': dialog._combo_road_type.currentData(),
        'name': dialog._field_road_name.text(),
    }


def _collect_org_data(dialog: 'PopupDialog') -> dict:
    return {
        'category': dialog._combo_org_cat.currentData(),
        'type': dialog._combo_org_type.currentData(),
        'name': dialog._field_org_name.text(),
    }


def _collect_city_data(dialog: 'PopupDialog') -> dict:
    return {
        'type': dialog._combo_subd_type.currentData(),
        'name': dialog._field_subd_name.text(),
    }


def _collect_num_data(dialog: 'PopupDialog') -> dict:
    return {
        'refType': dialog._combo_road_ref.currentData(),
        'number': dialog._field_num_val.text(),
        'repetition': dialog._field_repetition.text(),
        'state': dialog._combo_num_state.currentData(),
        'activityCat': dialog._combo_activity_cat.currentData(),
        'activityType': dialog._combo_activity_type.currentData(),
    }


def _collect_pan_data(dialog: 'PopupDialog') -> dict:
    return {
        'mountStatus': dialog._combo_mount_status.currentData(),
        'refType': dialog._combo_panel_ref.currentData(),
    }


_COLLECT_FORM_DISPATCH: dict[str, Callable] = {
    'zone': _collect_zone_data,
    'roads': _collect_road_data,
    'org': _collect_org_data,
    'city': _collect_city_data,
    'num': _collect_num_data,
    'pan': _collect_pan_data,
}


class PopupDialog(QDialog):
    """Dialog for updating attributes of a selected feature."""

    def __init__(
        self, layer_name_value, layer_name_key, attribute, iface, *, parent=None
    ) -> None:
        super().__init__(parent)
        self._tr_locale = current_locale()

        self.layer_name_value = layer_name_value
        self.layer_name_key = layer_name_key
        self.attribute = str(attribute)
        self.iface = iface

        self._current_form_data: dict[str, Any] = {}
        self.ref_identify_tool: IdentifyTool | None = None
        self._ref_layer: str = ''
        self._ref_id: str = ''

        # Build UI with real Qt Widgets
        self._init_ui()

        # Apply theme QSS to the dialog shell
        self.setStyleSheet(get_theme_qss(current_theme()))
        self.setWindowTitle(self.layer_name_key)

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        self.setObjectName('rnaPopupDialog')
        self.setMinimumSize(700, 500)
        self.resize(760, 560)
        self.setSizeGripEnabled(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Page stack: 6 form pages (zone, roads, org, city, num, pan)
        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

        build_zone_page(self, self._stack)
        build_road_page(self, self._stack)
        build_org_page(self, self._stack)
        build_city_page(self, self._stack)
        build_num_page(self, self._stack)
        build_pan_page(self, self._stack)

        # Switch to the correct page
        idx = _PAGE_MAP.get(self.layer_name_value, 0)
        self._stack.setCurrentIndex(idx)

        # Populate combos and form data
        self._populate_combos()
        self._connect_signals()
        self.set_form()

    # ------------------------------------------------------------------
    # Signal wiring
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        page_key = self.layer_name_value

        if page_key == 'org':
            self._combo_org_cat.currentIndexChanged.connect(self._on_org_cat_changed)

        if page_key == 'num':
            self._btn_select_ref.clicked.connect(self._on_select_ref)
            self._combo_activity_cat.currentIndexChanged.connect(
                self._on_activity_cat_changed
            )

        if page_key == 'pan':
            self._btn_select_panel_ref.clicked.connect(self._on_select_panel_ref)

    # ------------------------------------------------------------------
    # Combo population
    # ------------------------------------------------------------------

    def _populate_combos(self) -> None:
        page_key = self.layer_name_value
        if page_key == 'zone':
            fill_zone_type(self._combo_zone_type)
        elif page_key == 'roads':
            fill_road_type(self._combo_road_type)
        elif page_key == 'org':
            fill_org_category(self._combo_org_cat)
            cat = self._combo_org_cat.currentData()
            if cat:
                fill_org_type(self._combo_org_type, cat)
        elif page_key == 'city':
            fill_subdivision_type(self._combo_subd_type)
        elif page_key == 'num':
            fill_road_reference(self._combo_road_ref)
            fill_numbering_state(self._combo_num_state)
            fill_activity_category(self._combo_activity_cat)
            cat = self._combo_activity_cat.currentData()
            fill_activity_type(self._combo_activity_type, cat)
        elif page_key == 'pan':
            fill_mounting_status(self._combo_mount_status)
            fill_panel_reference(self._combo_panel_ref)

    def _on_org_cat_changed(self, _index: int = 0) -> None:
        cat = self._combo_org_cat.currentData()
        if cat:
            fill_org_type(self._combo_org_type, cat)

    def _on_activity_cat_changed(self, _index: int = 0) -> None:
        cat = self._combo_activity_cat.currentData()
        fill_activity_type(self._combo_activity_type, cat)

    # ------------------------------------------------------------------
    # Form population (DB → widgets)
    # ------------------------------------------------------------------

    def set_form(self) -> None:
        """Load feature data from DB and populate form widgets."""
        data_list = qgis_config().get('mapper') or []
        for data in data_list:
            if data.get('layer') == self.layer_name_key:
                session = get_session()
                try:
                    model_name = data.get('model')
                    model = getattr(_models, model_name, None)
                    if model is None:
                        logger.warning('Unknown model: %s', model_name)
                        continue

                    query = (
                        session.query(model)
                        .filter(
                            model.id == self.attribute,
                        )
                        .first()
                    )
                    if query:
                        handler = POPULATE_DISPATCH.get(self.layer_name_key)
                        if handler:
                            form_data = handler(self, query, self._tr_locale)
                            self._current_form_data.update(form_data)
                            self._set_form_values(form_data)
                finally:
                    session.close()

    def _set_form_values(self, data: dict) -> None:
        handler = _SET_FORM_DISPATCH.get(self.layer_name_value)
        if handler:
            handler(self, data)

    @staticmethod
    def _set_combo_by_data(combo: QComboBox, value: object) -> None:
        """Set a combo's current index by data value."""
        if value is not None and value != '':
            idx = combo.findData(value)
            if idx >= 0:
                combo.setCurrentIndex(idx)

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def _on_save(self, page_key: str) -> None:
        self._current_form_data = self._collect_form_data(page_key)
        dispatch = {
            'zone': _update_zone,
            'roads': _update_road,
            'org': _update_organization,
            'city': _update_subdivision,
            'num': _update_numbering,
            'pan': _update_panel,
        }
        handler = dispatch.get(page_key)
        if handler:
            handler(self)

    def _collect_form_data(self, page_key: str) -> dict:
        handler = _COLLECT_FORM_DISPATCH.get(page_key)
        if handler:
            return handler(self)
        return {}

    # ------------------------------------------------------------------
    # Reference selection (map tool)
    # ------------------------------------------------------------------

    def _on_select_ref(self) -> None:
        layer_name = self._combo_road_ref.currentData()
        self._start_ref_selection(layer_name)

    def _on_select_panel_ref(self) -> None:
        layer_name = self._combo_panel_ref.currentData()
        self._start_ref_selection(layer_name)

    def _start_ref_selection(self, layer_name: str = '') -> None:
        """Activate map tool to select a reference for the current page."""
        from .identify_tool import (  # pylint: disable=import-outside-toplevel
            IdentifyTool,
        )

        project = QgsProject.instance()

        if layer_name:
            layer = project.mapLayersByName(layer_name)
            if layer:
                self.iface.setActiveLayer(layer[0])
                canvas = self.iface.mapCanvas()
                self.ref_identify_tool = IdentifyTool(
                    canvas,
                    mode=IdentifyTool.MODE_REF,
                )
                self.ref_identify_tool.set_iface(self.iface)
                self.ref_identify_tool.ref_selected.connect(self._on_reference_selected)
                self.ref_identify_tool.set_active_layer(layer[0])
                canvas.setMapTool(self.ref_identify_tool)
        else:
            QMessageBox.critical(
                self,
                get_string('Error', self._tr_locale),
                get_string('Reference type not specified', self._tr_locale),
            )

        layer = project.mapLayersByName(self.layer_name_key)
        if layer:
            self.iface.setActiveLayer(layer[0])

    def _on_reference_selected(self, feature_id: int, layer_name: str) -> None:
        """Called when the user selects a reference feature on the map."""
        self._ref_id = str(feature_id)
        self._ref_layer = layer_name

    # ------------------------------------------------------------------
    # Public API used by popup_handlers
    # ------------------------------------------------------------------
