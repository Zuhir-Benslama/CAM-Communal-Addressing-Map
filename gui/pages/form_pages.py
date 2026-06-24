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
    w = QWidget()
    w.setObjectName('zoneForm')
    layout = QVBoxLayout(w)
    layout.setContentsMargins(0, 0, 0, 0)

    form = QFormLayout()
    form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
    form.setSpacing(6)
    dialog._combo_zone_type = QComboBox()
    dialog._combo_zone_type.setObjectName('zone_type')
    label = QLabel('Type:')
    label.setObjectName('label_25')
    form.addRow(label, dialog._combo_zone_type)
    dialog._field_nom_zone = QLineEdit()
    dialog._field_nom_zone.setObjectName('nom_zone')
    label = QLabel('Name:')
    label.setObjectName('label_28')
    form.addRow(label, dialog._field_nom_zone)
    layout.addLayout(form)

    dialog._btn_save_zone = QPushButton('Save')
    dialog._btn_save_zone.setObjectName('submit_zone')
    layout.addWidget(dialog._btn_save_zone)
    layout.addStretch()

    dialog._form_stack.addWidget(w)
    dialog._held_widgets.append(w)


def build_road_form(dialog: Any) -> None:
    w = QWidget()
    w.setObjectName('roadForm')
    layout = QVBoxLayout(w)
    layout.setContentsMargins(0, 0, 0, 0)

    form = QFormLayout()
    form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
    form.setSpacing(6)
    dialog._combo_type_road = QComboBox()
    dialog._combo_type_road.setObjectName('type_road')
    label = QLabel('Type:')
    label.setObjectName('label_25')
    form.addRow(label, dialog._combo_type_road)
    dialog._field_road_name = QLineEdit()
    dialog._field_road_name.setObjectName('road_name')
    label = QLabel('Name:')
    label.setObjectName('label_28')
    form.addRow(label, dialog._field_road_name)
    layout.addLayout(form)

    btn_row = QHBoxLayout()
    dialog._btn_list_roads = QPushButton('Roads List')
    dialog._btn_list_roads.setObjectName('list_roads')
    btn_row.addWidget(dialog._btn_list_roads, 1)
    dialog._btn_save_road = QPushButton('Save')
    dialog._btn_save_road.setObjectName('submit_road')
    btn_row.addWidget(dialog._btn_save_road, 1)
    layout.addLayout(btn_row)
    layout.addStretch()

    dialog._form_stack.addWidget(w)
    dialog._held_widgets.append(w)


def build_org_form(dialog: Any) -> None:
    w = QWidget()
    w.setObjectName('orgForm')
    layout = QVBoxLayout(w)
    layout.setContentsMargins(0, 0, 0, 0)

    form = QFormLayout()
    form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
    form.setSpacing(6)
    dialog._combo_org_cat = QComboBox()
    dialog._combo_org_cat.setObjectName('org_cat')
    label = QLabel('Category:')
    label.setObjectName('label_41')
    form.addRow(label, dialog._combo_org_cat)
    dialog._combo_org_type = QComboBox()
    dialog._combo_org_type.setObjectName('org_type')
    label = QLabel('Type:')
    label.setObjectName('label_25')
    form.addRow(label, dialog._combo_org_type)
    dialog._field_org_name = QLineEdit()
    dialog._field_org_name.setObjectName('org_name')
    label = QLabel('Name:')
    label.setObjectName('label_28')
    form.addRow(label, dialog._field_org_name)
    layout.addLayout(form)

    btn_row = QHBoxLayout()
    dialog._btn_list_orgs = QPushButton('Facilities List')
    dialog._btn_list_orgs.setObjectName('list_orgs')
    btn_row.addWidget(dialog._btn_list_orgs, 1)
    dialog._btn_save_org = QPushButton('Save')
    dialog._btn_save_org.setObjectName('submit_org')
    btn_row.addWidget(dialog._btn_save_org, 1)
    layout.addLayout(btn_row)
    layout.addStretch()

    dialog._form_stack.addWidget(w)
    dialog._held_widgets.append(w)


def build_city_form(dialog: Any) -> None:
    w = QWidget()
    w.setObjectName('cityForm')
    layout = QVBoxLayout(w)
    layout.setContentsMargins(0, 0, 0, 0)

    form = QFormLayout()
    form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
    form.setSpacing(6)
    dialog._combo_subd_type = QComboBox()
    dialog._combo_subd_type.setObjectName('subd_type')
    label = QLabel('Type:')
    label.setObjectName('label_25')
    form.addRow(label, dialog._combo_subd_type)
    dialog._field_subd_name = QLineEdit()
    dialog._field_subd_name.setObjectName('subd_name')
    label = QLabel('Name:')
    label.setObjectName('label_28')
    form.addRow(label, dialog._field_subd_name)
    layout.addLayout(form)

    btn_row = QHBoxLayout()
    dialog._btn_list_cities = QPushButton('Subdivisions List')
    dialog._btn_list_cities.setObjectName('list_subds')
    btn_row.addWidget(dialog._btn_list_cities, 1)
    dialog._btn_save_city = QPushButton('Save')
    dialog._btn_save_city.setObjectName('submit_subd')
    btn_row.addWidget(dialog._btn_save_city, 1)
    layout.addLayout(btn_row)
    layout.addStretch()

    dialog._form_stack.addWidget(w)
    dialog._held_widgets.append(w)


def build_num_form(dialog: Any) -> None:
    w = QWidget()
    w.setObjectName('numForm')
    layout = QVBoxLayout(w)
    layout.setContentsMargins(0, 0, 0, 0)

    form = QFormLayout()
    form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
    form.setSpacing(6)
    dialog._combo_road_ref = QComboBox()
    dialog._combo_road_ref.setObjectName('road_ref')
    label = QLabel('Ref Type:')
    label.setObjectName('label_36')
    form.addRow(label, dialog._combo_road_ref)

    dialog._btn_select_road_ref = QPushButton('Select Reference')
    dialog._btn_select_road_ref.setObjectName('select_road_ref')
    form.addRow(dialog._btn_select_road_ref)
    dialog._field_num_val = QLineEdit()
    dialog._field_num_val.setObjectName('num_val')
    label = QLabel('Number:')
    label.setObjectName('label_34')
    form.addRow(label, dialog._field_num_val)
    dialog._field_repetition = QLineEdit()
    dialog._field_repetition.setObjectName('repetition')
    label = QLabel('Duplicated:')
    label.setObjectName('label_38')
    form.addRow(label, dialog._field_repetition)
    dialog._combo_num_state = QComboBox()
    dialog._combo_num_state.setObjectName('num_state')
    label = QLabel('State:')
    label.setObjectName('label_16')
    form.addRow(label, dialog._combo_num_state)
    dialog._combo_activity_cat = QComboBox()
    dialog._combo_activity_cat.setObjectName('activity_cat')
    label = QLabel('Activity Cat:')
    label.setObjectName('label_35')
    form.addRow(label, dialog._combo_activity_cat)
    dialog._combo_activity_type = QComboBox()
    dialog._combo_activity_type.setObjectName('activity_type')
    label = QLabel('Activity Type:')
    label.setObjectName('label_36_act_type')
    form.addRow(label, dialog._combo_activity_type)
    layout.addLayout(form)

    btn_row = QHBoxLayout()
    dialog._btn_list_nums = QPushButton('Entrances List')
    dialog._btn_list_nums.setObjectName('list_nums')
    btn_row.addWidget(dialog._btn_list_nums, 1)
    dialog._btn_save_num = QPushButton('Save')
    dialog._btn_save_num.setObjectName('submit_num')
    btn_row.addWidget(dialog._btn_save_num, 1)
    layout.addLayout(btn_row)
    layout.addStretch()

    dialog._form_stack.addWidget(w)
    dialog._held_widgets.append(w)


def build_pan_form(dialog: Any) -> None:
    w = QWidget()
    w.setObjectName('panForm')
    layout = QVBoxLayout(w)
    layout.setContentsMargins(0, 0, 0, 0)

    form = QFormLayout()
    form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
    form.setSpacing(6)
    dialog._combo_mount_status = QComboBox()
    dialog._combo_mount_status.setObjectName('mount_status')
    label = QLabel('Mount Status:')
    label.setObjectName('label_30')
    form.addRow(label, dialog._combo_mount_status)
    dialog._combo_panel_ref = QComboBox()
    dialog._combo_panel_ref.setObjectName('panel_ref')
    label = QLabel('Ref Type:')
    label.setObjectName('label_40')
    form.addRow(label, dialog._combo_panel_ref)

    dialog._btn_select_panel_ref = QPushButton('Select Reference')
    dialog._btn_select_panel_ref.setObjectName('select_panel_ref')
    form.addRow(dialog._btn_select_panel_ref)

    layout.addLayout(form)

    btn_row = QHBoxLayout()
    dialog._btn_list_panels = QPushButton('Panels List')
    dialog._btn_list_panels.setObjectName('list_panels')
    btn_row.addWidget(dialog._btn_list_panels, 1)
    dialog._btn_save_pan = QPushButton('Save')
    dialog._btn_save_pan.setObjectName('submit_pan')
    btn_row.addWidget(dialog._btn_save_pan, 1)
    layout.addLayout(btn_row)
    layout.addStretch()

    dialog._form_stack.addWidget(w)
    dialog._held_widgets.append(w)
