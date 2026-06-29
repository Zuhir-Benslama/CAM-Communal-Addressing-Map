"""QSS theme configuration and mod_spatialite library discovery."""

import logging
import os
import subprocess
from pathlib import Path

from ..shared.constants import PLUGIN_DIR, THEME_DARK, THEME_LIGHT, Theme

logger = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(PLUGIN_DIR) / 'resources'

_COLORS = {
    'DARK_BG': '#1a1b26',
    'DARK_SURFACE': '#24253a',
    'DARK_OVERLAY': '#2f3048',
    'DARK_BORDER': '#3b3d54',
    'DARK_TEXT': '#c9d1d9',
    'DARK_TEXT_SEC': '#8b949e',
    'DARK_ACCENT': '#58a6ff',
    'DARK_ACCENT_HOVER': '#79b8ff',
    'DARK_SUCCESS': '#3fb950',
    'DARK_DANGER': '#f85149',
    'DARK_SELECTION': '#264f78',
    'LIGHT_BG': '#f6f8fa',
    'LIGHT_SURFACE': '#ffffff',
    'LIGHT_OVERLAY': '#eaeef2',
    'LIGHT_BORDER': '#d0d7de',
    'LIGHT_TEXT': '#1f2328',
    'LIGHT_TEXT_SEC': '#656d76',
    'LIGHT_ACCENT': '#0969da',
    'LIGHT_ACCENT_HOVER': '#0550ae',
    'LIGHT_SUCCESS': '#1a7f37',
    'LIGHT_DANGER': '#cf222e',
    'LIGHT_SELECTION': '#b6d4fe',
}


def _load_qss_template(filename: str) -> str:
    """Load a QSS template and replace {{VAR}} with color values."""
    path = _TEMPLATE_DIR / filename
    try:
        with open(path, encoding='utf-8') as f:
            template = f.read()
        for key, value in _COLORS.items():
            template = template.replace('{{' + key + '}}', value)
        template = template.replace('{{', '{')
        template = template.replace('}}', '}')
        return template
    except FileNotFoundError:
        logger.warning('QSS template not found: %s', path)
        return ''


DARK_QSS = _load_qss_template('dark_qss.template')
DARK_QSS_DIALOG = _load_qss_template('dark_dialog_qss.template')
LIGHT_QSS = _load_qss_template('light_qss.template')
LIGHT_QSS_DIALOG = _load_qss_template('light_dialog_qss.template')

THEMES = {
    THEME_DARK: (DARK_QSS, DARK_QSS_DIALOG),
    THEME_LIGHT: (LIGHT_QSS, LIGHT_QSS_DIALOG),
}

DEFAULT_THEME = THEME_DARK


def normalize_theme(theme_name: Theme | str | None) -> Theme:
    """Map persisted or legacy theme values to a :class:`Theme` enum."""
    if isinstance(theme_name, Theme):
        return theme_name
    if theme_name is None:
        return DEFAULT_THEME
    if isinstance(theme_name, str):
        key = theme_name.strip()
        if not key:
            return DEFAULT_THEME
        lowered = key.lower()
        if lowered in ('light', 'فاتح'):
            return THEME_LIGHT
        if lowered in ('dark', 'داكن'):
            return THEME_DARK
        try:
            return Theme(key)
        except ValueError:
            pass
    return DEFAULT_THEME


def get_theme_qss(theme_name: Theme | str | None) -> str:
    """Return the main QSS stylesheet for *theme_name*."""
    theme = normalize_theme(theme_name)
    return THEMES.get(theme, THEMES[DEFAULT_THEME])[0]


def get_dialog_qss(theme_name: Theme | str | None) -> str:
    """Return the dialog QSS stylesheet for *theme_name*."""
    theme = normalize_theme(theme_name)
    return THEMES.get(theme, THEMES[DEFAULT_THEME])[1]


def _find_in_candidate_paths(candidates: list[str]) -> str | None:
    """Return the first existing path from *candidates*, or None."""
    for p in candidates:
        if Path(p).exists():
            return p
    return None


def _find_via_ldconfig() -> str | None:
    """Locate mod_spatialite.so via ``ldconfig -p`` output."""
    try:
        result = subprocess.run(
            ['ldconfig', '-p'],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in result.stdout.splitlines():
            if 'mod_spatialite' not in line:
                continue
            parts = line.split('=>')
            if len(parts) == 2:
                path = parts[1].strip()
                if Path(path).exists():
                    return path
    except (subprocess.CalledProcessError, FileNotFoundError, PermissionError, OSError):
        logger.debug(
            'mod_spatialite not found via ldconfig',
            exc_info=True,
        )
    return None


def find_mod_spatialite_dll() -> str:
    """Locate the mod_spatialite shared library on the system."""
    env_path = os.getenv('MOD_SPATIALITE_DLL')
    if env_path:
        return env_path
    if os.name == 'nt':
        return 'mod_spatialite.dll'
    if os.uname().sysname == 'Darwin':
        return 'mod_spatialite.dylib'

    candidates = [
        '/usr/lib/spatialite50/lib/mod_spatialite.so',
        '/usr/libspatialite50/lib/mod_spatialite.so',
        '/usr/lib/spatialite/mod_spatialite.so',
        '/usr/lib/mod_spatialite.so',
        '/usr/lib64/mod_spatialite.so',
        '/usr/lib/x86_64-linux-gnu/mod_spatialite.so',
    ]
    found = _find_in_candidate_paths(candidates)
    if found:
        return found

    found = _find_via_ldconfig()
    if found:
        return found

    return 'mod_spatialite.so'
