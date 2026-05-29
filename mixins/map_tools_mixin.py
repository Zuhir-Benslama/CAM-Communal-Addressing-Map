"""Map tool management mixin for measure and identify interactions."""
# mypy: disable-error-code="attr-defined"

from __future__ import annotations

from typing import Optional

from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject

from ..gui.measure_tool import MeasureTool
from ..gui.identify_tool import IdentifyTool
from ..constants import LAYER_PANELS
from ._protocols import (
    HasIface, HasUiWidgets, HasMapToolsContext, HasFullMapToolsContext,
    HasSelectContext, HasRefSelectContext,
)


class MapToolsMixin:
    """Mixin providing map tool activation for measurement and feature
    selection."""

    identify_tool: Optional[IdentifyTool]
    ref_identify_tool: Optional[IdentifyTool]
    measure_tool: Optional[MeasureTool]

    def _selection_handler(self: HasMapToolsContext, layer=None) -> None:
        """Activate identify tool for feature selection on the active layer."""
        if self.ref_identify_tool:
            self.ref_identify_tool.unset_map_tool()
        canvas = self.iface.mapCanvas()
        self.identify_tool = IdentifyTool(canvas)
        self.identify_tool.set_iface(self.iface)
        target = layer or self.iface.activeLayer()
        self.identify_tool.set_active_layer(target)
        canvas.setMapTool(self.identify_tool)

    def activate_measure(self: HasMapToolsContext) -> None:
        """Activate the distance measurement tool on the map canvas."""
        self.measure_tool = MeasureTool(self.iface.mapCanvas(), self.iface)
        self.iface.mapCanvas().setMapTool(self.measure_tool)

    def start_selecting(self: HasSelectContext) -> None:
        """Activate the identify tool on the currently selected layer."""
        layer_name = self._current_layer_name()
        layers = QgsProject.instance().mapLayersByName(layer_name)
        if not layers:
            QMessageBox.critical(
                self, self._tr("Error"),
                self._tr("No active vector layer."),
            )
            return
        self.iface.setActiveLayer(layers[0])
        self._selection_handler(layer=layers[0])

    def stop(self: HasMapToolsContext) -> None:
        """Deactivate all active map tools and clear measurements."""
        layer = self.iface.activeLayer()
        if layer:
            if self.identify_tool:
                self.identify_tool.unset_map_tool()

            if self.ref_identify_tool:
                self.ref_identify_tool.unset_map_tool()
            if self.measure_tool:
                self.measure_tool.clear()

    def on_edition_release(self: HasMapToolsContext, _event) -> None:
        """Stop active tools when the edition context menu is triggered."""
        self.stop()

    def _reconnect_context_menu(self: HasIface) -> None:
        """Reconnect the custom context menu to ensure it stays active."""
        canvas = self.iface.mapCanvas()
        try:
            canvas.customContextMenuRequested.disconnect(
                self.on_edition_release)
        except TypeError:
            pass
        try:
            canvas.customContextMenuRequested.connect(self.on_edition_release)
        except TypeError:
            pass
        canvas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def _on_map_tool_changed(self: HasIface, _new_tool) -> None:
        """Reconnect context menu when the map tool changes."""
        try:
            self.iface.mapCanvas()
        except RuntimeError:
            return
        self._reconnect_context_menu()

    def set_default_cursor(self: HasIface) -> None:
        """Reset the cursor to the default arrow cursor on the map canvas."""
        self.iface.mapCanvas().setCursor(Qt.CursorShape.ArrowCursor)

    def _select_ref(
        self: HasFullMapToolsContext, combo,
    ) -> None:
        """Activate identify tool in reference mode for selecting a
        reference feature."""
        self.ref_name.clear()
        project = QgsProject.instance()
        layer_name = combo.currentData() or combo.currentText()
        if layer_name:
            layer = project.mapLayersByName(layer_name)
            if layer:
                self.iface.setActiveLayer(layer[0])
                canvas = self.iface.mapCanvas()
                self.ref_identify_tool = IdentifyTool(
                    canvas, mode=IdentifyTool.MODE_REF,
                )
                self.ref_identify_tool.set_iface(self.iface)
                self.ref_identify_tool.set_ref_name(self.ref_name)
                self.ref_identify_tool.set_active_layer(layer[0])
                canvas.setMapTool(self.ref_identify_tool)
        else:
            QMessageBox.critical(
                self,
                self._tr("Error"),
                self._tr("Reference type not specified"),
            )
        self.set_default_cursor()

    def select_ref_handler(self: HasUiWidgets) -> None:
        """Activate reference selection for the first reference combo."""
        self._select_ref(self.road_ref)

    def select_panel_ref_handler(self: HasUiWidgets) -> None:
        """Activate reference selection for the panel reference combo."""
        self._select_ref(self.panel_ref)

    def ref_pan_selected(self: HasRefSelectContext) -> None:
        """Handle panel reference selection event."""
        if not self.ref_identify_tool:
            return
        ref_data = self.ref_identify_tool.get_pkuid()
        if not ref_data:
            QMessageBox.critical(
                self,
                self._tr("Error"),
                self._tr("Reference type not specified"),
            )
            return

        layer = QgsProject.instance().mapLayersByName(LAYER_PANELS)
        if layer:
            self.iface.setActiveLayer(layer[0])
