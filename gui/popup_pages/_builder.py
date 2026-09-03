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
from ..form_specs import FieldRow
from ._specs import PAGE_SPECS

if TYPE_CHECKING:
    from ..popup_dialog import PopupDialog


def build_named_page(
    dialog: 'PopupDialog',
    stack: QStackedWidget,
    *,
    name: str,
) -> None:
    """Build the popup form page identified by *name*.

    The page's object name, save kind, and field rows come from
    :data:`_specs.PAGE_SPECS` — see :mod:`gui.form_specs`.
    """
    spec = PAGE_SPECS[name]
    _build_page(
        dialog,
        stack,
        object_name=spec['object_name'],
        save_kind=spec['save_kind'],
        rows=spec['rows'],
    )


def build_all_pages(dialog: 'PopupDialog', stack: QStackedWidget) -> None:
    """Build every popup form page in spec order."""
    for name in PAGE_SPECS:
        build_named_page(dialog, stack, name=name)


def _build_page(
    dialog: 'PopupDialog',
    stack: QStackedWidget,
    *,
    object_name: str,
    save_kind: str,
    rows: list[FieldRow],
) -> None:
    """Build a form page with the given rows and a Save button.

    Rows come from :mod:`gui.form_specs`; ``popup_attr`` names the
    attribute set on the dialog. ``'button'`` rows render as a bare
    button (no label) inside the form.
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
    for row in rows:
        if row.kind == 'combo':
            widget = QComboBox()
        elif row.kind == 'text':
            widget = QLineEdit()
        else:
            widget = QPushButton(get_string(row.label, loc))
        if row.obj_name:
            widget.setObjectName(row.obj_name)
        setattr(dialog, row.popup_attr, widget)
        if row.kind == 'button':
            form.addRow(widget)
        else:
            form.addRow(get_string(row.label, loc), widget)

    layout.addLayout(form)
    layout.addStretch()

    btn = QPushButton(get_string('Save', loc))
    btn.clicked.connect(lambda: dialog._on_save(save_kind))
    layout.addWidget(btn)

    stack.addWidget(w)
