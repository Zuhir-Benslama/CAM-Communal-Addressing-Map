import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

try:
    from ..app.users.dependencies import login_required
except ImportError:
    from app.users.dependencies import login_required
