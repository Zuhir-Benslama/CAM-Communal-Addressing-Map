"""Popup dialog for viewing and editing feature attributes — Qt Widgets version."""

import logging
from typing import TYPE_CHECKING

from qgis.core import QgsProject
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..app.core.config import get_theme_qss
from ..app.core.database import get_session
from ..app.orders import models as _models
from ..app.users.repository import qgis_config
from ..constants import current_locale, current_theme
from ..scripts.lookup_data import get_string
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

        self._current_form_data: dict = {}
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

        self._build_zone_page()
        self._build_road_page()
        self._build_org_page()
        self._build_city_page()
        self._build_num_page()
        self._build_pan_page()

        # Switch to the correct page
        idx = _PAGE_MAP.get(self.layer_name_value, 0)
        self._stack.setCurrentIndex(idx)

        # Populate combos and form data
        self._populate_combos()
        self._connect_signals()
        self.set_form()

    # ------------------------------------------------------------------
    # Page builders
    # ------------------------------------------------------------------

    def _build_zone_page(self) -> None:
        w = QWidget()
        w.setObjectName('zonePage')
        layout = QVBoxLayout(w)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(8)

        self._combo_zone_type = QComboBox()
        self._combo_zone_type.setObjectName('zone_type')
        self._combo_zone_type.setMaximumWidth(280)
        form.addRow('Type:', self._combo_zone_type)

        self._field_zone_name = QLineEdit()
        self._field_zone_name.setObjectName('nom_zone')
        self._field_zone_name.setMaximumWidth(280)
        form.addRow('Name:', self._field_zone_name)

        layout.addLayout(form)
        layout.addStretch()

        btn = QPushButton('Save')
        btn.setMaximumWidth(200)
        btn.clicked.connect(lambda: self._on_save('zone'))
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._stack.addWidget(w)

    def _build_road_page(self) -> None:
        w = QWidget()
        w.setObjectName('roadPage')
        layout = QVBoxLayout(w)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(8)

        self._combo_road_type = QComboBox()
        self._combo_road_type.setObjectName('type_road')
        self._combo_road_type.setMaximumWidth(280)
        form.addRow('Type:', self._combo_road_type)

        self._field_road_name = QLineEdit()
        self._field_road_name.setObjectName('road_name')
        self._field_road_name.setMaximumWidth(280)
        form.addRow('Name:', self._field_road_name)

        layout.addLayout(form)
        layout.addStretch()

        btn = QPushButton('Save')
        btn.setMaximumWidth(200)
        btn.clicked.connect(lambda: self._on_save('roads'))
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._stack.addWidget(w)

    def _build_org_page(self) -> None:
        w = QWidget()
        w.setObjectName('orgPage')
        layout = QVBoxLayout(w)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(8)

        self._combo_org_cat = QComboBox()
        self._combo_org_cat.setObjectName('org_cat')
        self._combo_org_cat.setMaximumWidth(280)
        form.addRow('Category:', self._combo_org_cat)

        self._combo_org_type = QComboBox()
        self._combo_org_type.setObjectName('org_type')
        self._combo_org_type.setMaximumWidth(280)
        form.addRow('Type:', self._combo_org_type)

        self._field_org_name = QLineEdit()
        self._field_org_name.setObjectName('org_name')
        self._field_org_name.setMaximumWidth(280)
        form.addRow('Name:', self._field_org_name)

        layout.addLayout(form)
        layout.addStretch()

        btn = QPushButton('Save')
        btn.setMaximumWidth(200)
        btn.clicked.connect(lambda: self._on_save('org'))
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._stack.addWidget(w)

    def _build_city_page(self) -> None:
        w = QWidget()
        w.setObjectName('cityPage')
        layout = QVBoxLayout(w)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(8)

        self._combo_subd_type = QComboBox()
        self._combo_subd_type.setObjectName('subd_type')
        self._combo_subd_type.setMaximumWidth(280)
        form.addRow('Type:', self._combo_subd_type)

        self._field_subd_name = QLineEdit()
        self._field_subd_name.setObjectName('subd_name')
        self._field_subd_name.setMaximumWidth(280)
        form.addRow('Name:', self._field_subd_name)

        layout.addLayout(form)
        layout.addStretch()

        btn = QPushButton('Save')
        btn.setMaximumWidth(200)
        btn.clicked.connect(lambda: self._on_save('city'))
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._stack.addWidget(w)

    def _build_num_page(self) -> None:
        w = QWidget()
        w.setObjectName('numPage')
        layout = QVBoxLayout(w)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(8)

        self._combo_road_ref = QComboBox()
        self._combo_road_ref.setObjectName('road_ref')
        self._combo_road_ref.setMaximumWidth(280)
        form.addRow('Ref Type:', self._combo_road_ref)

        ref_row = QHBoxLayout()
        self._label_ref_name = QLabel()
        ref_row.addWidget(self._label_ref_name, stretch=1)
        self._btn_select_ref = QPushButton('Select Reference')
        self._btn_select_ref.setMaximumWidth(200)
        ref_row.addWidget(self._btn_select_ref)
        form.addRow('Reference:', ref_row)

        self._field_num_val = QLineEdit()
        self._field_num_val.setObjectName('num_val')
        self._field_num_val.setMaximumWidth(280)
        form.addRow('Number:', self._field_num_val)

        self._field_repetition = QLineEdit()
        self._field_repetition.setObjectName('repetition')
        self._field_repetition.setMaximumWidth(280)
        form.addRow('Duplicated:', self._field_repetition)

        self._combo_num_state = QComboBox()
        self._combo_num_state.setObjectName('num_state')
        self._combo_num_state.setMaximumWidth(280)
        form.addRow('State:', self._combo_num_state)

        self._combo_activity_cat = QComboBox()
        self._combo_activity_cat.setObjectName('activity_cat')
        self._combo_activity_cat.setMaximumWidth(280)
        form.addRow('Activity Cat:', self._combo_activity_cat)

        self._combo_activity_type = QComboBox()
        self._combo_activity_type.setObjectName('activity_type')
        self._combo_activity_type.setMaximumWidth(280)
        form.addRow('Activity Type:', self._combo_activity_type)

        layout.addLayout(form)
        layout.addStretch()

        btn = QPushButton('Save')
        btn.setMaximumWidth(200)
        btn.clicked.connect(lambda: self._on_save('num'))
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._stack.addWidget(w)

    def _build_pan_page(self) -> None:
        w = QWidget()
        w.setObjectName('panPage')
        layout = QVBoxLayout(w)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(8)

        self._combo_mount_status = QComboBox()
        self._combo_mount_status.setObjectName('mount_status')
        self._combo_mount_status.setMaximumWidth(280)
        form.addRow('Mount Status:', self._combo_mount_status)

        self._combo_panel_ref = QComboBox()
        self._combo_panel_ref.setObjectName('panel_ref')
        self._combo_panel_ref.setMaximumWidth(280)
        form.addRow('Ref Type:', self._combo_panel_ref)

        ref_row = QHBoxLayout()
        self._label_ref_name2 = QLabel()
        ref_row.addWidget(self._label_ref_name2, stretch=1)
        self._btn_select_panel_ref = QPushButton('Select Reference')
        self._btn_select_panel_ref.setMaximumWidth(200)
        ref_row.addWidget(self._btn_select_panel_ref)
        form.addRow('Reference:', ref_row)

        layout.addLayout(form)
        layout.addStretch()

        btn = QPushButton('Save')
        btn.setMaximumWidth(200)
        btn.clicked.connect(lambda: self._on_save('pan'))
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self._stack.addWidget(w)

    # ------------------------------------------------------------------
    # Signal wiring
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        page_key = self.layer_name_value

        if page_key == 'org':
            self._combo_org_cat.currentIndexChanged.connect(
                lambda: self._on_org_cat_changed()
            )

        if page_key == 'num':
            self._btn_select_ref.clicked.connect(self._on_select_ref)
            self._combo_activity_cat.currentIndexChanged.connect(
                lambda: self._on_activity_cat_changed()
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

    def _on_org_cat_changed(self) -> None:
        cat = self._combo_org_cat.currentData()
        if cat:
            fill_org_type(self._combo_org_type, cat)

    def _on_activity_cat_changed(self) -> None:
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
        """Populate widgets from a populate_* data dict."""
        page_key = self.layer_name_value
        if page_key == 'zone':
            self._set_combo_by_data(self._combo_zone_type, data.get('type'))
            if data.get('name'):
                self._field_zone_name.setText(str(data['name']))
        elif page_key == 'roads':
            self._set_combo_by_data(self._combo_road_type, data.get('type'))
            if data.get('name'):
                self._field_road_name.setText(str(data['name']))
        elif page_key == 'org':
            self._set_combo_by_data(self._combo_org_cat, data.get('category'))
            self._set_combo_by_data(self._combo_org_type, data.get('type'))
            if data.get('name'):
                self._field_org_name.setText(str(data['name']))
        elif page_key == 'city':
            self._set_combo_by_data(self._combo_subd_type, data.get('type'))
            if data.get('name'):
                self._field_subd_name.setText(str(data['name']))
        elif page_key == 'num':
            self._set_combo_by_data(self._combo_road_ref, data.get('refType'))
            if data.get('refName'):
                self._label_ref_name.setText(str(data['refName']))
            if data.get('number'):
                self._field_num_val.setText(str(data['number']))
            if data.get('repetition'):
                self._field_repetition.setText(str(data['repetition']))
            self._set_combo_by_data(self._combo_num_state, data.get('state'))
            self._set_combo_by_data(
                self._combo_activity_cat, data.get('activityCat')
            )
            self._set_combo_by_data(
                self._combo_activity_type, data.get('activityType')
            )
        elif page_key == 'pan':
            self._set_combo_by_data(
                self._combo_mount_status, data.get('mountStatus')
            )
            self._set_combo_by_data(self._combo_panel_ref, data.get('refType'))
            if data.get('refName'):
                self._label_ref_name2.setText(str(data['refName']))

    @staticmethod
    def _set_combo_by_data(combo: QComboBox, value) -> None:
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
        if page_key == 'zone':
            return {
                'type': self._combo_zone_type.currentData(),
                'name': self._field_zone_name.text(),
            }
        if page_key == 'roads':
            return {
                'type': self._combo_road_type.currentData(),
                'name': self._field_road_name.text(),
            }
        if page_key == 'org':
            return {
                'category': self._combo_org_cat.currentData(),
                'type': self._combo_org_type.currentData(),
                'name': self._field_org_name.text(),
            }
        if page_key == 'city':
            return {
                'type': self._combo_subd_type.currentData(),
                'name': self._field_subd_name.text(),
            }
        if page_key == 'num':
            return {
                'refType': self._combo_road_ref.currentData(),
                'number': self._field_num_val.text(),
                'repetition': self._field_repetition.text(),
                'state': self._combo_num_state.currentData(),
                'activityCat': self._combo_activity_cat.currentData(),
                'activityType': self._combo_activity_type.currentData(),
            }
        if page_key == 'pan':
            return {
                'mountStatus': self._combo_mount_status.currentData(),
                'refType': self._combo_panel_ref.currentData(),
            }
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

        self._clear_ref_name()
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
                self.ref_identify_tool.ref_selected.connect(
                    self._on_reference_selected
                )
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

    def _clear_ref_name(self) -> None:
        self._label_ref_name.setText('')
        self._label_ref_name2.setText('')

    def _on_reference_selected(self, feature_id, layer_name) -> None:
        """Called when the user selects a reference feature on the map."""
        self._ref_id = str(feature_id)
        self._ref_layer = layer_name
        display_name = f'{layer_name} [{feature_id}]'
        page_key = self.layer_name_value
        if page_key == 'num':
            self._label_ref_name.setText(display_name)
        elif page_key == 'pan':
            self._label_ref_name2.setText(display_name)

    # ------------------------------------------------------------------
    # Public API used by popup_handlers
    # ------------------------------------------------------------------

    @property
    def bridge(self) -> object:
        return self

    def _set_combo_value(self, combo_name: str, value: str) -> None:
        """Set a combo by value (stored for populate handlers)."""
        self._current_form_data[combo_name] = value
