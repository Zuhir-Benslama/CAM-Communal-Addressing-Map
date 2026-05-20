"""Popup dialog for viewing and editing feature attributes."""
import logging
import os

from qgis.PyQt import uic
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtWidgets import (
    QComboBox, QDateEdit, QDialog, QFormLayout, QLayout, QLineEdit,
    QMessageBox, QPushButton, QSizePolicy, QWidget,
)
logger = logging.getLogger(__name__)
from .. import models as _models
from ..models import (
    get_session, Road, Organization, Subdivision,
    Zone, PanelSign, Numbering
)
from ..constants import (
    validate_text, current_theme, get_theme_qss,
    current_locale, locale_value,
)
from ..scripts.lookup_data import get_string, apply_widget_texts
from ..gui.ui_fillers import (
    fill_org_category, fill_road_type, fill_road_reference,
    fill_panel_reference, fill_activity_category,
    fill_numbering_state, fill_mounting_status, fill_subdivision_type,
    fill_type_zone, fill_type_org, fill_type_act,
)
from ..db.operations import qgis_config
from ..layer.refresh import refresh_all_layers
from ..constants import (
    LAYER_ROADS, LAYER_FACILITIES, LAYER_SUBDIVISIONS,
    LAYER_ZONES, LAYER_NUMBERING, LAYER_PANELS
)
from qgis.core import QgsProject



FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'PopupDialog.ui'))
class PopupDialog(QDialog,FORM_CLASS):
    """Dialog for updating attributes of a selected feature."""
    def __init__(self, layer_name_value, layer_name_key, attribute, iface,
                 parent=None) -> None:
        """Initialize the popup dialog with layer and attribute."""
        super(PopupDialog, self).__init__(parent)
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
        self.identify_tool2=None
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
        self.setObjectName('rnaPopupDialog')
        self.setSizeGripEnabled(True)
        self.setMinimumSize(700, 500)
        self.setMaximumSize(16777215, 16777215)
        if self.width() < 760:
            self.resize(760, 560)

        self.router.setMaximumHeight(16777215)
        self.frame_12.setProperty('surfaceRole', 'header')

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

    def _populate_road(self, query, loc):
        self.nom_voie.setText(locale_value(query, 'Nom', loc))
        self.dec_voie.setText(query.num_decision)
        index = self.type_voie.findData(query.Type)
        if index != -1:
            self.type_voie.setCurrentIndex(index)

    def _populate_facility(self, query, loc):
        self.nom_org.setText(locale_value(query, 'Nom', loc))
        index = self.cat_org.findData(query.cat)
        if index != -1:
            fill_type_org(self.type_org, query.cat)
            self.cat_org.setCurrentIndex(index)
        index = self.type_org.findData(query.Type)
        if index != -1:
            self.type_org.setCurrentIndex(index)

    def _populate_subdivision(self, query, loc):
        self.nom_city.setText(locale_value(query, 'Nom', loc))
        index = self.type_city.findData(query.Type)
        if index != -1:
            self.type_city.setCurrentIndex(index)

    def _populate_zone(self, query, loc):
        self.nom_zone.setText(locale_value(query, 'Nom', loc))
        index = self.type_zone.findData(query.Type)
        if index != -1:
            self.type_zone.setCurrentIndex(index)

    def _populate_numbering(self, query, loc):
        self.num_val.setText(query.valeur)
        self.repetition.setText(query.repetition)
        if query.idLine:
            self.dyn_ref3.setCurrentText(LAYER_ROADS)
            self.ref_name3.setText(
                locale_value(query.road, 'Type', loc)
                + ' ' + locale_value(query.road, 'Nom', loc))
        elif query.idPoly:
            self.dyn_ref3.setCurrentText(LAYER_SUBDIVISIONS)
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
        if query.idLine:
            self.dyn_ref4.setCurrentText(LAYER_ROADS)
            self.ref_name4.setText(
                locale_value(query.road, 'Type', loc)
                + ' ' + locale_value(query.road, 'Nom', loc))
        elif query.idOrg:
            self.dyn_ref4.setCurrentText(LAYER_FACILITIES)
            self.ref_name4.setText(
                locale_value(query.organization, 'Type', loc)
                + ' '
                + locale_value(query.organization, 'Nom', loc))
        elif query.idPoly:
            self.dyn_ref4.setCurrentText(LAYER_SUBDIVISIONS)
            self.ref_name4.setText(locale_value(query.subdivision, 'Nom', loc))
        index = self.etat_mont.findData(query.Stituation)
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
                num_decision=validate_text(self.dec_voie.text()),
                Nom=validate_text(self.nom_voie.text()),
                Type=self.type_voie.currentData(),
            )
            QMessageBox.information(
                self, get_string("Success", self._tr_locale), get_string("تم تحديث هذا الطريق بنجاح", self._tr_locale))
        except Exception as e:
            logger.exception("Failed to update road: %s", e)
            QMessageBox.critical(self, get_string("Error", self._tr_locale), get_string('لا يمكن تحديث  الطريق', self._tr_locale))
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
                self, get_string("Success", self._tr_locale), get_string("تم تحديث هذا المرفق بنجاح", self._tr_locale))
        except Exception as e:
            logger.exception("Failed to update organization: %s", e)
            QMessageBox.critical(self, get_string("Error", self._tr_locale), get_string('لا يمكن تحديث  المرفق', self._tr_locale))
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
            QMessageBox.information(self, get_string("Success", self._tr_locale), get_string("تم تحديث هذا الحي بنجاح", self._tr_locale))
        except Exception as e:
            logger.exception("Failed to update subdivision: %s", e)
            QMessageBox.critical(self, get_string("Error", self._tr_locale), get_string('لا يمكن تحديث  الحي', self._tr_locale))
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
                self, get_string("Success", self._tr_locale), get_string("تم تحديث هذه المنطقة بنجاح", self._tr_locale))
        except Exception as e:
            logger.exception("Failed to update zone: %s", e)
            QMessageBox.critical(self, get_string("Error", self._tr_locale), get_string('لا يمكن تحديث   المنطقة', self._tr_locale))
        finally:
            session.close()
        refresh_all_layers(self.iface)
        self.close()

    def select_numbering_reference(self) -> None:
        """Activate map tool to select a reference for numbering."""
        from .identify_tool import IdentifyTool
        self.ref_name3.clear()
        project = QgsProject.instance()
        if self.dyn_ref3.currentText():
            layer_name = self.dyn_ref3.currentText()
            layer = project.mapLayersByName(layer_name)
            if layer:
                self.iface.setActiveLayer(layer[0])
                canvas = self.iface.mapCanvas()
                self.identify_tool2 = IdentifyTool(
                    canvas, mode=IdentifyTool.MODE_REF)
                self.identify_tool2.set_iface(self.iface)
                self.identify_tool2.set_ref_name(self.ref_name3)
                self.identify_tool2.set_active_layer(layer[0])
                canvas.setMapTool(self.identify_tool2)

        else:
            QMessageBox.critical(self, get_string("Error", self._tr_locale), get_string("نوع المرجع غير محدد", self._tr_locale))


        layer = project.mapLayersByName(self.layer_name_key)
        if layer:
            self.iface.setActiveLayer(layer[0])



    def select_panel_reference(self) -> None:
        """Activate map tool to select a reference for panel."""
        from .identify_tool import IdentifyTool
        self.ref_name4.clear()
        project = QgsProject.instance()
        if (self.dyn_ref4.currentText()):
            layer_name = self.dyn_ref4.currentText()
            layer = project.mapLayersByName(layer_name)
            if layer:
                self.iface.setActiveLayer(layer[0])
                canvas = self.iface.mapCanvas()
                self.identify_tool2 = IdentifyTool(
                    canvas, mode=IdentifyTool.MODE_REF)
                self.identify_tool2.set_iface(self.iface)
                self.identify_tool2.set_ref_name(self.ref_name4)
                self.identify_tool2.set_active_layer(layer[0])
                canvas.setMapTool(self.identify_tool2)

        else:
            QMessageBox.critical(self, get_string("Error", self._tr_locale), get_string("نوع المرجع غير محدد", self._tr_locale))

        layer = project.mapLayersByName(self.layer_name_key)
        if layer:
            self.iface.setActiveLayer(layer[0])




    def update_panel(self) -> None:
        """Update panel feature in the database."""
        session = get_session()
        try:
            obj = None
            if (self.identify_tool2):
                obj = self.identify_tool2.get_pkuid()

            if (obj):
                if (obj.get('layer_name') == LAYER_FACILITIES):
                    PanelSign.update(session, pkuid=self.attribute,
                                      idLine=None,
                                      idPoly=None,
                                      idOrg=obj.get('pkuid'),
                                      Stituation=self.etat_mont.currentData())

                if (obj.get('layer_name') == LAYER_ROADS):
                    PanelSign.update(session, pkuid=self.attribute,
                                      idLine=obj.get('pkuid'),
                                      idPoly=None,
                                      idOrg=None,
                                      Stituation=self.etat_mont.currentData())

                if (obj.get('layer_name') == LAYER_SUBDIVISIONS):
                    PanelSign.update(session, pkuid=self.attribute,
                                      idLine=None,
                                      idPoly=obj.get('pkuid'),
                                      idOrg=None,
                                      Stituation=self.etat_mont.currentData())
            else:
                PanelSign.update(session, pkuid=self.attribute,
                                  Stituation=self.etat_mont.currentData())

            QMessageBox.information(
                self, get_string("Success", self._tr_locale), get_string("تم تحديث هذه اللوحة بنجاح", self._tr_locale))
        except Exception as e:
            logger.exception("Failed to update panel: %s", e)
            QMessageBox.critical(self, get_string("Error", self._tr_locale), get_string('لا يمكن تحديث  اللوحة', self._tr_locale))
        finally:
            session.close()
        refresh_all_layers(self.iface)
        self.close()



    def update_numbering(self) -> None:
        """Update numbering feature in the database."""
        session = get_session()
        try:
            obj=None
            if(self.identify_tool2):
                obj = self.identify_tool2.get_pkuid()

            if(obj):
                if (obj.get('layer_name') == LAYER_FACILITIES):
                    Numbering.update(
                        session, pkuid=self.attribute,
                        repetition=validate_text(self.repetition.text()),
                        valeur=validate_text(self.num_val.text()),
                        etat=self.num_etat.currentData(),
                        idLine=None,
                        idPoly=None,
                        activity_cat=self.cat_act_3.currentData(),
                        activity_type=self.type_act_3.currentData(),
                        idOrg=obj.get('pkuid')
                    )

                if (obj.get('layer_name') == LAYER_ROADS):
                    Numbering.update(
                        session, pkuid=self.attribute,
                        repetition=validate_text(self.repetition.text()),
                        valeur=validate_text(self.num_val.text()),
                        etat=self.num_etat.currentData(),
                        idLine=obj.get('pkuid'),
                        idPoly=None,
                        activity_cat=self.cat_act_3.currentData(),
                        activity_type=self.type_act_3.currentData(),
                        idOrg=None
                    )

                if (obj.get('layer_name') == LAYER_SUBDIVISIONS):
                    Numbering.update(
                        session, pkuid=self.attribute,
                        repetition=validate_text(self.repetition.text()),
                        valeur=validate_text(self.num_val.text()),
                        etat=self.num_etat.currentData(),
                        idLine=None,
                        activity_cat=self.cat_act_3.currentData(),
                        activity_type=self.type_act_3.currentData(),
                        idPoly=obj.get('pkuid'),
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
                self, get_string("Success", self._tr_locale), get_string("تم تحديث هذا المدخل بنجاح", self._tr_locale))
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

