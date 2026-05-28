"""Type protocols for mixin host contracts."""
# pylint: disable=too-few-public-methods
from typing import Protocol, runtime_checkable, Any, Optional, Dict

from qgis.gui import QgisInterface


@runtime_checkable
class HasTranslation(Protocol):
    """Mixin host provides translation method."""
    def _tr(self, source: str) -> str:
        """Translate *source* string for the current locale."""
        ...


@runtime_checkable
class HasIface(Protocol):
    """Mixin host provides QGIS interface."""
    iface: QgisInterface


@runtime_checkable
class HasCurrentLayer(Protocol):
    """Mixin host provides current layer name."""
    def _current_layer_name(self) -> str:
        """Return the name of the currently active layer."""
        ...


@runtime_checkable
class HasLayerTools(Protocol):
    """Mixin host provides map tool references."""
    identify_tool: Any
    ref_identify_tool: Any
    measure_tool: Any


@runtime_checkable
class HasAuthState(Protocol):
    """Mixin host provides authentication state."""
    current_user: Optional[Dict[str, Any]]
    sat_view: Optional[str]
    rast: Optional[str]


@runtime_checkable
class HasPlanState(Protocol):
    """Mixin host provides plan export state."""
    type_plan: str
    type_to_hide: str
    def _generate_chart(self, *args: Any, **kwargs: Any) -> None:
        """Generate a chart for the current plan data."""
        ...


@runtime_checkable
class HasFeatureState(Protocol):
    """Mixin host provides feature tracking state."""
    _last_feature_wkt: Optional[str]
    _last_feature_pkuid: Optional[str]
    _geometry_ready: Optional[str]
    update_object: Dict[str, Any]


@runtime_checkable
class HasUiWidgets(Protocol):
    """Mixin host provides UI widget references (broadest contract)."""
    menu: Any
    router: Any
    num_val: Any
    ref_name: Any
    road_ref: Any
    panel_ref: Any
    paper: Any
    dateEdit: Any
    lineEdit_by: Any
    lineEdit_type: Any
    lineEdit_nummokh: Any
    map_options: Any
    wilaya_list: Any
    commune_of_wilaya: Any
    org_cat: Any
    org_type: Any
    activity_cat: Any
    activity_type: Any
    def _select_ref(self, *args: Any, **kwargs: Any) -> None:
        """Open reference selection tool for a combo box."""
        ...


@runtime_checkable
class HasDrawSignals(Protocol):
    """Mixin host provides drawing signal handlers."""
    def on_feature_added(self, *args: Any, **kwargs: Any) -> None:
        """Handle the feature-added signal from a layer."""
        ...
    def on_geometry_changed(self, *args: Any, **kwargs: Any) -> None:
        """Handle the geometry-changed signal from a layer."""
        ...
    def on_edition_release(self, *args: Any, **kwargs: Any) -> None:
        """Handle the edit context menu release signal."""
        ...
    def _reconnect_context_menu(self) -> None:
        """Re-connect the custom context menu handler."""
        ...
    def _draw_handler(self, *args: Any, **kwargs: Any) -> None:
        """Activate drawing mode for a specific layer."""
        ...
    def _update_handler(self, *args: Any, **kwargs: Any) -> None:
        """Activate geometry update mode for a specific layer."""
        ...


@runtime_checkable
class HasExportMethods(Protocol):
    """Mixin host provides export-related methods."""
    def north(self) -> None:
        """Render a north arrow on the layout."""
        ...
    def scale(self) -> None:
        """Render a scale bar on the layout."""
        ...
    def map_situation(self) -> None:
        """Render a situation map on the layout."""
        ...
    def symbols(self) -> None:
        """Render legend symbols on the layout."""
        ...
    def _render_and_export(self, *args: Any, **kwargs: Any) -> None:
        """Export the current map layout to an image file."""
        ...


@runtime_checkable
class UiForm(Protocol):
    """Type stub for dynamically loaded Qt UI forms (setupUi)."""
    def setupUi(self, obj: object) -> None:
        """Set up the UI on the given parent object."""
        ...


# --- Combined protocols (replaces unsupported `A & B` syntax) ---

@runtime_checkable
class HasDrawContext(HasIface, HasDrawSignals, Protocol):
    """Mixin host needed for draw operations."""


@runtime_checkable
class HasBasicEditContext(
    HasUiWidgets, HasFeatureState, HasTranslation, Protocol,
):
    """Mixin host needed for basic entity editing."""


@runtime_checkable
class HasFullEditContext(
    HasBasicEditContext, HasLayerTools, HasDrawSignals, Protocol,
):
    """Mixin host needed for full entity editing with ref tools."""


@runtime_checkable
class HasChartContext(HasTranslation, HasPlanState, Protocol):
    """Mixin host needed for chart operations."""


@runtime_checkable
class HasExportContext(
    HasTranslation, HasPlanState, HasIface, HasAuthState,
    HasExportMethods, HasUiWidgets, Protocol,
):
    """Mixin host needed for export operations."""


@runtime_checkable
class HasLayerOpsContext(
    HasIface, HasDrawSignals, HasFeatureState,
    HasUiWidgets, HasCurrentLayer, Protocol,
):
    """Mixin host for layer ops feature-add signal."""


@runtime_checkable
class HasTabSwitchContext(
    HasPlanState, HasUiWidgets, HasIface,
    HasLayerTools, HasAuthState, Protocol,
):
    """Mixin host for tab switching operations."""


@runtime_checkable
class HasGeometryChangedContext(HasIface, HasTranslation, Protocol):
    """Mixin host for geometry change handling."""


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
    HasIface, HasLayerTools, HasTranslation, HasUiWidgets, Protocol,
):
    """Mixin host for full map tool operations with ref selection."""


@runtime_checkable
class HasSelectContext(
    HasCurrentLayer, HasIface, HasTranslation, Protocol,
):
    """Mixin host for layer selection operations."""


@runtime_checkable
class HasAuthContext(HasUiWidgets, HasTranslation, Protocol):
    """Mixin host for basic auth UI operations."""


@runtime_checkable
class HasAuthMapContext(
    HasUiWidgets, HasTranslation, HasAuthState, Protocol,
):
    """Mixin host for auth map layer operations."""


@runtime_checkable
class HasLoginContext(
    HasUiWidgets, HasIface, HasAuthState, HasTranslation, Protocol,
):
    """Mixin host for login flow operations."""


@runtime_checkable
class HasCloseContext(
    HasIface, HasAuthState, HasLayerTools, HasUiWidgets, Protocol,
):
    """Mixin host for close event operations."""


@runtime_checkable
class HasRefSelectContext(
    HasIface, HasLayerTools, HasTranslation, Protocol,
):
    """Mixin host for reference selection operations."""
