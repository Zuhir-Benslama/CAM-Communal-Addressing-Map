from typing import Any, Callable
from functools import wraps
import toml

from ..core.database import get_session
from ..users.models import User
from ..shared.constants import COOKIE_FILE
from qgis.PyQt.QtWidgets import QWidget


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
            login_page = self.router.findChild(QWidget, 'login')
            if login_page:
                self.router.setCurrentWidget(login_page)
            return

        session = get_session()
        try:
            user = session.query(User).filter(
                User.id == uid, User.api_key == cookie, User.active == True
            ).first()
        finally:
            session.close()

        if not user:
            login_page = self.router.findChild(QWidget, 'login')
            if login_page:
                self.router.setCurrentWidget(login_page)
            return

        return func(self, *args, **kwargs)

    return wrapper
