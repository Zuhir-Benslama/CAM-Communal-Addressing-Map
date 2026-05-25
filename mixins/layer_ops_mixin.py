"""Layer operations mixin for feature CRUD and tab-based layer management."""

import logging
import os
import uuid

from qgis.PyQt.QtWidgets import (
    QMessageBox, QFormLayout, QLineEdit, QComboBox, QSpinBox, QCheckBox,
)
from qgis.core import QgsLayerTreeLayer, QgsProject
from shapely import wkt
from shapely.geometry import Point, Polygon, LineString
from geoalchemy2.elements import WKTElement

from ..app.users.repository import qgis_config, get_user_location
from ..app.orders import models as _models
from ..app.core.database import get_session
from ..constants import (
    LAYER_ROADS, LAYER_FACILITIES, LAYER_SUBDIVISIONS,
    LAYER_ZONES, LAYER_NUMBERING, LAYER_PANELS, SRID,
    LAYER_MUNICIPALITY, DEFAULT_STYLE_DIR, CUSTOM_STYLE_DIR,
)
from ..gui.entity_list_dialog import EntityListDialog

logger = logging.getLogger(__name__)


class LayerOpsMixin:
    """Mixin for layer tab management, feature validation, and
    entity listing."""

    def _reset_tools(self) -> None:
        """Deactivate all active map tools and clear measurements."""
        if self.identify_tool:
            self.identify_tool.unset_map_tool()
        if self.ref_identify_tool:
            self.ref_identify_tool.unset_map_tool()
        if self.measure_tool:
            self.measure_tool.clear()

    def _show_layers_for_label(self, root, layer_label: str) -> None:
        """Show the selected operation layer plus configured dependencies."""
        visible_names = {LAYER_MUNICIPALITY}
        if self.sat_view:
            visible_names.add(self.sat_view)
        if self.rast:
            visible_names.add(self.rast)
        if layer_label:
            visible_names.add(layer_label)

        data_list = qgis_config().get('other_layers')
        for layer_cfg in data_list:
            if layer_cfg.get('label') == layer_label and layer_cfg.get('show_with'):
                visible_names.update(layer_cfg.get('show_with'))
                break

        target_layer = None
        for layer_node in root.children():
            if not isinstance(layer_node, QgsLayerTreeLayer):
                continue
            lyr = layer_node.layer()
            if not lyr:
                continue
            if lyr.isEditable():
                lyr.rollBack()
                lyr.commitChanges()
            layer_node.setItemVisibilityChecked(lyr.name() in visible_names)
            if lyr.name() == layer_label:
                target_layer = lyr

        if target_layer:
            self.iface.setActiveLayer(target_layer)

    def _show_base_layers(self, root) -> None:
        """Ensure base/context layers stay visible."""
        for name in [self.sat_view, self.rast, LAYER_MUNICIPALITY]:
            if not name:
                continue
            layers = QgsProject.instance().mapLayersByName(name)
            if layers:
                node = root.findLayer(layers[0].id())
                if node:
                    node.setItemVisibilityChecked(True)

    def _current_ops_layer(self) -> str:
        """Return the currently selected layer name via the mixin protocol."""
        if hasattr(self, "_current_layer_name"):
            return self._current_layer_name()
        return ""

    def on_opt_selected(self, index) -> None:
        """Handle tab selection: toggle layer visibility and load styles."""
        self.type_plan = ""
        # Use cached tab text for internal routing (locale-independent)
        if hasattr(self.menu, '_rna_tab_src'):
            tab_name = self.menu._rna_tab_src[index]
        else:
            tab_name = self.menu.tabText(index)
        root = QgsProject.instance().layerTreeRoot()
        self._reset_tools()

        selected_layer = ""
        if tab_name == 'Operations':
            selected_layer = self._current_ops_layer()
        elif tab_name not in ['Report', 'Settings']:
            selected_layer = tab_name

        if selected_layer:
            self._show_layers_for_label(root, selected_layer)
            data_list = qgis_config().get('other_layers')
            last_tab = getattr(self, '_last_loaded_tab', None)
            selected_key = (
                f"ops:{selected_layer}" if tab_name == 'Operations'
                else selected_layer
            )
            if selected_key != last_tab:
                for layer_cfg in data_list:
                    lbl = layer_cfg.get('label')
                    layers = QgsProject.instance().mapLayersByName(lbl)
                    if layers:
                        filename = os.path.join(DEFAULT_STYLE_DIR, layer_cfg.get('style'))
                        layers[0].loadNamedStyle(filename)
                self._last_loaded_tab = selected_key

        elif tab_name == "Settings":
            for layer_node in root.children():
                if not isinstance(layer_node, QgsLayerTreeLayer):
                    continue
                lyr = layer_node.layer()
                if not lyr:
                    continue
                if lyr.isEditable():
                    lyr.rollBack()
                    lyr.commitChanges()
                layer_node.setItemVisibilityChecked(False)
            self._show_base_layers(root)

        elif tab_name == "Report":
            for layer_node in root.children():
                if not isinstance(layer_node, QgsLayerTreeLayer):
                    continue
                lyr = layer_node.layer()
                if not lyr:
                    continue
                if lyr.isEditable():
                    lyr.rollBack()
                    lyr.commitChanges()
                layer_node.setItemVisibilityChecked(False)
            self._show_base_layers(root)
            data_list = qgis_config().get('other_layers')
            for layer_cfg in data_list:
                tmpl_list = QgsProject.instance().mapLayersByName(layer_cfg.get('label'))
                if not tmpl_list:
                    continue
                tmpl = tmpl_list[0]
                filename = os.path.join(CUSTOM_STYLE_DIR, layer_cfg.get('style'))
                tmpl.loadNamedStyle(filename)
                for i in [LAYER_SUBDIVISIONS, LAYER_FACILITIES, LAYER_ROADS]:
                    always_shown = QgsProject.instance().mapLayersByName(i)
                    if always_shown:
                        layer_to_show = root.findLayer(always_shown[0].id())
                        if layer_to_show:
                            layer_to_show.setItemVisibilityChecked(True)

        else:
            for layer_node in root.children():
                if not isinstance(layer_node, QgsLayerTreeLayer):
                    continue
                lyr = layer_node.layer()
                if not lyr:
                    continue
                if lyr.isEditable():
                    lyr.rollBack()
                    lyr.commitChanges()
                if lyr.name() in [LAYER_PANELS, LAYER_NUMBERING]:
                    layer_node.setItemVisibilityChecked(False)
                else:
                    layer_node.setItemVisibilityChecked(True)

        self.iface.mapCanvas().refresh()

    def clear_forms(self, layout) -> None:
        """Clear all widgets (QLineEdit, QComboBox, etc.) in the given
        form layout."""
        for i in range(layout.rowCount()):
            widget = layout.itemAt(i, QFormLayout.FieldRole)
            if widget:
                if isinstance(widget.widget(), QLineEdit):
                    widget.widget().clear()
                elif isinstance(widget.widget(), QComboBox):
                    widget.widget().setCurrentIndex(0)
                elif isinstance(widget.widget(), QSpinBox):
                    widget.widget().setValue(widget.widget().minimum())
                elif isinstance(widget.widget(), QCheckBox):
                    widget.widget().setChecked(False)

    def list_road_entries(self) -> None:
        """Open an entity list dialog for roads."""
        dlg = EntityListDialog(model_name="Road", list_of=LAYER_ROADS)
        dlg.exec_()

    def list_organizations(self) -> None:
        """Open an entity list dialog for organizations."""
        dlg = EntityListDialog(
            model_name="Organization", list_of=LAYER_FACILITIES,
        )
        dlg.exec_()

    def list_subdivisions(self) -> None:
        """Open an entity list dialog for subdivisions."""
        dlg = EntityListDialog(
            model_name="Subdivision", list_of=LAYER_SUBDIVISIONS,
        )
        dlg.exec_()

    def list_numberings(self) -> None:
        """Open an entity list dialog for numberings."""
        dlg = EntityListDialog(model_name="Numbering", list_of='Numberings')
        dlg.exec_()

    def list_panel_signs(self) -> None:
        """Open an entity list dialog for panel signs."""
        dlg = EntityListDialog(model_name="PanelSign", list_of='Panels')
        dlg.exec_()

    def _check_geometry_in_zone(self, geometry_wkt: str) -> int:
        """Check if geometry is within the user's allowed zone.

        Returns:
            0 = outside zone
            1 = Point within polygon
            2 = Polygon intersects zone
            3 = LineString intersects zone
        """
        uloc = wkt.loads(get_user_location())
        current_obj = wkt.loads(geometry_wkt)

        if isinstance(current_obj, Point) and current_obj.within(uloc):
            return 1
        if isinstance(current_obj, Polygon) and current_obj.intersects(uloc):
            return 2
        if isinstance(current_obj, LineString) and current_obj.intersects(uloc):
            return 3
        return 0

    def on_feature_added(self, fid) -> None:
        """Validate added feature geometry against the user's allowed zone."""
        layer = self.iface.activeLayer()
        if layer and layer.isEditable():
            obj = layer.getFeature(fid)
            obj['pkuid'] = str(uuid.uuid4())
            layer.updateFeature(obj)

            if obj.isValid():
                case = self._check_geometry_in_zone(obj.geometry().asWkt())

                if case == 0:
                    del_obj = layer.getFeature(fid)
                    if del_obj.isValid():
                        layer.deleteFeature(fid)
                    self._reconnect_context_menu()
                else:
                    self._last_feature_pkuid = obj['pkuid']
                    self._last_feature_wkt = obj.geometry().asWkt()
                    layer.featureAdded.disconnect(self.on_feature_added)
                    layer.commitChanges()
                    self._reconnect_context_menu()
                    canvas = self.iface.mapCanvas()
                    canvas.unsetMapTool(canvas.mapTool())
                    self.is_org.setChecked(False)
                    self.is_road.setChecked(False)
                    self.is_city.setChecked(False)
                    self.is_num.setChecked(False)
                    self.is_pan.setChecked(False)
                    self.is_zone.setChecked(False)
                    layer_check_map = {
                        LAYER_ROADS: self.is_road,
                        LAYER_FACILITIES: self.is_org,
                        LAYER_SUBDIVISIONS: self.is_city,
                        LAYER_NUMBERING: self.is_num,
                        LAYER_PANELS: self.is_pan,
                        LAYER_ZONES: self.is_zone,
                    }
                    target_checkbox = layer_check_map.get(layer.name())
                    if target_checkbox:
                        target_checkbox.setChecked(True)

            current_index = self.menu.currentIndex()
            if hasattr(self.menu, '_rna_tab_src'):
                tab_text = self.menu._rna_tab_src[current_index]
            else:
                tab_text = self.menu.tabText(current_index)
            selected_ops = self._current_ops_layer()
            if LAYER_NUMBERING in (tab_text, selected_ops):
                self.num_val.setFocus()

    def on_geometry_changed(self, fid) -> None:
        """Validate geometry edits and persist changes to the database."""
        layer = self.iface.activeLayer()
        if layer and layer.isEditable():
            feature = layer.getFeature(fid)
            if not feature.isValid():
                return

            case = self._check_geometry_in_zone(feature.geometry().asWkt())

            if case == 0:
                layer.rollBack()
                QMessageBox.warning(
                    self, self._tr("Modification cancelled"),
                    self._tr("Geometry outside your allowed area."),
                )
                return

            geometry_wkt = feature.geometry().asWkt()
            data_list = qgis_config().get('mapper')
            for data in data_list:
                if data.get('layer') == layer.name():
                    model_name = data.get('model')
                    model = getattr(_models, model_name, None)
                    if model:
                        session = get_session()
                        try:
                            model.update(
                                session,
                                pkuid=feature['pkuid'],
                                geometry=WKTElement(
                                    str(geometry_wkt), srid=SRID
                                ),
                            )
                        except Exception as e:  # noqa: W0718
                            logger.exception("Failed to save feature: %s", e)
                            QMessageBox.critical(
                                self, self._tr("Erreur"), str(e))
                        finally:
                            session.close()
