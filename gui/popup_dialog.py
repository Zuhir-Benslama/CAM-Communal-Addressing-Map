"""Popup dialog for viewing and editing feature attributes."""
import logging
import os

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtWidgets import (
    QComboBox, QDateEdit, QDialog, QFormLayout, QLayout, QLineEdit,
    QMessageBox, QPushButton, QSizePolicy, QWidget,
)
from qgis.core import QgsProject

from ..app.orders import models as _models
from ..app.orders.models import (
    Road, Organization, Subdivision, Zone, PanelSign, Numbering,
)
from ..app.core.database import get_session
from ..constants import (
    validate_text, current_theme, get_theme_qss,
    current_locale, locale_value,
    LAYER_ROADS, LAYER_FACILITIES, LAYER_SUBDIVISIONS,
    LAYER_ZONES, LAYER_NUMBERING, LAYER_PANELS,
)
from ..scripts.lookup_data import get_string, apply_widget_texts
from .ui_fillers import (
    fill_org_category, fill_road_type, fill_road_reference,
    fill_panel_reference, fill_activity_category,
    fill_numbering_state, fill_mounting_status, fill_subdivision_type,
    fill_type_zone, fill_type_org, fill_type_act,
)
from ..app.users.repository import qgis_config
from ..layer.refresh import refresh_all_layers

logger = logging.getLogger(__name__)

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'PopupDialog.ui'))
class PopupDialog(QDialog,FORM_CLASS):
    """Dialog for updating attributes of a selected feature."""
    def __init__(self, layer_name_value, layer_name_key, attribute, iface,
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

        fill_org_category(self.cat_org)
        self.cat_org.currentIndexChanged.connect(self.on_select_catOrg)
        self.ref_identify_tool=None
        fill_road_type(self.type_voie)
        fill_road_reference(self.dyn_ref3)
        fill_panel_reference(self.dyn_ref4)
        fill_activity_category(self.cat_act_3)

        fill_numbering_state(self.num_etat)


        fill_mounting_status(self.etat_mont)



        fill_subdivision_type(self.type_city)
        fill_type_zone(self.type_zone)


        self.set_form()
        self.setWindowTitle(self.layer_name_key)
        self.route(self.layer_name_value)
        self.submit_voie.clicked.connect(self.update_road)
        self.submit_zone.clicked.connect(self.update_zone)
        self.submit_city.clicked.connect(self.update_subdivision)
        self.submit_org.clicked.connect(self.update_organization)
        self.submit_num.clicked.connect(self.update_numbering)
        self.submit_pan.clicked.connect(self.update_panel)

        self.select_ref3.clicked.connect(self.select_numbering_reference)
        self.select_ref4.clicked.connect(self.select_panel_reference)
        self.cat_act_3.currentIndexChanged.connect(self.on_select_catAct)

    def _apply_ui_polish(self) -> None:
        """Apply consistent sizing, spacing, and styling to the dialog."""
        self.setObjectName('rnaPopupDialog')
        self.setSizeGripEnabled(True)
        self.setMinimumSize(700, 500)
        self.setMaximumSize(16777215, 16777215)
        if self.width() < 760:
            self.resize(760, 560)

        self.router.setMaximumHeight(16777215)
        for layout in self.findChildren(QLayout):
            if isinstance(layout, QFormLayout):
                if layout.horizontalSpacing() < 12:
                    layout.setHorizontalSpacing(12)
                if layout.verticalSpacing() < 10:
                    layout.setVerticalSpacing(10)
            elif layout.spacing() < 8:
                layout.setSpacing(8)

        for widget in self.findChildren(QLineEdit):
            widget.setMinimumHeight(max(widget.minimumHeight(), 34))
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        for widget in self.findChildren(QComboBox):
            widget.setMinimumHeight(max(widget.minimumHeight(), 34))
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        for widget in self.findChildren(QDateEdit):
            widget.setMinimumHeight(max(widget.minimumHeight(), 34))
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        for button in self.findChildren(QPushButton):
            name = button.objectName()
            if name.startswith('submit_'):
                button.setProperty('role', 'primary')
            elif name.startswith('select_'):
                button.setProperty('role', 'tool')
            else:
                button.setProperty('role', 'ghost')
            button.setMinimumHeight(max(button.minimumHeight(), 34))
            button.setMaximumWidth(16777215)
            button.setIconSize(QSize(16, 16))
    def on_select_catAct(self, index) -> None:
        """Populate activity type based on category selection."""
        current_index = self.cat_act_3.currentIndex()
        selected_value = self.cat_act_3.itemData(current_index)
        fill_type_act(self.type_act_3, selected_value)

    def on_select_catOrg(self, index) -> None:
        """Populate org type based on category selection."""
        current_index = self.cat_org.currentIndex()
        selected_value = self.cat_org.itemData(current_index)
        fill_type_org(self.type_org, selected_value)

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
        self.nom_voie.setText(locale_value(query, 'Nom', loc))
        index = self.type_voie.findData(query.Type)
        if index != -1:
            self.type_voie.setCurrentIndex(index)

    def _populate_facility(self, query, loc):
        """Populate facility form fields from a DB query result."""
        self.nom_org.setText(locale_value(query, 'Nom', loc))
        index = self.cat_org.findData(query.cat)
        if index != -1:
            fill_type_org(self.type_org, query.cat)
            self.cat_org.setCurrentIndex(index)
        index = self.type_org.findData(query.Type)
        if index != -1:
            self.type_org.setCurrentIndex(index)

    def _populate_subdivision(self, query, loc):
        """Populate subdivision form fields from a DB query result."""
        self.nom_city.setText(locale_value(query, 'Nom', loc))
        index = self.type_city.findData(query.Type)
        if index != -1:
            self.type_city.setCurrentIndex(index)

    def _populate_zone(self, query, loc):
        """Populate zone form fields from a DB query result."""
        self.nom_zone.setText(locale_value(query, 'Nom', loc))
        index = self.type_zone.findData(query.Type)
        if index != -1:
            self.type_zone.setCurrentIndex(index)

    def _populate_numbering(self, query, loc):
        """Populate numbering form fields from a DB query result."""
        self.num_val.setText(query.valeur)
        self.repetition.setText(query.repetition)
        if query.idLine:
            self._set_combo_value(self.dyn_ref3, LAYER_ROADS)
            self.ref_name3.setText(
                locale_value(query.road, 'Type', loc)
                + ' ' + locale_value(query.road, 'Nom', loc))
        elif query.idPoly:
            self._set_combo_value(self.dyn_ref3, LAYER_SUBDIVISIONS)
            self.ref_name3.setText(
                locale_value(query.subdivision, 'Nom', loc))
        index = self.num_etat.findData(query.etat)
        if index != -1:
            self.num_etat.setCurrentIndex(index)
        index = self.cat_act_3.findData(query.activity_cat)
        if index != -1:
            fill_type_act(self.type_act_3, query.activity_cat)
            self.cat_act_3.setCurrentIndex(index)
        index = self.type_act_3.findData(query.activity_type)
        if index != -1:
            self.type_act_3.setCurrentIndex(index)

    def _populate_panel(self, query, loc):
        """Populate panel form fields from a DB query result."""
        if query.idLine:
            self._set_combo_value(self.dyn_ref4, LAYER_ROADS)
            self.ref_name4.setText(
                locale_value(query.road, 'Type', loc)
                + ' ' + locale_value(query.road, 'Nom', loc))
        elif query.idOrg:
            self._set_combo_value(self.dyn_ref4, LAYER_FACILITIES)
            self.ref_name4.setText(
                locale_value(query.organization, 'Type', loc)
                + ' '
                + locale_value(query.organization, 'Nom', loc))
        elif query.idPoly:
            self._set_combo_value(self.dyn_ref4, LAYER_SUBDIVISIONS)
            self.ref_name4.setText(locale_value(query.subdivision, 'Nom', loc))
        index = self.etat_mont.findData(query.situation)
        if index != -1:
            self.etat_mont.setCurrentIndex(index)

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
        data_list = qgis_config().get('mapper')
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
                        getattr(model, 'pkuid') == self.attribute
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
                session, pkuid=self.attribute,
                Nom=validate_text(self.nom_voie.text()),
                Type=self.type_voie.currentData(),
            )
            QMessageBox.information(
                self, get_string("Success", self._tr_locale), get_string("This road has been updated successfully", self._tr_locale))
        except Exception as e:
            logger.exception("Failed to update road: %s", e)
            QMessageBox.critical(self, get_string("Error", self._tr_locale), get_string('Cannot update road', self._tr_locale))
        finally:
            session.close()
        refresh_all_layers(self.iface)
        self.close()
    def update_organization(self) -> None:
        """Update organization feature in the database."""
        session = get_session()
        try:
            Organization.update(
                session, pkuid=self.attribute, Cat=self.cat_org.currentData(),
                Nom=validate_text(self.nom_org.text()),
                Type=self.type_org.currentData()
            )
            QMessageBox.information(
                self, get_string("Success", self._tr_locale), get_string("This facility has been updated successfully", self._tr_locale))
        except Exception as e:
            logger.exception("Failed to update organization: %s", e)
            QMessageBox.critical(self, get_string("Error", self._tr_locale), get_string('Cannot update facility', self._tr_locale))
        finally:
            session.close()
        refresh_all_layers(self.iface)
        self.close()

    def update_subdivision(self) -> None:
        """Update subdivision feature in the database."""
        session = get_session()
        try:
            Subdivision.update(
                session, pkuid=self.attribute,
                Nom=validate_text(self.nom_city.text()),
                Type=self.type_city.currentData()
            )
            QMessageBox.information(self, get_string("Success", self._tr_locale), get_string("This subdivision has been updated successfully", self._tr_locale))
        except Exception as e:
            logger.exception("Failed to update subdivision: %s", e)
            QMessageBox.critical(self, get_string("Error", self._tr_locale), get_string('Cannot update subdivision', self._tr_locale))
        finally:
            session.close()
        refresh_all_layers(self.iface)
        self.close()

    def update_zone(self) -> None:
        """Update zone feature in the database."""
        session = get_session()
        try:
            Zone.update(
                session, pkuid=self.attribute,
                Nom=validate_text(self.nom_zone.text()),
                Type=self.type_zone.currentData()
            )
            QMessageBox.information(
                self, get_string("Success", self._tr_locale), get_string("This zone has been updated successfully", self._tr_locale))
        except Exception as e:
            logger.exception("Failed to update zone: %s", e)
            QMessageBox.critical(self, get_string("Error", self._tr_locale), get_string('Cannot update zone', self._tr_locale))
        finally:
            session.close()
        refresh_all_layers(self.iface)
        self.close()

    def select_numbering_reference(self) -> None:
        """Activate map tool to select a reference for numbering."""
        from .identify_tool import IdentifyTool
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
            QMessageBox.critical(self, get_string("Error", self._tr_locale), get_string("Reference type not specified", self._tr_locale))


        layer = project.mapLayersByName(self.layer_name_key)
        if layer:
            self.iface.setActiveLayer(layer[0])



    def select_panel_reference(self) -> None:
        """Activate map tool to select a reference for panel."""
        from .identify_tool import IdentifyTool
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
            QMessageBox.critical(self, get_string("Error", self._tr_locale), get_string("Reference type not specified", self._tr_locale))

        layer = project.mapLayersByName(self.layer_name_key)
        if layer:
            self.iface.setActiveLayer(layer[0])




    def update_panel(self) -> None:
        """Update panel feature in the database."""
        session = get_session()
        try:
            ref_data = None
            if self.ref_identify_tool:
                ref_data = self.ref_identify_tool.get_pkuid()

            if ref_data:
                if ref_data.get('layer_name') == LAYER_FACILITIES:
                    PanelSign.update(session, pkuid=self.attribute,
                                      idLine=None,
                                      idPoly=None,
                                      idOrg=ref_data.get('pkuid'),
                                      situation=self.etat_mont.currentData())

                if ref_data.get('layer_name') == LAYER_ROADS:
                    PanelSign.update(session, pkuid=self.attribute,
                                      idLine=ref_data.get('pkuid'),
                                      idPoly=None,
                                      idOrg=None,
                                      situation=self.etat_mont.currentData())

                if ref_data.get('layer_name') == LAYER_SUBDIVISIONS:
                    PanelSign.update(session, pkuid=self.attribute,
                                      idLine=None,
                                      idPoly=ref_data.get('pkuid'),
                                      idOrg=None,
                                      situation=self.etat_mont.currentData())
            else:
                PanelSign.update(session, pkuid=self.attribute,
                                  situation=self.etat_mont.currentData())

            QMessageBox.information(
                self, get_string("Success", self._tr_locale), get_string("This panel has been updated successfully", self._tr_locale))
        except Exception as e:
            logger.exception("Failed to update panel: %s", e)
            QMessageBox.critical(self, get_string("Error", self._tr_locale), get_string('Cannot update panel', self._tr_locale))
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
                ref_data = self.ref_identify_tool.get_pkuid()

            if ref_data:
                if ref_data.get('layer_name') == LAYER_FACILITIES:
                    Numbering.update(
                        session, pkuid=self.attribute,
                        repetition=validate_text(self.repetition.text()),
                        valeur=validate_text(self.num_val.text()),
                        etat=self.num_etat.currentData(),
                        idLine=None,
                        idPoly=None,
                        activity_cat=self.cat_act_3.currentData(),
                        activity_type=self.type_act_3.currentData(),
                        idOrg=ref_data.get('pkuid')
                    )

                if ref_data.get('layer_name') == LAYER_ROADS:
                    Numbering.update(
                        session, pkuid=self.attribute,
                        repetition=validate_text(self.repetition.text()),
                        valeur=validate_text(self.num_val.text()),
                        etat=self.num_etat.currentData(),
                        idLine=ref_data.get('pkuid'),
                        idPoly=None,
                        activity_cat=self.cat_act_3.currentData(),
                        activity_type=self.type_act_3.currentData(),
                        idOrg=None
                    )

                if ref_data.get('layer_name') == LAYER_SUBDIVISIONS:
                    Numbering.update(
                        session, pkuid=self.attribute,
                        repetition=validate_text(self.repetition.text()),
                        valeur=validate_text(self.num_val.text()),
                        etat=self.num_etat.currentData(),
                        idLine=None,
                        activity_cat=self.cat_act_3.currentData(),
                        activity_type=self.type_act_3.currentData(),
                        idPoly=ref_data.get('pkuid'),
                        idOrg=None
                    )
            else:
                Numbering.update(
                    session, pkuid=self.attribute,
                    repetition=validate_text(self.repetition.text()),
                    valeur=validate_text(self.num_val.text()),
                    activity_cat=self.cat_act_3.currentData(),
                    activity_type=self.type_act_3.currentData(),
                    etat=self.num_etat.currentData()
                )

            QMessageBox.information(
                self, get_string("Success", self._tr_locale), get_string("This numbering has been updated successfully", self._tr_locale))
        except Exception as e:
            logger.exception("Failed to update numbering: %s", e)
            QMessageBox.critical(self, get_string("Error", self._tr_locale), f'{e}')
        finally:
            session.close()
        refresh_all_layers(self.iface)
        self.close()
    def route(self, page_index) -> None:
        """Switch the stacked widget to the given page."""
        page = self.router.findChild(QWidget, page_index)
        if page:
            self.router.setCurrentWidget(page)
