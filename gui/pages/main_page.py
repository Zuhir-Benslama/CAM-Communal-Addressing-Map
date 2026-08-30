"""Main page builder (toolbar, form container, footer)."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..dialog_helpers import make_section_frame
from .form_pages import (
    build_city_form,
    build_num_form,
    build_org_form,
    build_pan_form,
    build_road_form,
    build_zone_form,
)
from .settings_page import build_settings_page

_ICON_DIR = str(Path(__file__).resolve().parent.parent.parent / 'resources')


if TYPE_CHECKING:
    from .main_dialog import MainDialog


def build_main_page(dialog: MainDialog) -> None:
    page = QWidget()
    page.setObjectName('main')
    layout = QVBoxLayout(page)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    # Toolbar
    toolbar = QWidget()
    toolbar.setObjectName('toolbarFrame')
    toolbar.setFixedHeight(48)

    t_layout = QHBoxLayout(toolbar)
    t_layout.setContentsMargins(12, 0, 12, 0)

    dialog._label_username = QLabel()
    dialog._label_username.setObjectName('label_username')
    dialog._label_username.setStyleSheet('font-size: 13px; font-weight: bold;')
    t_layout.addWidget(dialog._label_username)

    t_layout.addStretch()

    dialog._btn_gear = QPushButton('\u2699')
    dialog._btn_gear.setFixedSize(34, 34)
    dialog._btn_gear.setObjectName('gearBtn')
    dialog._btn_gear.setStyleSheet('font-size: 18px; padding: 0px;')
    dialog._btn_gear.setToolTip('Settings')
    t_layout.addWidget(dialog._btn_gear)

    layout.addWidget(toolbar)

    # Main content stack: 0=forms, 1=settings
    dialog._main_stack = QStackedWidget()
    layout.addWidget(dialog._main_stack, stretch=1)

    _build_form_page(dialog)
    build_settings_page(dialog)

    dialog._main_stack.setCurrentIndex(0)

    # Footer
    footer = QLabel('Space Applications Center \u00a9')
    footer.setObjectName('footer')
    footer.setFixedHeight(36)

    footer.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    footer.setStyleSheet('padding-left: 12px; font-size: 10px;')
    layout.addWidget(footer)

    dialog._page_stack.addWidget(page)
    dialog._held_widgets.append(page)
    dialog._held_widgets.append(toolbar)


def _section_title(layout: QVBoxLayout, text: str, obj_name: str) -> None:
    """Add a bold section title to the given layout."""
    title = QLabel(text)
    title.setObjectName(obj_name)
    title.setStyleSheet('font-size: 13px; font-weight: bold;')
    layout.addWidget(title)


def _build_plan_section(dialog: MainDialog, layout: QVBoxLayout) -> QWidget:
    """Build the phase (layer) selection section."""
    plan_frame = make_section_frame()
    plan_layout = plan_frame.layout()
    _section_title(plan_layout, 'Phase', 'groupBox_plan_selection')

    dialog._combo_layer_selector = QComboBox()
    dialog._combo_layer_selector.setObjectName('layer_selector')
    plan_layout.addWidget(dialog._combo_layer_selector)

    layout.addWidget(plan_frame)
    return plan_frame


_TOOLBAR_BUTTONS = [
    # (dialog attribute, object name, icon file, tooltip)
    ('_btn_draw', 'drawBtn', 'draw.svg', 'Draw'),
    ('_btn_select', 'selectBtn', 'select.svg', 'Select'),
    ('_btn_edit', 'editBtn', 'edit.svg', 'Edit'),
    ('_btn_measure', 'mesure_dist', 'measure.svg', 'Measure Distance'),
]


def _build_actions_section(dialog: MainDialog, layout: QVBoxLayout) -> QWidget:
    """Build the map tools toolbar section."""
    action_frame = make_section_frame()
    action_layout = action_frame.layout()
    _section_title(action_layout, 'Tools', 'groupBox_actions')

    btn_row = QHBoxLayout()
    btn_row.setSpacing(6)
    for attr, obj_name, icon_file, tooltip in _TOOLBAR_BUTTONS:
        btn = QPushButton()
        btn.setObjectName(obj_name)
        btn.setIcon(QIcon(str(Path(_ICON_DIR) / icon_file)))
        btn.setToolTip(tooltip)
        setattr(dialog, attr, btn)
        btn_row.addWidget(btn, 1)
    action_layout.addLayout(btn_row)

    layout.addWidget(action_frame)
    return action_frame


_FORM_BUILDERS = [
    build_zone_form,
    build_road_form,
    build_org_form,
    build_city_form,
    build_num_form,
    build_pan_form,
]


def _build_data_section(dialog: MainDialog, layout: QVBoxLayout) -> QWidget:
    """Build the feature form section containing the per-layer forms."""
    form_frame = make_section_frame()
    form_layout = form_frame.layout()
    _section_title(form_layout, 'Feature', 'groupBox_form_data')

    dialog._form_stack = QStackedWidget()
    for build in _FORM_BUILDERS:
        build(dialog)
    form_layout.addWidget(dialog._form_stack, stretch=1)

    layout.addWidget(form_frame, stretch=1)
    return form_frame


def _build_form_page(dialog: MainDialog) -> None:
    page = QWidget()
    page.setObjectName('mainForm')
    layout = QVBoxLayout(page)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(12)

    plan_frame = _build_plan_section(dialog, layout)
    action_frame = _build_actions_section(dialog, layout)
    form_frame = _build_data_section(dialog, layout)

    dialog._main_stack.addWidget(page)
    dialog._held_widgets.append(page)
    dialog._held_widgets.append(plan_frame)
    dialog._held_widgets.append(action_frame)
    dialog._held_widgets.append(form_frame)
