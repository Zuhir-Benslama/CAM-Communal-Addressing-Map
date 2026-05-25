"""Reporting mixin for generating statistical reports and purchase orders."""

import logging

from datetime import datetime
from qgis.PyQt.QtWidgets import QMessageBox

from ..constants import (
    current_theme, get_theme_qss,
    NUM_PLANNED, PAN_MOUNTED, PAN_PLANNED, PAN_TO_MOVE, PAN_TO_FIX,
    LAYER_SUBDIVISIONS, LAYER_FACILITIES, LAYER_ROADS,
)
from ..app.orders.repository import (
    count_numberings, count_panels,
    query_missing_pan, query_missing_num, query_missing_rep,
)

logger = logging.getLogger(__name__)


class ReportMixin:
    """Mixin for generating statistical reports and purchase order documents."""

    def _notify_unavailable(self, feature: str) -> None:
        """Show a message that the reporting feature is no longer available."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(self._tr("Not Available"))
        msg.setStyleSheet(get_theme_qss(current_theme()))
        msg.setText(self._tr(f"{feature} is no longer available"))
        msg.setInformativeText(
            self._tr("The reporting script has been removed from this version.")
        )
        msg.exec_()

    def gen_report(self) -> bool:
        """Show notice that report generation is no longer available."""
        self._notify_unavailable("Report generation")
        return False

    def bon_commande(self) -> bool:
        """Show notice that purchase order generation is no longer available."""
        self._notify_unavailable("Purchase order generation")
        return False
