"""Authentication operations: sign up, sign in, logout."""
import jwt
import toml
import os
import logging

from marshmallow import ValidationError

from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsProject, QgsMessageLog

from ..db.operations import create_cookie, hash_password, verify_password
from ..models import User, get_session, get_auth_session
from ..db.schema import AuthSchema, SignupSchema
from ..constants import COOKIE_FILE, current_theme, get_theme_qss

logger = logging.getLogger(__name__)

JWT_SECRET = os.getenv(
    'RNA_JWT_SECRET', 'change-me-in-production-rna-default-secret'
)


def sign_up(
    username: str, password: str, affectation_id: int, phone: str,
    email: str, first_name: str, lastname: str
) -> bool:
    """Register a new user in both spatial and auth databases.
    Returns True on success, False on validation error.
    """
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
        return True
    except ValidationError as err:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet(get_theme_qss(current_theme()))
        error_details = "".join(
            f"{field}: {'; '.join(messages)}\n"
            for field, messages in err.messages.items()
        )
        msg.setInformativeText(error_details)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        return False


def sign_in(username: str, password: str, label) -> bool:
    """Authenticate a user and create a session cookie."""
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
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Error")
                msg.setStyleSheet(get_theme_qss(current_theme()))
                msg.setInformativeText("Username doesn't exist")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
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
                            auth_user.to_dict(), JWT_SECRET,
                            algorithm='HS256'
                        )
                        if spatial_user:
                            spatial_user.api_key = str(token)
                            spatial_session.commit()
                        auth_user.api_key = str(token)
                        auth_session.commit()
                        label.setText(auth_user.username)
                        create_cookie(token, auth_user.id)
                    finally:
                        spatial_session.close()
                    return True
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Error")
                msg.setStyleSheet(get_theme_qss(current_theme()))
                msg.setInformativeText("Wrong password try again !")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
        except Exception as e:
            QgsMessageLog.logMessage(
                f"sign_in error: {e}", 'RNA', level=2
            )
            logger.error("An error occurred: %s", e)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Error")
            msg.setStyleSheet(get_theme_qss(current_theme()))
            msg.setInformativeText(str(e))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            auth_session.rollback()
        finally:
            auth_session.close()
    except ValidationError as err:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        error_details = "".join(
            f"{field}: {'; '.join(messages)}\n"
            for field, messages in err.messages.items()
        )
        msg.setInformativeText(error_details)
        msg.setStyleSheet(get_theme_qss(current_theme()))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    return False


def remove_all_layers(iface) -> None:
    """Remove all map layers from the QGIS project."""
    project = QgsProject.instance()
    layers = project.mapLayers().values()
    for layer in layers:
        project.removeMapLayer(layer)
    iface.mapCanvas().refresh()


def logout(iface, dlg) -> None:
    """Log out the current user, clear session, and close the dialog."""
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
                        User.active is True
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
