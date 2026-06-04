"""Vector layer editing and update operations."""

import logging

from qgis.core import Qgis, QgsMapLayer, QgsProject, QgsWkbTypes

from ..constants import NOTIFY_DURATION, current_locale
from ..scripts.widget_texts import get_string

logger = logging.getLogger(__name__)


def _activate_add_feature(iface, layer) -> None:
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


def edit_line_layer(iface) -> None:
    """Enable editing and add feature tool on the active layer."""
    active_layer = iface.activeLayer()

    if active_layer and active_layer.type() == QgsMapLayer.VectorLayer:
        _activate_add_feature(iface, active_layer)
    else:
        loc = current_locale()
        iface.messageBar().pushMessage(
            get_string('Error', loc),
            get_string('No active vector layer.', loc),
            level=Qgis.Critical,
            duration=NOTIFY_DURATION,
        )


def save_changes(iface) -> None:
    """Commit pending edits on the active vector layer."""
    loc = current_locale()
    layer = iface.activeLayer()
    if not layer or layer.type() != QgsMapLayer.VectorLayer:
        iface.messageBar().pushMessage(
            get_string('Error', loc),
            get_string('No active vector layer to save changes.', loc),
            level=Qgis.Critical,
            duration=NOTIFY_DURATION,
        )
        return

    if not layer.isEditable():
        iface.messageBar().pushMessage(
            get_string('Info', loc),
            get_string('Layer is not in edit mode.', loc),
            level=Qgis.Warning,
            duration=NOTIFY_DURATION,
        )
        return

    if layer.commitChanges():
        iface.messageBar().pushMessage(
            get_string('Info', loc),
            get_string('Changes saved successfully.', loc),
            level=Qgis.Info,
            duration=NOTIFY_DURATION,
        )
    else:
        iface.messageBar().pushMessage(
            get_string('Error', loc),
            get_string('Failed to save changes.', loc),
            level=Qgis.Critical,
            duration=NOTIFY_DURATION,
        )


def start_editing_layer(iface, layer_name) -> None:
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


def stop_editing_layer(iface, layer_name) -> None:
    """Stop editing and commit changes on a named layer."""
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
        if layer.isEditable():
            iface.setActiveLayer(layer)
            if layer.commitChanges():
                iface.messageBar().pushMessage(
                    get_string('Info', loc),
                    get_string('Edit stopped for layer', loc) + f' {layer.name()}.',
                    level=Qgis.Info,
                    duration=NOTIFY_DURATION,
                )
            else:
                iface.messageBar().pushMessage(
                    get_string('Error', loc),
                    get_string('Cannot stop editing for layer', loc)
                    + f' {layer.name()}.',
                    level=Qgis.Critical,
                    duration=NOTIFY_DURATION,
                )
        else:
            iface.messageBar().pushMessage(
                get_string('Info', loc),
                get_string('Layer is not in edit mode.', loc) + f' {layer.name()}',
                level=Qgis.Warning,
                duration=NOTIFY_DURATION,
            )
    else:
        iface.messageBar().pushMessage(
            get_string('Error', loc),
            get_string('No active vector layer.', loc),
            level=Qgis.Critical,
            duration=NOTIFY_DURATION,
        )


def update_layer(iface, layer_name) -> None:
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
