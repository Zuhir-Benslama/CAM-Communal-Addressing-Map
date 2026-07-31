"""Road page builder for PopupDialog."""

from typing import TYPE_CHECKING, Any

from ._builder import build_page

if TYPE_CHECKING:
    from ..popup_dialog import PopupDialog


def build_road_page(dialog: 'PopupDialog', stack: Any) -> None:
    build_page(
        dialog,
        stack,
        object_name='roadPage',
        save_kind='roads',
        rows=[
            ('_combo_road_type', 'combo', 'type_road', 'Type:'),
            ('_field_road_name', 'edit', 'road_name', 'Name:'),
        ],
    )
