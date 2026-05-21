"""Routing decorators: login_required for authenticated access."""
from typing import Any, Callable
from functools import wraps
import toml

from ..core.database import get_session
from ..users.models import User
from ..shared.constants import COOKIE_FILE


def _navigate_to_login(self) -> None:
    """Navigate to the login page if the router widget is available."""
    router = getattr(self, 'router', None)
    if router is not None:
        login_page = router.findChild(lambda w: w.objectName() == 'login')
        if login_page:
            router.setCurrentWidget(login_page)


def login_required(func) -> Callable:
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        filename = COOKIE_FILE
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = toml.load(f)
        except (FileNotFoundError, toml.TomlDecodeError):
            data = {}

        cookie = data.get('Session', {}).get('cookie', None)
        uid = data.get('Session', {}).get('uid', None)

        if not cookie or not uid:
            _navigate_to_login(self)
            return None

        session = get_session()
        try:
            user = session.query(User).filter(
                User.id == uid, User.api_key == cookie, User.active.is_(True)
            ).first()
        finally:
            session.close()

        if not user:
            _navigate_to_login(self)
            return None

        return func(self, *args, **kwargs)

    return wrapper
