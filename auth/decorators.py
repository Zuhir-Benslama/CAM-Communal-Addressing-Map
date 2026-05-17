"""Decorators for authentication enforcement."""
from typing import Any, Callable
from functools import wraps
import toml
from ..models import get_session, User
from ..constants import COOKIE_FILE
from qgis.PyQt.QtWidgets import QWidget

def login_required(func) -> Callable:
    """Decorator to require valid login for a view."""
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        """Check cookie and redirect to login if invalid."""
        # Load the session data from the TOML file
        filename = COOKIE_FILE
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = toml.load(f)
        except FileNotFoundError:
            data = {}  # Default to empty if file not found
        except toml.TomlDecodeError:
            data = {}  # In case the TOML file is not properly formatted

        # Extract cookie and uid, defaulting to None if they don't exist
        cookie = data.get('Session', {}).get('cookie', None)
        uid = data.get('Session', {}).get('uid', None)

        if not cookie or not uid:
            # If no cookie or uid, handle accordingly (redirect to login, etc.)
            login_page = self.router.findChild(QWidget, 'login')
            if login_page:
                self.router.setCurrentWidget(login_page)
            return

        # Query the database for the user
        session = get_session()
        try:
            user = session.query(User).filter(
                User.id == uid, User.api_key == cookie, User.active == True
            ).first()
        finally:
            session.close()

        if not user:
            # If no valid user is found, redirect to login
            login_page = self.router.findChild(QWidget, 'login')
            if login_page:
                self.router.setCurrentWidget(login_page)
            return

        # If user is valid, proceed with the original function
        return func(self, *args, **kwargs)

    return wrapper
