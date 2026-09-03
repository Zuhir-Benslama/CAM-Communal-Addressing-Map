"""Shared constants: paths, layer names, enums, and settings keys."""

from enum import Enum
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parent.parent.parent

SRID = 4326
CRS = f'EPSG:{SRID}'

COOKIE_FILE = PLUGIN_DIR / 'data' / 'cookie.toml'
DATABASE_FILE = PLUGIN_DIR / 'data' / 'database.sqlite'
AUTH_DATABASE_FILE = PLUGIN_DIR / 'data' / 'auth.sqlite'
QGIS_CONFIG_FILE = PLUGIN_DIR / 'data' / 'qgis_config.json'
STYLE_QML = PLUGIN_DIR / 'style' / 'style.qml'

# Report method codes (CLI args to scripts/reporting.py)
REPORT_METHOD_ORDER = 1
REPORT_METHOD_REPORT = 2
REPORT_METHOD_MAP_A3 = 3
REPORT_METHOD_MAP_A4 = 4
DEFAULT_STYLE_DIR = PLUGIN_DIR / 'style' / 'default'
CUSTOM_STYLE_DIR = PLUGIN_DIR / 'style' / 'customized'
TEMPLATE_REP = PLUGIN_DIR / 'templates' / 'rep.odt'
TEMPLATE_CMD = PLUGIN_DIR / 'templates' / 'cmd.odt'
TMP_JSON = PLUGIN_DIR / 'data' / 'tmp.json'
MAP_PNG = PLUGIN_DIR / 'resources' / 'map.png'
ICON_PNG = PLUGIN_DIR / 'resources' / 'icon.png'
VIEWS_SQL = PLUGIN_DIR / 'data' / 'Views.sql'
TEMPLATE_DATA_DIR = PLUGIN_DIR / 'template_data'
WILAYAS_JSON = TEMPLATE_DATA_DIR / 'wilayas.json'
DAIRA_JSON = TEMPLATE_DATA_DIR / 'daira.json'
COMMUNES_JSON = TEMPLATE_DATA_DIR / 'communes.json'
COMMUNES_GEOJSON = TEMPLATE_DATA_DIR / 'communes.geojson'
COMMUNES_DB = TEMPLATE_DATA_DIR / 'communes.db'

MAP_A3_TEMPLATE = PLUGIN_DIR / 'templates' / 'map_a3.odt'
MAP_A0_TEMPLATE = PLUGIN_DIR / 'templates' / 'map_a0.odt'
SITUATION_PNG = PLUGIN_DIR / 'resources' / 'situation.png'
NORTH_ARROW_SVG = PLUGIN_DIR / 'resources' / 'north_arrow.svg'
SYMBOLS_SVG = PLUGIN_DIR / 'resources' / 'symbols.svg'
SCALE_BAR_SVG = PLUGIN_DIR / 'resources' / 'scale_bar.svg'
CHART_SVG = PLUGIN_DIR / 'resources' / 'chart.svg'
REPORTING_SCRIPT = PLUGIN_DIR / 'scripts' / 'reporting.py'

MEMORY_PROVIDER = 'memory'
NOTIFY_DURATION = 3

LAYER_MUNICIPALITY = 'My Municipality'
LAYER_ROADS = 'Roads'
LAYER_FACILITIES = 'Facilities'
LAYER_SUBDIVISIONS = 'Subdivisions'
LAYER_ZONES = 'Zones'
LAYER_NUMBERING = 'Numbering'
LAYER_PANELS = 'Panels'

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

PANEL_TYPE_MAP = {
    LAYER_ROADS: 'roads',
    LAYER_FACILITIES: 'facilities',
    LAYER_SUBDIVISIONS: 'subdivisions',
}


class PanelStatus(str, Enum):
    """Panel mount statuses stored in the database."""

    # NOTE: enum member names are the semantic labels, values are the
    # persisted lowercase storage codes (do not rename without migration).
    MOUNTED = 'installed'
    PLANNED = 'planned'
    TO_MOVE = 'to_move'
    TO_FIX = 'to_fix'


class ActivityStatus(str, Enum):
    """Activity status (currently only No Activity)."""

    # Value doubles as the display label and combo sentinel; it is not
    # persisted, so it is safe to keep capitalised.
    NONE = 'No Activity'


class Theme(str, Enum):
    """Theme enum (Dark / Light)."""

    DARK = 'Dark'
    LIGHT = 'Light'


PAN_MOUNTED = PanelStatus.MOUNTED
PAN_PLANNED = PanelStatus.PLANNED
PAN_TO_MOVE = PanelStatus.TO_MOVE
PAN_TO_FIX = PanelStatus.TO_FIX

NUM_PLANNED = 'planned'

NO_ACTIVITY = ActivityStatus.NONE
DEFAULT_PANEL_DIM = '30X40'

# Geometry zone-check result codes
ZONE_OUTSIDE = 0
ZONE_POINT_WITHIN = 1
ZONE_POLYGON_INTERSECT = 2
ZONE_LINE_INTERSECT = 3

# Default dialog window sizes
DIALOG_MIN_WIDTH = 360
DIALOG_DEFAULT_HEIGHT = 680
DIALOG_RESIZE_HEIGHT = 720

POPUP_MIN_WIDTH = 700
POPUP_MIN_HEIGHT = 500
POPUP_RESIZE_WIDTH = 760
POPUP_RESIZE_HEIGHT = 560

# Measure tool constants
MEASURE_COLOR = '255,0,0'
MEASURE_FILL_COLOR = '255,0,0,180'
MEASURE_MARKER_ICON_SIZE = 12
MEASURE_MARKER_PEN_WIDTH = 2
MEASURE_LABEL_FONT_SIZE = 11
MEASURE_LABEL_MIN_SIZE = 8
MEASURE_LABEL_MAX_SIZE = 14
MEASURE_LABEL_Z_VALUE = 1000
MEASURE_BLUR_RADIUS = 5
MEASURE_BAR_DURATION = 10

# Layout/export constants
SYMBOL_DPI = 900
EXPORT_DPI = 300
SYMBOL_FONT_SIZE = 14
BOLD_FONT_POINT_SIZE = 30
LEGEND_SYMBOL_WIDTH = 15
LEGEND_SYMBOL_HEIGHT = 10
SITUATION_MAP_WIDTH = 257
SITUATION_MAP_HEIGHT = 170
SITUATION_MAP_SCALE = 150000
NORTH_ARROW_PAGE = 50
NORTH_ARROW_SIZE = 40
NORTH_ARROW_POS = 25
SCALE_BAR_PAGE = 1
SCALE_BAR_RECT = 80
SCALE_BAR_LENGTH_MM = 100
SCALE_BAR_THRESHOLD_KM = 1000
MAP_PAGE_MARGIN = 20
MAP_SYMBOL_LAYOUT_W = 200
MAP_SYMBOL_LAYOUT_H = 350
PAGE_SPACING = 20

SETTINGS_ORG = 'CAM'
SETTINGS_APP = 'CAM'
SETTINGS_KEY_THEME = 'theme'
SETTINGS_KEY_LOCALE = 'locale'

THEME_DARK = Theme.DARK
THEME_LIGHT = Theme.LIGHT

LOCALE_AR = 'ar'
LOCALE_FR = 'fr'
LOCALE_EN = 'en'

AVAILABLE_LOCALES = [
    (LOCALE_AR, 'Arabic'),
    (LOCALE_FR, 'Français'),
    (LOCALE_EN, 'English'),
]
