"""
models package — SQLAlchemy models, engine, and session management.

Split into submodules for maintainability:
  base.py    — Base, engine/session functions, utilities
  user.py    — User model
  lookup.py  — (placeholder — static lookups moved to scripts.lookup_data)
  spatial.py — Spatial data models
"""

from .base import (
    Base, _allowlist_columns, find_mod_spatialite_dll,
    get_current_user, get_engine, get_session,
    get_auth_engine, get_auth_session,
    get_all_fields_and_labels,
)

from .user import User



from .spatial import (
    Localite, Zone, Subdivision, Road, Organization,
    Numbering, PanelSign,
)
