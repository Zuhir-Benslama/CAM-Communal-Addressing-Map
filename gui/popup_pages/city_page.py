"""City (subdivision) page builder for PopupDialog."""

from typing import TYPE_CHECKING, Any

from ._builder import build_page

if TYPE_CHECKING:
    from ..popup_dialog import PopupDialog


def build_city_page(dialog: 'PopupDialog', stack: Any) -> None:
    build_page(
        dialog,
        stack,
        object_name='cityPage',
        save_kind='city',
        rows=[
            ('_combo_subd_type', 'combo', 'subd_type', 'Type:'),
            ('_field_subd_name', 'edit', 'subd_name', 'Name:'),
        ],
    )
