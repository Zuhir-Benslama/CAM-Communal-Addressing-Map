"""Layer editing mixin for adding and updating features via forms."""

import logging

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsProject

from ..layer.editing import update_layer
from ..db.writers import (
    add_panel_sign, add_organization, add_road,
    add_numbering, add_subdivision, add_zone,
)
from ..constants import (
    LAYER_ROADS, LAYER_FACILITIES, LAYER_SUBDIVISIONS,
    LAYER_ZONES, LAYER_NUMBERING, LAYER_PANELS, validate_text,
    current_locale,
)

logger = logging.getLogger(__name__)


class LayerEditMixin:
    """Mixin for updating layer geometries and adding features via forms.

    Cross-mixin protocol (attributes set by map_tools_mixin or owning dialog):
        _last_feature_wkt (str | None) — WKT geometry of the last created feature
        _last_feature_pkuid (str | None) — PK of the last created feature
        identify_tool2 (IdentifyTool | None) — reference selection tool (get_pkuid)
        measure_tool / measure_tool2 (MeasureTool | None) — measurement line tool
        update_object (bool) — flag for edit-vs-insert mode
        is_pan / is_org / is_road / is_num / is_city / is_zone (QCheckBox)
        num_val / repetition / nom_voie / dec_voie / nom_org / nom_city / nom_zone
        cat_org / type_org / type_voie / type_city / type_zone / num_etat / etat_mont
        cat_act / type_act (QComboBox)
    """

    def _update_handler(self, layer_name: str) -> None:
        """Enable geometry editing for a named layer."""
        layers = QgsProject.instance().mapLayersByName(layer_name)
        if not layers:
            return
        layer = layers[0]
        try:
            layer.geometryChanged.disconnect(self.on_geometry_changed)
        except TypeError:
            pass
        layer.geometryChanged.connect(self.on_geometry_changed)
        update_layer(self.iface, layer_name)

    def start_editing(self) -> None:
        self._update_handler(self._current_layer_name())

    def add_panel(self) -> None:
        """Add a new panel sign linked to a selected road, org, or
        subdivision."""
        obj = self.identify_tool2.get_pkuid()
        if self.is_pan.isChecked():
            if not self.update_object:
                geometry_wkt = getattr(self, '_last_feature_wkt', None)
                pkuid = getattr(self, '_last_feature_pkuid', None)
                if not geometry_wkt or not pkuid:
                    logger.warning("No geometry or pkuid available for panel")
                    return
                try:
                    if obj.get('layer_name') == LAYER_FACILITIES:
                        add_panel_sign(
                            geometry_wkt=geometry_wkt, pkuid=pkuid,
                            etat_mont=self.etat_mont.currentData(),
                            idLine=None, idPoly=None, idOrg=obj.get('pkuid'),
                        )
                    if obj.get('layer_name') == LAYER_ROADS:
                        add_panel_sign(
                            geometry_wkt=geometry_wkt, pkuid=pkuid,
                            etat_mont=self.etat_mont.currentData(),
                            idLine=obj.get('pkuid'), idPoly=None, idOrg=None,
                        )
                    if obj.get('layer_name') == LAYER_SUBDIVISIONS:
                        add_panel_sign(
                            geometry_wkt=geometry_wkt, pkuid=pkuid,
                            etat_mont=self.etat_mont.currentData(),
                            idLine=None, idPoly=obj.get('pkuid'), idOrg=None,
                        )

                    if self.measure_tool2:
                        self.show_confirm_dialog(
                            title=self._tr("Success"),
                            message=self._tr(
                                "تمت إضافة هذه اللوحة بنجاح\n"
                                " هل تريد مسح خط القياس ؟"
                            ),
                            yes_callback=self.measure_tool2.clear,
                        )
                    else:
                        QMessageBox.information(
                            self, self._tr("Success"),
                            self._tr("تمت إضافة هذا المدخل بنجاح"),
                        )
                except Exception as e:
                    logger.exception("Failed to add panel: %s", e)
                    QMessageBox.critical(self, self._tr("Error"), str(e))
        self.identify_tool2.unset_map_tool()
        self._draw_handler(LAYER_PANELS)

    def add_organization(self) -> None:
        """Add a new organization through the form."""
        if self.is_org.isChecked():
            geometry_wkt = getattr(self, '_last_feature_wkt', None)
            pkuid = getattr(self, '_last_feature_pkuid', None)
            if not geometry_wkt or not pkuid:
                logger.warning(
                    "No geometry or pkuid available for organization")
                return
            try:
                loc = current_locale()
                nom = validate_text(self.nom_org.text())
                kwargs = dict(
                    geometry_wkt=geometry_wkt, pkuid=pkuid,
                    cat_org=self.cat_org.currentData(),
                    nom_org=nom,
                    type_org=self.type_org.currentData(),
                )
                if loc != 'ar':
                    kwargs[f'nom_org_{loc}'] = nom
                add_organization(**kwargs)
                QMessageBox.information(
                    self, self._tr("Success"), self._tr("تمت إضافة هذا المرفق بنجاح"),
                )
            except Exception as e:
                logger.exception("Failed to add organization: %s", e)
                QMessageBox.critical(
                    self, self._tr("Error"),
                    self._tr('لا يمكن إضافة المرفق ، المرفق موجود بالفعل'),
                )

    def add_road(self) -> None:
        """Add a new road through the form."""
        if self.is_road.isChecked():
            geometry_wkt = getattr(self, '_last_feature_wkt', None)
            pkuid = getattr(self, '_last_feature_pkuid', None)
            if not geometry_wkt or not pkuid:
                logger.warning("No geometry or pkuid available for road")
                return
            try:
                loc = current_locale()
                nom = validate_text(self.nom_voie.text())
                kwargs = dict(
                    geometry_wkt=geometry_wkt, pkuid=pkuid,
                    dec_voie=validate_text(self.dec_voie.text()),
                    nom_voie=nom,
                    type_voie=self.type_voie.currentData(),
                )
                if loc != 'ar':
                    kwargs[f'nom_voie_{loc}'] = nom
                add_road(**kwargs)
                QMessageBox.information(
                    self, self._tr("Success"), self._tr("تمت إضافة هذا الطريق بنجاح"),
                )
            except Exception as e:
                logger.exception("Failed to add road: %s", e)
                QMessageBox.critical(
                    self, self._tr("Error"),
                    self._tr('لا يمكن إضافة الطريق , الطريق موجود بالفعل'),
                )

    def key_press_event(self, event) -> None:
        """Handle Enter key press to trigger add_numbering."""
        if event.key() == Qt.Key_Return:
            self.add_numbering()

    def key_press_event2(self, event) -> None:
        """Handle Enter key press to trigger add_panel."""
        if event.key() == Qt.Key_Return:
            self.add_panel()

    def show_confirm_dialog(
        self, title: str, message: str,
        yes_callback=None, no_callback=None,
    ) -> bool:
        """Display a confirmation dialog with yes/no callbacks."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        yes_button = msg_box.button(QMessageBox.Yes)
        no_button = msg_box.button(QMessageBox.No)
        yes_button.setText(self._tr("نعم"))
        no_button.setText(self._tr("لا"))

        result = msg_box.exec_()

        if result == QMessageBox.Yes:
            if yes_callback:
                yes_callback()
            return True
        if no_callback:
            no_callback()
        return False

    def add_numbering(self) -> None:
        """Add a new numbering linked to a selected road or subdivision."""
        if self.is_num.isChecked():
            geometry_wkt = getattr(self, '_last_feature_wkt', None)
            pkuid = getattr(self, '_last_feature_pkuid', None)
            if not geometry_wkt or not pkuid:
                logger.warning("No geometry or pkuid available for numbering")
                return
            try:
                obj = self.identify_tool2.get_pkuid()
            except Exception as e:
                logger.warning("Failed to get pkuid from identify tool: %s", e)
                obj = None
            try:
                if obj and obj.get('layer_name') == LAYER_ROADS:
                    add_numbering(
                        geometry_wkt=geometry_wkt, pkuid=pkuid,
                        repetition=validate_text(self.repetition.text()),
                        valeur=validate_text(self.num_val.text()),
                        etat=self.num_etat.currentData(),
                        cat_act=self.cat_act.currentData(),
                        type_act=self.type_act.currentData(),
                        idLine=obj.get('pkuid'), idPoly=None,
                    )
                elif obj and obj.get('layer_name') == LAYER_SUBDIVISIONS:
                    add_numbering(
                        geometry_wkt=geometry_wkt, pkuid=pkuid,
                        repetition=validate_text(self.repetition.text()),
                        valeur=validate_text(self.num_val.text()),
                        etat=self.num_etat.currentData(),
                        cat_act=self.cat_act.currentData(),
                        type_act=self.type_act.currentData(),
                        idLine=None, idPoly=obj.get('pkuid'),
                    )

                if self.measure_tool:
                    self.show_confirm_dialog(
                        title=self._tr("Success"),
                        message=self._tr(
                            "تمت إضافة هذا المدخل بنجاح\n هل تمسح خط القياس ؟"
                        ),
                        yes_callback=self.measure_tool.clear,
                    )
                else:
                    QMessageBox.information(
                        self, self._tr("Success"),
                        self._tr("تمت إضافة هذا المدخل بنجاح"),
                    )
            except Exception as e:
                logger.exception("Failed to add numbering: %s", e)
                QMessageBox.critical(self, self._tr("Error"), str(e))

        self.num_val.setFocus()
        self.num_val.clear()
        self._draw_handler(LAYER_NUMBERING)

    def add_city(self) -> None:
        """Add a new subdivision through the form."""
        if self.is_city.isChecked():
            geometry_wkt = getattr(self, '_last_feature_wkt', None)
            pkuid = getattr(self, '_last_feature_pkuid', None)
            if not geometry_wkt or not pkuid:
                logger.warning("No geometry or pkuid available for subdivision")
                return
            try:
                loc = current_locale()
                name = validate_text(self.nom_city.text())
                kwargs = dict(
                    geometry_wkt=geometry_wkt, pkuid=pkuid,
                    name=name,
                    subdivision_type=self.type_city.currentData(),
                )
                if loc != 'ar':
                    kwargs[f'name_{loc}'] = name
                add_subdivision(**kwargs)
                QMessageBox.information(
                    self, self._tr("Success"), self._tr("تمت إضافة هذا الحي بنجاح"),
                )
            except Exception as e:
                logger.exception("Failed to add city: %s", e)
                QMessageBox.critical(self, self._tr("Error"), str(e))

    def add_zone(self) -> None:
        """Add a new zone through the form."""
        if self.is_zone.isChecked():
            if not self.update_object:
                geometry_wkt = getattr(self, '_last_feature_wkt', None)
                pkuid = getattr(self, '_last_feature_pkuid', None)
                if not geometry_wkt or not pkuid:
                    logger.warning("No geometry or pkuid available for zone")
                    return
                try:
                    loc = current_locale()
                    name = validate_text(self.nom_zone.text())
                    kwargs = dict(
                        geometry_wkt=geometry_wkt, pkuid=pkuid,
                        name=name,
                        zone_type=self.type_zone.currentData(),
                    )
                    if loc != 'ar':
                        kwargs[f'name_{loc}'] = name
                    add_zone(**kwargs)
                    QMessageBox.information(
                        self, self._tr("Success"),
                        self._tr("تمت إضافة هذه المنطقة بنجاح"),
                    )
                except Exception as e:
                    logger.exception("Failed to add zone: %s", e)
                    QMessageBox.critical(
                        self, self._tr("Error"),
                        self._tr('لا يمكن إضافة المنطقة , المنطقة موجودة بالفعل'),
                    )
