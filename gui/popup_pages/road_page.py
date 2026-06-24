"""Road page builder for PopupDialog."""

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


def build_road_page(dialog: 'PopupDialog', stack: Any) -> None:
    w = QWidget()
    w.setObjectName('roadPage')
    layout = QVBoxLayout(w)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(12)

    form = QFormLayout()
    form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
    form.setSpacing(8)

    dialog._combo_road_type = QComboBox()
    dialog._combo_road_type.setObjectName('type_road')
    form.addRow('Type:', dialog._combo_road_type)

    dialog._field_road_name = QLineEdit()
    dialog._field_road_name.setObjectName('road_name')
    form.addRow('Name:', dialog._field_road_name)

    layout.addLayout(form)
    layout.addStretch()

    btn = QPushButton('Save')
    btn.clicked.connect(lambda: dialog._on_save('roads'))
    layout.addWidget(btn)

    stack.addWidget(w)
