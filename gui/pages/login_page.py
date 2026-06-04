"""Login page builder for MainDialog."""

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..dialog_helpers import make_section_frame


def build_login_page(dialog) -> None:
    page = QWidget()
    page.setObjectName('login')

    layout = QVBoxLayout(page)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(0)

    section = make_section_frame()
    section_layout = section.layout()

    title = QLabel('RNA')
    title.setStyleSheet('font-size: 20px; font-weight: bold;')
    section_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

    section_layout.addSpacing(12)

    form = QFormLayout()
    form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
    form.setSpacing(8)

    dialog._field_username = QLineEdit()
    dialog._field_username.setObjectName('username')
    label = QLabel('Username:')
    label.setObjectName('label_10')
    form.addRow(label, dialog._field_username)

    dialog._field_password = QLineEdit()
    dialog._field_password.setObjectName('password')
    dialog._field_password.setEchoMode(QLineEdit.EchoMode.Password)
    label = QLabel('Password:')
    label.setObjectName('label_11')
    form.addRow(label, dialog._field_password)

    dialog._combo_map_options = QComboBox()
    dialog._combo_map_options.setObjectName('map_options')
    label = QLabel('Map:')
    label.setObjectName('label_14')
    form.addRow(label, dialog._combo_map_options)

    section_layout.addLayout(form)
    section_layout.addSpacing(12)

    dialog._btn_sign_in = QPushButton('Sign In')
    dialog._btn_sign_in.setObjectName('sign_in_user')
    section_layout.addWidget(dialog._btn_sign_in)

    dialog._btn_add_user = QPushButton('Add User')
    dialog._btn_add_user.setObjectName('add_u')
    section_layout.addWidget(dialog._btn_add_user)

    dialog._btn_restore_db = QPushButton('Restore Database')
    dialog._btn_restore_db.setObjectName('restore_db')
    section_layout.addWidget(dialog._btn_restore_db)

    section_layout.addStretch()

    layout.addWidget(section)

    dialog._page_stack.addWidget(page)
    dialog._held_widgets.append(page)
