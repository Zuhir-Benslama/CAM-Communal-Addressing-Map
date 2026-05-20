import sys as _sys
import os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))

try:
    from ..app.users.schemas import AuthSchema, SignupSchema
except ImportError:
    from app.users.schemas import AuthSchema, SignupSchema
