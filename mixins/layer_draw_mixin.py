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

    def draw_road_handler(self) -> None:
        """Start editing the roads layer."""
        layer = QgsProject.instance().mapLayersByName(LAYER_ROADS)[0]
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
        start_editing_layer(self.iface, LAYER_ROADS)

    def draw_org_handler(self) -> None:
        """Start editing the organizations (facilities) layer."""
        layer = QgsProject.instance().mapLayersByName(LAYER_FACILITIES)[0]
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
        start_editing_layer(self.iface, LAYER_FACILITIES)

    def draw_pan_handler(self) -> None:
        """Start editing the panels layer."""
        layer = QgsProject.instance().mapLayersByName(LAYER_PANELS)[0]
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
        start_editing_layer(self.iface, LAYER_PANELS)

    def draw_city_handler(self) -> None:
        """Start editing the subdivisions layer."""
        layer = QgsProject.instance().mapLayersByName(LAYER_SUBDIVISIONS)[0]
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
        start_editing_layer(self.iface, LAYER_SUBDIVISIONS)

    def draw_num_handler(self) -> None:
        """Start editing the numbering layer."""
        layer = QgsProject.instance().mapLayersByName(LAYER_NUMBERING)[0]
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
        start_editing_layer(self.iface, LAYER_NUMBERING)

    def draw_zone_handler(self) -> None:
        """Start editing the zones layer."""
        layer = QgsProject.instance().mapLayersByName(LAYER_ZONES)[0]
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
        start_editing_layer(self.iface, LAYER_ZONES)
