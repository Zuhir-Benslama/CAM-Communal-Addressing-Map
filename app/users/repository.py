"""Data access layer for user and session persistence."""
import json
import logging
import os
from typing import Any, Optional

import toml

from geoalchemy2 import WKTElement
from ..shared.constants import COOKIE_FILE, QGIS_CONFIG_FILE, LOCALITES_JSON, LOCALITE_GEOJSON, SRID
from ..core.database import get_session
from ..users.models import User

logger = logging.getLogger(__name__)


def _load_localites() -> list[dict[str, Any]]:
    """Load commune metadata from JSON file."""
    try:
        with open(LOCALITES_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.error("Failed to load %s", LOCALITES_JSON)
        return []


def _load_localite_geojson() -> dict[str, Any]:
    """Load commune geometries from GeoJSON file."""
    try:
        with open(LOCALITE_GEOJSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.error("Failed to load %s", LOCALITE_GEOJSON)
        return {"type": "FeatureCollection", "features": []}


def _get_commune_by_id(commune_id: int) -> Optional[dict[str, Any]]:
    """Look up a commune by its old localite.id."""
    for c in _load_localites():
        if c["id"] == commune_id:
            return c
    return None


def _get_commune_by_code(commune_code: str) -> Optional[dict[str, Any]]:
    """Look up a commune by its commune_code."""
    for c in _load_localites():
        if c["commune_code"] == commune_code:
            return c
    return None


def get_current_user() -> Optional[dict]:
    """Return authenticated user info from cookie, or None."""
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
        commune = _get_commune_by_code(user.commune_code) if user.commune_code else None
        return {
            'id': user.id,
            'commune_code': user.commune_code,
            'wilaya_code': user.wilaya_code,
            'wilaya': commune['wilaya'] if commune else '',
            'commune': commune['commune_ar'] if commune else '',
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    finally:
        session.close()


def _get_authenticated_user() -> Optional[dict[str, Any]]:
    """Return commune info for the currently authenticated user."""
    user_data = get_current_user()
    if not user_data:
        return None
    return _get_commune_by_code(user_data.get('commune_code') or '')


def get_user_location() -> Optional[str]:
    """Return the WKT geometry of the authenticated user's municipality."""
    user_data = get_current_user()
    if not user_data:
        return None
    commune_code = user_data.get('commune_code')
    if not commune_code:
        return None

    fc = _load_localite_geojson()
    for feature in fc.get('features', []):
        if feature.get('properties', {}).get('commune_code') == commune_code:
            geom = feature.get('geometry')
            if geom:
                # Convert GeoJSON geometry to WKT
                geom_type = geom.get('type', '')
                coords = geom.get('coordinates', [])
                wkt = _geojson_to_wkt(geom_type, coords)
                return wkt
    return None


def _geojson_to_wkt(geom_type: str, coords: list) -> str:
    """Convert a GeoJSON geometry to WKT string."""
    if geom_type == 'MultiPolygon':
        parts = []
        for polygon in coords:
            rings = []
            for ring in polygon:
                pts = ', '.join(f'{p[0]} {p[1]}' for p in ring)
                rings.append(f'({pts})')
            parts.append('(' + ', '.join(rings) + ')')
        return f'MULTIPOLYGON ({", ".join(parts)})'
    elif geom_type == 'Polygon':
        rings = []
        for ring in coords:
            pts = ', '.join(f'{p[0]} {p[1]}' for p in ring)
            rings.append(f'({pts})')
        return f'POLYGON ({", ".join(rings)})'
    elif geom_type == 'MultiLineString':
        parts = []
        for line in coords:
            pts = ', '.join(f'{p[0]} {p[1]}' for p in line)
            parts.append(f'({pts})')
        return f'MULTILINESTRING ({", ".join(parts)})'
    elif geom_type == 'LineString':
        pts = ', '.join(f'{p[0]} {p[1]}' for p in coords)
        return f'LINESTRING ({pts})'
    elif geom_type == 'MultiPoint':
        pts = ', '.join(f'{p[0]} {p[1]}' for p in coords)
        return f'MULTIPOINT ({pts})'
    elif geom_type == 'Point':
        return f'POINT ({coords[0]} {coords[1]})'
    return ''


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
