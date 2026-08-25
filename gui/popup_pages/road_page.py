"""Road page builder for PopupDialog."""

from typing import TYPE_CHECKING

from qgis.PyQt.QtWidgets import QStackedWidget

from ..form_specs import ROAD_ROWS
from ._builder import build_page

if TYPE_CHECKING:
    from ..popup_dialog import PopupDialog


def build_road_page(dialog: 'PopupDialog', stack: QStackedWidget) -> None:
    build_page(
        dialog,
        stack,
        object_name='roadPage',
        save_kind='roads',
        rows=ROAD_ROWS,
    )
