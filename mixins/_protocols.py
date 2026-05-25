"""Type protocols for mixin host contracts."""
from typing import Protocol, runtime_checkable, Any, Optional, Dict

from qgis.gui import QgisInterface


@runtime_checkable
class HasTranslation(Protocol):
    """Mixin host provides translation method."""
    def _tr(self, source: str) -> str: ...


@runtime_checkable
class HasIface(Protocol):
    """Mixin host provides QGIS interface."""
    iface: QgisInterface


@runtime_checkable
class HasCurrentLayer(Protocol):
    """Mixin host provides current layer name."""
    def _current_layer_name(self) -> str: ...


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


@runtime_checkable
class HasFeatureState(Protocol):
    """Mixin host provides feature tracking state."""
    _last_feature_wkt: Optional[str]
    _last_feature_pkuid: Optional[str]
    update_object: Dict[str, Any]


@runtime_checkable
class HasUiWidgets(Protocol):
    """Mixin host provides UI widget references (broadest contract)."""
    menu: Any
    router: Any
    num_val: Any
    is_pan: Any
    is_org: Any
    is_road: Any
    is_num: Any
    is_city: Any
    is_zone: Any
    ref_name: Any
    road_ref: Any
    panel_ref: Any
    paper: Any
    dateEdit: Any
    lineEdit_by: Any
    lineEdit_type: Any
    lineEdit_nummokh: Any


@runtime_checkable
class HasDrawSignals(Protocol):
    """Mixin host provides drawing signal handlers."""
    def on_feature_added(self, *args: Any, **kwargs: Any) -> None: ...
    def on_geometry_changed(self, *args: Any, **kwargs: Any) -> None: ...
    def on_edition_release(self, *args: Any, **kwargs: Any) -> None: ...
    def _reconnect_context_menu(self) -> None: ...
    def _draw_handler(self, *args: Any, **kwargs: Any) -> None: ...


@runtime_checkable
class HasExportMethods(Protocol):
    """Mixin host provides export-related methods."""
    def north(self) -> None: ...
    def scale(self) -> None: ...
    def map_situation(self) -> None: ...
    def symbols(self) -> None: ...


@runtime_checkable
class UiForm(Protocol):
    """Type stub for dynamically loaded Qt UI forms (setupUi)."""
    def setupUi(self, obj: object) -> None: ...
