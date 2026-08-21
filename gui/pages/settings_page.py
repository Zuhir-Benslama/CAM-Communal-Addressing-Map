"""Settings page builder for MainDialog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qgis.PyQt.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..dialog_helpers import add_form_row, make_section_frame

if TYPE_CHECKING:
    from .main_dialog import MainDialog


def _section_title(layout: QVBoxLayout, text: str, obj_name: str) -> None:
    """Add a bold section title to the given layout."""
    title = QLabel(text)
    title.setObjectName(obj_name)
    title.setStyleSheet('font-size: 13px; font-weight: bold;')
    layout.addWidget(title)


def _build_maps_reports_section(dialog: MainDialog, s_layout: QVBoxLayout) -> None:
    """Build the 'Maps, Reports and Backup' section."""
    section = make_section_frame()
    sl = section.layout()
    _section_title(sl, 'Maps, Reports and Backup', 'groupBox_3')

    dialog._combo_action = QComboBox()
    dialog._combo_action.setObjectName('_action_combo')
    sl.addWidget(dialog._combo_action)

    dialog._combo_paper = QComboBox()
    dialog._combo_paper.setObjectName('paper')
    dialog._combo_paper.setVisible(False)
    sl.addWidget(dialog._combo_paper)

    dialog._btn_save_action = QPushButton('Save')
    dialog._btn_save_action.setObjectName('print')
    sl.addWidget(dialog._btn_save_action)

    s_layout.addWidget(section)
    dialog._held_widgets.append(section)


def _build_add_feature_section(dialog: MainDialog, s_layout: QVBoxLayout) -> None:
    """Build the 'Add New Feature' section."""
    section = make_section_frame()
    sl = section.layout()
    _section_title(sl, 'Add New Feature', 'groupBox_add_types')

    nf_form = QFormLayout()
    nf_form.setSpacing(6)
    dialog.feature_combo = QComboBox()
    dialog.feature_combo.setObjectName('feature_combo')
    add_form_row(nf_form, 'Category:', 'label_feature', dialog.feature_combo)
    dialog.subtype_combo = QComboBox()
    dialog.subtype_combo.setObjectName('subtype_combo')
    dialog.subtype_combo.setEditable(True)
    add_form_row(nf_form, 'Type:', 'label_type', dialog.subtype_combo)
    dialog._label_subtype = QLabel('Subtype:')
    dialog._label_subtype.setObjectName('label_subtype')
    dialog._field_new_type = QLineEdit()
    dialog._field_new_type.setObjectName('new_type')
    nf_form.addRow(dialog._label_subtype, dialog._field_new_type)
    sl.addLayout(nf_form)

    dialog._btn_save_new_type = QPushButton('Save')
    dialog._btn_save_new_type.setObjectName('add_type_btn')
    sl.addWidget(dialog._btn_save_new_type)

    s_layout.addWidget(section)
    dialog._held_widgets.append(section)


def _build_theme_locale_section(
    dialog: MainDialog,
    s_layout: QVBoxLayout,
) -> QWidget:
    """Build the 'Theme and Language' section and return it."""
    section = make_section_frame()
    sl = section.layout()
    _section_title(sl, 'Theme and Language', '_settings_group')

    tl_form = QFormLayout()
    tl_form.setSpacing(6)
    dialog._combo_theme = QComboBox()
    dialog._combo_theme.setObjectName('_theme_combo')
    add_form_row(tl_form, 'Theme:', '_theme_label', dialog._combo_theme)
    dialog._combo_locale = QComboBox()
    dialog._combo_locale.setObjectName('_locale_combo')
    add_form_row(tl_form, 'Language:', '_locale_label', dialog._combo_locale)
    sl.addLayout(tl_form)

    s_layout.addWidget(section)
    return section


def build_settings_page(dialog: MainDialog) -> None:
    """Build the settings page and register it on the dialog."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setObjectName('settingsTab')
    content = QWidget()
    content.setObjectName('settingsContent')
    scroll.setWidget(content)
    s_layout = QVBoxLayout(content)
    s_layout.setContentsMargins(8, 8, 8, 8)
    s_layout.setSpacing(12)

    _build_maps_reports_section(dialog, s_layout)
    _build_add_feature_section(dialog, s_layout)
    theme_section = _build_theme_locale_section(dialog, s_layout)
    s_layout.addStretch()

    dialog._main_stack.addWidget(scroll)
    dialog._held_widgets.append(scroll)
    dialog._held_widgets.append(content)
    dialog._held_widgets.append(theme_section)
