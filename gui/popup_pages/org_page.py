"""Organization page builder for PopupDialog."""

from typing import TYPE_CHECKING

from qgis.PyQt.QtWidgets import QStackedWidget

from ..form_specs import ORG_ROWS
from ._builder import build_page

if TYPE_CHECKING:
    from ..popup_dialog import PopupDialog


def build_org_page(dialog: 'PopupDialog', stack: QStackedWidget) -> None:
    build_page(
        dialog,
        stack,
        object_name='orgPage',
        save_kind='org',
        rows=ORG_ROWS,
    )
