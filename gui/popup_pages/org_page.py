"""Organization page builder for PopupDialog."""

from typing import TYPE_CHECKING

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from ..popup_dialog import PopupDialog


def build_org_page(dialog: 'PopupDialog', stack) -> None:
    w = QWidget()
    w.setObjectName('orgPage')
    layout = QVBoxLayout(w)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(12)

    form = QFormLayout()
    form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
    form.setSpacing(8)

    dialog._combo_org_cat = QComboBox()
    dialog._combo_org_cat.setObjectName('org_cat')
    form.addRow('Category:', dialog._combo_org_cat)

    dialog._combo_org_type = QComboBox()
    dialog._combo_org_type.setObjectName('org_type')
    form.addRow('Type:', dialog._combo_org_type)

    dialog._field_org_name = QLineEdit()
    dialog._field_org_name.setObjectName('org_name')
    form.addRow('Name:', dialog._field_org_name)

    layout.addLayout(form)
    layout.addStretch()

    btn = QPushButton('Save')
    btn.clicked.connect(lambda: dialog._on_save('org'))
    layout.addWidget(btn)

    stack.addWidget(w)
