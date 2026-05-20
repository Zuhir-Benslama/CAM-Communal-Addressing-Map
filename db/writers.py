import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

try:
    from ..app.orders.repository import (
        add_panel_sign, add_organization, add_road, add_numbering,
        add_subdivision, add_zone,
    )
except ImportError:
    from app.orders.repository import (
        add_panel_sign, add_organization, add_road, add_numbering,
        add_subdivision, add_zone,
    )
