import os

PLUGIN_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SRID = 4326
CRS = f"EPSG:{SRID}"

COOKIE_FILE = os.path.join(PLUGIN_DIR, "data", "cookie.toml")
DATABASE_FILE = os.path.join(PLUGIN_DIR, "data", "database.sqlite")
AUTH_DATABASE_FILE = os.path.join(PLUGIN_DIR, "data", "auth.sqlite")
QGIS_CONFIG_FILE = os.path.join(PLUGIN_DIR, "data", "qgis_config.json")
STYLE_QML = os.path.join(PLUGIN_DIR, "style", "style.qml")
DEFAULT_STYLE_DIR = os.path.join(PLUGIN_DIR, "style", "default")
CUSTOM_STYLE_DIR = os.path.join(PLUGIN_DIR, "style", "customized")
TEMPLATE_REP = os.path.join(PLUGIN_DIR, "templates", "rep.odt")
TEMPLATE_CMD = os.path.join(PLUGIN_DIR, "templates", "cmd.odt")
TMP_JSON = os.path.join(PLUGIN_DIR, "data", "tmp.json")
REPORTING_SCRIPT = os.path.join(PLUGIN_DIR, "scripts", "reporting.py")
MAP_PNG = os.path.join(PLUGIN_DIR, "resources", "map.png")
ICON_PNG = os.path.join(PLUGIN_DIR, "resources", "icon.png")
VIEWS_SQL = os.path.join(PLUGIN_DIR, "data", "Views.sql")
TEMPLATE_DATA_DIR = os.path.join(PLUGIN_DIR, "template_data")

MAP_A3_TEMPLATE = os.path.join(PLUGIN_DIR, "templates", "map_a3.odt")
MAP_A0_TEMPLATE = os.path.join(PLUGIN_DIR, "templates", "map_a0.odt")
SITUATION_PNG = os.path.join(PLUGIN_DIR, "resources", "situation.png")
NORTH_ARROW_SVG = os.path.join(PLUGIN_DIR, "resources", "north_arrow.svg")
SYMBOLS_SVG = os.path.join(PLUGIN_DIR, "resources", "symbols.svg")
SCALE_BAR_SVG = os.path.join(PLUGIN_DIR, "resources", "scale_bar.svg")
CHART_SVG = os.path.join(PLUGIN_DIR, "resources", "chart.svg")

MEMORY_PROVIDER = "memory"
NOTIFY_DURATION = 3

LAYER_MUNICIPALITY = "بلديتي"
LAYER_ROADS = "الطرق"
LAYER_FACILITIES = "المرافق"
LAYER_SUBDIVISIONS = "التجزئات"
LAYER_ZONES = "المناطق"
LAYER_NUMBERING = "الترقيم"
LAYER_PANELS = "اللوحات"

LAYER_NAMES = [
    LAYER_MUNICIPALITY, LAYER_SUBDIVISIONS, LAYER_ZONES,
    LAYER_FACILITIES, LAYER_ROADS, LAYER_PANELS, LAYER_NUMBERING,
]

LAYER_KEY = {
    LAYER_PANELS: "pan", LAYER_FACILITIES: "org",
    LAYER_SUBDIVISIONS: "city", LAYER_ROADS: "roads",
    LAYER_NUMBERING: "num", LAYER_ZONES: "zone",
}

LAYER_MODEL = {
    LAYER_ROADS: "Road", LAYER_FACILITIES: "Organization",
    LAYER_SUBDIVISIONS: "Subdivision",
}

PAN_MOUNTED = "مركبة"
PAN_PLANNED = "مبرمجة"
PAN_TO_MOVE = "لنقلها"
PAN_TO_FIX = "لتصحيحها"

NUM_PLANNED = "مبرمجة"

NO_ACTIVITY = "بدون نشاط"
DEFAULT_PANEL_DIM = "30X40"

SETTINGS_ORG = "RNA"
SETTINGS_APP = "RNA"
SETTINGS_KEY_THEME = "theme"
SETTINGS_KEY_LOCALE = "locale"

THEME_DARK = "داكن"
THEME_LIGHT = "فاتح"

AVAILABLE_LOCALES = [
    ("ar", "العربية"), ("fr", "Français"), ("en", "English"),
]
