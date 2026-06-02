"""Authentication service: sign-up, sign-in, logout, and session management."""

import json
import logging
import os
import tempfile

import jwt
import toml
from marshmallow import ValidationError
from qgis.core import QgsMessageLog, QgsProject

from ..core.database import get_session
from ..core.security import get_jwt_secret, hash_password, verify_password
from ..shared.constants import COMMUNES_JSON, COOKIE_FILE, DAIRA_JSON
from ..users.models import User
from ..users.repository import create_cookie
from ..users.schemas import AuthSchema, SignupSchema

logger = logging.getLogger(__name__)


def _lookup_wilaya_code(commune_code: str) -> int | None:
    """Resolve wilaya_code from commune_code using communes/daira JSON."""
    try:
        with open(COMMUNES_JSON, encoding='utf-8') as f:
            communes = json.load(f)
        with open(DAIRA_JSON, encoding='utf-8') as f:
            dairas = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    code = int(commune_code) if commune_code else None
    if code is None:
        return None
    for c in communes.values():
        v = c.get('commune_code')
        if v is not None and int(v) == code:
            daira = dairas.get(str(c.get('daira_id')))
            if daira:
                return int(daira.get('wilaya_id', 0))
            break
    return None


def sign_up(
    *,
    username: str,
    password: str,
    commune_code: str,
    phone: str,
    email: str,
    first_name: str,
    lastname: str,
) -> tuple[bool, list[str] | None]:
    """Register a new user. Returns (success, error_details_or_None)."""
    signup_data = {
        'username': username,
        'first_name': first_name,
        'last_name': lastname,
        'password': password,
        'commune_code': commune_code,
        'email': email,
        'phone': phone,
    }
    schema = SignupSchema()
    try:
        schema.load(signup_data)
        wilaya_code = _lookup_wilaya_code(commune_code)

        session = get_session()
        try:
            user = User(
                username=username,
                password=hash_password(password),
                active=True,
                phone=phone,
                email=email,
                first_name=first_name,
                last_name=lastname,
                commune_code=commune_code,
                wilaya_code=wilaya_code,
                api_key='',
            )
            session.add(user)
            session.commit()
        except Exception:  # pylint: disable=W0718
            session.rollback()
            raise
        finally:
            session.close()
        return True, None
    except ValidationError as err:
        error_details = [
            f'{field}: {"; ".join(messages)}'
            for field, messages in err.messages.items()
        ]
        return False, error_details


def sign_in(
    username: str,
    password: str,
) -> tuple[bool, str | None, str | None]:
    """Authenticate a user. Returns (success, username_or_None, error_or_None)."""
    credentials = {'USERNAME': username, 'PASSWORD': password}
    schema = AuthSchema()
    try:
        schema.load(credentials)
        session = get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                return False, None, "Username doesn't exist"
            if not verify_password(password, user.password):
                return False, None, 'Wrong password try again !'
            token = jwt.encode(user.to_dict(), get_jwt_secret(), algorithm='HS256')
            user.api_key = str(token)
            session.commit()
            create_cookie(token, user.id)
            return True, user.username, None
        except Exception as e:  # pylint: disable=W0718
            session.rollback()
            QgsMessageLog.logMessage(f'sign_in error: {e}', 'RNA', level=2)
            logger.error('An error occurred: %s', e)
            return False, None, str(e)
        finally:
            session.close()
    except ValidationError as err:
        error_details = '; '.join(
            f'{field}: {"; ".join(messages)}'
            for field, messages in err.messages.items()
        )
        return False, None, error_details


def remove_all_layers(iface) -> None:
    """Remove all layers from the QGIS project and refresh the canvas."""
    project = QgsProject.instance()
    layers = project.mapLayers().values()
    for layer in layers:
        project.removeMapLayer(layer)
    iface.mapCanvas().refresh()


def logout(iface, dlg) -> None:
    """Clear session cookie, revoke API key, remove layers, and close dialog."""
    filename = COOKIE_FILE

    with open(filename, encoding='utf-8') as f:
        cookie_data = toml.load(f)
    cookie = cookie_data.get('Session', {}).get('cookie', None)
    uid = cookie_data.get('Session', {}).get('uid', None)
    if cookie and uid:
        session = get_session()
        try:
            user = (
                session.query(User)
                .filter(User.id == uid, User.api_key == cookie, User.active.is_(True))
                .first()
            )
            if user:
                user.api_key = None
            session.commit()
            cookie_data['Session']['cookie'] = None
            cookie_data['Session']['uid'] = None

            fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(filename) or '.')
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    toml.dump(cookie_data, f)
                os.replace(tmp_path, filename)
            except Exception:
                os.unlink(tmp_path)
                raise
        finally:
            session.close()
        remove_all_layers(iface)
        if dlg:
            dlg.close()
