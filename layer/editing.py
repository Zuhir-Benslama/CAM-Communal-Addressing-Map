"""Vector layer editing and update operations."""
import logging

from qgis.core import QgsProject, QgsMapLayer, QgsWkbTypes, Qgis

from ..constants import NOTIFY_DURATION

logger = logging.getLogger(__name__)


def _activate_add_feature(iface, layer) -> None:
    """Enable editing and activate the add-feature tool for a vector layer."""
    layer.startEditing()
    geometry_type = layer.geometryType()

    messages = {
        QgsWkbTypes.PointGeometry: (
            "Capture Point activé pour la couche vectorielle sélectionnée."),
        QgsWkbTypes.LineGeometry: (
            "Capture Line activé pour la couche vectorielle sélectionnée."),
        QgsWkbTypes.PolygonGeometry: (
            "Capture Polygon activé pour la couche vectorielle sélectionnée."),
    }

    msg = messages.get(geometry_type)
    if msg:
        iface.actionAddFeature().trigger()
        iface.messageBar().pushMessage(
            "Info", msg, level=Qgis.Info, duration=NOTIFY_DURATION
        )
    else:
        iface.messageBar().pushMessage(
            "Erreur", "Type de géométrie non pris en charge.",
            level=Qgis.Critical, duration=NOTIFY_DURATION
        )


def edit_line_layer(iface) -> None:
    """Enable editing and add feature tool on the active layer."""
    active_layer = iface.activeLayer()

    if active_layer and active_layer.type() == QgsMapLayer.VectorLayer:
        _activate_add_feature(iface, active_layer)
    else:
        iface.messageBar().pushMessage(
            "Erreur", "Aucune couche vectorielle active.",
            level=Qgis.Critical, duration=NOTIFY_DURATION
        )


def save_changes(iface) -> None:
    """Commit pending edits on the active vector layer."""
    layer = iface.activeLayer()
    if not layer or layer.type() != QgsMapLayer.VectorLayer:
        iface.messageBar().pushMessage(
            "Erreur",
            "Aucune couche vectorielle active "
            "pour enregistrer les modifications.",
            level=Qgis.Critical, duration=NOTIFY_DURATION
        )
        return

    if not layer.isEditable():
        iface.messageBar().pushMessage(
            "Info", "La couche n'est pas en mode édition.",
            level=Qgis.Warning, duration=NOTIFY_DURATION
        )
        return

    if layer.commitChanges():
        iface.messageBar().pushMessage(
            "Info", "Modifications enregistrées avec succès.",
            level=Qgis.Info, duration=NOTIFY_DURATION
        )
    else:
        iface.messageBar().pushMessage(
            "Erreur", "Échec de l'enregistrement des modifications.",
            level=Qgis.Critical, duration=NOTIFY_DURATION
        )


def start_editing_layer(iface, layer_name) -> None:
    """Start editing mode on a named layer and activate add feature tool."""
    layers = QgsProject.instance().mapLayersByName(layer_name)
    if not layers:
        iface.messageBar().pushMessage(
            "Erreur", f"Aucune couche trouvée avec le nom '{layer_name}'.",
            level=Qgis.Critical, duration=NOTIFY_DURATION
        )
        return

    layer = layers[0]
    if layer.type() == QgsMapLayer.VectorLayer:
        iface.setActiveLayer(layer)
        _activate_add_feature(iface, layer)
    else:
        iface.messageBar().pushMessage(
            "Erreur", "La couche spécifiée n'est pas une couche vectorielle.",
            level=Qgis.Critical, duration=NOTIFY_DURATION
        )


def stop_editing_layer(iface, layer_name) -> None:
    """Stop editing and commit changes on a named layer."""
    layers = QgsProject.instance().mapLayersByName(layer_name)
    if not layers:
        iface.messageBar().pushMessage(
            "Erreur", f"Aucune couche trouvée avec le nom '{layer_name}'.",
            level=Qgis.Critical, duration=NOTIFY_DURATION
        )
        return

    layer = layers[0]
    if layer.type() == QgsMapLayer.VectorLayer:
        if layer.isEditable():
            iface.setActiveLayer(layer)
            if layer.commitChanges():
                iface.messageBar().pushMessage(
                    "Info", f"Édition arrêtée pour la couche : {layer.name()}.",
                    level=Qgis.Info, duration=NOTIFY_DURATION
                )
            else:
                iface.messageBar().pushMessage(
                    "Erreur",
                    f"Impossible d'arrêter l'édition "
                    f"pour la couche : {layer.name()}.",
                    level=Qgis.Critical, duration=NOTIFY_DURATION
                )
        else:
            iface.messageBar().pushMessage(
                "Info", f"La couche {layer.name()} n'est pas en mode édition.",
                level=Qgis.Warning, duration=NOTIFY_DURATION
            )
    else:
        iface.messageBar().pushMessage(
            "Erreur",
            f"La couche {layer.name()} n'est pas une couche vectorielle.",
            level=Qgis.Critical, duration=NOTIFY_DURATION
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
        logger.warning("Vertex tool action not available.")
