"""Layer operations mixin for feature CRUD and tab-based layer management."""

import logging
import uuid

from qgis.PyQt.QtWidgets import (
    QMessageBox, QFormLayout, QLineEdit, QComboBox, QSpinBox, QCheckBox,
)
from qgis.core import QgsProject
from shapely import wkt
from shapely.geometry import Point, Polygon, LineString
from geoalchemy2.elements import WKTElement

from ..db.operations import qgis_config
from ..db.operations import get_user_location
from .. import models as _models
from ..models import get_session
from ..constants import (
    LAYER_ROADS, LAYER_FACILITIES, LAYER_SUBDIVISIONS,
    LAYER_ZONES, LAYER_NUMBERING, LAYER_PANELS, SRID,
)
from ..gui.entity_list_dialog import EntityListDialog

logger = logging.getLogger(__name__)


class LayerOpsMixin:
    """Mixin for layer tab management, feature validation, and
    entity listing."""

    def on_opt_selected(self, index) -> None:
        """Handle tab selection: toggle layer visibility and load styles."""
        import os
        from ..constants import (
            LAYER_MUNICIPALITY, LAYER_PANELS, LAYER_NUMBERING,
            DEFAULT_STYLE_DIR, CUSTOM_STYLE_DIR,
        )

        self.type_plan = ""
        tab_name = self.menu.tabText(index)
        root = QgsProject.instance().layerTreeRoot()
        for layer_node in root.children():
            if layer_node.layer().isEditable():
                layer_node.layer().rollBack()
                layer_node.layer().commitChanges()
            if self.identify_tool:
                self.identify_tool.unset_map_tool()
            if self.identify_tool2:
                self.identify_tool2.unset_map_tool()
            if self.measure_tool:
                self.measure_tool.clear()
            if self.measure_tool2:
                self.measure_tool2.clear()

            layer_node.setItemVisibilityChecked(False)

        for i in [self.sat_view, self.rast, LAYER_MUNICIPALITY]:
            always_shown = QgsProject.instance().mapLayersByName(i)
            if always_shown:
                layer_to_show = root.findLayer(always_shown[0].id())
                if layer_to_show:
                    layer_to_show.setItemVisibilityChecked(True)

        if tab_name not in ['تقرير', 'اعدادات']:
            data_list = qgis_config().get('other_layers')
            l = QgsProject.instance().mapLayersByName(tab_name)
            if l:
                root.findLayer(l[0].id()).setItemVisibilityChecked(True)
                self.iface.setActiveLayer(l[0])

                for dl in data_list:
                    if dl.get("label") == tab_name and dl.get("show_with"):
                        for sw in dl.get("show_with"):
                            l = QgsProject.instance().mapLayersByName(sw)
                            if l:
                                _node = root.findLayer(l[0].id())
                                if _node:
                                    _node.setItemVisibilityChecked(True)

                data_list = qgis_config().get('other_layers')
                for dl in data_list:
                    lbl = dl.get('label')
                    l = QgsProject.instance().mapLayersByName(lbl)[0]
                    filename = os.path.join(DEFAULT_STYLE_DIR, dl.get('style'))
                    l.loadNamedStyle(filename)

        elif tab_name == "اعدادات":
            pass

        elif tab_name == "تقرير":
            data_list = qgis_config().get('other_layers')
            for dl in data_list:
                tmpl = QgsProject.instance().mapLayersByName(dl.get('label'))[0]
                filename = os.path.join(CUSTOM_STYLE_DIR, dl.get('style'))
                tmpl.loadNamedStyle(filename)
                for i in [LAYER_SUBDIVISIONS, LAYER_FACILITIES, LAYER_ROADS]:
                    always_shown = QgsProject.instance().mapLayersByName(i)
                    if always_shown:
                        layer_to_show = root.findLayer(always_shown[0].id())
                        if layer_to_show:
                            layer_to_show.setItemVisibilityChecked(True)

        else:
            for layer_node in root.children():
                if layer_node.layer().name() in [LAYER_PANELS, LAYER_NUMBERING]:
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

    def list_roads(self) -> None:
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
        dlg = EntityListDialog(model_name="Numbering", list_of='المداخل')
        dlg.exec_()

    def list_panels(self) -> None:
        """Open an entity list dialog for panel signs."""
        dlg = EntityListDialog(model_name="PanelSign", list_of='اللواحات')
        dlg.exec_()

    def on_feature_added(self, feature) -> None:
        """Validate added feature geometry against the user's allowed zone."""
        layer = self.iface.activeLayer()
        if layer and layer.isEditable():
            obj = layer.getFeature(feature)
            obj['pkuid'] = str(uuid.uuid4())
            layer.updateFeature(obj)

            if obj.isValid():
                uloc = wkt.loads(get_user_location())
                current_obj = wkt.loads(obj.geometry().asWkt())

                case = 0
                if isinstance(current_obj, Point) and current_obj.within(uloc):
                    case = 1
                elif (
                    isinstance(current_obj, Polygon)
                    and current_obj.intersects(uloc)
                ):
                    case = 2
                elif (
                    isinstance(current_obj, LineString)
                    and current_obj.intersects(uloc)
                ):
                    case = 3
                else:
                    case = 0

                if case == 0:
                    del_obj = layer.getFeature(feature)
                    if del_obj.isValid():
                        layer.deleteFeature(feature)
                    self._reconnect_context_menu()
                else:
                    self._last_feature_pkuid = obj['pkuid']
                    self._last_feature_wkt = obj.geometry().asWkt()
                    layer.featureAdded.disconnect(self.on_feature_added)
                    layer.commitChanges()
                    self._reconnect_context_menu()
                    canvas = self.iface.mapCanvas()
                    canvas.unsetMapTool(canvas.mapTool())
                    current_index = self.menu.currentIndex()
                    current_tab_text = self.menu.tabText(current_index)
                    self.is_org.setChecked(False)
                    self.is_road.setChecked(False)
                    self.is_city.setChecked(False)
                    self.is_num.setChecked(False)
                    self.is_pan.setChecked(False)
                    self.is_zone.setChecked(False)
                    if layer.name() == current_tab_text:
                        if layer.name() == LAYER_ROADS:
                            self.is_road.setChecked(True)
                        elif layer.name() == LAYER_FACILITIES:
                            self.is_org.setChecked(True)
                        elif layer.name() == LAYER_SUBDIVISIONS:
                            self.is_city.setChecked(True)
                        elif layer.name() == LAYER_NUMBERING:
                            self.is_num.setChecked(True)
                        elif layer.name() == LAYER_PANELS:
                            self.is_pan.setChecked(True)
                        elif layer.name() == LAYER_ZONES:
                            self.is_zone.setChecked(True)

            current_index = self.menu.currentIndex()
            tab_text = self.menu.tabText(current_index)
            if tab_text == LAYER_NUMBERING:
                self.num_val.setFocus()

    def on_geometry_changed(self, fid) -> None:
        """Validate geometry edits and persist changes to the database."""
        layer = self.iface.activeLayer()
        if layer and layer.isEditable():
            feature = layer.getFeature(fid)
            if not feature.isValid():
                return

            uloc = wkt.loads(get_user_location())
            current_obj = wkt.loads(feature.geometry().asWkt())

            case = 0
            if isinstance(current_obj, Point) and current_obj.within(uloc):
                case = 1
            if (
                isinstance(current_obj, Polygon)
                and current_obj.intersects(uloc)
            ):
                case = 2
            if (
                isinstance(current_obj, LineString)
                and current_obj.intersects(uloc)
            ):
                case = 3

            if case == 0:
                layer.rollBack()
                QMessageBox.warning(
                    self, "Modification annulée",
                    "Géométrie en dehors de votre zone autorisée.",
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
                        except Exception as e:
                            logger.exception("Failed to save feature: %s", e)
                            QMessageBox.critical(self, "Erreur", str(e))
                        finally:
                            session.close()
