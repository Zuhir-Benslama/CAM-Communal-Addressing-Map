import logging
import os
import shutil
import subprocess
from typing import Optional


def validate_text(value: str, max_length: int = 255) -> str:
    value = value.strip()
    if len(value) > max_length:
        value = value[:max_length]
    return value


_SUBPROCESS_FLAGS: dict = {}
if os.name == 'nt':
    _SUBPROCESS_FLAGS['creationflags'] = subprocess.CREATE_NO_WINDOW


def get_qgis_python() -> Optional[str]:
    python = os.getenv('PYTHON_QGIS_BAT')
    if python:
        if not os.path.isfile(python) or not os.access(python, os.X_OK):
            logging.getLogger(__name__).warning(
                "PYTHON_QGIS_BAT path is not executable: %s, "
                "falling back to default",
                python,
            )
        else:
            return python
    if os.name == 'nt':
        return 'python.exe'
    if shutil.which('python3'):
        return 'python3'
    return 'python3'


PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))

# CRS / SRID
SRID = 4326
CRS = f"EPSG:{SRID}"

# File names (relative to PLUGIN_DIR)
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

# QGIS layer provider
MEMORY_PROVIDER = "memory"

# Notification duration (seconds)
NOTIFY_DURATION = 3

# Arabic layer names
LAYER_MUNICIPALITY = "بلديتي"
LAYER_ROADS = "الطرق"
LAYER_FACILITIES = "المرافق"
LAYER_SUBDIVISIONS = "التجزئات"
LAYER_ZONES = "المناطق"
LAYER_NUMBERING = "الترقيم"
LAYER_PANELS = "اللوحات"

LAYER_NAMES = [
    LAYER_MUNICIPALITY,
    LAYER_SUBDIVISIONS,
    LAYER_ZONES,
    LAYER_FACILITIES,
    LAYER_ROADS,
    LAYER_PANELS,
    LAYER_NUMBERING,
]

# Mapping: Arabic name -> English key
LAYER_KEY = {
    LAYER_PANELS: "pan",
    LAYER_FACILITIES: "org",
    LAYER_SUBDIVISIONS: "city",
    LAYER_ROADS: "roads",
    LAYER_NUMBERING: "num",
    LAYER_ZONES: "zone",
}

# Mapping: Arabic name -> model name for ListeELT
LAYER_MODEL = {
    LAYER_ROADS: "Road",
    LAYER_FACILITIES: "Organization",
    LAYER_SUBDIVISIONS: "Subdivision",
}

# Panneautage state strings
PAN_MOUNTED = "مركبة"
PAN_PLANNED = "مبرمجة"
PAN_TO_MOVE = "لنقلها"
PAN_TO_FIX = "لتصحيحها"

# Numerotation state
NUM_PLANNED = "مبرمجة"

# Map / export templates
MAP_A3_TEMPLATE = os.path.join(PLUGIN_DIR, "templates", "map_a3.odt")
MAP_A0_TEMPLATE = os.path.join(PLUGIN_DIR, "templates", "map_a0.odt")
SITUATION_PNG = os.path.join(PLUGIN_DIR, "resources", "situation.png")
NORTH_ARROW_SVG = os.path.join(PLUGIN_DIR, "resources", "north_arrow.svg")
SYMBOLS_SVG = os.path.join(PLUGIN_DIR, "resources", "symbols.svg")
SCALE_BAR_SVG = os.path.join(PLUGIN_DIR, "resources", "scale_bar.svg")
CHART_SVG = os.path.join(PLUGIN_DIR, "resources", "chart.svg")

# Sentinel / default values
NO_ACTIVITY = "بدون نشاط"
DEFAULT_PANEL_DIM = "30X40"

# ---------------------------------------------------------------------------
# Settings / preferences
# ---------------------------------------------------------------------------
SETTINGS_ORG = "RNA"
SETTINGS_APP = "RNA"
SETTINGS_KEY_THEME = "theme"
SETTINGS_KEY_LOCALE = "locale"

THEME_DARK = "داكن"
THEME_LIGHT = "فاتح"

AVAILABLE_LOCALES = [
    ("ar", "العربية"),
    ("fr", "Français"),
    ("en", "English"),
]

# ---------------------------------------------------------------------------
# Theme QSS stylesheets
# ---------------------------------------------------------------------------
DARK_BG = "#1a1b26"
DARK_SURFACE = "#24253a"
DARK_OVERLAY = "#2f3048"
DARK_BORDER = "#3b3d54"
DARK_TEXT = "#c9d1d9"
DARK_TEXT_SEC = "#8b949e"
DARK_ACCENT = "#58a6ff"
DARK_ACCENT_HOVER = "#79b8ff"
DARK_SUCCESS = "#3fb950"
DARK_DANGER = "#f85149"
DARK_SELECTION = "#264f78"

LIGHT_BG = "#f6f8fa"
LIGHT_SURFACE = "#ffffff"
LIGHT_OVERLAY = "#eaeef2"
LIGHT_BORDER = "#d0d7de"
LIGHT_TEXT = "#1f2328"
LIGHT_TEXT_SEC = "#656d76"
LIGHT_ACCENT = "#0969da"
LIGHT_ACCENT_HOVER = "#0550ae"
LIGHT_SUCCESS = "#1a7f37"
LIGHT_DANGER = "#cf222e"
LIGHT_SELECTION = "#b6d4fe"

DARK_QSS = f"""
    * {{
        background-color: {DARK_BG};
        color: {DARK_TEXT};
        font-size: 15px;
    }}
    QGroupBox {{
        background-color: {DARK_SURFACE};
        border: 1px solid {DARK_BORDER};
        border-radius: 8px;
        margin-top: 18px;
        padding: 16px 12px 12px 12px;
        font-weight: 600;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        padding: 2px 10px;
        color: {DARK_ACCENT};
    }}
    QPushButton {{
        background-color: {DARK_OVERLAY};
        color: {DARK_TEXT};
        border: 1px solid {DARK_BORDER};
        border-radius: 6px;
        padding: 8px 16px;
        min-height: 1.2em;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: {DARK_BORDER};
        border-color: {DARK_ACCENT};
    }}
    QPushButton:pressed {{
        background-color: #1e1f35;
    }}
    QPushButton:disabled {{
        background-color: {DARK_BG};
        color: {DARK_TEXT_SEC};
    }}
    QLineEdit {{
        background-color: {DARK_OVERLAY};
        color: {DARK_TEXT};
        border: 1px solid {DARK_BORDER};
        border-radius: 6px;
        padding: 10px 14px;
        min-height: 1.2em;
        selection-background-color: {DARK_SELECTION};
    }}
    QLineEdit:focus {{
        border-color: {DARK_ACCENT};
    }}
    QComboBox {{
        background-color: {DARK_OVERLAY};
        color: {DARK_TEXT};
        border: 1px solid {DARK_BORDER};
        border-radius: 6px;
        padding: 10px 14px;
        min-height: 1.2em;
        combobox-popup: 0;
    }}
    QComboBox:hover {{
        border-color: {DARK_ACCENT};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox::down-arrow {{
        image: none;
    }}
    QComboBox QAbstractItemView {{
        background-color: {DARK_SURFACE};
        color: {DARK_TEXT};
        border: 1px solid {DARK_BORDER};
        border-radius: 4px;
        selection-background-color: {DARK_OVERLAY};
        selection-color: {DARK_TEXT};
    }}
    QTabWidget::pane {{
        background-color: {DARK_BG};
        border: 1px solid {DARK_BORDER};
        border-top: none;
        border-radius: 0 0 6px 6px;
    }}
    QTabBar::tab {{
        background-color: {DARK_OVERLAY};
        color: {DARK_TEXT_SEC};
        border: 1px solid {DARK_BORDER};
        border-bottom: none;
        border-radius: 6px 6px 0 0;
        padding: 9px 16px;
        margin-right: 2px;
        font-weight: 500;
    }}
    QTabBar::tab:selected {{
        background-color: {DARK_BG};
        color: {DARK_TEXT};
        border-bottom: 2px solid {DARK_ACCENT};
        margin-bottom: -1px;
    }}
    QTabBar::tab:hover:!selected {{
        background-color: {DARK_SURFACE};
        color: {DARK_TEXT};
    }}
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    QScrollBar:vertical {{
        background-color: {DARK_BG};
        width: 10px;
        border: none;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {DARK_BORDER};
        border-radius: 5px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {DARK_TEXT_SEC};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background-color: {DARK_BG};
        height: 10px;
        border: none;
        border-radius: 5px;
    }}
    QScrollBar::handle:horizontal {{
        background-color: {DARK_BORDER};
        border-radius: 5px;
        min-width: 30px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background-color: {DARK_TEXT_SEC};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}
    QFrame[frameShape="4"], QFrame[frameShape="5"] {{
        background-color: {DARK_SURFACE};
        border: 1px solid {DARK_BORDER};
        border-radius: 8px;
    }}
    QLabel {{
        color: {DARK_TEXT};
    }}
    QCheckBox {{
        color: {DARK_TEXT_SEC};
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid {DARK_BORDER};
        border-radius: 3px;
        background-color: {DARK_OVERLAY};
    }}
    QCheckBox::indicator:checked {{
        background-color: {DARK_ACCENT};
        border-color: {DARK_ACCENT};
    }}
    QDateEdit {{
        background-color: {DARK_OVERLAY};
        color: {DARK_TEXT};
        border: 1px solid {DARK_BORDER};
        border-radius: 6px;
        padding: 10px 14px;
        min-height: 1.2em;
    }}
    QDateEdit:focus {{
        border-color: {DARK_ACCENT};
    }}
    QStackedWidget {{
        background-color: {DARK_BG};
    }}
    QTableWidget {{
        background-color: {DARK_SURFACE};
        color: {DARK_TEXT};
        border: 1px solid {DARK_BORDER};
        border-radius: 6px;
        gridline-color: {DARK_BORDER};
    }}
    QTableWidget::item:selected {{
        background-color: {DARK_SELECTION};
        color: {DARK_TEXT};
    }}
    QHeaderView::section {{
        background-color: {DARK_OVERLAY};
        color: {DARK_TEXT};
        border: 1px solid {DARK_BORDER};
        padding: 4px 8px;
    }}
"""

DARK_QSS_DIALOG = f"""
    QFileDialog {{
        background-color: {DARK_BG};
        color: {DARK_TEXT};
    }}
    QFileDialog QLabel {{ color: {DARK_TEXT}; }}
    QFileDialog QTreeView, QFileDialog QListView {{
        background-color: {DARK_SURFACE};
        color: {DARK_TEXT};
        border: 1px solid {DARK_BORDER};
        border-radius: 4px;
        selection-background-color: {DARK_SELECTION};
        selection-color: {DARK_TEXT};
    }}
    QFileDialog QPushButton {{
        background-color: {DARK_OVERLAY};
        color: {DARK_TEXT};
        border: 1px solid {DARK_BORDER};
        border-radius: 6px;
        padding: 6px 14px;
    }}
    QFileDialog QPushButton:hover {{
        background-color: {DARK_BORDER};
        border-color: {DARK_ACCENT};
    }}
    QFileDialog QPushButton:pressed {{
        background-color: #1e1f35;
    }}
    QFileDialog QComboBox, QFileDialog QLineEdit {{
        background-color: {DARK_OVERLAY};
        color: {DARK_TEXT};
        border: 1px solid {DARK_BORDER};
        border-radius: 6px;
        padding: 6px 10px;
    }}
"""

LIGHT_QSS = f"""
    * {{
        background-color: {LIGHT_BG};
        color: {LIGHT_TEXT};
        font-size: 15px;
    }}
    QGroupBox {{
        background-color: {LIGHT_SURFACE};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 8px;
        margin-top: 18px;
        padding: 16px 12px 12px 12px;
        font-weight: 600;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        padding: 2px 10px;
        color: {LIGHT_ACCENT};
    }}
    QPushButton {{
        background-color: {LIGHT_OVERLAY};
        color: {LIGHT_TEXT};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 6px;
        padding: 8px 16px;
        min-height: 1.2em;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: {LIGHT_BORDER};
        border-color: {LIGHT_ACCENT};
    }}
    QPushButton:pressed {{
        background-color: #dae0e7;
    }}
    QPushButton:disabled {{
        background-color: {LIGHT_BG};
        color: {LIGHT_TEXT_SEC};
    }}
    QLineEdit {{
        background-color: {LIGHT_SURFACE};
        color: {LIGHT_TEXT};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 6px;
        padding: 10px 14px;
        min-height: 1.2em;
        selection-background-color: {LIGHT_SELECTION};
    }}
    QLineEdit:focus {{
        border-color: {LIGHT_ACCENT};
    }}
    QComboBox {{
        background-color: {LIGHT_SURFACE};
        color: {LIGHT_TEXT};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 6px;
        padding: 10px 14px;
        min-height: 1.2em;
        combobox-popup: 0;
    }}
    QComboBox:hover {{
        border-color: {LIGHT_ACCENT};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox::down-arrow {{
        image: none;
    }}
    QComboBox QAbstractItemView {{
        background-color: {LIGHT_SURFACE};
        color: {LIGHT_TEXT};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 4px;
        selection-background-color: {LIGHT_OVERLAY};
        selection-color: {LIGHT_TEXT};
    }}
    QTabWidget::pane {{
        background-color: {LIGHT_BG};
        border: 1px solid {LIGHT_BORDER};
        border-top: none;
        border-radius: 0 0 6px 6px;
    }}
    QTabBar::tab {{
        background-color: {LIGHT_OVERLAY};
        color: {LIGHT_TEXT_SEC};
        border: 1px solid {LIGHT_BORDER};
        border-bottom: none;
        border-radius: 6px 6px 0 0;
        padding: 9px 16px;
        margin-right: 2px;
        font-weight: 500;
    }}
    QTabBar::tab:selected {{
        background-color: {LIGHT_BG};
        color: {LIGHT_TEXT};
        border-bottom: 2px solid {LIGHT_ACCENT};
        margin-bottom: -1px;
    }}
    QTabBar::tab:hover:!selected {{
        background-color: {LIGHT_SURFACE};
        color: {LIGHT_TEXT};
    }}
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    QScrollBar:vertical {{
        background-color: {LIGHT_BG};
        width: 10px;
        border: none;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {LIGHT_BORDER};
        border-radius: 5px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {LIGHT_TEXT_SEC};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background-color: {LIGHT_BG};
        height: 10px;
        border: none;
        border-radius: 5px;
    }}
    QScrollBar::handle:horizontal {{
        background-color: {LIGHT_BORDER};
        border-radius: 5px;
        min-width: 30px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background-color: {LIGHT_TEXT_SEC};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}
    QFrame[frameShape="4"], QFrame[frameShape="5"] {{
        background-color: {LIGHT_SURFACE};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 8px;
    }}
    QLabel {{
        color: {LIGHT_TEXT};
    }}
    QCheckBox {{
        color: {LIGHT_TEXT_SEC};
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid {LIGHT_BORDER};
        border-radius: 3px;
        background-color: {LIGHT_SURFACE};
    }}
    QCheckBox::indicator:checked {{
        background-color: {LIGHT_ACCENT};
        border-color: {LIGHT_ACCENT};
    }}
    QDateEdit {{
        background-color: {LIGHT_SURFACE};
        color: {LIGHT_TEXT};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 6px;
        padding: 10px 14px;
        min-height: 1.2em;
    }}
    QDateEdit:focus {{
        border-color: {LIGHT_ACCENT};
    }}
    QStackedWidget {{
        background-color: {LIGHT_BG};
    }}
    QTableWidget {{
        background-color: {LIGHT_SURFACE};
        color: {LIGHT_TEXT};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 6px;
        gridline-color: {LIGHT_BORDER};
    }}
    QTableWidget::item:selected {{
        background-color: {LIGHT_SELECTION};
        color: {LIGHT_TEXT};
    }}
    QHeaderView::section {{
        background-color: {LIGHT_OVERLAY};
        color: {LIGHT_TEXT};
        border: 1px solid {LIGHT_BORDER};
        padding: 4px 8px;
    }}
"""

LIGHT_QSS_DIALOG = f"""
    QFileDialog {{
        background-color: {LIGHT_BG};
        color: {LIGHT_TEXT};
    }}
    QFileDialog QLabel {{ color: {LIGHT_TEXT}; }}
    QFileDialog QTreeView, QFileDialog QListView {{
        background-color: {LIGHT_SURFACE};
        color: {LIGHT_TEXT};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 4px;
        selection-background-color: {LIGHT_SELECTION};
        selection-color: {LIGHT_TEXT};
    }}
    QFileDialog QPushButton {{
        background-color: {LIGHT_OVERLAY};
        color: {LIGHT_TEXT};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 6px;
        padding: 6px 14px;
    }}
    QFileDialog QPushButton:hover {{
        background-color: {LIGHT_BORDER};
        border-color: {LIGHT_ACCENT};
    }}
    QFileDialog QPushButton:pressed {{
        background-color: #dae0e7;
    }}
    QFileDialog QComboBox, QFileDialog QLineEdit {{
        background-color: {LIGHT_SURFACE};
        color: {LIGHT_TEXT};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 6px;
        padding: 6px 10px;
    }}
"""

THEMES = {
    THEME_DARK: (DARK_QSS, DARK_QSS_DIALOG),
    THEME_LIGHT: (LIGHT_QSS, LIGHT_QSS_DIALOG),
}

DEFAULT_THEME = THEME_DARK


def current_locale() -> str:
    """Detect the current UI locale from QSettings."""
    from qgis.PyQt.QtCore import QSettings
    s = QSettings(SETTINGS_ORG, SETTINGS_APP)
    locale = s.value(SETTINGS_KEY_LOCALE, '')
    if not locale:
        locale_val = QSettings().value('locale/userLocale')
        locale = locale_val[0:2] if locale_val else 'en'
    return locale


def locale_value(instance, field_base: str, locale: str = '') -> str:
    """Return locale-appropriate value from a model instance.

    For locale 'ar', returns the base field (e.g. `Nom`).
    For 'fr'/'en', returns `Nom_fr`/`Nom_en`, falling back to base.
    """
    if not locale:
        locale = current_locale()
    if locale == 'ar':
        return getattr(instance, field_base, '') or ''
    locale_field = f'{field_base}_{locale}'
    value = getattr(instance, locale_field, None)
    return value if value else (getattr(instance, field_base, '') or '')


def get_theme_qss(theme_name: str) -> str:
    return THEMES.get(theme_name, THEMES[DEFAULT_THEME])[0]


def get_dialog_qss(theme_name: str) -> str:
    return THEMES.get(theme_name, THEMES[DEFAULT_THEME])[1]


def current_theme() -> str:
    from PyQt5.QtCore import QSettings
    return QSettings(SETTINGS_ORG, SETTINGS_APP).value(
        SETTINGS_KEY_THEME, DEFAULT_THEME,
    )
