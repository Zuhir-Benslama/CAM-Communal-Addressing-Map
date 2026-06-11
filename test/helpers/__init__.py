"""Test helpers — shared utilities for mock setup.

Re-exports all public helpers so existing
``from test.helpers import ...`` imports keep working.
"""

from ._core_mocks import setup_mocks
from ._gui_mocks import setup_gui_mocks
from ._shared import (
    _mirror_app_modules,
    _mock_constants_base,
    _mock_model_table,
    _qt_widgets_module,
    _setup_package_tree,
    get_qapp,
    get_qt_widget_class,
    make_mock_iface,
    make_mock_layer,
    wire_module_attributes,
)
