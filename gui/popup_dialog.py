"""Popup dialog for viewing and editing feature attributes."""
import logging
import os
from typing import TYPE_CHECKING, Optional

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtWidgets import (
    QComboBox, QDateEdit, QDialog, QFormLayout, QLayout, QLineEdit,
    QMessageBox, QPushButton, QSizePolicy, QWidget,
)
from qgis.core import QgsProject

from sqlalchemy.exc import SQLAlchemyError

from ..app.core.config import get_theme_qss
from ..app.core.database import get_session
from ..app.orders import models as _models
from ..app.orders.models import (
    Road, Organization, Subdivision, Zone, PanelSign, Numbering,
)
from ..app.users.repository import qgis_config
from ..constants import (
    current_locale, current_theme, locale_value, validate_text,
    LAYER_ROADS, LAYER_FACILITIES, LAYER_SUBDIVISIONS,
    LAYER_ZONES, LAYER_NUMBERING, LAYER_PANELS,
)
from ..layer.refresh import refresh_all_layers
from ..scripts.lookup_data import apply_widget_texts, get_string
from .ui_fillers import (
    fill_activity_category, fill_activity_type,
    fill_mounting_status, fill_numbering_state,
    fill_org_category, fill_org_type,
    fill_panel_reference, fill_road_reference, fill_road_type,
    fill_subdivision_type, fill_zone_type,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .identify_tool import IdentifyTool
    from ..mixins._protocols import UiForm
    FORM_CLASS = UiForm
else:
    FORM_CLASS, _ = uic.loadUiType(os.path.join(
        os.path.dirname(__file__), 'PopupDialog.ui'))


class PopupDialog(QDialog, FORM_CLASS):  # type: ignore[misc,valid-type]
    """Dialog for updating attributes of a selected feature."""
    def __init__(self, layer_name_value, layer_name_key, attribute, iface, *,
                 parent=None) -> None:
        """Initialize the popup dialog with layer and attribute."""
        super().__init__(parent)
        self._tr_locale = current_locale()

        self.layer_name_value = layer_name_value
        self.layer_name_key = layer_name_key
        self.attribute = str(attribute)
        self.iface = iface
        self.setupUi(self)
        self._apply_ui_polish()
        apply_widget_texts(self, self._tr_locale)
        self.setStyleSheet(get_theme_qss(current_theme()))

        fill_org_category(self.org_cat)
        self.org_cat.currentIndexChanged.connect(self.on_select_org_cat)
        self.ref_identify_tool: Optional[IdentifyTool] = None
        fill_road_type(self.type_road)
        fill_road_reference(self.dyn_ref3)
        fill_panel_reference(self.dyn_ref4)
        fill_activity_category(self.cat_act_3)

        fill_numbering_state(self.num_state)

        fill_mounting_status(self.mount_status)

        fill_subdivision_type(self.subd_type)
        fill_zone_type(self.zone_type)

        self.set_form()
        self.setWindowTitle(self.layer_name_key)
        self.route(self.layer_name_value)
        self.submit_road.clicked.connect(self.update_road)
        self.submit_zone.clicked.connect(self.update_zone)
        self.submit_subd.clicked.connect(self.update_subdivision)
        self.submit_org.clicked.connect(self.update_organization)
        self.submit_num.clicked.connect(self.update_numbering)
        self.submit_pan.clicked.connect(self.update_panel)

        self.select_ref3.clicked.connect(self.select_numbering_reference)
        self.select_ref4.clicked.connect(self.select_panel_reference)
        self.cat_act_3.currentIndexChanged.connect(self.on_select_activity_cat)

    def _set_dialog_defaults(self) -> None:
        """Configure default dialog sizing and geometry."""
        self.setObjectName('rnaPopupDialog')
        self.setSizeGripEnabled(True)
        self.setMinimumSize(700, 500)
        self.setMaximumSize(16777215, 16777215)
        if self.width() < 760:
            self.resize(760, 560)

    def _adjust_formlayout_spacing(self, layout: QFormLayout) -> None:
        """Normalize spacing and label widths for a form layout."""
        if layout.horizontalSpacing() < 16:
            layout.setHorizontalSpacing(16)
        if layout.verticalSpacing() < 12:
            layout.setVerticalSpacing(12)
        for i in range(layout.rowCount()):
            item = layout.itemAt(i, QFormLayout.LabelRole)
            if item and item.widget():
                item.widget().setMinimumWidth(120)

    def _adjust_layouts(self) -> None:
        """Normalize spacing across all child layouts."""
        self.router.setMaximumHeight(16777215)
        for layout in self.findChildren(QLayout):
            if isinstance(layout, QFormLayout):
                self._adjust_formlayout_spacing(layout)
            elif layout.spacing() < 8:
                layout.setSpacing(8)

    def _center_footer_widgets(self) -> None:
        """Ensure footer labels and submit buttons span the full row."""
        if hasattr(self, 'formLayout_2') and hasattr(self, 'label_26'):
            self.formLayout_2.setWidget(
                0, QFormLayout.SpanningRole, self.label_26,
            )
            self.label_26.setAlignment(Qt.AlignCenter)
        if hasattr(self, 'formLayout_3') and hasattr(self, 'submit_pan'):
            self.formLayout_3.setWidget(
                2, QFormLayout.SpanningRole, self.submit_pan,
            )

    def _size_input_widgets(self) -> None:
        """Apply consistent height and expanding policy to input widgets."""
        for widget in self.findChildren(QLineEdit):
            widget.setMinimumHeight(max(widget.minimumHeight(), 34))
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        for widget in self.findChildren(QComboBox):
            widget.setMinimumHeight(max(widget.minimumHeight(), 34))
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        for widget in self.findChildren(QDateEdit):
            widget.setMinimumHeight(max(widget.minimumHeight(), 34))
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def _style_buttons(self) -> None:
        """Assign role properties and consistent sizing to buttons."""
        for button in self.findChildren(QPushButton):
            name = button.objectName()
            if name.startswith('submit_'):
                button.setProperty('role', 'primary')
                button.setMinimumWidth(180)
                button.setMaximumWidth(220)
                parent = button.parentWidget()
                parent_layout = parent.layout() if parent is not None else None
                if parent_layout is not None:
                    parent_layout.setAlignment(button, Qt.AlignHCenter)
            elif name.startswith('select_'):
                button.setProperty('role', 'tool')
                button.setMaximumWidth(16777215)
            else:
                button.setProperty('role', 'ghost')
                button.setMaximumWidth(16777215)
            button.setMinimumHeight(max(button.minimumHeight(), 34))
            button.setIconSize(QSize(16, 16))

    def _apply_ui_polish(self) -> None:
        """Apply consistent sizing, spacing, and styling to the dialog."""
        self._set_dialog_defaults()
        self._adjust_layouts()
        self._center_footer_widgets()
        self._size_input_widgets()
        self._style_buttons()

    def on_select_activity_cat(self, _index) -> None:
        """Populate activity type based on category selection."""
        current_index = self.cat_act_3.currentIndex()
        selected_value = self.cat_act_3.itemData(current_index)
        fill_activity_type(self.activity_type_3, selected_value)

    def on_select_org_cat(self, _index) -> None:
        """Populate org type based on category selection."""
        current_index = self.org_cat.currentIndex()
        selected_value = self.org_cat.itemData(current_index)
        fill_org_type(self.org_type, selected_value)

    def _set_combo_value(self, combo, value: str) -> None:
        """Set combo by stable itemData first, then by visible text."""
        idx = combo.findData(value)
        if idx != -1:
            combo.setCurrentIndex(idx)
            return
        idx = combo.findText(value)
        if idx != -1:
            combo.setCurrentIndex(idx)

    def _populate_road(self, query, loc):
        """Populate road form fields from a DB query result."""
        self.road_name.setText(locale_value(query, 'name', loc))
        index = self.type_road.findData(query.type)
        if index != -1:
            self.type_road.setCurrentIndex(index)

    def _populate_facility(self, query, loc):
        """Populate facility form fields from a DB query result."""
        self.org_name.setText(locale_value(query, 'name', loc))
        index = self.org_cat.findData(query.category)
        if index != -1:
            fill_org_type(self.org_type, query.category)
            self.org_cat.setCurrentIndex(index)
        index = self.org_type.findData(query.type)
        if index != -1:
            self.org_type.setCurrentIndex(index)

    def _populate_subdivision(self, query, loc):
        """Populate subdivision form fields from a DB query result."""
        self.subd_name.setText(locale_value(query, 'name', loc))
        index = self.subd_type.findData(query.type)
        if index != -1:
            self.subd_type.setCurrentIndex(index)

    def _populate_zone(self, query, loc):
        """Populate zone form fields from a DB query result."""
        self.nom_zone.setText(locale_value(query, 'name', loc))
        index = self.zone_type.findData(query.type)
        if index != -1:
            self.zone_type.setCurrentIndex(index)

    def _populate_numbering(self, query, loc):
        """Populate numbering form fields from a DB query result."""
        self.num_val.setText(query.value)
        self.repetition.setText(query.repetition)
        if query.road_id:
            self._set_combo_value(self.dyn_ref3, LAYER_ROADS)
            self.ref_name3.setText(
                locale_value(query.road, 'type', loc) +
                ' ' + locale_value(query.road, 'name', loc))
        elif query.subdivision_id:
            self._set_combo_value(self.dyn_ref3, LAYER_SUBDIVISIONS)
            self.ref_name3.setText(
                locale_value(query.subdivision, 'name', loc))
        index = self.num_state.findData(query.state)
        if index != -1:
            self.num_state.setCurrentIndex(index)
        index = self.cat_act_3.findData(query.activity_cat)
        if index != -1:
            fill_activity_type(self.activity_type_3, query.activity_cat)
            self.cat_act_3.setCurrentIndex(index)
        index = self.activity_type_3.findData(query.activity_type)
        if index != -1:
            self.activity_type_3.setCurrentIndex(index)

    def _populate_panel(self, query, loc):
        """Populate panel form fields from a DB query result."""
        if query.road_id:
            self._set_combo_value(self.dyn_ref4, LAYER_ROADS)
            self.ref_name4.setText(
                locale_value(query.road, 'type', loc) +
                ' ' + locale_value(query.road, 'name', loc))
        elif query.organization_id:
            self._set_combo_value(self.dyn_ref4, LAYER_FACILITIES)
            self.ref_name4.setText(
                locale_value(query.organization, 'type', loc) +
                ' ' + locale_value(query.organization, 'name', loc))
        elif query.subdivision_id:
            self._set_combo_value(self.dyn_ref4, LAYER_SUBDIVISIONS)
            self.ref_name4.setText(locale_value(query.subdivision, 'name', loc))
        index = self.mount_status.findData(query.status)
        if index != -1:
            self.mount_status.setCurrentIndex(index)

    _POPULATE_DISPATCH = {
        LAYER_ROADS: _populate_road,
        LAYER_FACILITIES: _populate_facility,
        LAYER_SUBDIVISIONS: _populate_subdivision,
        LAYER_ZONES: _populate_zone,
        LAYER_NUMBERING: _populate_numbering,
        LAYER_PANELS: _populate_panel,
    }

    def set_form(self) -> None:
        """Populate form fields from the selected feature."""
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
                        model.id == self.attribute
                    ).first()
                    if query:
                        handler = self._POPULATE_DISPATCH.get(
                            self.layer_name_key)
                        if handler:
                            handler(self, query, self._tr_locale)
                finally:
                    session.close()

    def update_road(self) -> None:
        """Update road feature in the database."""
        session = get_session()
        try:
            Road.update(
                session, id=self.attribute,
                name=validate_text(self.road_name.text()),
                type=self.type_road.currentData(),
            )
            QMessageBox.information(
                self,
                get_string("Success", self._tr_locale),
                get_string(
                    "This road has been updated successfully", self._tr_locale,
                ),
            )
        except (ValueError, SQLAlchemyError) as e:
            logger.exception("Failed to update road: %s", e)
            QMessageBox.critical(
                self,
                get_string("Error", self._tr_locale),
                get_string('Cannot update road', self._tr_locale),
            )
        finally:
            session.close()
        refresh_all_layers(self.iface)
        self.close()

    def update_organization(self) -> None:
        """Update organization feature in the database."""
        session = get_session()
        try:
            Organization.update(
                session, id=self.attribute,
                category=self.org_cat.currentData(),
                name=validate_text(self.org_name.text()),
                type=self.org_type.currentData(),
            )
            QMessageBox.information(
                self,
                get_string("Success", self._tr_locale),
                get_string(
                    "This facility has been updated successfully",
                    self._tr_locale,
                ),
            )
        except (ValueError, SQLAlchemyError) as e:
            logger.exception("Failed to update organization: %s", e)
            QMessageBox.critical(
                self,
                get_string("Error", self._tr_locale),
                get_string('Cannot update facility', self._tr_locale),
            )
        finally:
            session.close()
        refresh_all_layers(self.iface)
        self.close()

    def update_subdivision(self) -> None:
        """Update subdivision feature in the database."""
        session = get_session()
        try:
            Subdivision.update(
                session, id=self.attribute,
                name=validate_text(self.subd_name.text()),
                type=self.subd_type.currentData()
            )
            QMessageBox.information(
                self,
                get_string("Success", self._tr_locale),
                get_string(
                    "This subdivision has been updated successfully",
                    self._tr_locale,
                ),
            )
        except (ValueError, SQLAlchemyError) as e:
            logger.exception("Failed to update subdivision: %s", e)
            QMessageBox.critical(
                self,
                get_string("Error", self._tr_locale),
                get_string('Cannot update subdivision', self._tr_locale),
            )
        finally:
            session.close()
        refresh_all_layers(self.iface)
        self.close()

    def update_zone(self) -> None:
        """Update zone feature in the database."""
        session = get_session()
        try:
            Zone.update(
                session, id=self.attribute,
                name=validate_text(self.nom_zone.text()),
                type=self.zone_type.currentData()
            )
            QMessageBox.information(
                self,
                get_string("Success", self._tr_locale),
                get_string(
                    "This zone has been updated successfully", self._tr_locale,
                ),
            )
        except (ValueError, SQLAlchemyError) as e:
            logger.exception("Failed to update zone: %s", e)
            QMessageBox.critical(
                self,
                get_string("Error", self._tr_locale),
                get_string('Cannot update zone', self._tr_locale),
            )
        finally:
            session.close()
        refresh_all_layers(self.iface)
        self.close()

    def select_numbering_reference(self) -> None:
        """Activate map tool to select a reference for numbering."""
        from .identify_tool import IdentifyTool  # pylint: disable=import-outside-toplevel
        self.ref_name3.clear()
        project = QgsProject.instance()
        layer_name = self.dyn_ref3.currentData() or self.dyn_ref3.currentText()
        if layer_name:
            layer = project.mapLayersByName(layer_name)
            if layer:
                self.iface.setActiveLayer(layer[0])
                canvas = self.iface.mapCanvas()
                self.ref_identify_tool = IdentifyTool(
                    canvas, mode=IdentifyTool.MODE_REF)
                self.ref_identify_tool.set_iface(self.iface)
                self.ref_identify_tool.set_ref_name(self.ref_name3)
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

    def select_panel_reference(self) -> None:
        """Activate map tool to select a reference for panel."""
        from .identify_tool import IdentifyTool  # pylint: disable=import-outside-toplevel
        self.ref_name4.clear()
        project = QgsProject.instance()
        layer_name = self.dyn_ref4.currentData() or self.dyn_ref4.currentText()
        if layer_name:
            layer = project.mapLayersByName(layer_name)
            if layer:
                self.iface.setActiveLayer(layer[0])
                canvas = self.iface.mapCanvas()
                self.ref_identify_tool = IdentifyTool(
                    canvas, mode=IdentifyTool.MODE_REF)
                self.ref_identify_tool.set_iface(self.iface)
                self.ref_identify_tool.set_ref_name(self.ref_name4)
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

    def update_panel(self) -> None:
        """Update panel feature in the database."""
        session = get_session()
        try:
            ref_data = None
            if self.ref_identify_tool:
                ref_data = self.ref_identify_tool.get_id()

            if ref_data:
                if ref_data.get('layer_name') == LAYER_FACILITIES:
                    PanelSign.update(
                        session, id=self.attribute,
                        road_id=None, subdivision_id=None,
                        organization_id=ref_data.get('id'),
                        status=self.mount_status.currentData(),
                    )

                if ref_data.get('layer_name') == LAYER_ROADS:
                    PanelSign.update(
                        session, id=self.attribute,
                        road_id=ref_data.get('id'),
                        subdivision_id=None, organization_id=None,
                        status=self.mount_status.currentData(),
                    )

                if ref_data.get('layer_name') == LAYER_SUBDIVISIONS:
                    PanelSign.update(
                        session, id=self.attribute,
                        road_id=None,
                        subdivision_id=ref_data.get('id'),
                        organization_id=None,
                        status=self.mount_status.currentData(),
                    )
            else:
                PanelSign.update(
                    session, id=self.attribute,
                    status=self.mount_status.currentData(),
                )

            QMessageBox.information(
                self,
                get_string("Success", self._tr_locale),
                get_string("This panel has been updated successfully",
                           self._tr_locale),
            )
        except (ValueError, SQLAlchemyError) as e:
            logger.exception("Failed to update panel: %s", e)
            QMessageBox.critical(
                self,
                get_string("Error", self._tr_locale),
                get_string('Cannot update panel', self._tr_locale),
            )
        finally:
            session.close()
        refresh_all_layers(self.iface)
        self.close()

    def update_numbering(self) -> None:
        """Update numbering feature in the database."""
        session = get_session()
        try:
            ref_data = None
            if self.ref_identify_tool:
                ref_data = self.ref_identify_tool.get_id()

            if ref_data:
                if ref_data.get('layer_name') == LAYER_FACILITIES:
                    Numbering.update(
                        session, id=self.attribute,
                        repetition=validate_text(self.repetition.text()),
                        value=validate_text(self.num_val.text()),
                        state=self.num_state.currentData(),
                        road_id=None,
                        subdivision_id=None,
                        activity_cat=self.cat_act_3.currentData(),
                        activity_type=self.activity_type_3.currentData(),
                        organization_id=ref_data.get('id')
                    )

                if ref_data.get('layer_name') == LAYER_ROADS:
                    Numbering.update(
                        session, id=self.attribute,
                        repetition=validate_text(self.repetition.text()),
                        value=validate_text(self.num_val.text()),
                        state=self.num_state.currentData(),
                        road_id=ref_data.get('id'),
                        subdivision_id=None,
                        activity_cat=self.cat_act_3.currentData(),
                        activity_type=self.activity_type_3.currentData(),
                        organization_id=None
                    )

                if ref_data.get('layer_name') == LAYER_SUBDIVISIONS:
                    Numbering.update(
                        session, id=self.attribute,
                        repetition=validate_text(self.repetition.text()),
                        value=validate_text(self.num_val.text()),
                        state=self.num_state.currentData(),
                        road_id=None,
                        activity_cat=self.cat_act_3.currentData(),
                        activity_type=self.activity_type_3.currentData(),
                        subdivision_id=ref_data.get('id'),
                        organization_id=None
                    )
            else:
                Numbering.update(
                    session, id=self.attribute,
                    repetition=validate_text(self.repetition.text()),
                    value=validate_text(self.num_val.text()),
                    activity_cat=self.cat_act_3.currentData(),
                    activity_type=self.activity_type_3.currentData(),
                    state=self.num_state.currentData()
                )

            QMessageBox.information(
                self,
                get_string("Success", self._tr_locale),
                get_string(
                    "This numbering has been updated successfully",
                    self._tr_locale,
                ),
            )
        except (ValueError, SQLAlchemyError) as e:
            logger.exception("Failed to update numbering: %s", e)
            QMessageBox.critical(
                self, get_string("Error", self._tr_locale), f'{e}',
            )
        finally:
            session.close()
        refresh_all_layers(self.iface)
        self.close()

    def route(self, page_index) -> None:
        """Switch the stacked widget to the given page."""
        page = self.router.findChild(QWidget, page_index)
        if page:
            self.router.setCurrentWidget(page)
