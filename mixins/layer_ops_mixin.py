"""Layer operations mixin for feature CRUD and tab-based layer management."""
# mypy: disable-error-code="attr-defined"

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Any

from geoalchemy2.elements import WKTElement
from qgis.core import QgsLayerTreeLayer, QgsProject
from qgis.PyQt.QtWidgets import QMessageBox
from shapely import wkt
from shapely.geometry import LineString, Point, Polygon
from sqlalchemy.exc import SQLAlchemyError

from ..app.core.database import get_session
from ..app.orders import models as _models
from ..app.users.repository import get_user_location, qgis_config
from ..constants import (
    DEFAULT_STYLE_DIR,
    LAYER_FACILITIES,
    LAYER_MUNICIPALITY,
    LAYER_NUMBERING,
    LAYER_PANELS,
    LAYER_ROADS,
    LAYER_SUBDIVISIONS,
    SRID,
    ZONE_LINE_INTERSECT,
    ZONE_OUTSIDE,
    ZONE_POINT_WITHIN,
    ZONE_POLYGON_INTERSECT,
)
from ..gui.entity_list_dialog import EntityListDialog
from ._protocols import (
    HasAuthIfaceContext,
    HasCurrentLayer,
    HasGeometryChangedContext,
    HasLayerOpsContext,
    HasLayerTools,
    HasTabSwitchContext,
)

logger = logging.getLogger(__name__)


class LayerOpsMixin:
    """Mixin for layer tab management, feature validation, and
    entity listing."""

    def _reset_tools(self: HasLayerTools) -> None:
        """Deactivate all active map tools and clear measurements."""
        if self.identify_tool:
            self.identify_tool.unset_map_tool()
        if self.ref_identify_tool:
            self.ref_identify_tool.unset_map_tool()
        if self.measure_tool:
            self.measure_tool.clear()

    def _show_layers_for_label(
        self: HasAuthIfaceContext,
        root,
        layer_label: str,
    ) -> None:
        """Show the selected operation layer plus configured dependencies."""
        visible_names = {LAYER_MUNICIPALITY}
        if self.sat_view:
            visible_names.add(self.sat_view)
        if self.rast:
            visible_names.add(self.rast)
        if layer_label:
            visible_names.add(layer_label)

        data_list = qgis_config().get('other_layers') or []
        for layer_cfg in data_list:
            if layer_cfg.get('label') == layer_label and layer_cfg.get('show_with'):
                visible_names.update(layer_cfg.get('show_with'))
                break

        target_layer = self._apply_layer_visibility(root, visible_names, layer_label)
        if target_layer:
            self.iface.setActiveLayer(target_layer)

    @staticmethod
    def _apply_layer_visibility(root, visible_names: set, layer_label: str) -> Any:
        """Set layer visibility, rollback editable layers, return target."""
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
        return target_layer

    def _hide_all_tab_layers(self, root) -> None:
        """Rollback editable layers and hide all."""
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

    @staticmethod
    def _load_tab_styles(data_list, style_dir: str) -> None:
        """Load named styles for each layer in the config list."""
        for layer_cfg in data_list:
            tmpl_list = QgsProject.instance().mapLayersByName(layer_cfg.get('label'))
            if not tmpl_list:
                continue
            filename = Path(style_dir) / layer_cfg.get('style')
            result = tmpl_list[0].loadNamedStyle(str(filename))
            if isinstance(result, tuple):
                success_val, _ = result
                is_success = bool(success_val)
                if not is_success:
                    logger.warning(
                        "Failed to load style for '%s' from %s",
                        layer_cfg.get('label'),
                        filename,
                    )
            else:
                logger.warning(
                    "Unexpected loadNamedStyle result for '%s': %s",
                    layer_cfg.get('label'),
                    result,
                )

    def _current_ops_layer(self: HasCurrentLayer) -> str:
        """Return the currently selected layer name via the mixin protocol."""
        if hasattr(self, '_current_layer_name'):
            return self._current_layer_name()
        return ''

    # ------------------------------------------------------------------
    # Tab handler dispatch helpers
    # ------------------------------------------------------------------

    def _handle_ops_tab(
        self: HasTabSwitchContext,
        root,
        tab_name: str,
        selected_layer: str,
    ) -> None:
        self._show_layers_for_label(root, selected_layer)
        data_list = qgis_config().get('other_layers')
        last_tab = getattr(self, '_last_loaded_tab', None)
        selected_key = (
            f'ops:{selected_layer}' if tab_name == 'Operations' else selected_layer
        )
        if selected_key != last_tab:
            self._load_tab_styles(data_list, str(DEFAULT_STYLE_DIR))
            self._last_loaded_tab = selected_key

    def _handle_default_tab(self: HasTabSwitchContext, root) -> None:
        self._hide_all_tab_layers(root)
        for layer_node in root.children():
            if not isinstance(layer_node, QgsLayerTreeLayer):
                continue
            lyr = layer_node.layer()
            if not lyr:
                continue
            if lyr.name() in [LAYER_PANELS, LAYER_NUMBERING]:
                layer_node.setItemVisibilityChecked(False)
            else:
                layer_node.setItemVisibilityChecked(True)

    # ------------------------------------------------------------------
    # Tab selection entry point
    # ------------------------------------------------------------------

    def on_opt_selected(
        self: HasTabSwitchContext,
        index,
    ) -> None:
        self.type_plan = ''
        tab_name = self.menu.tabText(index)
        root = QgsProject.instance().layerTreeRoot()
        self._reset_tools()

        selected_layer = self._current_ops_layer()

        if selected_layer:
            self._handle_ops_tab(root, tab_name, selected_layer)
        else:
            self._handle_default_tab(root)

        self.iface.mapCanvas().refresh()

    def list_road_entries(self) -> None:
        """Open an entity list dialog for roads."""
        dlg = EntityListDialog(model_name='Road', list_of=LAYER_ROADS)
        dlg.exec()

    def list_organizations(self) -> None:
        """Open an entity list dialog for organizations."""
        dlg = EntityListDialog(
            model_name='Organization',
            list_of=LAYER_FACILITIES,
        )
        dlg.exec()

    def list_subdivisions(self) -> None:
        """Open an entity list dialog for subdivisions."""
        dlg = EntityListDialog(
            model_name='Subdivision',
            list_of=LAYER_SUBDIVISIONS,
        )
        dlg.exec()

    def list_numberings(self) -> None:
        """Open an entity list dialog for numberings."""
        dlg = EntityListDialog(model_name='Numbering', list_of=LAYER_NUMBERING)
        dlg.exec()

    def list_panel_signs(self) -> None:
        """Open an entity list dialog for panel signs."""
        dlg = EntityListDialog(model_name='PanelSign', list_of=LAYER_PANELS)
        dlg.exec()

    def _check_geometry_in_zone(self, geometry_wkt: str) -> int:
        """Check if geometry is within the user's allowed zone.

        Returns:
            ZONE_OUTSIDE — outside zone
            ZONE_POINT_WITHIN — Point within polygon
            ZONE_POLYGON_INTERSECT — Polygon intersects zone
            ZONE_LINE_INTERSECT — LineString intersects zone
        """
        user_location = get_user_location()
        if user_location is None:
            logger.warning('No user location available; skipping zone check')
            return ZONE_POINT_WITHIN
        uloc = wkt.loads(user_location)
        current_obj = wkt.loads(geometry_wkt)

        if isinstance(current_obj, Point) and current_obj.within(uloc):
            return ZONE_POINT_WITHIN
        if isinstance(current_obj, Polygon) and current_obj.intersects(uloc):
            return ZONE_POLYGON_INTERSECT
        if isinstance(current_obj, LineString) and current_obj.intersects(uloc):
            return ZONE_LINE_INTERSECT
        return ZONE_OUTSIDE

    def on_feature_added(
        self: HasLayerOpsContext,
        fid,
    ) -> None:
        """Validate added feature geometry against the user's allowed zone."""
        layer = self.iface.activeLayer()
        if layer and layer.isEditable():
            obj = layer.getFeature(fid)
            obj['id'] = str(uuid.uuid4())
            layer.updateFeature(obj)

            if obj.isValid():
                case = self._check_geometry_in_zone(obj.geometry().asWkt())

                if case == ZONE_OUTSIDE:
                    del_obj = layer.getFeature(fid)
                    if del_obj.isValid():
                        layer.deleteFeature(fid)
                    self._reconnect_context_menu()
                else:
                    self._last_feature_id = obj['id']
                    self._last_feature_wkt = obj.geometry().asWkt()
                    layer.featureAdded.disconnect(self.on_feature_added)
                    layer.commitChanges()
                    self._reconnect_context_menu()
                    canvas = self.iface.mapCanvas()
                    canvas.unsetMapTool(canvas.mapTool())
                    self._geometry_ready = layer.name()

            current_index = self.menu.currentIndex()
            tab_text = self.menu.tabText(current_index)
            selected_ops = self._current_ops_layer()
            if LAYER_NUMBERING in (tab_text, selected_ops):
                self.num_val.setFocus()

    def on_geometry_changed(self: HasGeometryChangedContext, fid) -> None:
        """Validate geometry edits and persist changes to the database."""
        layer = self.iface.activeLayer()
        if layer and layer.isEditable():
            feature = layer.getFeature(fid)
            if not feature.isValid():
                return

            case = self._check_geometry_in_zone(feature.geometry().asWkt())

            if case == ZONE_OUTSIDE:
                layer.rollBack()
                QMessageBox.warning(
                    self,
                    self._tr('Modification cancelled'),
                    self._tr('Geometry outside your allowed area.'),
                )
                return

            geometry_wkt = feature.geometry().asWkt()
            data_list = qgis_config().get('mapper') or []
            for data in data_list:
                if data.get('layer') == layer.name():
                    model_name = data.get('model')
                    model = getattr(_models, model_name, None)
                    if model:
                        session = get_session()
                        try:
                            model.update(
                                session,
                                id=feature['id'],
                                geometry=WKTElement(str(geometry_wkt), srid=SRID),
                            )
                        except (SQLAlchemyError, ValueError) as e:
                            logger.exception('Failed to save feature')
                            QMessageBox.critical(self, self._tr('Error'), str(e))
                        finally:
                            session.close()
