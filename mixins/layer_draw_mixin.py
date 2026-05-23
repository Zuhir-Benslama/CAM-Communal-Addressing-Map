"""Drawing mixin for activating edit mode on map layers."""

import logging

from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject

from ..layer.editing import start_editing_layer

logger = logging.getLogger(__name__)


class LayerDrawMixin:
    """Mixin to start drawing/editing sessions on specific map layers."""

    def _draw_handler(self, layer_name: str) -> None:
        """Start editing a named layer with feature-added tracking."""
        layers = QgsProject.instance().mapLayersByName(layer_name)
        if not layers:
            logger.warning("Layer '%s' not found for drawing", layer_name)
            return
        layer = layers[0]
        try:
            layer.featureAdded.disconnect(self.on_feature_added)
        except TypeError:
            pass
        layer.featureAdded.connect(self.on_feature_added)
        try:
            self.iface.mapCanvas().customContextMenuRequested.disconnect(
                self.on_edition_release,
            )
        except TypeError:
            pass
        self.iface.mapCanvas().setContextMenuPolicy(Qt.DefaultContextMenu)
        start_editing_layer(self.iface, layer_name)

    def start_drawing(self) -> None:
        """Start drawing on the currently selected layer."""
        self._draw_handler(self._current_layer_name())
