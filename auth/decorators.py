"""auth/decorators.py re-exports."""
# pylint: disable=unused-import
try:
    from RNA.app.users.dependencies import login_required
except ImportError:
    from plans_adressage.app.users.dependencies import login_required
