"""Main page builder (toolbar, form container, footer)."""

import os

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

_ICON_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'resources')


def build_main_page(dialog) -> None:
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


def _build_form_page(dialog) -> None:
    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(12)

    # Plan Selection
    plan_frame = make_section_frame()
    plan_layout = plan_frame.layout()

    plan_title = QLabel('Phase')
    plan_title.setObjectName('groupBox_plan_selection')
    plan_title.setStyleSheet('font-size: 13px; font-weight: bold;')
    plan_layout.addWidget(plan_title)

    dialog._combo_layer_selector = QComboBox()
    dialog._combo_layer_selector.setObjectName('layer_selector')
    plan_layout.addWidget(dialog._combo_layer_selector)

    layout.addWidget(plan_frame)

    # Actions
    action_frame = make_section_frame()
    action_layout = action_frame.layout()

    action_title = QLabel('Tools')
    action_title.setObjectName('groupBox_actions')
    action_title.setStyleSheet('font-size: 13px; font-weight: bold;')
    action_layout.addWidget(action_title)

    btn_row = QHBoxLayout()
    btn_row.setSpacing(6)
    dialog._btn_draw = QPushButton()
    dialog._btn_draw.setObjectName('drawBtn')
    dialog._btn_draw.setIcon(QIcon(os.path.join(_ICON_DIR, 'draw.svg')))
    dialog._btn_draw.setToolTip('Draw')
    btn_row.addWidget(dialog._btn_draw, 1)
    dialog._btn_select = QPushButton()
    dialog._btn_select.setObjectName('selectBtn')
    dialog._btn_select.setIcon(QIcon(os.path.join(_ICON_DIR, 'select.svg')))
    dialog._btn_select.setToolTip('Select')
    btn_row.addWidget(dialog._btn_select, 1)
    dialog._btn_edit = QPushButton()
    dialog._btn_edit.setObjectName('editBtn')
    dialog._btn_edit.setIcon(QIcon(os.path.join(_ICON_DIR, 'edit.svg')))
    dialog._btn_edit.setToolTip('Edit')
    btn_row.addWidget(dialog._btn_edit, 1)
    dialog._btn_measure = QPushButton()
    dialog._btn_measure.setObjectName('mesure_dist')
    dialog._btn_measure.setIcon(QIcon(os.path.join(_ICON_DIR, 'measure.svg')))
    dialog._btn_measure.setToolTip('Measure Distance')
    btn_row.addWidget(dialog._btn_measure, 1)
    action_layout.addLayout(btn_row)

    layout.addWidget(action_frame)

    # Form Data
    form_frame = make_section_frame()
    form_layout = form_frame.layout()

    form_title = QLabel('Feature')
    form_title.setObjectName('groupBox_form_data')
    form_title.setStyleSheet('font-size: 13px; font-weight: bold;')
    form_layout.addWidget(form_title)

    dialog._form_stack = QStackedWidget()
    build_zone_form(dialog)
    build_road_form(dialog)
    build_org_form(dialog)
    build_city_form(dialog)
    build_num_form(dialog)
    build_pan_form(dialog)
    form_layout.addWidget(dialog._form_stack, stretch=1)

    layout.addWidget(form_frame, stretch=1)

    dialog._main_stack.addWidget(page)
    dialog._held_widgets.append(page)
    dialog._held_widgets.append(plan_frame)
    dialog._held_widgets.append(action_frame)
    dialog._held_widgets.append(form_frame)
