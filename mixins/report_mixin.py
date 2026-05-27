"""Reporting mixin for generating statistical reports and purchase orders."""
# mypy: disable-error-code="attr-defined"

from __future__ import annotations

import logging

from qgis.PyQt.QtWidgets import QMessageBox

from ..constants import current_theme, get_theme_qss
from ._protocols import HasTranslation

logger = logging.getLogger(__name__)


class ReportMixin:
    """Mixin for generating statistical reports and purchase order documents."""

    def _notify_unavailable(self: HasTranslation, feature: str) -> None:
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

    def gen_report(self: HasTranslation) -> bool:
        """Show notice that report generation is no longer available."""
        self._notify_unavailable("Report generation")
        return False

    def bon_commande(self: HasTranslation) -> bool:
        """Show notice that purchase order generation is no longer available."""
        self._notify_unavailable("Purchase order generation")
        return False
