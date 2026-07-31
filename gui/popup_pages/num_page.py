"""Numbering page builder for PopupDialog."""

from typing import TYPE_CHECKING, Any

from ._builder import build_page

if TYPE_CHECKING:
    from ..popup_dialog import PopupDialog


def build_num_page(dialog: 'PopupDialog', stack: Any) -> None:
    build_page(
        dialog,
        stack,
        object_name='numPage',
        save_kind='num',
        rows=[
            ('_combo_road_ref', 'combo', 'road_ref', 'Ref Type:'),
            ('_btn_select_ref', 'button', '', 'Select Reference'),
            ('_field_num_val', 'edit', 'num_val', 'Number:'),
            ('_field_repetition', 'edit', 'repetition', 'Duplicated:'),
            ('_combo_num_state', 'combo', 'num_state', 'State:'),
            ('_combo_activity_cat', 'combo', 'activity_cat', 'Activity Cat:'),
            ('_combo_activity_type', 'combo', 'activity_type', 'Activity Type:'),
        ],
    )
