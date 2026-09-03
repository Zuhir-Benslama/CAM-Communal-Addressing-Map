"""Data access layer for user and session persistence."""

import json
import logging
from pathlib import Path
from typing import Any

import toml

from ..core.database import get_session
from ..shared.constants import (
    COOKIE_FILE,
    QGIS_CONFIG_FILE,
    WILAYAS_JSON,
)
from ..shared.geo import (
    find_commune_by_code,
    get_commune_wkt,
    load_communes,
)
from ..users.models import User

logger = logging.getLogger(__name__)


def _load_localites() -> list[dict[str, Any]]:
    """Load commune metadata from communes.json."""
    return load_communes()


def _get_commune_by_code(commune_code: str) -> dict[str, Any] | None:
    """Look up a commune by its commune_code (handles int/str)."""
    if not commune_code:
        return None
    return find_commune_by_code(_load_localites(), commune_code)


def load_session_cookie() -> dict[str, Any] | None:
    """Read the session cookie file; None if missing or unparsable."""
    try:
        with Path(COOKIE_FILE).open(encoding='utf-8') as f:
            return toml.load(f)
    except FileNotFoundError:
        return None
    except toml.TomlDecodeError:
        logger.warning('Corrupt session cookie file %s', COOKIE_FILE, exc_info=True)
        return None
    except OSError:
        logger.warning('Failed to read session cookie %s', COOKIE_FILE, exc_info=True)
        return None


def find_active_session_user(session: Any, uid: str, cookie: str) -> Any | None:
    """Return the active user matching a session uid/cookie pair."""
    return (
        session.query(User)
        .filter(User.id == uid, User.session_token == cookie, User.active.is_(True))
        .first()
    )


def get_current_user() -> dict | None:
    """Return authenticated user info from cookie, or None."""
    data = load_session_cookie()
    if not data:
        return None
    cookie = data.get('Session', {}).get('cookie', None)
    uid = data.get('Session', {}).get('uid', None)
    if not cookie or not uid:
        return None

    session = get_session()
    try:
        user = find_active_session_user(session, uid, cookie)
        if not user:
            return None
        commune = _get_commune_by_code(user.commune_code) if user.commune_code else None
        # Look up wilaya name
        wilaya_name = ''
        if user.wilaya_code is not None:
            try:
                with Path(WILAYAS_JSON).open(encoding='utf-8') as f:
                    wilayas = json.load(f)
                w = wilayas.get(str(user.wilaya_code))
                if w:
                    wilaya_name = w.get('wilaya_ar', '')
            except (FileNotFoundError, json.JSONDecodeError):
                logger.warning(
                    'Failed to load wilaya names from %s', WILAYAS_JSON, exc_info=True
                )
        commune_name = ''
        if commune:
            commune_name = commune.get('commune_ar') or commune.get('commune_fr') or ''
        return {
            'id': user.id,
            'commune_code': user.commune_code,
            'wilaya_code': user.wilaya_code,
            'wilaya': wilaya_name,
            'commune': commune_name,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    finally:
        session.close()


def _get_authenticated_user() -> dict[str, Any] | None:
    """Return commune info for the currently authenticated user."""
    user_data = get_current_user()
    if not user_data:
        return None
    return _get_commune_by_code(user_data.get('commune_code') or '')


def get_user_location() -> str | None:
    """Return the WKT geometry of the authenticated user's municipality."""
    commune = _get_authenticated_user()
    if not commune:
        return None
    commune_id = commune.get('commune_id')
    if not commune_id:
        return None
    return get_commune_wkt(commune_id)


def create_cookie(cookie: str, uid: str) -> None:
    """Persist a session cookie to disk (permissions 0600)."""
    data = {'Session': {'cookie': cookie, 'uid': uid}}
    filename = COOKIE_FILE
    try:
        with Path(filename).open('w', encoding='utf-8') as f:
            toml.dump(data, f)
        Path(filename).chmod(0o600)
    except (OSError, PermissionError):
        logger.exception('Failed to write cookie file %s', filename)
        raise


_qgis_config_cache = None


def reset_qgis_config_cache() -> None:
    """Clear the cached QGIS config (useful for test isolation)."""
    global _qgis_config_cache
    _qgis_config_cache = None


def qgis_config() -> dict:
    """Return the QGIS layer configuration from the JSON config file (cached)."""
    global _qgis_config_cache
    if _qgis_config_cache is not None:
        return _qgis_config_cache
    filename = QGIS_CONFIG_FILE
    try:
        with Path(filename).open(encoding='utf-8') as file:
            _qgis_config_cache = json.load(file)
            return _qgis_config_cache
    except FileNotFoundError:
        logger.exception('QGIS config file not found: %s', filename)
        raise
    except json.JSONDecodeError:
        logger.exception('Invalid JSON in config file %s', filename)
        raise
