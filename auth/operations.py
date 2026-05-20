import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

try:
    from ..app.core.security import JWT_SECRET
    from ..app.users.service import sign_up, sign_in, logout, remove_all_layers
except ImportError:
    from app.core.security import JWT_SECRET
    from app.users.service import sign_up, sign_in, logout, remove_all_layers
