"""Individual form page builders (zone, road, org, city, num, pan)."""

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


def build_zone_form(dialog: Any) -> None:
    _build_entity_form(dialog, _ZONE_CONFIG)


def build_road_form(dialog: Any) -> None:
    _build_entity_form(dialog, _ROAD_CONFIG)


def build_org_form(dialog: Any) -> None:
    _build_entity_form(dialog, _ORG_CONFIG)


def build_city_form(dialog: Any) -> None:
    _build_entity_form(dialog, _CITY_CONFIG)


def build_num_form(dialog: Any) -> None:
    _build_entity_form(dialog, _NUM_CONFIG)


def build_pan_form(dialog: Any) -> None:
    _build_entity_form(dialog, _PAN_CONFIG)


_FORM_CONFIG = tuple[
    str, list[tuple[str, str, str, str, str]], list[tuple[str, str, str]]
]


def _build_entity_form(dialog: Any, config: _FORM_CONFIG) -> None:
    name, fields, buttons = config
    w = QWidget()
    w.setObjectName(f'{name}Form')
    layout = QVBoxLayout(w)
    layout.setContentsMargins(0, 0, 0, 0)

    form = QFormLayout()
    form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
    form.setSpacing(6)

    for kind, attr, obj_name, label_text, label_obj in fields:
        if kind == 'combo':
            widget: QComboBox | QLineEdit | QPushButton = QComboBox()
        elif kind == 'text':
            widget = QLineEdit()
        elif kind == 'ref_button':
            widget = QPushButton(label_text)
            widget.setObjectName(obj_name)
            setattr(dialog, attr, widget)
            form.addRow(widget)
            continue

        widget.setObjectName(obj_name)
        label = QLabel(label_text)
        label.setObjectName(label_obj)
        form.addRow(label, widget)
        setattr(dialog, attr, widget)

    layout.addLayout(form)

    if buttons:
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


_ZONE_CONFIG: _FORM_CONFIG = (
    'zone',
    [
        ('combo', '_combo_zone_type', 'zone_type', 'Type:', 'label_25'),
        ('text', '_field_nom_zone', 'nom_zone', 'Name:', 'label_28'),
    ],
    [
        ('_btn_save_zone', 'submit_zone', 'Save'),
    ],
)

_ROAD_CONFIG: _FORM_CONFIG = (
    'road',
    [
        ('combo', '_combo_type_road', 'type_road', 'Type:', 'label_25'),
        ('text', '_field_road_name', 'road_name', 'Name:', 'label_28'),
    ],
    [
        ('_btn_list_roads', 'list_roads', 'Roads List'),
        ('_btn_save_road', 'submit_road', 'Save'),
    ],
)

_ORG_CONFIG: _FORM_CONFIG = (
    'org',
    [
        ('combo', '_combo_org_cat', 'org_cat', 'Category:', 'label_41'),
        ('combo', '_combo_org_type', 'org_type', 'Type:', 'label_25'),
        ('text', '_field_org_name', 'org_name', 'Name:', 'label_28'),
    ],
    [
        ('_btn_list_orgs', 'list_orgs', 'Facilities List'),
        ('_btn_save_org', 'submit_org', 'Save'),
    ],
)

_CITY_CONFIG: _FORM_CONFIG = (
    'city',
    [
        ('combo', '_combo_subd_type', 'subd_type', 'Type:', 'label_25'),
        ('text', '_field_subd_name', 'subd_name', 'Name:', 'label_28'),
    ],
    [
        ('_btn_list_cities', 'list_subds', 'Subdivisions List'),
        ('_btn_save_city', 'submit_subd', 'Save'),
    ],
)

_NUM_CONFIG: _FORM_CONFIG = (
    'num',
    [
        ('combo', '_combo_road_ref', 'road_ref', 'Ref Type:', 'label_36'),
        (
            'ref_button',
            '_btn_select_road_ref',
            'select_road_ref',
            'Select Reference',
            '',
        ),
        ('text', '_field_num_val', 'num_val', 'Number:', 'label_34'),
        ('text', '_field_repetition', 'repetition', 'Duplicated:', 'label_38'),
        ('combo', '_combo_num_state', 'num_state', 'State:', 'label_16'),
        ('combo', '_combo_activity_cat', 'activity_cat', 'Activity Cat:', 'label_35'),
        (
            'combo',
            '_combo_activity_type',
            'activity_type',
            'Activity Type:',
            'label_36_act_type',
        ),
    ],
    [
        ('_btn_list_nums', 'list_nums', 'Entrances List'),
        ('_btn_save_num', 'submit_num', 'Save'),
    ],
)

_PAN_CONFIG: _FORM_CONFIG = (
    'pan',
    [
        ('combo', '_combo_mount_status', 'mount_status', 'Mount Status:', 'label_30'),
        ('combo', '_combo_panel_ref', 'panel_ref', 'Ref Type:', 'label_40'),
        (
            'ref_button',
            '_btn_select_panel_ref',
            'select_panel_ref',
            'Select Reference',
            '',
        ),
    ],
    [
        ('_btn_list_panels', 'list_panels', 'Panels List'),
        ('_btn_save_pan', 'submit_pan', 'Save'),
    ],
)
