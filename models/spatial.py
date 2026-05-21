"""models/spatial.py re-exports."""
# pylint: disable=unused-import
try:
    from RNA.app.orders.models import (
        Localite, Zone, Road, Organization,
        Subdivision, Numbering, PanelSign,
    )
except ImportError:
    from plans_adressage.app.orders.models import (
        Localite, Zone, Road, Organization,
        Subdivision, Numbering, PanelSign,
    )
