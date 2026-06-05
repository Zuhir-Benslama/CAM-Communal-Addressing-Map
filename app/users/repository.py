"""Data access layer for user and session persistence."""

import json
import logging
import os
import sqlite3
from typing import Any

import toml

from ..core.database import get_session
from ..shared.constants import (
    COMMUNES_DB,
    COMMUNES_JSON,
    COOKIE_FILE,
    QGIS_CONFIG_FILE,
    WILAYAS_JSON,
)
from ..users.models import User

logger = logging.getLogger(__name__)


def _load_localites() -> list[dict[str, Any]]:
    """Load commune metadata from communes.json."""
    try:
        with open(COMMUNES_JSON, encoding='utf-8') as f:
            return list(json.load(f).values())
    except (FileNotFoundError, json.JSONDecodeError):
        logger.error('Failed to load %s', COMMUNES_JSON)
        return []


def _get_commune_by_id(commune_id: int) -> dict[str, Any] | None:
    """Look up a commune by its commune_id."""
    data = _load_localites()
    for c in data:
        if int(c.get('commune_id', 0)) == commune_id:
            return c
    return None


def _get_commune_by_code(commune_code: str) -> dict[str, Any] | None:
    """Look up a commune by its commune_code (handles int/str)."""
    if not commune_code:
        return None
    try:
        code = int(commune_code)
    except (ValueError, TypeError):
        return None
    for c in _load_localites():
        v = c.get('commune_code')
        if v is not None and int(v) == code:
            return c
    return None


def get_current_user() -> dict | None:
    """Return authenticated user info from cookie, or None."""
    filename = COOKIE_FILE
    try:
        with open(filename, encoding='utf-8') as f:
            data = toml.load(f)
    except (FileNotFoundError, toml.TomlDecodeError):
        return None
    cookie = data.get('Session', {}).get('cookie', None)
    uid = data.get('Session', {}).get('uid', None)
    if not cookie or not uid:
        return None

    session = get_session()
    try:
        user = (
            session.query(User)
            .filter(User.id == uid, User.session_token == cookie, User.active.is_(True))
            .first()
        )
        if not user:
            return None
        commune = _get_commune_by_code(user.commune_code) if user.commune_code else None
        # Look up wilaya name
        wilaya_name = ''
        if user.wilaya_code is not None:
            try:
                with open(WILAYAS_JSON, encoding='utf-8') as f:
                    wilayas = json.load(f)
                w = wilayas.get(str(user.wilaya_code))
                if w:
                    wilaya_name = w.get('wilaya_ar', '')
            except (FileNotFoundError, json.JSONDecodeError):
                pass
        return {
            'id': user.id,
            'commune_code': user.commune_code,
            'wilaya_code': user.wilaya_code,
            'wilaya': wilaya_name,
            'commune': commune['commune_ar'] if commune else '',
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
    user_data = get_current_user()
    if not user_data:
        return None
    commune_code = user_data.get('commune_code')
    if not commune_code:
        return None

    # Find commune_id from commune_code
    commune_id = None
    for c in _load_localites():
        v = c.get('commune_code')
        if v is not None and int(v) == int(commune_code):
            commune_id = int(c.get('commune_id', 0))
            break
    if commune_id is None:
        return None

    try:
        with sqlite3.connect(COMMUNES_DB) as conn:
            sql = 'SELECT wkt FROM geometries WHERE commune_id = ?'
            cur = conn.execute(sql, (commune_id,))
            row = cur.fetchone()
            if row:
                return row[0]
    except sqlite3.Error:
        logger.error('Failed to query %s', COMMUNES_DB)
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
        logger.error('Failed to write cookie file %s: %s', filename, e)
        raise


_qgis_config_cache = None


def qgis_config() -> dict:
    """Return the QGIS layer configuration from the JSON config file (cached)."""
    global _qgis_config_cache
    if _qgis_config_cache is not None:
        return _qgis_config_cache
    filename = QGIS_CONFIG_FILE
    try:
        with open(filename, encoding='utf-8') as file:
            _qgis_config_cache = json.load(file)
            return _qgis_config_cache
    except FileNotFoundError:
        logger.error('QGIS config file not found: %s', filename)
        raise
    except json.JSONDecodeError as e:
        logger.error('Invalid JSON in config file %s: %s', filename, e)
        raise
