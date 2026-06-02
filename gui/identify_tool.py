"""Map identify tool for feature selection and editing."""

import enum
import logging
from typing import Any

from qgis.core import QgsExpression, QgsFeatureRequest
from qgis.gui import QgsMapToolIdentify
from qgis.PyQt.QtCore import Qt, pyqtSignal
from qgis.PyQt.QtWidgets import QMenu

from ..app.core.database import get_session
from ..app.orders import models as _models
from ..app.users.repository import qgis_config
from ..constants import LAYER_KEY, current_locale
from ..scripts.lookup_data import get_string

logger = logging.getLogger(__name__)


class IdentifyMode(enum.Enum):
    FORM = 'form'
    REF = 'ref'


class IdentifyTool(QgsMapToolIdentify):
    """Map tool for identifying features and editing/deleting them."""

    MODE_FORM = IdentifyMode.FORM
    MODE_REF = IdentifyMode.REF

    ref_selected = pyqtSignal(object, str)

    def __init__(self, canvas, mode=MODE_FORM) -> None:
        super().__init__(canvas)
        self.canvas = canvas
        self._active_layer = None
        self._iface = None
        self.mode = mode

        self.dlg: Any = None
        if mode == self.MODE_REF:
            self.feature_id = None
            self.feature_type = None
            self.feature_name = None
            self.ref_name = None

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

    def get_id(self) -> dict:
        """Return the selected feature's PK and layer name."""
        return {'id': self.feature_id, 'layer_name': self.get_active_layer().name()}

    def canvasReleaseEvent(self, event) -> None:
        """Handle map canvas click: identify feature under the cursor."""
        if event.button() == Qt.MouseButton.LeftButton:
            _ = self.toMapCoordinates(event.pos())

            results = self.identify(
                event.x(),
                event.y(),
                [self.get_active_layer()],
                QgsMapToolIdentify.TopDownAll,
            )

            if results:
                for result in results:
                    feature = result.mFeature

                    menu = QMenu()
                    if self.mode == self.MODE_FORM:
                        form_action = menu.addAction(
                            get_string('View or Update Form', current_locale())
                        )
                        form_action.triggered.connect(
                            lambda f=feature: self.display_or_update_form_feature(
                                f['id']
                            )
                        )

                        remove_action = menu.addAction(
                            get_string('Remove Item', current_locale())
                        )
                        remove_action.triggered.connect(
                            lambda f=feature: self.delete_feature(f['id'])
                        )
                    else:
                        name_locale = self._locale_feature_attr(feature, 'name')
                        type_locale = self._locale_feature_attr(feature, 'type')
                        ref_action = menu.addAction(
                            get_string('Set Item as Reference', current_locale())
                        )
                        ref_action.triggered.connect(
                            lambda f=feature, t=type_locale, n=name_locale: (
                                self.feature_as_ref(
                                    f['id'],
                                    t,
                                    n,
                                )
                            )
                        )

                    menu.exec_(event.globalPos())
                    break
            else:
                logger.info('No features identified at this location.')

        elif event.button() == Qt.MouseButton.RightButton:
            self.canvas.unsetMapTool(self)

    def unset_map_tool(self) -> None:
        """Unset this identify tool from the canvas."""
        self.canvas.unsetMapTool(self)

    def display_or_update_form_feature(self, feature_id) -> None:
        """Open the popup dialog for the identified feature."""
        from .popup_dialog import PopupDialog  # pylint: disable=import-outside-toplevel

        layer_name = self.get_active_layer().name()
        layer_map = LAYER_KEY
        if self.dlg:
            self.dlg.close()
            self.dlg = None

        self.dlg = PopupDialog(
            layer_name_value=layer_map.get(layer_name),
            iface=self.get_iface(),
            layer_name_key=layer_name,
            attribute=feature_id,
        )
        self.dlg.show()
        self.dlg.exec()

    def delete_feature(self, feature_id) -> None:
        """Delete the identified feature from DB and map layer."""
        layer_name = self.get_active_layer().name()
        data_list = qgis_config().get('mapper') or []
        for data in data_list:
            if data.get('layer') == layer_name:
                session = get_session()
                try:
                    model_name = data.get('model')
                    model = getattr(_models, model_name, None)
                    if model is None:
                        logger.warning('Unknown model: %s', model_name)
                        return

                    query = session.query(model).filter(model.id == feature_id).first()

                    if query:
                        query.delete(session)
                finally:
                    session.close()

                request = QgsFeatureRequest().setFilterExpression(
                    f'"id" = {QgsExpression.quotedValue(feature_id)}'
                )
                layer = self.get_active_layer()
                layer.startEditing()
                features_to_remove = layer.getFeatures(request)
                for feature in features_to_remove:
                    layer.deleteFeature(feature.id())

                layer.commitChanges()
                layer.triggerRepaint()

        self.canvas.refresh()

    def _locale_feature_attr(self, feature, base_name: str) -> str:
        """Read locale-appropriate attribute from a QGIS feature."""
        loc = current_locale()
        if loc != 'ar':
            locale_field = f'{base_name}_{loc}'
            if locale_field in feature.fields().names():
                locale_val = feature[locale_field]
                if locale_val:
                    return str(locale_val)
        return str(feature[base_name]) if feature[base_name] else ''

    def feature_as_ref(self, feature_id, feature_type, feature_name) -> None:
        """Store the selected feature as a reference for another entity."""
        self.feature_id = feature_id
        self.feature_type = feature_type
        self.feature_name = feature_name
        if self.feature_id:
            layer = self.get_active_layer()
            layer_name = layer.name() if layer else ''
            self.ref_selected.emit(self.feature_id, layer_name)
            self.canvas.unsetMapTool(self)
