"""Individual form page builders (zone, road, org, city, num, pan)."""

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

from ..form_specs import (
    CITY_ROWS,
    NUM_ROWS,
    ORG_ROWS,
    PAN_ROWS,
    ROAD_ROWS,
    ZONE_ROWS,
    FieldRow,
)

if TYPE_CHECKING:
    from .main_dialog import MainDialog


def build_zone_form(dialog: MainDialog) -> None:
    _build_entity_form(dialog, 'zone', ZONE_ROWS)


def build_road_form(dialog: MainDialog) -> None:
    _build_entity_form(dialog, 'road', ROAD_ROWS)


def build_org_form(dialog: MainDialog) -> None:
    _build_entity_form(dialog, 'org', ORG_ROWS)


def build_city_form(dialog: MainDialog) -> None:
    _build_entity_form(dialog, 'city', CITY_ROWS)


def build_num_form(dialog: MainDialog) -> None:
    _build_entity_form(dialog, 'num', NUM_ROWS)


def build_pan_form(dialog: MainDialog) -> None:
    _build_entity_form(dialog, 'pan', PAN_ROWS)


def _build_entity_form(
    dialog: MainDialog,
    name: str,
    rows: list[FieldRow],
) -> None:
    w = QWidget()
    w.setObjectName(f'{name}Form')
    layout = QVBoxLayout(w)
    layout.setContentsMargins(0, 0, 0, 0)

    form = QFormLayout()
    form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
    form.setSpacing(6)

    for row in rows:
        if row.kind == 'combo':
            widget: QComboBox | QLineEdit | QPushButton = QComboBox()
        elif row.kind == 'text':
            widget = QLineEdit()
        else:
            widget = QPushButton(row.label)
        widget.setObjectName(row.obj_name)
        setattr(dialog, row.main_attr, widget)
        if row.kind == 'button':
            form.addRow(widget)
            continue

        label = QLabel(row.label)
        label.setObjectName(row.label_obj)
        form.addRow(label, widget)

    layout.addLayout(form)

    buttons = _BUTTONS[name]
    btn_row = QHBoxLayout()
    for attr, obj_name, text in buttons:
        btn = QPushButton(text)
        btn.setObjectName(obj_name)
        btn_row.addWidget(btn, 1)
        setattr(dialog, attr, btn)
    layout.addLayout(btn_row)

    layout.addStretch()
    dialog._form_stack.addWidget(w)
    dialog._held_widgets.append(w)


_BUTTONS: dict[str, list[tuple[str, str, str]]] = {
    'zone': [('_btn_save_zone', 'submit_zone', 'Save')],
    'road': [
        ('_btn_list_roads', 'list_roads', 'Roads List'),
        ('_btn_save_road', 'submit_road', 'Save'),
    ],
    'org': [
        ('_btn_list_orgs', 'list_orgs', 'Facilities List'),
        ('_btn_save_org', 'submit_org', 'Save'),
    ],
    'city': [
        ('_btn_list_cities', 'list_subds', 'Subdivisions List'),
        ('_btn_save_city', 'submit_subd', 'Save'),
    ],
    'num': [
        ('_btn_list_nums', 'list_nums', 'Entrances List'),
        ('_btn_save_num', 'submit_num', 'Save'),
    ],
    'pan': [
        ('_btn_list_panels', 'list_panels', 'Panels List'),
        ('_btn_save_pan', 'submit_pan', 'Save'),
    ],
}
