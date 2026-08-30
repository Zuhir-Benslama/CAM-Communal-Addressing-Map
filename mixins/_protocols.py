"""Type protocols for mixin host contracts."""

# pylint: disable=too-few-public-methods
from typing import Any, Protocol, runtime_checkable

from qgis.gui import QgisInterface


@runtime_checkable
class HasTranslation(Protocol):
    """Mixin host provides translation method."""

    _tr_locale: str

    def _tr(self, source: str) -> str:
        """Translate *source* string for the current locale."""


@runtime_checkable
class HasIface(Protocol):
    """Mixin host provides QGIS interface."""

    iface: QgisInterface


@runtime_checkable
class HasCurrentLayer(Protocol):
    """Mixin host provides current layer name."""

    def _current_layer_name(self) -> str:
        """Return the name of the currently active layer."""


@runtime_checkable
class HasLayerTools(Protocol):
    """Mixin host provides map tool references."""

    identify_tool: Any
    ref_identify_tool: Any
    measure_tool: Any

    def set_default_cursor(self) -> None:
        """Reset the cursor to the default arrow cursor."""


@runtime_checkable
class HasAuthState(Protocol):
    """Mixin host provides authentication and dialog state."""

    current_user: dict[str, Any] | None
    sat_view: str | None
    rast: str | None
    popup_dialog: Any


@runtime_checkable
class HasPlanState(Protocol):
    """Mixin host provides plan export state."""

    type_plan: str
    type_to_hide: str

    def _generate_chart(self, *args: Any, **kwargs: Any) -> None:
        """Generate a chart for the current plan data."""


@runtime_checkable
class HasFeatureState(Protocol):
    """Mixin host provides feature tracking state."""

    _last_feature_wkt: str | None
    _last_feature_id: str | None
    _geometry_ready: str | None


@runtime_checkable
class HasOutputDir(Protocol):
    """Mixin host provides an output directory path."""

    _output_dir: str


# --- Domain-specific widget protocols ---


@runtime_checkable
class HasNavWidgets(Protocol):
    """Mixin host provides navigation widgets (menu, router)."""

    menu: Any
    router: Any


@runtime_checkable
class HasMapOptionWidgets(Protocol):
    """Mixin host provides map option selector widget."""

    map_options: Any


@runtime_checkable
class HasLocationWidgets(Protocol):
    """Mixin host provides wilaya/commune location selector widgets."""

    wilaya_list: Any
    commune_of_wilaya: Any


@runtime_checkable
class HasCategoryWidgets(Protocol):
    """Mixin host provides category/type selector widgets."""

    org_cat: Any
    org_type: Any
    activity_cat: Any
    activity_type: Any


@runtime_checkable
class HasRefWidgets(Protocol):
    """Mixin host provides reference selector widgets."""

    road_ref: Any
    panel_ref: Any


@runtime_checkable
class HasFormWidgets(Protocol):
    """Mixin host provides form input and combo widgets."""

    num_val: Any
    paper: Any
    mount_status: Any
    nom_zone: Any
    num_state: Any
    org_name: Any
    repetition: Any
    road_name: Any
    subd_name: Any
    subd_type: Any
    type_road: Any
    zone_type: Any


@runtime_checkable
class HasAuthFormWidgets(Protocol):
    """Mixin host provides authentication form input widgets."""

    uname: Any
    pwd: Any
    email: Any
    fname: Any
    lname: Any
    pnum: Any
    username: Any
    password: Any
    label_username: Any


@runtime_checkable
class HasUiWidgets(
    HasNavWidgets,
    HasMapOptionWidgets,
    HasLocationWidgets,
    HasCategoryWidgets,
    HasRefWidgets,
    HasFormWidgets,
    HasAuthFormWidgets,
    Protocol,
):
    """Backward-compatible union of all domain-specific widget protocols."""

    def _select_ref(self, *args: Any, **kwargs: Any) -> None:
        """Open reference selection tool for a combo box."""


@runtime_checkable
class HasDrawSignals(Protocol):
    """Mixin host provides drawing signal handlers."""

    def on_feature_added(self, *args: Any, **kwargs: Any) -> None:
        """Handle the feature-added signal from a layer."""

    def on_geometry_changed(self, *args: Any, **kwargs: Any) -> None:
        """Handle the geometry-changed signal from a layer."""

    def on_edition_release(self, *args: Any, **kwargs: Any) -> None:
        """Handle the edit context menu release signal."""

    def _reconnect_context_menu(self) -> None:
        """Re-connect the custom context menu handler."""

    def _draw_handler(self, *args: Any, **kwargs: Any) -> None:
        """Activate drawing mode for a specific layer."""

    def _update_handler(self, *args: Any, **kwargs: Any) -> None:
        """Activate geometry update mode for a specific layer."""


@runtime_checkable
class HasExportMethods(Protocol):
    """Mixin host provides export-related methods."""

    def north(self) -> bool:
        """Export a north arrow SVG; True only on success."""

    def scale(self) -> bool:
        """Export a scale bar SVG; True only on success."""

    def map_situation(self) -> bool:
        """Export a situation map PNG; True only on success."""

    def symbols(self) -> str | None:
        """Render legend symbols on the layout."""

    def _render_and_export(self, *args: Any, **kwargs: Any) -> None:
        """Export the current map layout to an image file."""


@runtime_checkable
class UiForm(Protocol):
    """Type stub for dynamically loaded Qt UI forms (setupUi)."""

    def setupUi(self, obj: object) -> None:
        """Set up the UI on the given parent object."""


# --- Combined protocols ---


@runtime_checkable
class HasDrawContext(HasIface, HasDrawSignals, HasCurrentLayer, Protocol):
    """Mixin host needed for draw operations (iface + signals + layer)."""


@runtime_checkable
class HasBasicEditContext(
    HasUiWidgets,
    HasFeatureState,
    HasTranslation,
    Protocol,
):
    """Mixin host needed for basic entity editing."""


@runtime_checkable
class HasFullEditContext(
    HasBasicEditContext,
    HasLayerTools,
    HasDrawSignals,
    Protocol,
):
    """Mixin host needed for full entity editing with ref tools."""


@runtime_checkable
class HasChartContext(HasTranslation, HasIface, HasPlanState, Protocol):
    """Mixin host needed for chart operations."""


@runtime_checkable
class HasExportContext(
    HasTranslation,
    HasPlanState,
    HasIface,
    HasAuthState,
    HasExportMethods,
    HasUiWidgets,
    HasOutputDir,
    Protocol,
):
    """Mixin host needed for export operations."""


@runtime_checkable
class HasReportContext(HasAuthState, HasTranslation, HasOutputDir, Protocol):
    """Mixin host needed for report generation."""


@runtime_checkable
class HasLayerOpsContext(
    HasIface,
    HasDrawSignals,
    HasFeatureState,
    HasUiWidgets,
    HasCurrentLayer,
    Protocol,
):
    """Mixin host for layer ops feature-add signal."""

    def _current_ops_layer(self) -> str:
        """Return the currently selected layer name."""

    def _check_geometry_in_zone(self, geometry_wkt: str) -> int:
        """Check if geometry is within the user's allowed zone."""


@runtime_checkable
class HasTabSwitchContext(
    HasPlanState,
    HasUiWidgets,
    HasIface,
    HasLayerTools,
    HasAuthState,
    Protocol,
):
    """Mixin host for tab switching operations."""

    def _reset_tools(self) -> None:
        """Deactivate all active map tools and clear measurements."""

    def _current_ops_layer(self) -> str:
        """Return the currently selected operation layer name."""

    def _show_layers_for_label(
        self,
        root: Any,
        layer_label: str,
    ) -> None:
        """Show the selected operation layer and dependencies."""

    def _hide_all_tab_layers(self, root: Any) -> None:
        """Rollback editable layers and hide all."""

    def _load_tab_styles(self, data_list: Any, style_dir: str) -> None:
        """Load named styles for each layer in the config list."""

    _last_loaded_tab: str | None


@runtime_checkable
class HasGeometryChangedContext(HasIface, HasTranslation, Protocol):
    """Mixin host for geometry change handling."""

    def _check_geometry_in_zone(self, geometry_wkt: str) -> int:
        """Check if geometry is within the user's allowed zone."""


@runtime_checkable
class HasAuthIfaceContext(HasAuthState, HasIface, Protocol):
    """Mixin host for auth + iface operations."""


@runtime_checkable
class HasSymbolPlanContext(HasPlanState, HasAuthState, Protocol):
    """Mixin host for symbol plan export operations."""


@runtime_checkable
class HasSymbolMapContext(HasAuthState, HasIface, Protocol):
    """Mixin host for symbol map situation operations."""


@runtime_checkable
class HasScaleContext(HasIface, HasTranslation, Protocol):
    """Mixin host for scale bar operations."""


@runtime_checkable
class HasMapToolsContext(HasIface, HasLayerTools, Protocol):
    """Mixin host for map tool operations."""


@runtime_checkable
class HasFullMapToolsContext(
    HasIface,
    HasLayerTools,
    HasTranslation,
    HasUiWidgets,
    Protocol,
):
    """Mixin host for full map tool operations with ref selection."""


@runtime_checkable
class HasSelectContext(
    HasCurrentLayer,
    HasIface,
    HasTranslation,
    Protocol,
):
    """Mixin host for layer selection operations."""


@runtime_checkable
class HasAuthContext(HasUiWidgets, HasTranslation, Protocol):
    """Mixin host for basic auth UI operations (signup form)."""

    def public_route(self, page_index: Any) -> None:
        """Navigate to a public (login/register) page."""


@runtime_checkable
class HasFullAuthContext(
    HasIface,
    HasAuthState,
    HasLayerTools,
    HasUiWidgets,
    HasTranslation,
    Protocol,
):
    """Mixin host for full auth operations (login, map layer, close)."""

    def add_map_layer(self) -> bool:
        """Add the selected raster or WMS map layer to the project."""

    def _add_satellite_layer(self, label: str, url: str) -> bool:
        """Add a satellite WMS layer to the project."""

    def _add_raster_file(self, label: str) -> bool:
        """Add a raster file to the project as a map layer."""

    def private_route(self, page_index: Any) -> None:
        """Navigate to a private (authenticated) page."""

    def on_opt_selected(self, index: Any) -> None:
        """Handle tab selection: toggle layer visibility and load styles."""

    def stop(self) -> None:
        """Deactivate all active map tools and clear measurements."""

    def _show_error(self, text: str) -> None:
        """Show a critical error message dialog."""

    def disconnect_map_canvas(self) -> None:
        """Detach from the singleton map canvas before unload."""

    def _restore_layout_direction(self) -> None:
        """Restore the application layout direction at dialog close."""
