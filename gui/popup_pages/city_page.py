"""City (subdivision) page builder for PopupDialog."""

from typing import TYPE_CHECKING, Any

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


def build_city_page(dialog: 'PopupDialog', stack: Any) -> None:
    w = QWidget()
    w.setObjectName('cityPage')
    layout = QVBoxLayout(w)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(12)

    form = QFormLayout()
    form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
    form.setSpacing(8)

    dialog._combo_subd_type = QComboBox()
    dialog._combo_subd_type.setObjectName('subd_type')
    form.addRow('Type:', dialog._combo_subd_type)

    dialog._field_subd_name = QLineEdit()
    dialog._field_subd_name.setObjectName('subd_name')
    form.addRow('Name:', dialog._field_subd_name)

    layout.addLayout(form)
    layout.addStretch()

    btn = QPushButton('Save')
    btn.clicked.connect(lambda: dialog._on_save('city'))
    layout.addWidget(btn)

    stack.addWidget(w)
