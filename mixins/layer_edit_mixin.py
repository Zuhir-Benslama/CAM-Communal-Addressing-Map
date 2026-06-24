"""Layer editing mixin for adding and updating features via forms."""
# mypy: disable-error-code="attr-defined"

from __future__ import annotations

import contextlib
import logging
from typing import Any

from qgis.core import QgsProject
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QMessageBox
from sqlalchemy.exc import SQLAlchemyError

from ..app.orders.repository import (
    add_numbering,
    add_organization,
    add_panel_sign,
    add_road,
    add_subdivision,
    add_zone,
)
from ..constants import (
    LAYER_FACILITIES,
    LAYER_NUMBERING,
    LAYER_PANELS,
    LAYER_ROADS,
    LAYER_SUBDIVISIONS,
    LAYER_ZONES,
    current_locale,
    validate_text,
)
from ..layer.editing import update_layer
from ._protocols import (
    HasBasicEditContext,
    HasDrawContext,
    HasFeatureState,
    HasFullEditContext,
    HasTranslation,
)

logger = logging.getLogger(__name__)


class LayerEditMixin:
    """Mixin for updating layer geometries and adding features via forms.

    Cross-mixin protocol (attributes set by map_tools_mixin or owning dialog):
        _last_feature_wkt (str | None) — WKT geometry of last created feature
        _last_feature_id (str | None) — PK of last created feature
        _geometry_ready (str | None) — layer name of last drawn geometry
        ref_identify_tool (IdentifyTool | None) — ref selection tool
        measure_tool (MeasureTool | None) — measurement line tool
        update_object (bool) — flag for edit-vs-insert mode
        num_val / repetition / road_name / road_decision / org_name
        / subd_name / nom_zone
        org_cat / org_type / type_road / subd_type / zone_type / num_state
        / mount_status
        activity_cat / activity_type (QComboBox)
    """

    def _update_handler(
        self: HasDrawContext,
        layer_name: str,
    ) -> None:
        """Enable geometry editing for a named layer."""
        layers = QgsProject.instance().mapLayersByName(layer_name)
        if not layers:
            return
        layer = layers[0]
        with contextlib.suppress(TypeError):
            layer.geometryChanged.disconnect(self.on_geometry_changed)
        layer.geometryChanged.connect(self.on_geometry_changed)
        update_layer(self.iface, layer_name)

    def start_editing(self: HasDrawContext) -> None:
        """Enable geometry editing on the currently selected layer."""
        self._update_handler(self._current_layer_name())

    def _get_geometry_and_id(
        self: HasFeatureState, entity_name: str
    ) -> tuple[Any, Any]:
        """Retrieve the captured geometry WKT and feature PK."""
        geometry_wkt = getattr(self, '_last_feature_wkt', None)
        feature_id = getattr(self, '_last_feature_id', None)
        if not geometry_wkt or not feature_id:
            logger.warning(
                'No geometry or id available for %s',
                entity_name,
            )
            return None, None
        return geometry_wkt, feature_id

    def _show_success(self: HasTranslation, message: str) -> None:
        """Show a success information dialog."""
        QMessageBox.information(
            self,
            self._tr('Success'),
            self._tr(message),
        )

    def _show_error(self: HasTranslation, message: str) -> None:
        """Show a critical error dialog."""
        QMessageBox.critical(self, self._tr('Error'), self._tr(message))

    def _make_locale_kwargs(self, field_base: str, value: str) -> dict:
        """Build locale-specific field kwargs for non-Arabic locales."""
        loc = current_locale()
        if loc != 'ar':
            return {f'{field_base}_{loc}': value}
        return {}

    def add_panel(
        self: HasFullEditContext,
    ) -> None:
        """Add a new panel sign linked to a selected road, org, or
        subdivision."""
        if self._geometry_ready != LAYER_PANELS:
            return
        if self.update_object:
            return
        ref_data = self.ref_identify_tool.get_id()
        if ref_data is None:
            logger.warning('No object selected for panel reference')
            return
        geometry_wkt, feature_id = self._get_geometry_and_id('panel')
        if not geometry_wkt or not feature_id:
            return
        try:
            layer = ref_data.get('layer_name')
            ref = ref_data.get('id')
            kwargs = {
                'geometry_wkt': geometry_wkt,
                'record_id': feature_id,
                'mount_status': self.mount_status.currentData(),
            }
            if layer == LAYER_FACILITIES:
                add_panel_sign(
                    **kwargs, road_id=None, subdivision_id=None, organization_id=ref
                )
            elif layer == LAYER_ROADS:
                add_panel_sign(
                    **kwargs, road_id=ref, subdivision_id=None, organization_id=None
                )
            elif layer == LAYER_SUBDIVISIONS:
                add_panel_sign(
                    **kwargs, road_id=None, subdivision_id=ref, organization_id=None
                )

            if self.measure_tool:
                self.show_confirm_dialog(
                    title=self._tr('Success'),
                    message=self._tr(
                        'Panel added successfully\n'
                        ' Do you want to clear the measurement line?'
                    ),
                    yes_callback=self.measure_tool.clear,
                )
            else:
                self._show_success('Panel added successfully')
        except (SQLAlchemyError, TypeError, AttributeError, ValueError) as e:
            logger.exception('Failed to add panel: %s', e)
            self._show_error(str(e))
        finally:
            self.ref_identify_tool.unset_map_tool()
            self._draw_handler(LAYER_PANELS)

    def add_organization(
        self: HasBasicEditContext,
    ) -> None:
        """Add a new organization through the form."""
        if self._geometry_ready != LAYER_FACILITIES:
            return
        geometry_wkt, feature_id = self._get_geometry_and_id('organization')
        if not geometry_wkt or not feature_id:
            return
        try:
            name_val = validate_text(self.org_name.text())
            kwargs = {
                'geometry_wkt': geometry_wkt,
                'record_id': feature_id,
                'org_cat': self.org_cat.currentData(),
                'org_name': name_val,
                'org_type': self.org_type.currentData(),
            }
            kwargs.update(self._make_locale_kwargs('org_name', name_val))
            add_organization(**kwargs)
            self._show_success('Facility added successfully')
        except SQLAlchemyError as e:
            logger.exception('Failed to add organization: %s', e)
            self._show_error('Cannot add facility, it already exists')

    def add_road(
        self: HasBasicEditContext,
    ) -> None:
        """Add a new road through the form."""
        if self._geometry_ready != LAYER_ROADS:
            return
        geometry_wkt, feature_id = self._get_geometry_and_id('road')
        if not geometry_wkt or not feature_id:
            return
        try:
            name_val = validate_text(self.road_name.text())
            kwargs = {
                'geometry_wkt': geometry_wkt,
                'record_id': feature_id,
                'road_decision': None,
                'road_name': name_val,
                'type_road': self.type_road.currentData(),
            }
            kwargs.update(self._make_locale_kwargs('road_name', name_val))
            add_road(**kwargs)
            self._show_success('Road added successfully')
        except SQLAlchemyError as e:
            logger.exception('Failed to add road: %s', e)
            self._show_error('Cannot add road, it already exists')

    def key_press_event(self, event: Any, action: str = 'add_numbering') -> None:
        """Handle Enter key press to trigger the given action."""
        if event.key() == Qt.Key.Key_Return:
            getattr(self, action)()

    def show_confirm_dialog(
        self: HasTranslation,
        title: str,
        message: str,
        yes_callback: Any = None,
        no_callback: Any = None,
    ) -> bool:
        """Display a confirmation dialog with yes/no callbacks."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        yes_button = msg_box.button(QMessageBox.Yes)
        no_button = msg_box.button(QMessageBox.No)
        yes_button.setText(self._tr('Yes'))
        no_button.setText(self._tr('No'))

        result = msg_box.exec()

        if result == QMessageBox.Yes:
            if yes_callback:
                yes_callback()
            return True
        if no_callback:
            no_callback()
        return False

    def add_numbering(
        self: HasFullEditContext,
    ) -> None:
        """Add a new numbering linked to a selected road or subdivision."""
        if self._geometry_ready != LAYER_NUMBERING:
            return
        geometry_wkt, feature_id = self._get_geometry_and_id('numbering')
        if not geometry_wkt or not feature_id:
            return
        try:
            ref_data = self.ref_identify_tool.get_id()
        except (TypeError, AttributeError) as e:
            logger.warning('Failed to get id from identify tool: %s', e)
            ref_data = None
        try:
            common = {
                'geometry_wkt': geometry_wkt,
                'record_id': feature_id,
                'repetition': validate_text(self.repetition.text()),
                'value': validate_text(self.num_val.text()),
                'state': self.num_state.currentData(),
                'activity_cat': self.activity_cat.currentData(),
                'activity_type': self.activity_type.currentData(),
            }
            if ref_data and ref_data.get('layer_name') == LAYER_ROADS:
                add_numbering(
                    **common,
                    road_id=ref_data.get('id'),
                    subdivision_id=None,
                )
            elif ref_data and ref_data.get('layer_name') == LAYER_SUBDIVISIONS:
                add_numbering(
                    **common,
                    road_id=None,
                    subdivision_id=ref_data.get('id'),
                )

            if self.measure_tool:
                self.show_confirm_dialog(
                    title=self._tr('Success'),
                    message=self._tr(
                        'Numbering added successfully\n'
                        ' Do you want to clear the measurement line?'
                    ),
                    yes_callback=self.measure_tool.clear,
                )
            else:
                self._show_success('Numbering added successfully')
        except (SQLAlchemyError, TypeError, AttributeError, ValueError) as e:
            logger.exception('Failed to add numbering: %s', e)
            self._show_error(str(e))

        self.num_val.setFocus()
        self.num_val.clear()
        self._draw_handler(LAYER_NUMBERING)

    def add_city(
        self: HasBasicEditContext,
    ) -> None:
        """Add a new subdivision through the form."""
        if self._geometry_ready != LAYER_SUBDIVISIONS:
            return
        geometry_wkt, feature_id = self._get_geometry_and_id('subdivision')
        if not geometry_wkt or not feature_id:
            return
        try:
            name_val = validate_text(self.subd_name.text())
            kwargs = {
                'geometry_wkt': geometry_wkt,
                'record_id': feature_id,
                'name': name_val,
                'subdivision_type': self.subd_type.currentData(),
            }
            kwargs.update(self._make_locale_kwargs('name', name_val))
            add_subdivision(**kwargs)
            self._show_success('Subdivision added successfully')
        except SQLAlchemyError as e:
            logger.exception('Failed to add city: %s', e)
            self._show_error(str(e))

    def add_zone(
        self: HasBasicEditContext,
    ) -> None:
        """Add a new zone through the form."""
        if self._geometry_ready != LAYER_ZONES:
            return
        if self.update_object:
            return
        geometry_wkt, feature_id = self._get_geometry_and_id('zone')
        if not geometry_wkt or not feature_id:
            return
        try:
            name_val = validate_text(self.nom_zone.text())
            kwargs = {
                'geometry_wkt': geometry_wkt,
                'record_id': feature_id,
                'name': name_val,
                'zone_type': self.zone_type.currentData(),
            }
            kwargs.update(self._make_locale_kwargs('name', name_val))
            add_zone(**kwargs)
            self._show_success('Zone added successfully')
        except SQLAlchemyError as e:
            logger.exception('Failed to add zone: %s', e)
            self._show_error('Cannot add zone, zone already exists')
