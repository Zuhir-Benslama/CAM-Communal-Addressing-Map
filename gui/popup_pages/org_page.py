"""Organization page builder for PopupDialog."""

from typing import TYPE_CHECKING

from qgis.PyQt.QtWidgets import QStackedWidget

from ._builder import build_page

if TYPE_CHECKING:
    from ..popup_dialog import PopupDialog


def build_org_page(dialog: 'PopupDialog', stack: QStackedWidget) -> None:
    build_page(
        dialog,
        stack,
        object_name='orgPage',
        save_kind='org',
        rows=[
            ('_combo_org_cat', 'combo', 'org_cat', 'Category:'),
            ('_combo_org_type', 'combo', 'org_type', 'Type:'),
            ('_field_org_name', 'edit', 'org_name', 'Name:'),
        ],
    )
