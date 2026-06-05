"""Panel sign page builder for PopupDialog."""

from typing import TYPE_CHECKING

from qgis.PyQt.QtWidgets import (
    QComboBox,
    QFormLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from ..popup_dialog import PopupDialog


def build_pan_page(dialog: 'PopupDialog', stack) -> None:
    w = QWidget()
    w.setObjectName('panPage')
    layout = QVBoxLayout(w)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(12)

    form = QFormLayout()
    form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
    form.setSpacing(8)

    dialog._combo_mount_status = QComboBox()
    dialog._combo_mount_status.setObjectName('mount_status')
    form.addRow('Mount Status:', dialog._combo_mount_status)

    dialog._combo_panel_ref = QComboBox()
    dialog._combo_panel_ref.setObjectName('panel_ref')
    form.addRow('Ref Type:', dialog._combo_panel_ref)

    dialog._btn_select_panel_ref = QPushButton('Select Reference')
    form.addRow(dialog._btn_select_panel_ref)

    layout.addLayout(form)
    layout.addStretch()

    btn = QPushButton('Save')
    btn.clicked.connect(lambda: dialog._on_save('pan'))
    layout.addWidget(btn)

    stack.addWidget(w)
