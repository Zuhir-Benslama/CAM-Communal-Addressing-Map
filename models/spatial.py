import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

try:
    from ..app.orders.models import (
        Localite, Zone, Subdivision, Road, Organization,
        Numbering, PanelSign,
    )
except ImportError:
    from app.orders.models import (
        Localite, Zone, Subdivision, Road, Organization,
        Numbering, PanelSign,
    )
