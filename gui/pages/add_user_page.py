"""Add user page builder for MainDialog."""

from typing import Any

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


def build_add_user_page(dialog: Any) -> None:
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
    form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
    form.setSpacing(6)

    dialog._field_fname = QLineEdit()
    dialog._field_fname.setObjectName('fname')
    label = QLabel('First Name:')
    label.setObjectName('label_3')
    form.addRow(label, dialog._field_fname)

    dialog._field_lname = QLineEdit()
    dialog._field_lname.setObjectName('lname')
    label = QLabel('Last Name:')
    label.setObjectName('label_7')
    form.addRow(label, dialog._field_lname)

    dialog._field_email = QLineEdit()
    dialog._field_email.setObjectName('email')
    label = QLabel('Email:')
    label.setObjectName('label_8')
    form.addRow(label, dialog._field_email)

    dialog._field_pnum = QLineEdit()
    dialog._field_pnum.setObjectName('pnum')
    label = QLabel('Phone:')
    label.setObjectName('label_9')
    form.addRow(label, dialog._field_pnum)

    dialog._field_uname = QLineEdit()
    dialog._field_uname.setObjectName('uname')
    label = QLabel('Username:')
    label.setObjectName('label_2_username')
    form.addRow(label, dialog._field_uname)

    dialog._field_pwd = QLineEdit()
    dialog._field_pwd.setObjectName('pwd')
    dialog._field_pwd.setEchoMode(QLineEdit.EchoMode.Password)
    label = QLabel('Password:')
    label.setObjectName('label_5')
    form.addRow(label, dialog._field_pwd)

    dialog.wilaya_list = QComboBox()
    dialog.wilaya_list.setObjectName('wilaya_list')
    label = QLabel('Wilaya:')
    label.setObjectName('label_12')
    form.addRow(label, dialog.wilaya_list)

    dialog.commune_of_wilaya = QComboBox()
    dialog.commune_of_wilaya.setObjectName('commune_of_wilaya')
    label = QLabel('Commune:')
    label.setObjectName('label_13')
    form.addRow(label, dialog.commune_of_wilaya)

    layout.addLayout(form)
    layout.addSpacing(12)

    btn_row = QHBoxLayout()
    dialog._btn_cancel_add = QPushButton('Cancel')
    dialog._btn_cancel_add.setObjectName('abort_uc')
    btn_row.addWidget(dialog._btn_cancel_add, 1)
    dialog._btn_save_add = QPushButton('Save')
    dialog._btn_save_add.setObjectName('submit_usr')
    btn_row.addWidget(dialog._btn_save_add, 1)
    layout.addLayout(btn_row)

    layout.addStretch()

    dialog._page_stack.addWidget(page)
    dialog._held_widgets.append(page)
