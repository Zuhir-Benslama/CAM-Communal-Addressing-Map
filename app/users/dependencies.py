"""Routing decorators: login_required for authenticated access."""

from collections.abc import Callable
from functools import wraps
from typing import Any

import toml

from ..core.database import get_session
from ..shared.constants import COOKIE_FILE
from ..users.models import User


def _navigate_to_login(self: Any) -> None:
    """Navigate to the login page if the router widget is available."""
    router = getattr(self, 'router', None)
    if router is not None:
        login_page = router.findChild(lambda w: w.objectName() == 'login')
        if login_page:
            router.setCurrentWidget(login_page)


def login_required(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator: redirect to login page if no valid session cookie exists."""

    @wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        filename = COOKIE_FILE
        try:
            with open(filename, encoding='utf-8') as f:
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
            user = (
                session.query(User)
                .filter(
                    User.id == uid,
                    User.session_token == cookie,
                    User.active.is_(True),
                )
                .first()
            )
        finally:
            session.close()

        if not user:
            _navigate_to_login(self)
            return None

        return func(self, *args, **kwargs)

    return wrapper
