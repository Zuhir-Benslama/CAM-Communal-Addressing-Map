"""Panel sign page builder for PopupDialog."""

from typing import TYPE_CHECKING, Any

from ._builder import build_page

if TYPE_CHECKING:
    from ..popup_dialog import PopupDialog


def build_pan_page(dialog: 'PopupDialog', stack: Any) -> None:
    build_page(
        dialog,
        stack,
        object_name='panPage',
        save_kind='pan',
        rows=[
            ('_combo_mount_status', 'combo', 'mount_status', 'Mount Status:'),
            ('_combo_panel_ref', 'combo', 'panel_ref', 'Ref Type:'),
            ('_btn_select_panel_ref', 'button', '', 'Select Reference'),
        ],
    )
