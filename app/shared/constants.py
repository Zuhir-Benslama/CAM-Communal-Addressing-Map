"""Shared constants: paths, layer names, enums, and settings keys."""

import os
from enum import Enum

PLUGIN_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)

SRID = 4326
CRS = f'EPSG:{SRID}'

COOKIE_FILE = os.path.join(PLUGIN_DIR, 'data', 'cookie.toml')
DATABASE_FILE = os.path.join(PLUGIN_DIR, 'data', 'database.sqlite')
AUTH_DATABASE_FILE = os.path.join(PLUGIN_DIR, 'data', 'auth.sqlite')
QGIS_CONFIG_FILE = os.path.join(PLUGIN_DIR, 'data', 'qgis_config.json')
STYLE_QML = os.path.join(PLUGIN_DIR, 'style', 'style.qml')
DEFAULT_STYLE_DIR = os.path.join(PLUGIN_DIR, 'style', 'default')
CUSTOM_STYLE_DIR = os.path.join(PLUGIN_DIR, 'style', 'customized')
TEMPLATE_REP = os.path.join(PLUGIN_DIR, 'templates', 'rep.odt')
TEMPLATE_CMD = os.path.join(PLUGIN_DIR, 'templates', 'cmd.odt')
TMP_JSON = os.path.join(PLUGIN_DIR, 'data', 'tmp.json')
MAP_PNG = os.path.join(PLUGIN_DIR, 'resources', 'map.png')
ICON_PNG = os.path.join(PLUGIN_DIR, 'resources', 'icon.png')
VIEWS_SQL = os.path.join(PLUGIN_DIR, 'data', 'Views.sql')
TEMPLATE_DATA_DIR = os.path.join(PLUGIN_DIR, 'template_data')
WILAYAS_JSON = os.path.join(TEMPLATE_DATA_DIR, 'wilayas.json')
DAIRA_JSON = os.path.join(TEMPLATE_DATA_DIR, 'daira.json')
COMMUNES_JSON = os.path.join(TEMPLATE_DATA_DIR, 'communes.json')
COMMUNES_GEOJSON = os.path.join(TEMPLATE_DATA_DIR, 'communes.geojson')
COMMUNES_DB = os.path.join(TEMPLATE_DATA_DIR, 'communes.db')

MAP_A3_TEMPLATE = os.path.join(PLUGIN_DIR, 'templates', 'map_a3.odt')
MAP_A0_TEMPLATE = os.path.join(PLUGIN_DIR, 'templates', 'map_a0.odt')
SITUATION_PNG = os.path.join(PLUGIN_DIR, 'resources', 'situation.png')
NORTH_ARROW_SVG = os.path.join(PLUGIN_DIR, 'resources', 'north_arrow.svg')
SYMBOLS_SVG = os.path.join(PLUGIN_DIR, 'resources', 'symbols.svg')
SCALE_BAR_SVG = os.path.join(PLUGIN_DIR, 'resources', 'scale_bar.svg')
CHART_SVG = os.path.join(PLUGIN_DIR, 'resources', 'chart.svg')
REPORTING_SCRIPT = os.path.join(PLUGIN_DIR, 'scripts', 'reporting.py')

MEMORY_PROVIDER = 'memory'
NOTIFY_DURATION = 3

# Layer names used as QGIS display names AND internal identifiers.
# The NEUTRAL_LAYER_* constants provide locale-independent aliases
# for programmatic lookups.
LAYER_MUNICIPALITY = 'My Municipality'
LAYER_ROADS = 'Roads'
LAYER_FACILITIES = 'Facilities'
LAYER_SUBDIVISIONS = 'Subdivisions'
LAYER_ZONES = 'Zones'
LAYER_NUMBERING = 'Numbering'
LAYER_PANELS = 'Panels'

NEUTRAL_LAYER_MUNICIPALITY = 'municipality'
NEUTRAL_LAYER_ROADS = 'roads'
NEUTRAL_LAYER_FACILITIES = 'facilities'
NEUTRAL_LAYER_SUBDIVISIONS = 'subdivisions'
NEUTRAL_LAYER_ZONES = 'zones'
NEUTRAL_LAYER_NUMBERING = 'numbering'
NEUTRAL_LAYER_PANELS = 'panels'

LAYER_NAMES = [
    LAYER_MUNICIPALITY,
    LAYER_SUBDIVISIONS,
    LAYER_ZONES,
    LAYER_FACILITIES,
    LAYER_ROADS,
    LAYER_PANELS,
    LAYER_NUMBERING,
]

LAYER_KEY = {
    LAYER_PANELS: 'pan',
    LAYER_FACILITIES: 'org',
    LAYER_SUBDIVISIONS: 'city',
    LAYER_ROADS: 'roads',
    LAYER_NUMBERING: 'num',
    LAYER_ZONES: 'zone',
}

LAYER_MODEL = {
    LAYER_ROADS: 'Road',
    LAYER_FACILITIES: 'Organization',
    LAYER_SUBDIVISIONS: 'Subdivision',
}

PANEL_TYPE_MAP = {
    LAYER_ROADS: 'roads',
    LAYER_FACILITIES: 'facilities',
    LAYER_SUBDIVISIONS: 'subdivisions',
}


class PanelStatus(str, Enum):
    """Panel mount statuses."""

    MOUNTED = 'installed'
    PLANNED = 'planned'
    TO_MOVE = 'to_move'
    TO_FIX = 'to_fix'


class ActivityStatus(str, Enum):
    """Activity status (currently only No Activity)."""

    NONE = 'No Activity'


class Theme(str, Enum):
    """Theme enum (Dark / Light)."""

    DARK = 'Dark'
    LIGHT = 'Light'

    @classmethod
    def _missing_(cls, value):
        """Handle backward-compat lookup of legacy theme values."""
        if value in ('Light', 'light', 'فاتح'):
            return cls.LIGHT
        if value in ('Dark', 'dark', 'داكن'):
            return cls.DARK
        return None


PAN_MOUNTED = PanelStatus.MOUNTED
PAN_PLANNED = PanelStatus.PLANNED
PAN_TO_MOVE = PanelStatus.TO_MOVE
PAN_TO_FIX = PanelStatus.TO_FIX

NUM_PLANNED = 'planned'

NO_ACTIVITY = ActivityStatus.NONE
DEFAULT_PANEL_DIM = '30X40'

SETTINGS_ORG = 'RNA'
SETTINGS_APP = 'RNA'
SETTINGS_KEY_THEME = 'theme'
SETTINGS_KEY_LOCALE = 'locale'

THEME_DARK = Theme.DARK
THEME_LIGHT = Theme.LIGHT

AVAILABLE_LOCALES = [
    ('ar', 'Arabic'),
    ('fr', 'Français'),
    ('en', 'English'),
]
