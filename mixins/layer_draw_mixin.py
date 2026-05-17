"""Drawing mixin for activating edit mode on map layers."""

import logging

from qgis.PyQt.QtCore import Qt
from qgis.core import QgsProject

from ..layer.editing import start_editing_layer
from ..constants import (
    LAYER_ROADS, LAYER_FACILITIES, LAYER_SUBDIVISIONS,
    LAYER_ZONES, LAYER_NUMBERING, LAYER_PANELS,
)

logger = logging.getLogger(__name__)


class LayerDrawMixin:
    """Mixin to start drawing/editing sessions on specific map layers."""

    def _draw_handler(self, layer_name: str) -> None:
        """Start editing a named layer with feature-added tracking."""
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
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

    def draw_road_handler(self) -> None:
        """Start editing the roads layer."""
        self._draw_handler(LAYER_ROADS)

    def draw_org_handler(self) -> None:
        """Start editing the organizations (facilities) layer."""
        self._draw_handler(LAYER_FACILITIES)

    def draw_pan_handler(self) -> None:
        """Start editing the panels layer."""
        self._draw_handler(LAYER_PANELS)

    def draw_city_handler(self) -> None:
        """Start editing the subdivisions layer."""
        self._draw_handler(LAYER_SUBDIVISIONS)

    def draw_num_handler(self) -> None:
        """Start editing the numbering layer."""
        self._draw_handler(LAYER_NUMBERING)

    def draw_zone_handler(self) -> None:
        """Start editing the zones layer."""
        self._draw_handler(LAYER_ZONES)
