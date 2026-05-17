"""Reporting mixin for generating statistical reports and purchase orders."""

import json
import logging
import subprocess

from datetime import datetime
from qgis.PyQt.QtWidgets import QMessageBox

from ..constants import get_qgis_python, _SUBPROCESS_FLAGS
from ..db.operations import (
    count_numberings, count_panels,
    query_missing_pan, query_missing_num, query_missing_rep,
)
from ..constants import (
    TMP_JSON, REPORTING_SCRIPT, current_theme, get_theme_qss,
    NUM_PLANNED, PAN_MOUNTED, PAN_PLANNED, PAN_TO_MOVE, PAN_TO_FIX,
    LAYER_SUBDIVISIONS, LAYER_FACILITIES, LAYER_ROADS,
)

logger = logging.getLogger(__name__)


class ReportMixin:
    """Mixin for generating statistical reports and purchase order documents."""

    def gen_report(self) -> bool:
        """Generate a statistical report via the external reporting script."""
        d = dict(
            prog=count_numberings(NUM_PLANNED),
            wrong=count_numberings('مرقمة وغير مطابقة'),
            right=count_numberings('مرقمة ومطابقة'),
            booked=count_numberings('محجوز(ة)'),
            date=datetime.now().date().strftime('%Y/%m/%d'),

            pan_city0=count_panels(LAYER_SUBDIVISIONS, PAN_MOUNTED),
            pan_org0=count_panels(LAYER_FACILITIES, PAN_MOUNTED),
            pan_road0=count_panels(LAYER_ROADS, PAN_MOUNTED),

            pan_city1=count_panels(LAYER_SUBDIVISIONS, PAN_PLANNED),
            pan_org1=count_panels(LAYER_FACILITIES, PAN_PLANNED),
            pan_road1=count_panels(LAYER_ROADS, PAN_PLANNED),

            pan_city2=count_panels(LAYER_SUBDIVISIONS, PAN_TO_MOVE),
            pan_org2=count_panels(LAYER_FACILITIES, PAN_TO_MOVE),
            pan_road2=count_panels(LAYER_ROADS, PAN_TO_MOVE),

            pan_city3=count_panels(LAYER_SUBDIVISIONS, PAN_TO_FIX),
            pan_org3=count_panels(LAYER_FACILITIES, PAN_TO_FIX),
            pan_road3=count_panels(LAYER_ROADS, PAN_TO_FIX),

            wilaya=self.current_user.get('wilaya'),
            commune=self.current_user.get('commune')
        )

        try:
            with open(TMP_JSON, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error("Error saving JSON file: %s", e)
            return False

        script_path = REPORTING_SCRIPT
        command = [f"{get_qgis_python()}", script_path, '--method', '2']

        try:
            subprocess.run(
                command, capture_output=True, text=True,
                check=True, **_SUBPROCESS_FLAGS,
            )
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Success")
            msg.setStyleSheet(get_theme_qss(current_theme()))
            msg.setInformativeText(self._tr("تم حفظ تقريرك في مستنداتك"))
            msg.exec_()
            return True
        except subprocess.CalledProcessError as e:
            logger.error("Subprocess failed with error: %s", e)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setStyleSheet(get_theme_qss(current_theme()))
            msg.setText(self._tr("فشل في إنشاء التقرير"))
            msg.setInformativeText(str(e))
            msg.exec_()
            return False
        except Exception as e:
            logger.exception("Unexpected error: %s", e)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setStyleSheet(get_theme_qss(current_theme()))
            msg.setText(self._tr("فشل في إنشاء التقرير"))
            msg.setInformativeText(str(e))
            msg.exec_()
            return False

    def bon_commande(self) -> bool:
        """Generate a purchase order via the external reporting script."""
        d = dict(
            date=datetime.now().date().strftime('%Y/%m/%d'),
            wilaya=self.current_user.get('wilaya'),
            commune=self.current_user.get('commune'),
            items=query_missing_pan(PAN_PLANNED),
            items2=query_missing_pan(PAN_TO_FIX),
            items3=query_missing_num(NUM_PLANNED),
            items4=query_missing_rep(NUM_PLANNED),
        )

        try:
            with open(TMP_JSON, 'w', encoding='utf-8') as f:
                json.dump(d, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error("Error saving JSON file: %s", e)
            return False

        script_path = REPORTING_SCRIPT
        command = [f"{get_qgis_python()}", script_path, '--method', '1']

        try:
            subprocess.run(
                command, capture_output=True, text=True,
                check=True, **_SUBPROCESS_FLAGS,
            )
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Success")
            msg.setStyleSheet(get_theme_qss(current_theme()))
            msg.setInformativeText("تم حفظ تقريرك في مستنداتك")
            msg.exec_()
            return True
        except subprocess.CalledProcessError as e:
            logger.error("Subprocess failed with error: %s", e)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setStyleSheet(get_theme_qss(current_theme()))
            msg.setText("فشل في إنشاء التقرير")
            msg.setInformativeText(str(e))
            msg.exec_()
            return False
        except Exception as e:
            logger.exception("Unexpected error: %s", e)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setStyleSheet(get_theme_qss(current_theme()))
            msg.setText("فشل في إنشاء التقرير")
            msg.setInformativeText(str(e))
            msg.exec_()
            return False
