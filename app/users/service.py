"""Authentication service: sign-up, sign-in, logout, and session management."""
import logging
import jwt
import toml
from marshmallow import ValidationError

from qgis.core import QgsProject, QgsMessageLog

from ..core.security import get_jwt_secret, hash_password, verify_password
from ..core.database import get_session, get_auth_session
from ..users.models import User
from ..users.schemas import AuthSchema, SignupSchema
from ..users.repository import create_cookie
from ..shared.constants import COOKIE_FILE

logger = logging.getLogger(__name__)


def sign_up(
    username: str, password: str, affectation_id: int, phone: str,
    email: str, first_name: str, lastname: str
) -> tuple[bool, list[str] | None]:
    data = {
        "username": username,
        "first_name": first_name,
        "last_name": lastname,
        "password": password,
        "affectation_id": affectation_id,
        "email": email,
        "phone": phone,
    }
    schema = SignupSchema()
    try:
        schema.load(data)
        spatial_session = get_session()
        auth_session = get_auth_session()
        try:
            user = User(
                username=username, password=hash_password(password),
                active=True, phone=phone, email=email,
                first_name=first_name, last_name=lastname,
                affectation_id=affectation_id, api_key=""
            )
            user.save(spatial_session)
            auth_session.add(User(
                id=user.id,
                username=username, password=hash_password(password),
                active=True, phone=phone, email=email,
                first_name=first_name, last_name=lastname,
                affectation_id=affectation_id, api_key=""
            ))
            auth_session.commit()
        finally:
            spatial_session.close()
            auth_session.close()
        return True, None
    except ValidationError as err:
        error_details = [
            f"{field}: {'; '.join(messages)}"
            for field, messages in err.messages.items()
        ]
        return False, error_details


def sign_in(
    username: str, password: str,
) -> tuple[bool, str | None, str | None]:
    data = {'USERNAME': username, 'PASSWORD': password}
    schema = AuthSchema()
    try:
        schema.load(data)
        auth_session = get_auth_session()
        try:
            existing_user = (
                auth_session.query(User).filter_by(username=username).first()
            )
            if not existing_user:
                return False, None, "Username doesn't exist"
            if verify_password(password, existing_user.password):
                spatial_session = get_session()
                try:
                    spatial_user = (
                        spatial_session.query(User)
                        .filter_by(username=username).first()
                    )
                    auth_user = (
                        auth_session.query(User)
                        .filter_by(username=username).first()
                    )
                    token = jwt.encode(
                        auth_user.to_dict(), get_jwt_secret(),
                        algorithm='HS256'
                    )
                    if spatial_user:
                        spatial_user.api_key = str(token)
                        spatial_session.commit()
                    auth_user.api_key = str(token)
                    auth_session.commit()
                    create_cookie(token, auth_user.id)
                finally:
                    spatial_session.close()
                return True, auth_user.username, None
            return False, None, "Wrong password try again !"
        except Exception as e:
            QgsMessageLog.logMessage(
                f"sign_in error: {e}", 'RNA', level=2
            )
            logger.error("An error occurred: %s", e)
            auth_session.rollback()
            return False, None, str(e)
        finally:
            auth_session.close()
    except ValidationError as err:
        error_details = "; ".join(
            f"{field}: {'; '.join(messages)}"
            for field, messages in err.messages.items()
        )
        return False, None, error_details


def remove_all_layers(iface) -> None:
    project = QgsProject.instance()
    layers = project.mapLayers().values()
    for layer in layers:
        project.removeMapLayer(layer)
    iface.mapCanvas().refresh()


def logout(iface, dlg) -> None:
    filename = COOKIE_FILE

    with open(filename, 'r', encoding='utf-8') as f:
        data = toml.load(f)
    cookie = data.get('Session', {}).get('cookie', None)
    uid = data.get('Session', {}).get('uid', None)
    if cookie and uid:
        spatial_session = get_session()
        auth_session = get_auth_session()
        try:
            for sess in (spatial_session, auth_session):
                user = (
                    sess.query(User)
                    .filter(
                        User.id == uid, User.api_key == cookie,
                        User.active.is_(True)
                    )
                    .first()
                )
                if user:
                    user.api_key = None
            spatial_session.commit()
            auth_session.commit()
            data['Session']['cookie'] = None
            data['Session']['uid'] = None

            with open(filename, 'w', encoding='utf-8') as f:
                toml.dump(data, f)
        finally:
            spatial_session.close()
            auth_session.close()
        remove_all_layers(iface)
        if dlg:
            dlg.close()
