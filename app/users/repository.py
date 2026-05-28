"""Data access layer for user and session persistence."""
import json
import logging
import os
from typing import Any, Optional

import toml

from sqlalchemy import func

from ..shared.constants import COOKIE_FILE, QGIS_CONFIG_FILE
from ..core.database import get_session
from ..users.models import User

logger = logging.getLogger(__name__)


def get_current_user() -> Optional[dict]:
    """Return authenticated user info from cookie, or None."""
    from ..orders.models import Localite
    filename = COOKIE_FILE
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = toml.load(f)
    except (FileNotFoundError, toml.TomlDecodeError):
        return None
    cookie = data.get('Session', {}).get('cookie', None)
    uid = data.get('Session', {}).get('uid', None)
    if not cookie or not uid:
        return None

    session = get_session()
    try:
        user = session.query(User).filter(
            User.id == uid, User.api_key == cookie, User.active.is_(True)
        ).first()
        if not user:
            return None
        localite = (
            session.query(Localite)
            .filter(Localite.id == user.affectation_id)
            .first()
        )
        if not localite:
            return None
        return {
            'id': user.id,
            'loc': user.affectation_id,
            'wilaya': localite.wilaya,
            'commune': localite.commune_ar
        }
    finally:
        session.close()


def _get_authenticated_user() -> Any:
    """Return the Localite record for the currently authenticated user."""
    from ..orders.models import Localite
    user_data = get_current_user()
    if not user_data:
        return None
    session = get_session()
    try:
        return session.query(Localite).filter(
            Localite.id == user_data['loc']
        ).first()
    finally:
        session.close()


def get_user_location() -> Any:
    """Return the WKT geometry of the authenticated user's municipality."""
    result = _get_authenticated_user()
    if result:
        session = get_session()
        try:
            row = session.query(func.ST_AsText(result.geometry)).first()
            wkt = str(row[0])
            return wkt
        finally:
            session.close()
    return None


def create_cookie(cookie: str, uid: str) -> None:
    """Persist a session cookie to disk (permissions 0600)."""
    data = {'Session': {'cookie': cookie, 'uid': uid}}
    filename = COOKIE_FILE
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            toml.dump(data, f)
        os.chmod(filename, 0o600)
    except (OSError, PermissionError) as e:
        logger.error("Failed to write cookie file %s: %s", filename, e)
        raise


_qgis_config_cache = None


def qgis_config() -> dict:
    """Return the QGIS layer configuration from the JSON config file (cached)."""
    global _qgis_config_cache
    if _qgis_config_cache is not None:
        return _qgis_config_cache
    filename = QGIS_CONFIG_FILE
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            _qgis_config_cache = json.load(file)
            return _qgis_config_cache
    except FileNotFoundError:
        logger.error("QGIS config file not found: %s", filename)
        raise
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in config file %s: %s", filename, e)
        raise
