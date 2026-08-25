"""Declarative field specs shared by the main-window forms and popup pages.

Each row describes one form field. ``main_attr``/``popup_attr`` name the
attribute set on :class:`~gui.main_dialog.MainDialog` and
:class:`~gui.popup_dialog.PopupDialog` respectively (they differ for a few
legacy widget names). ``label_obj`` is the QLabel objectName used by the
main-window QSS; it is unused by the popup pages.
"""

from typing import NamedTuple


class FieldRow(NamedTuple):
    """One form field row shared by both form builders."""

    kind: str  # 'combo' | 'text' | 'button'
    obj_name: str  # Qt objectName ('' for buttons)
    label: str  # display label ('' rendered as-is for buttons)
    main_attr: str  # attribute on MainDialog
    popup_attr: str  # attribute on PopupDialog
    label_obj: str = ''  # QLabel objectName (main window only)


ZONE_ROWS = [
    FieldRow(
        'combo',
        'zone_type',
        'Type:',
        '_combo_zone_type',
        '_combo_zone_type',
        'label_25',
    ),
    FieldRow(
        'text', 'nom_zone', 'Name:', '_field_nom_zone', '_field_zone_name', 'label_28'
    ),
]

ROAD_ROWS = [
    FieldRow(
        'combo',
        'type_road',
        'Type:',
        '_combo_type_road',
        '_combo_road_type',
        'label_25',
    ),
    FieldRow(
        'text', 'road_name', 'Name:', '_field_road_name', '_field_road_name', 'label_28'
    ),
]

ORG_ROWS = [
    FieldRow(
        'combo', 'org_cat', 'Category:', '_combo_org_cat', '_combo_org_cat', 'label_41'
    ),
    FieldRow(
        'combo', 'org_type', 'Type:', '_combo_org_type', '_combo_org_type', 'label_25'
    ),
    FieldRow(
        'text', 'org_name', 'Name:', '_field_org_name', '_field_org_name', 'label_28'
    ),
]

CITY_ROWS = [
    FieldRow(
        'combo',
        'subd_type',
        'Type:',
        '_combo_subd_type',
        '_combo_subd_type',
        'label_25',
    ),
    FieldRow(
        'text', 'subd_name', 'Name:', '_field_subd_name', '_field_subd_name', 'label_28'
    ),
]

NUM_ROWS = [
    FieldRow(
        'combo',
        'road_ref',
        'Ref Type:',
        '_combo_road_ref',
        '_combo_road_ref',
        'label_36',
    ),
    FieldRow(
        'button', '', 'Select Reference', '_btn_select_road_ref', '_btn_select_ref'
    ),
    FieldRow(
        'text', 'num_val', 'Number:', '_field_num_val', '_field_num_val', 'label_34'
    ),
    FieldRow(
        'text',
        'repetition',
        'Duplicated:',
        '_field_repetition',
        '_field_repetition',
        'label_38',
    ),
    FieldRow(
        'combo',
        'num_state',
        'State:',
        '_combo_num_state',
        '_combo_num_state',
        'label_16',
    ),
    FieldRow(
        'combo',
        'activity_cat',
        'Activity Cat:',
        '_combo_activity_cat',
        '_combo_activity_cat',
        'label_35',
    ),
    FieldRow(
        'combo',
        'activity_type',
        'Activity Type:',
        '_combo_activity_type',
        '_combo_activity_type',
        'label_36_act_type',
    ),
]

PAN_ROWS = [
    FieldRow(
        'combo',
        'mount_status',
        'Mount Status:',
        '_combo_mount_status',
        '_combo_mount_status',
        'label_30',
    ),
    FieldRow(
        'combo',
        'panel_ref',
        'Ref Type:',
        '_combo_panel_ref',
        '_combo_panel_ref',
        'label_40',
    ),
    FieldRow(
        'button',
        '',
        'Select Reference',
        '_btn_select_panel_ref',
        '_btn_select_panel_ref',
    ),
]
