"""Panel sign page builder for PopupDialog."""

from typing import TYPE_CHECKING

from qgis.PyQt.QtWidgets import QStackedWidget

from ._builder import build_named_page

if TYPE_CHECKING:
    from ..popup_dialog import PopupDialog


def build_pan_page(dialog: 'PopupDialog', stack: QStackedWidget) -> None:
    build_named_page(dialog, stack, name='pan')
