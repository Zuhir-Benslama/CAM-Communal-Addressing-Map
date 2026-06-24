"""Numbering page builder for PopupDialog."""

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


def build_num_page(dialog: 'PopupDialog', stack: Any) -> None:
    w = QWidget()
    w.setObjectName('numPage')
    layout = QVBoxLayout(w)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(12)

    form = QFormLayout()
    form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
    form.setSpacing(8)

    dialog._combo_road_ref = QComboBox()
    dialog._combo_road_ref.setObjectName('road_ref')
    form.addRow('Ref Type:', dialog._combo_road_ref)

    dialog._btn_select_ref = QPushButton('Select Reference')
    form.addRow(dialog._btn_select_ref)

    dialog._field_num_val = QLineEdit()
    dialog._field_num_val.setObjectName('num_val')
    form.addRow('Number:', dialog._field_num_val)

    dialog._field_repetition = QLineEdit()
    dialog._field_repetition.setObjectName('repetition')
    form.addRow('Duplicated:', dialog._field_repetition)

    dialog._combo_num_state = QComboBox()
    dialog._combo_num_state.setObjectName('num_state')
    form.addRow('State:', dialog._combo_num_state)

    dialog._combo_activity_cat = QComboBox()
    dialog._combo_activity_cat.setObjectName('activity_cat')
    form.addRow('Activity Cat:', dialog._combo_activity_cat)

    dialog._combo_activity_type = QComboBox()
    dialog._combo_activity_type.setObjectName('activity_type')
    form.addRow('Activity Type:', dialog._combo_activity_type)

    layout.addLayout(form)
    layout.addStretch()

    btn = QPushButton('Save')
    btn.clicked.connect(lambda: dialog._on_save('num'))
    layout.addWidget(btn)

    stack.addWidget(w)
