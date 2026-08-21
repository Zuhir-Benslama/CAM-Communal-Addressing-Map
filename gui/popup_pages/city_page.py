"""City (subdivision) page builder for PopupDialog."""

from typing import TYPE_CHECKING

from qgis.PyQt.QtWidgets import QStackedWidget

from ._builder import build_page

if TYPE_CHECKING:
    from ..popup_dialog import PopupDialog


def build_city_page(dialog: 'PopupDialog', stack: QStackedWidget) -> None:
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
