"""models/user.py re-exports."""
# pylint: disable=unused-import
try:
    from RNA.app.users.models import User
except ImportError:
    from plans_adressage.app.users.models import User
