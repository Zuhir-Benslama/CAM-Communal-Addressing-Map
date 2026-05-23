"""Layer editing mixin for adding and updating features via forms."""

import logging

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsProject

from ..layer.editing import update_layer
from ..app.orders.repository import (
    add_panel_sign, add_organization, add_road,
    add_numbering, add_subdivision, add_zone,
)
from ..constants import (
    LAYER_ROADS, LAYER_FACILITIES, LAYER_SUBDIVISIONS,
    LAYER_NUMBERING, LAYER_PANELS, validate_text,
    current_locale,
)

logger = logging.getLogger(__name__)


class LayerEditMixin:
    """Mixin for updating layer geometries and adding features via forms.

    Cross-mixin protocol (attributes set by map_tools_mixin or owning dialog):
        _last_feature_wkt (str | None) — WKT geometry of the last created feature
        _last_feature_pkuid (str | None) — PK of the last created feature
        ref_identify_tool (IdentifyTool | None) — reference selection tool (get_pkuid)
        measure_tool (MeasureTool | None) — measurement line tool
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
        """Enable geometry editing on the currently selected layer."""
        self._update_handler(self._current_layer_name())

    def _get_geometry_and_pkuid(self, entity_name: str):
        """Retrieve the captured geometry WKT and feature PK."""
        geometry_wkt = getattr(self, '_last_feature_wkt', None)
        pkuid = getattr(self, '_last_feature_pkuid', None)
        if not geometry_wkt or not pkuid:
            logger.warning("No geometry or pkuid available for %s", entity_name)
            return None, None
        return geometry_wkt, pkuid

    def _show_success(self, message: str) -> None:
        """Show a success information dialog."""
        QMessageBox.information(
            self, self._tr("Success"), self._tr(message),
        )

    def _show_error(self, message: str) -> None:
        """Show a critical error dialog."""
        QMessageBox.critical(self, self._tr("Error"), self._tr(message))

    def _make_locale_kwargs(self, field_base: str, value: str) -> dict:
        """Build locale-specific field kwargs for non-Arabic locales."""
        loc = current_locale()
        if loc != 'ar':
            return {f'{field_base}_{loc}': value}
        return {}

    def add_panel(self) -> None:
        """Add a new panel sign linked to a selected road, org, or
        subdivision."""
        if not self.is_pan.isChecked():
            return
        if self.update_object:
            return
        ref_data = self.ref_identify_tool.get_pkuid()
        if ref_data is None:
            logger.warning("No object selected for panel reference")
            return
        geometry_wkt, pkuid = self._get_geometry_and_pkuid('panel')
        if not geometry_wkt or not pkuid:
            return
        try:
            layer = ref_data.get('layer_name')
            ref = ref_data.get('pkuid')
            kwargs = {
                'geometry_wkt': geometry_wkt, 'pkuid': pkuid,
                'etat_mont': self.etat_mont.currentData(),
            }
            if layer == LAYER_FACILITIES:
                add_panel_sign(**kwargs, road_id=None, subdivision_id=None, organization_id=ref)
            elif layer == LAYER_ROADS:
                add_panel_sign(**kwargs, road_id=ref, subdivision_id=None, organization_id=None)
            elif layer == LAYER_SUBDIVISIONS:
                add_panel_sign(**kwargs, road_id=None, subdivision_id=ref, organization_id=None)

            if self.measure_tool:
                self.show_confirm_dialog(
                    title=self._tr("Success"),
                    message=self._tr(
                        "Panel added successfully\n Do you want to clear the measurement line?"
                    ),
                    yes_callback=self.measure_tool.clear,
                )
            else:
                self._show_success("Panel added successfully")
        except Exception as e:
            logger.exception("Failed to add panel: %s", e)
            self._show_error(str(e))
        finally:
            self.ref_identify_tool.unset_map_tool()
            self._draw_handler(LAYER_PANELS)

    def add_organization(self) -> None:
        """Add a new organization through the form."""
        if not self.is_org.isChecked():
            return
        geometry_wkt, pkuid = self._get_geometry_and_pkuid('organization')
        if not geometry_wkt or not pkuid:
            return
        try:
            nom = validate_text(self.nom_org.text())
            kwargs = {
                'geometry_wkt': geometry_wkt, 'pkuid': pkuid,
                'cat_org': self.cat_org.currentData(),
                'nom_org': nom,
                'type_org': self.type_org.currentData(),
            }
            kwargs.update(self._make_locale_kwargs('nom_org', nom))
            add_organization(**kwargs)
            self._show_success("Facility added successfully")
        except Exception as e:
            logger.exception("Failed to add organization: %s", e)
            self._show_error('Cannot add facility, it already exists')

    def add_road(self) -> None:
        """Add a new road through the form."""
        if not self.is_road.isChecked():
            return
        geometry_wkt, pkuid = self._get_geometry_and_pkuid('road')
        if not geometry_wkt or not pkuid:
            return
        try:
            nom = validate_text(self.nom_voie.text())
            kwargs = {
                'geometry_wkt': geometry_wkt, 'pkuid': pkuid,
                'dec_voie': None,
                'nom_voie': nom,
                'type_voie': self.type_voie.currentData(),
            }
            kwargs.update(self._make_locale_kwargs('nom_voie', nom))
            add_road(**kwargs)
            self._show_success("Road added successfully")
        except Exception as e:
            logger.exception("Failed to add road: %s", e)
            self._show_error('Cannot add road, it already exists')

    def key_press_event(self, event, action: str = 'add_numbering') -> None:
        """Handle Enter key press to trigger the given action."""
        if event.key() == Qt.Key_Return:
            getattr(self, action)()

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
        yes_button.setText(self._tr("Yes"))
        no_button.setText(self._tr("No"))

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
        if not self.is_num.isChecked():
            return
        geometry_wkt, pkuid = self._get_geometry_and_pkuid('numbering')
        if not geometry_wkt or not pkuid:
            return
        try:
            ref_data = self.ref_identify_tool.get_pkuid()
        except Exception as e:
            logger.warning("Failed to get pkuid from identify tool: %s", e)
            ref_data = None
        try:
            common = {
                'geometry_wkt': geometry_wkt, 'pkuid': pkuid,
                'repetition': validate_text(self.repetition.text()),
                'valeur': validate_text(self.num_val.text()),
                'etat': self.num_etat.currentData(),
                'cat_act': self.cat_act.currentData(),
                'type_act': self.type_act.currentData(),
            }
            if ref_data and ref_data.get('layer_name') == LAYER_ROADS:
                add_numbering(**common, road_id=ref_data.get('pkuid'), subdivision_id=None)
            elif ref_data and ref_data.get('layer_name') == LAYER_SUBDIVISIONS:
                add_numbering(**common, road_id=None, subdivision_id=ref_data.get('pkuid'))

            if self.measure_tool:
                self.show_confirm_dialog(
                    title=self._tr("Success"),
                    message=self._tr(
                        "Numbering added successfully\n Do you want to clear the measurement line?"
                    ),
                    yes_callback=self.measure_tool.clear,
                )
            else:
                self._show_success("Numbering added successfully")
        except Exception as e:
            logger.exception("Failed to add numbering: %s", e)
            self._show_error(str(e))

        self.num_val.setFocus()
        self.num_val.clear()
        self._draw_handler(LAYER_NUMBERING)

    def add_city(self) -> None:
        """Add a new subdivision through the form."""
        if not self.is_city.isChecked():
            return
        geometry_wkt, pkuid = self._get_geometry_and_pkuid('subdivision')
        if not geometry_wkt or not pkuid:
            return
        try:
            name = validate_text(self.nom_city.text())
            kwargs = {
                'geometry_wkt': geometry_wkt, 'pkuid': pkuid,
                'name': name,
                'subdivision_type': self.type_city.currentData(),
            }
            kwargs.update(self._make_locale_kwargs('name', name))
            add_subdivision(**kwargs)
            self._show_success("Subdivision added successfully")
        except Exception as e:
            logger.exception("Failed to add city: %s", e)
            self._show_error(str(e))

    def add_zone(self) -> None:
        """Add a new zone through the form."""
        if not self.is_zone.isChecked():
            return
        if self.update_object:
            return
        geometry_wkt, pkuid = self._get_geometry_and_pkuid('zone')
        if not geometry_wkt or not pkuid:
            return
        try:
            name = validate_text(self.nom_zone.text())
            kwargs = {
                'geometry_wkt': geometry_wkt, 'pkuid': pkuid,
                'name': name,
                'zone_type': self.type_zone.currentData(),
            }
            kwargs.update(self._make_locale_kwargs('name', name))
            add_zone(**kwargs)
            self._show_success("Zone added successfully")
        except Exception as e:
            logger.exception("Failed to add zone: %s", e)
            self._show_error('Cannot add zone, zone already exists')
