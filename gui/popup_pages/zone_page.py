"""Zone page builder for PopupDialog."""

from typing import TYPE_CHECKING, Any

from ._builder import build_page

if TYPE_CHECKING:
    from ..popup_dialog import PopupDialog


def build_zone_page(dialog: 'PopupDialog', stack: Any) -> None:
    build_page(
        dialog,
        stack,
        object_name='zonePage',
        save_kind='zone',
        rows=[
            ('_combo_zone_type', 'combo', 'zone_type', 'Type:'),
            ('_field_zone_name', 'edit', 'nom_zone', 'Name:'),
        ],
    )
