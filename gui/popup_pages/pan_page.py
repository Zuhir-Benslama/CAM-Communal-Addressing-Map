"""Panel sign page builder for PopupDialog."""

from typing import TYPE_CHECKING

from qgis.PyQt.QtWidgets import QStackedWidget

from ..form_specs import PAN_ROWS
from ._builder import build_page

if TYPE_CHECKING:
    from ..popup_dialog import PopupDialog


def build_pan_page(dialog: 'PopupDialog', stack: QStackedWidget) -> None:
    build_page(
        dialog,
        stack,
        object_name='panPage',
        save_kind='pan',
        rows=PAN_ROWS,
    )
