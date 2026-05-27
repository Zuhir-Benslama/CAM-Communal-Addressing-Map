"""QSS theme configuration and mod_spatialite library discovery."""
import os
import subprocess
import logging

from ..shared.constants import THEME_DARK, THEME_LIGHT, PLUGIN_DIR

logger = logging.getLogger(__name__)

_TEMPLATE_DIR = os.path.join(PLUGIN_DIR, 'resources')

_COLORS = {
    'DARK_BG': "#1a1b26",
    'DARK_SURFACE': "#24253a",
    'DARK_OVERLAY': "#2f3048",
    'DARK_BORDER': "#3b3d54",
    'DARK_TEXT': "#c9d1d9",
    'DARK_TEXT_SEC': "#8b949e",
    'DARK_ACCENT': "#58a6ff",
    'DARK_ACCENT_HOVER': "#79b8ff",
    'DARK_SUCCESS': "#3fb950",
    'DARK_DANGER': "#f85149",
    'DARK_SELECTION': "#264f78",
    'LIGHT_BG': "#f6f8fa",
    'LIGHT_SURFACE': "#ffffff",
    'LIGHT_OVERLAY': "#eaeef2",
    'LIGHT_BORDER': "#d0d7de",
    'LIGHT_TEXT': "#1f2328",
    'LIGHT_TEXT_SEC': "#656d76",
    'LIGHT_ACCENT': "#0969da",
    'LIGHT_ACCENT_HOVER': "#0550ae",
    'LIGHT_SUCCESS': "#1a7f37",
    'LIGHT_DANGER': "#cf222e",
    'LIGHT_SELECTION': "#b6d4fe",
}


def _load_qss_template(filename: str) -> str:
    """Load a QSS template and replace {{VAR}} with color values."""
    path = os.path.join(_TEMPLATE_DIR, filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            template = f.read()
        for key, value in _COLORS.items():
            template = template.replace('{{' + key + '}}', value)
        template = template.replace('{{', '{')
        template = template.replace('}}', '}')
        return template
    except FileNotFoundError:
        logger.warning("QSS template not found: %s", path)
        return ""


DARK_QSS = _load_qss_template('dark_qss.template')
DARK_QSS_DIALOG = _load_qss_template('dark_dialog_qss.template')
LIGHT_QSS = _load_qss_template('light_qss.template')
LIGHT_QSS_DIALOG = _load_qss_template('light_dialog_qss.template')

THEMES = {
    THEME_DARK: (DARK_QSS, DARK_QSS_DIALOG),
    THEME_LIGHT: (LIGHT_QSS, LIGHT_QSS_DIALOG),
}

DEFAULT_THEME = THEME_DARK


def get_theme_qss(theme_name: str) -> str:
    return THEMES.get(theme_name, THEMES[DEFAULT_THEME])[0]  # type: ignore


def get_dialog_qss(theme_name: str) -> str:
    return THEMES.get(theme_name, THEMES[DEFAULT_THEME])[1]  # type: ignore


def _find_in_candidate_paths(candidates: list[str]) -> str | None:
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def _find_via_ldconfig() -> str | None:
    try:
        result = subprocess.run(
            ['ldconfig', '-p'], capture_output=True, text=True, check=True,
        )
        for line in result.stdout.splitlines():
            if 'mod_spatialite' not in line:
                continue
            parts = line.split('=>')
            if len(parts) == 2:
                path = parts[1].strip()
                if os.path.exists(path):
                    return path
    except (subprocess.CalledProcessError, FileNotFoundError,
            PermissionError, OSError):
        logger.debug(
            "mod_spatialite not found via ldconfig", exc_info=True,
        )
    return None


def find_mod_spatialite_dll() -> str:
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
