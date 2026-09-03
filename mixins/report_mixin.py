"""Reporting mixin for generating statistical reports and purchase orders."""
# mypy: disable-error-code="attr-defined"

from __future__ import annotations

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path

from qgis.PyQt.QtWidgets import QMessageBox

from ..app.orders.repository import (
    count_numberings,
    count_numberings_total,
    count_organizations,
    count_panels,
    count_panels_by_dimension,
    count_panels_total,
    count_roads,
    count_subdivisions,
    count_zones,
    query_missing_num,
    query_missing_pan,
    query_missing_rep,
)
from ..app.shared.utils import run_reporting_script
from ..constants import (
    DEFAULT_PANEL_DIM,
    LAYER_FACILITIES,
    LAYER_ROADS,
    LAYER_SUBDIVISIONS,
    NUM_PLANNED,
    PAN_MOUNTED,
    PAN_PLANNED,
    PAN_TO_FIX,
    PAN_TO_MOVE,
    REPORT_METHOD_ORDER,
    REPORT_METHOD_REPORT,
    TMP_JSON,
    current_theme,
    get_theme_qss,
)
from ._protocols import HasReportContext, HasTranslation

logger = logging.getLogger(__name__)


class ReportMixin:
    """Mixin for generating statistical reports and purchase order documents."""

    def _run_report(
        self: HasTranslation,
        method: str,
        data: dict,
        label: str = 'report',
    ) -> bool:
        """Run the external reporting script and display result dialogs."""
        try:
            with Path(TMP_JSON).open('w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except OSError:
            logger.exception('Error saving JSON file')
            return False

        success_msg = (
            self._tr('Report saved to your documents')
            if label == 'report'
            else self._tr('Order saved to your documents')
        )
        fail_msg = (
            self._tr('Failed to generate report')
            if label == 'report'
            else self._tr('Failed to generate order')
        )

        try:
            run_reporting_script(method)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle(self._tr('Success'))
            msg.setStyleSheet(get_theme_qss(current_theme()))
            msg.setInformativeText(success_msg)
            msg.exec()
        except subprocess.CalledProcessError as e:
            logger.exception('Subprocess failed with error')
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle(self._tr('Error'))
            msg.setStyleSheet(get_theme_qss(current_theme()))
            msg.setText(fail_msg)
            msg.setInformativeText(str(e))
            msg.exec()
            return False
        except OSError:
            logger.exception('Failed to run reporting script')
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle(self._tr('Error'))
            msg.setStyleSheet(get_theme_qss(current_theme()))
            msg.setText(fail_msg)
            msg.exec()
            return False
        else:
            return True

    def generate_report(self: HasReportContext) -> bool:
        """Generate a statistical report via the external reporting script."""
        if self.current_user is None:
            logger.error('No current user for report generation')
            return False
        report_data = {
            'locale': self._tr_locale,
            'prog': count_numberings(NUM_PLANNED),
            'wrong': count_numberings('numbered_mismatched'),
            'right': count_numberings('numbered_matched'),
            'booked': count_numberings('booked'),
            'num_total': count_numberings_total(),
            'date': datetime.now().astimezone().date().strftime('%Y/%m/%d'),
            'pan_city0': count_panels(LAYER_SUBDIVISIONS, PAN_MOUNTED),
            'pan_org0': count_panels(LAYER_FACILITIES, PAN_MOUNTED),
            'pan_road0': count_panels(LAYER_ROADS, PAN_MOUNTED),
            'pan_city1': count_panels(LAYER_SUBDIVISIONS, PAN_PLANNED),
            'pan_org1': count_panels(LAYER_FACILITIES, PAN_PLANNED),
            'pan_road1': count_panels(LAYER_ROADS, PAN_PLANNED),
            'pan_city2': count_panels(LAYER_SUBDIVISIONS, PAN_TO_MOVE),
            'pan_org2': count_panels(LAYER_FACILITIES, PAN_TO_MOVE),
            'pan_road2': count_panels(LAYER_ROADS, PAN_TO_MOVE),
            'pan_city3': count_panels(LAYER_SUBDIVISIONS, PAN_TO_FIX),
            'pan_org3': count_panels(LAYER_FACILITIES, PAN_TO_FIX),
            'pan_road3': count_panels(LAYER_ROADS, PAN_TO_FIX),
            'pan_total': count_panels_total(),
            'pan_std': count_panels_by_dimension(DEFAULT_PANEL_DIM),
            'zones': count_zones(),
            'roads': count_roads(),
            'subs': count_subdivisions(),
            'orgs': count_organizations(),
            'wilaya': self.current_user.get('wilaya'),
            'commune': self.current_user.get('commune'),
            'creation_date': datetime.now().astimezone().date().strftime('%Y-%m-%d'),
            'output_dir': self._output_dir,
        }
        return self._run_report(REPORT_METHOD_REPORT, report_data, label='report')

    def purchase_order(self: HasReportContext) -> bool:
        """Generate a purchase order via the external reporting script."""
        if self.current_user is None:
            logger.error('No current user for purchase order generation')
            return False
        order_data = {
            'date': datetime.now().astimezone().date().strftime('%Y/%m/%d'),
            'wilaya': self.current_user.get('wilaya'),
            'commune': self.current_user.get('commune'),
            'items': query_missing_pan(PAN_PLANNED),
            'items2': query_missing_pan(PAN_TO_FIX),
            'items3': query_missing_num(NUM_PLANNED),
            'items4': query_missing_rep(NUM_PLANNED),
            'output_dir': self._output_dir,
        }
        return self._run_report(REPORT_METHOD_ORDER, order_data, label='order')
