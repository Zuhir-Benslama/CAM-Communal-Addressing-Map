"""Map identify tool for feature selection and editing."""
from typing import Any
from qgis.PyQt.QtCore import Qt
from qgis.gui import QgsMapToolIdentify
from qgis.core import QgsExpression, QgsFeatureRequest
from qgis.PyQt.QtWidgets import QMenu
from .. import models as _models
from ..constants import LAYER_KEY
from ..db.operations import qgis_config
from ..models import get_session
import logging
logger = logging.getLogger(__name__)


class IdentifyTool(QgsMapToolIdentify):
    """Map tool for identifying features and editing/deleting them."""

    MODE_FORM = "form"
    MODE_REF = "ref"

    def __init__(self, canvas, mode=MODE_FORM) -> None:
        super().__init__(canvas)
        self.canvas = canvas
        self._active_layer = None
        self._iface = None
        self.mode = mode

        if mode == self.MODE_REF:
            self.pkuid = None
            self.type = None
            self.nom = None
            self.ref_name = None
        else:
            self.dlg = None

    def set_active_layer(self, layer) -> None:
        """Set the active layer to identify features on."""
        self._active_layer = layer

    def get_active_layer(self) -> Any:
        """Return the currently active identify layer."""
        return self._active_layer

    def set_iface(self, iface) -> None:
        """Set the QGIS interface instance."""
        self._iface = iface

    def get_iface(self) -> Any:
        """Return the QGIS interface instance."""
        return self._iface

    def set_ref_name(self, ref_name) -> None:
        """Set the reference name widget for ref mode."""
        self.ref_name = ref_name

    def get_pkuid(self) -> dict:
        """Return the selected feature's PK and layer name."""
        return {
            "pkuid": self.pkuid,
            "layer_name": self.get_active_layer().name()
        }

    def canvasReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            _ = self.toMapCoordinates(event.pos())

            results = self.identify(
                event.x(), event.y(), [self.get_active_layer()],
                QgsMapToolIdentify.TopDownAll
            )

            if results:
                for result in results:
                    feature = result.mFeature

                    menu = QMenu()
                    if self.mode == self.MODE_FORM:
                        action1 = menu.addAction(
                            "\u0639\u0631\u0636"
                            " \u0627\u0644\u0646\u0645\u0648\u0630\u062c"
                            " \u0623\u0648 \u062a\u062d\u062f\u064a\u062b\u0647"
                        )
                        action1.triggered.connect(
                            lambda: self.display_or_update_form_feature(
                                feature['pkuid'])
                        )

                        action2 = menu.addAction(
                            "\u0625\u0632\u0627\u0644\u0629"
                            " \u0627\u0644\u0639\u0646\u0635\u0631"
                        )
                        action2.triggered.connect(
                            lambda: self.delete_feature(feature['pkuid'])
                        )
                    else:
                        action1 = menu.addAction(
                            "\u062a\u0639\u064a\u064a\u0646"
                            " \u0627\u0644\u0639\u0646\u0635\u0631"
                            " \u0643\u0645\u0631\u062c\u0639"
                        )
                        action1.triggered.connect(
                            lambda: self.feature_as_ref(
                                feature['pkuid'],
                                feature['Type'],
                                feature['Nom'],
                            )
                        )

                    menu.exec_(event.globalPos())
                    break
            else:
                logger.info("No features identified at this location.")

        elif event.button() == Qt.RightButton:
            self.canvas.unsetMapTool(self)

    def unset_map_tool(self) -> None:
        """Unset this identify tool from the canvas."""
        self.canvas.unsetMapTool(self)

    def display_or_update_form_feature(self, feature_id) -> None:
        """Open the popup dialog for the identified feature."""
        from .popup_dialog import PopupDialog
        layer_name = self.get_active_layer().name()
        map = LAYER_KEY
        if self.dlg:
            self.dlg.close()
            self.dlg = None

        self.dlg = PopupDialog(
            layer_name_value=map.get(layer_name), iface=self.get_iface(),
            layer_name_key=layer_name, attribute=feature_id
        )
        self.dlg.show()
        self.dlg.exec_()

    def delete_feature(self, feature_id) -> None:
        """Delete the identified feature from DB and map layer."""
        layer_name = self.get_active_layer().name()
        data_list = qgis_config().get('mapper')
        for data in data_list:
            if data.get('layer') == layer_name:
                session = get_session()
                try:
                    model_name = data.get('model')
                    model = getattr(_models, model_name, None)
                    if model is None:
                        logger.warning("Unknown model: %s", model_name)
                        return

                    query = session.query(model).filter(
                        getattr(model, 'pkuid') == feature_id
                    ).first()

                    if query:
                        query.delete(session)
                finally:
                    session.close()

                request = QgsFeatureRequest().setFilterExpression(
                    f'"pkuid" = {QgsExpression.quotedValue(feature_id)}'
                )
                layer = self.get_active_layer()
                layer.startEditing()
                features_to_remove = layer.getFeatures(request)
                for feature in features_to_remove:
                    layer.deleteFeature(feature.id())

                layer.commitChanges()
                layer.triggerRepaint()

        self.canvas.refresh()

    def feature_as_ref(self, feature_pkuid, feature_type, feature_nom) -> None:
        """Store the selected feature as a reference for another entity."""
        self.pkuid = feature_pkuid
        self.type = feature_type
        self.nom = feature_nom
        if self.pkuid:
            self.ref_name.setText(f"\u200F{self.type} \u200F{self.nom}")
            self.canvas.unsetMapTool(self)
