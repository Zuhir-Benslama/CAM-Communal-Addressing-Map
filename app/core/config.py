import os
import logging

from ..shared.constants import THEME_DARK, THEME_LIGHT

logger = logging.getLogger(__name__)

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
    QFrame[surfaceRole="header"],
    QFrame[surfaceRole="toolbar"],
    QFrame[surfaceRole="footer"] {{
        background-color: {DARK_SURFACE};
        border: 1px solid {DARK_BORDER};
        border-radius: 10px;
    }}
    QPushButton[role="primary"] {{
        background-color: {DARK_ACCENT};
        color: #ffffff;
        border: 1px solid {DARK_ACCENT};
        font-weight: 600;
    }}
    QPushButton[role="primary"]:hover {{
        background-color: {DARK_ACCENT_HOVER};
        border-color: {DARK_ACCENT_HOVER};
    }}
    QPushButton[role="primary"]:pressed {{
        background-color: #3e87d8;
    }}
    QPushButton[role="tool"] {{
        background-color: #2b3350;
        border: 1px solid #445078;
        color: {DARK_TEXT};
        font-weight: 600;
    }}
    QPushButton[role="tool"]:hover {{
        background-color: #36406a;
        border-color: {DARK_ACCENT};
    }}
    QPushButton[role="danger"] {{
        background-color: {DARK_DANGER};
        border: 1px solid {DARK_DANGER};
        color: #ffffff;
        font-weight: 600;
    }}
    QPushButton[role="danger"]:hover {{
        background-color: #ff665d;
        border-color: #ff665d;
    }}
    QPushButton[role="ghost"] {{
        background-color: transparent;
        border: 1px solid {DARK_BORDER};
        color: {DARK_TEXT};
    }}
    QPushButton[role="ghost"]:hover {{
        background-color: {DARK_OVERLAY};
        border-color: {DARK_ACCENT};
    }}
    QLabel[uiHint="muted"] {{
        color: {DARK_TEXT_SEC};
    }}
    QLabel[uiHint="page"] {{
        color: {DARK_TEXT};
        font-weight: 600;
    }}
    QTableWidget {{
        alternate-background-color: #20263a;
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
    QFrame[surfaceRole="header"],
    QFrame[surfaceRole="toolbar"],
    QFrame[surfaceRole="footer"] {{
        background-color: {LIGHT_SURFACE};
        border: 1px solid {LIGHT_BORDER};
        border-radius: 10px;
    }}
    QPushButton[role="primary"] {{
        background-color: {LIGHT_ACCENT};
        color: #ffffff;
        border: 1px solid {LIGHT_ACCENT};
        font-weight: 600;
    }}
    QPushButton[role="primary"]:hover {{
        background-color: {LIGHT_ACCENT_HOVER};
        border-color: {LIGHT_ACCENT_HOVER};
    }}
    QPushButton[role="primary"]:pressed {{
        background-color: #003f8c;
    }}
    QPushButton[role="tool"] {{
        background-color: #eef4ff;
        border: 1px solid #b4c6e6;
        color: #1b355f;
        font-weight: 600;
    }}
    QPushButton[role="tool"]:hover {{
        background-color: #dbe9ff;
        border-color: {LIGHT_ACCENT};
    }}
    QPushButton[role="danger"] {{
        background-color: {LIGHT_DANGER};
        border: 1px solid {LIGHT_DANGER};
        color: #ffffff;
        font-weight: 600;
    }}
    QPushButton[role="danger"]:hover {{
        background-color: #b6232f;
        border-color: #b6232f;
    }}
    QPushButton[role="ghost"] {{
        background-color: transparent;
        border: 1px solid {LIGHT_BORDER};
        color: {LIGHT_TEXT};
    }}
    QPushButton[role="ghost"]:hover {{
        background-color: {LIGHT_OVERLAY};
        border-color: {LIGHT_ACCENT};
    }}
    QLabel[uiHint="muted"] {{
        color: {LIGHT_TEXT_SEC};
    }}
    QLabel[uiHint="page"] {{
        color: {LIGHT_TEXT};
        font-weight: 600;
    }}
    QTableWidget {{
        alternate-background-color: #f2f5f8;
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


def get_theme_qss(theme_name: str) -> str:
    return THEMES.get(theme_name, THEMES[DEFAULT_THEME])[0]


def get_dialog_qss(theme_name: str) -> str:
    return THEMES.get(theme_name, THEMES[DEFAULT_THEME])[1]


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
    for p in candidates:
        if os.path.exists(p):
            return p

    try:
        result = __import__('subprocess').run(
            ['ldconfig', '-p'], capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines():
            if 'mod_spatialite' in line:
                parts = line.split('=>')
                if len(parts) == 2:
                    path = parts[1].strip()
                    if os.path.exists(path):
                        return path
    except Exception:
        logger.debug("mod_spatialite not found at candidate path", exc_info=True)

    return 'mod_spatialite.so'
