"""Map tool management mixin for measure and identify interactions."""

from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject

from ..gui.measure_tool import MeasureTool
from ..gui.identify_tool import IdentifyTool
from ..constants import LAYER_NUMBERING, LAYER_PANELS


class MapToolsMixin:
    """Mixin providing map tool activation for measurement and feature
    selection."""

    def _selection_handler(self, layer=None) -> None:
        """Activate identify tool for feature selection on the active layer."""
        if self.identify_tool2:
            self.identify_tool2.unset_map_tool()
        canvas = self.iface.mapCanvas()
        self.identify_tool = IdentifyTool(canvas)
        self.identify_tool.set_iface(self.iface)
        target = layer or self.iface.activeLayer()
        self.identify_tool.set_active_layer(target)
        canvas.setMapTool(self.identify_tool)

    def measure_distance(self) -> None:
        """Activate the distance measurement tool on the map canvas."""
        self.measure_tool = MeasureTool(self.iface.mapCanvas(), self.iface)
        self.iface.mapCanvas().setMapTool(self.measure_tool)

    def measure_distance2(self) -> None:
        """Activate a secondary distance measurement tool."""
        self.measure_tool2 = MeasureTool(self.iface.mapCanvas(), self.iface)
        self.iface.mapCanvas().setMapTool(self.measure_tool2)

    def set_zone_selection(self) -> None:
        """Activate the identify tool for zone feature selection."""
        self._selection_handler()

    def set_pan_selection(self) -> None:
        """Activate the identify tool for panel feature selection."""
        self._selection_handler()

    def set_num_selection(self) -> None:
        """Activate the identify tool for numbering feature selection."""
        self._selection_handler()

    def set_city_selection(self) -> None:
        """Activate the identify tool for subdivision feature selection."""
        self._selection_handler()

    def set_road_selection(self) -> None:
        """Activate the identify tool for road feature selection."""
        self._selection_handler()

    def set_org_selection(self) -> None:
        """Activate the identify tool for organization feature selection."""
        self._selection_handler()

    def stop(self) -> None:
        """Deactivate all active map tools and clear measurements."""
        layer = self.iface.activeLayer()
        if layer:
            if self.identify_tool:
                self.identify_tool.unset_map_tool()

            if self.identify_tool2:
                self.identify_tool2.unset_map_tool()
            if self.measure_tool:
                self.measure_tool.clear()
            if self.measure_tool2:
                self.measure_tool2.clear()

    def on_edition_release(self, event) -> None:
        """Stop active tools when the edition context menu is triggered."""
        self.stop()

    def _reconnect_context_menu(self) -> None:
        canvas = self.iface.mapCanvas()
        try:
            canvas.customContextMenuRequested.disconnect(self.on_edition_release)
        except TypeError:
            pass
        try:
            canvas.customContextMenuRequested.connect(self.on_edition_release)
        except TypeError:
            pass
        canvas.setContextMenuPolicy(Qt.CustomContextMenu)

    def _on_map_tool_changed(self, new_tool) -> None:
        try:
            self.iface.mapCanvas()
        except RuntimeError:
            return
        self._reconnect_context_menu()

    def select_ref_handler(self) -> None:
        """Activate identify tool in reference mode for selecting a
        reference feature."""
        self.ref_name.clear()
        project = QgsProject.instance()
        if self.dyn_ref.currentText():
            layer_name = self.dyn_ref.currentText()
            layer = project.mapLayersByName(layer_name)
            if layer:
                self.iface.setActiveLayer(layer[0])
                canvas = self.iface.mapCanvas()
                self.identify_tool2 = IdentifyTool(
                    canvas, mode=IdentifyTool.MODE_REF,
                )
                self.identify_tool2.set_iface(self.iface)
                self.identify_tool2.set_ref_name(self.ref_name)
                self.identify_tool2.set_active_layer(layer[0])
                canvas.setMapTool(self.identify_tool2)
        else:
            QMessageBox.critical(self, self._tr("Error"), self._tr("نوع المرجع غير محدد"))

        self.set_default_cursor()
        layer = QgsProject.instance().mapLayersByName(self.layer_name_key)

    def select_ref_handler2(self) -> None:
        self.ref_name.clear()
        project = QgsProject.instance()
        if self.dyn_ref2.currentText():
            layer_name = self.dyn_ref2.currentText()
            layer = project.mapLayersByName(layer_name)
            if layer:
                self.iface.setActiveLayer(layer[0])
                canvas = self.iface.mapCanvas()
                self.identify_tool2 = IdentifyTool(
                    canvas, mode=IdentifyTool.MODE_REF,
                )
                self.identify_tool2.set_iface(self.iface)
                self.identify_tool2.set_ref_name(self.ref_name)
                self.identify_tool2.set_active_layer(layer[0])
                canvas.setMapTool(self.identify_tool2)
        else:
            QMessageBox.critical(self, self._tr("Error"), self._tr("نوع المرجع غير محدد"))
        self.set_default_cursor()
        layer = QgsProject.instance().mapLayersByName(self.layer_name_key)

    def ref_pan_selected(self) -> None:
        """Handle panel reference selection event."""
        if not self.identify_tool2:
            return
        obj = self.identify_tool2.get_pkuid()
        if not obj:
            QMessageBox.critical(self, self._tr("Error"), self._tr("نوع المرجع غير محدد"))

        layer = project.mapLayersByName(LAYER_PANELS)
        if layer:
            self.iface.setActiveLayer(layer[0])
