"""Add user page builder for MainDialog."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qgis.PyQt.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..dialog_helpers import add_form_row

if TYPE_CHECKING:
    from .main_dialog import MainDialog

# (dialog attribute, object name, label text, label object name)
_TEXT_FIELD_ROWS = [
    ('_field_fname', 'fname', 'First Name:', 'label_3'),
    ('_field_lname', 'lname', 'Last Name:', 'label_7'),
    ('_field_email', 'email', 'Email:', 'label_8'),
    ('_field_pnum', 'pnum', 'Phone:', 'label_9'),
    ('_field_uname', 'uname', 'Username:', 'label_2_username'),
]


def _add_text_fields(dialog: MainDialog, form: QFormLayout) -> None:
    """Append the plain text fields (names, email, phone, username)."""
    for attr, obj_name, label_text, label_obj in _TEXT_FIELD_ROWS:
        field = QLineEdit()
        field.setObjectName(obj_name)
        setattr(dialog, attr, field)
        add_form_row(form, label_text, label_obj, field)


def _add_password_field(dialog: MainDialog, form: QFormLayout) -> None:
    """Append the masked password field."""
    field = QLineEdit()
    field.setObjectName('pwd')
    field.setEchoMode(QLineEdit.EchoMode.Password)
    dialog._field_pwd = field
    add_form_row(form, 'Password:', 'label_5', field)


def _add_location_fields(dialog: MainDialog, form: QFormLayout) -> None:
    """Append the wilaya / commune combo boxes."""
    dialog.wilaya_list = QComboBox()
    dialog.wilaya_list.setObjectName('wilaya_list')
    add_form_row(form, 'Wilaya:', 'label_12', dialog.wilaya_list)

    dialog.commune_of_wilaya = QComboBox()
    dialog.commune_of_wilaya.setObjectName('commune_of_wilaya')
    add_form_row(form, 'Commune:', 'label_13', dialog.commune_of_wilaya)


def _add_action_buttons(dialog: MainDialog, layout: QVBoxLayout) -> None:
    """Append the Cancel / Save button row."""
    btn_row = QHBoxLayout()
    dialog._btn_cancel_add = QPushButton('Cancel')
    dialog._btn_cancel_add.setObjectName('abort_uc')
    btn_row.addWidget(dialog._btn_cancel_add, 1)
    dialog._btn_save_add = QPushButton('Save')
    dialog._btn_save_add.setObjectName('submit_usr')
    btn_row.addWidget(dialog._btn_save_add, 1)
    layout.addLayout(btn_row)


def build_add_user_page(dialog: MainDialog) -> None:
    """Build the Add User page and register it on the dialog."""
    page = QWidget()
    page.setObjectName('add_usr')
    layout = QVBoxLayout(page)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(8)

    title = QLabel('Add User')
    title.setObjectName('add_u')
    title.setStyleSheet('font-size: 18px; font-weight: bold;')
    layout.addWidget(title)

    form = QFormLayout()
    form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
    form.setSpacing(6)
    _add_text_fields(dialog, form)
    _add_password_field(dialog, form)
    _add_location_fields(dialog, form)

    layout.addLayout(form)
    layout.addSpacing(12)
    _add_action_buttons(dialog, layout)

    layout.addStretch()

    dialog._page_stack.addWidget(page)
    dialog._held_widgets.append(page)
