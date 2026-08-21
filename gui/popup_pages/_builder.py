"""Shared parametrized builder for popup form pages."""

from typing import TYPE_CHECKING

from qgis.PyQt.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ...scripts.widget_texts import get_string

if TYPE_CHECKING:
    from ..popup_dialog import PopupDialog


def build_page(
    dialog: 'PopupDialog',
    stack: QStackedWidget,
    *,
    object_name: str,
    save_kind: str,
    rows: list[tuple[str, str, str, str]],
) -> None:
    """Build a form page with the given rows and a Save button.

    Each row is ``(attr, kind, object_name, label)`` where *kind* is
    ``'combo'``, ``'edit'``, or ``'button'``. For ``'button'`` rows the
    label is used as the button text and no form label is rendered.
    """
    w = QWidget()
    w.setObjectName(object_name)
    layout = QVBoxLayout(w)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(12)

    form = QFormLayout()
    form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
    form.setSpacing(8)

    loc = dialog._tr_locale
    for attr, kind, obj_name, label in rows:
        if kind == 'combo':
            widget = QComboBox()
        elif kind == 'edit':
            widget = QLineEdit()
        else:
            widget = QPushButton(get_string(label, loc))
        if obj_name:
            widget.setObjectName(obj_name)
        setattr(dialog, attr, widget)
        if kind == 'button':
            form.addRow(widget)
        else:
            form.addRow(get_string(label, loc), widget)

    layout.addLayout(form)
    layout.addStretch()

    btn = QPushButton(get_string('Save', loc))
    btn.clicked.connect(lambda: dialog._on_save(save_kind))
    layout.addWidget(btn)

    stack.addWidget(w)
