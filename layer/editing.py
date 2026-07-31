"""Vector layer editing and update operations."""

import logging
from typing import Any

from qgis.core import Qgis, QgsMapLayer, QgsProject, QgsWkbTypes

from ..constants import NOTIFY_DURATION, current_locale
from ..scripts.widget_texts import get_string

logger = logging.getLogger(__name__)


def _activate_add_feature(iface: Any, layer: Any) -> None:
    """Enable editing and activate the add-feature tool for a vector layer."""
    layer.startEditing()
    geometry_type = layer.geometryType()

    loc = current_locale()
    messages = {
        QgsWkbTypes.PointGeometry: get_string(
            'Capture Point activated for selected vector layer.', loc
        ),
        QgsWkbTypes.LineGeometry: get_string(
            'Capture Line activated for selected vector layer.', loc
        ),
        QgsWkbTypes.PolygonGeometry: get_string(
            'Capture Polygon activated for selected vector layer.', loc
        ),
    }

    msg = messages.get(geometry_type)
    if msg:
        iface.actionAddFeature().trigger()
        iface.messageBar().pushMessage(
            get_string('Info', loc), msg, level=Qgis.Info, duration=NOTIFY_DURATION
        )
    else:
        iface.messageBar().pushMessage(
            get_string('Error', loc),
            get_string('Unsupported geometry type.', loc),
            level=Qgis.Critical,
            duration=NOTIFY_DURATION,
        )


def start_editing_layer(iface: Any, layer_name: str) -> None:
    """Start editing mode on a named layer and activate add feature tool."""
    loc = current_locale()
    layers = QgsProject.instance().mapLayersByName(layer_name)
    if not layers:
        iface.messageBar().pushMessage(
            get_string('Error', loc),
            get_string('No layer found with the name', loc) + f" '{layer_name}'.",
            level=Qgis.Critical,
            duration=NOTIFY_DURATION,
        )
        return

    layer = layers[0]
    if layer.type() == QgsMapLayer.VectorLayer:
        iface.setActiveLayer(layer)
        _activate_add_feature(iface, layer)
    else:
        iface.messageBar().pushMessage(
            get_string('Error', loc),
            get_string('Unsupported geometry type.', loc),
            level=Qgis.Critical,
            duration=NOTIFY_DURATION,
        )


def update_layer(iface: Any, layer_name: str) -> None:
    """Enable vertex tool on a named layer for geometry editing."""
    layers = QgsProject.instance().mapLayersByName(layer_name)

    if not layers:
        logger.warning("Layer '%s' not found.", layer_name)
        return

    layer = layers[0]
    iface.setActiveLayer(layer)

    if layer.type() != QgsMapLayer.VectorLayer:
        return

    if not layer.isEditable():
        layer.startEditing()

    iface.mapCanvas().refresh()

    vertex_tool_action = iface.actionVertexTool()

    if vertex_tool_action:
        vertex_tool_action.trigger()
        iface.mapCanvas().refreshAllLayers()
    else:
        logger.warning('Vertex tool action not available.')
