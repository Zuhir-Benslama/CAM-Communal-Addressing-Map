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
        if self.identify_tool2:
            self.identify_tool2.unset_map_tool()
        canvas = self.iface.mapCanvas()
        self.identify_tool = IdentifyTool(canvas)
        self.identify_tool.set_iface(self.iface)
        self.identify_tool.set_active_layer(self.iface.activeLayer())
        canvas.setMapTool(self.identify_tool)

    def set_pan_selection(self) -> None:
        """Activate the identify tool for panel feature selection."""
        if self.identify_tool2:
            self.identify_tool2.unset_map_tool()
        canvas = self.iface.mapCanvas()
        self.identify_tool = IdentifyTool(canvas)
        self.identify_tool.set_iface(self.iface)
        self.identify_tool.set_active_layer(self.iface.activeLayer())
        canvas.setMapTool(self.identify_tool)

    def set_num_selection(self) -> None:
        """Activate the identify tool for numbering feature selection."""
        if self.identify_tool2:
            self.identify_tool2.unset_map_tool()
        canvas = self.iface.mapCanvas()
        self.identify_tool = IdentifyTool(canvas)
        self.identify_tool.set_iface(self.iface)
        self.identify_tool.set_active_layer(self.iface.activeLayer())
        canvas.setMapTool(self.identify_tool)

    def set_city_selection(self) -> None:
        """Activate the identify tool for subdivision feature selection."""
        if self.identify_tool2:
            self.identify_tool2.unset_map_tool()
        canvas = self.iface.mapCanvas()
        self.identify_tool = IdentifyTool(canvas)
        self.identify_tool.set_iface(self.iface)
        self.identify_tool.set_active_layer(self.iface.activeLayer())
        canvas.setMapTool(self.identify_tool)

    def set_road_selection(self) -> None:
        """Activate the identify tool for road feature selection."""
        if self.identify_tool2:
            self.identify_tool2.unset_map_tool()
        canvas = self.iface.mapCanvas()
        self.identify_tool = IdentifyTool(canvas)
        self.identify_tool.set_iface(self.iface)
        self.identify_tool.set_active_layer(self.iface.activeLayer())
        canvas.setMapTool(self.identify_tool)

    def set_org_selection(self) -> None:
        """Activate the identify tool for organization feature selection."""
        if self.identify_tool2:
            self.identify_tool2.unset_map_tool()
        canvas = self.iface.mapCanvas()
        self.identify_tool = IdentifyTool(canvas)
        self.identify_tool.set_iface(self.iface)
        self.identify_tool.set_active_layer(self.iface.activeLayer())
        canvas.setMapTool(self.identify_tool)

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
        try:
            self.iface.mapCanvas().customContextMenuRequested.connect(
                self.on_edition_release,
            )
        except TypeError:
            pass
        self.iface.mapCanvas().setContextMenuPolicy(Qt.CustomContextMenu)

    def _on_map_tool_changed(self, new_tool) -> None:
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
            QMessageBox.critical(self, "Error", "نوع المرجع غير محدد")

        layer = project.mapLayersByName(LAYER_NUMBERING)
        if layer:
            self.iface.setActiveLayer(layer[0])

    def select_ref_handler2(self) -> None:
        """Activate secondary identify tool in reference mode for panel
        reference selection."""
        self.ref_name2.clear()
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
                self.identify_tool2.set_ref_name(self.ref_name2)
                self.identify_tool2.set_active_layer(layer[0])
                canvas.setMapTool(self.identify_tool2)
        else:
            QMessageBox.critical(self, "Error", "نوع المرجع غير محدد")

        layer = project.mapLayersByName(LAYER_PANELS)
        if layer:
            self.iface.setActiveLayer(layer[0])
