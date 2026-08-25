"""City (subdivision) page builder for PopupDialog."""

from typing import TYPE_CHECKING

from qgis.PyQt.QtWidgets import QStackedWidget

from ..form_specs import CITY_ROWS
from ._builder import build_page

if TYPE_CHECKING:
    from ..popup_dialog import PopupDialog


def build_city_page(dialog: 'PopupDialog', stack: QStackedWidget) -> None:
    build_page(
        dialog,
        stack,
        object_name='cityPage',
        save_kind='city',
        rows=CITY_ROWS,
    )
