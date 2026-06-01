"""Import/export mixin for rendering maps to PNG."""
from __future__ import annotations

import json
import logging
import subprocess
from datetime import datetime

from qgis.core import QgsMapRendererSequentialJob, QgsMapSettings
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtWidgets import QApplication, QMessageBox

from ..constants import (
    _SUBPROCESS_FLAGS,
    MAP_PNG,
    REPORTING_SCRIPT,
    TMP_JSON,
    get_qgis_python,
    validate_text,
)
from ..layer.refresh import refresh_all_layers
from ._protocols import (
    HasExportContext,
    HasFormWidgets,
)

logger = logging.getLogger(__name__)

EXPORT_MAP_SIZE = QSize(2200, 2200)


class ImportExportMixin:
    """Mixin for exporting map canvases and invoking external
    reporting scripts."""

    def _render_and_export(
        self: HasExportContext,
        _method: str, include_situation: bool = False,
    ) -> None:
        """Render map canvas and invoke external reporting script."""
        if not (self.type_plan and self.type_to_hide):
            QMessageBox.critical(
                self, self._tr("Error"),
                self._tr("Numbering map or Panel map\n"
                         "You must select the map type to print"),
            )
            return

        self.north()
        self.scale()
        if include_situation:
            self.map_situation()

        refresh_all_layers(self.iface)

        canvas = self.iface.mapCanvas()
        canvas.refreshAllLayers()
        QApplication.processEvents()
        extent = canvas.extent()
        extent.scale(1.1)

        map_settings = canvas.mapSettings()
        map_settings.setExtent(extent)
        map_settings.setOutputSize(EXPORT_MAP_SIZE)
        map_settings.setFlag(
            QgsMapSettings.Flag.Antialiasing, True,
        )

        render_job = QgsMapRendererSequentialJob(map_settings)
        render_job.start()
        render_job.waitForFinished()

        rendered_image = render_job.renderedImage()

        if rendered_image.save(MAP_PNG, "png"):
            current_scale = canvas.scale()
            symb = self.symbols()
            if symb:
                now = datetime.now()
                first = self.current_user.get('first_name', '') or ''
                last = self.current_user.get('last_name', '') or ''
                export_data = {
                    'type_plan': self.type_plan,
                    'date': now.strftime("%Y/%m/%d %H:%M"),
                    'by': validate_text(f"{first} {last}".strip()),
                    'wilaya': self.current_user.get('wilaya'),
                    'commune': self.current_user.get('commune'),
                    'zone': validate_text(
                        self.current_user.get('commune', '')
                    ),
                    'scale': f"1:{round(current_scale)}",
                    'num_plan': self.type_plan,
                    'output_dir': self._output_dir,
                }
                try:
                    with open(TMP_JSON, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, ensure_ascii=False, indent=4)
                except Exception:  # pylint: disable=W0718
                    logger.exception("Error saving JSON data to %s", TMP_JSON)
                    QMessageBox.critical(
                        self, self._tr("Error"),
                        self._tr("Failed to write export data"),
                    )
                    return

                required_keys = ('type_plan', 'num_plan', 'scale', 'by', 'date')
                missing = [k for k in required_keys if k not in export_data]
                if missing:
                    logger.error("Missing keys in export data: %s", missing)
                    QMessageBox.critical(
                        self, self._tr("Error"),
                        self._tr("Internal error: missing export data"),
                    )
                    return

                try:
                    subprocess.run(
                        [f"{get_qgis_python()}", REPORTING_SCRIPT,
                         '--method', _method],
                        capture_output=True, text=True,
                        check=True, **_SUBPROCESS_FLAGS,
                    )
                    QMessageBox.information(
                        self, self._tr("Success"),
                        self._tr("Map saved to your documents"),
                    )
                except subprocess.CalledProcessError as e:
                    err_msg = e.stderr.strip() if e.stderr else "(no output)"
                    logger.error(
                        "Map export failed (exit %d): %s",
                        e.returncode, err_msg,
                    )
                    QMessageBox.critical(
                        self, self._tr("Error"),
                        f"{self._tr('Failed to generate map PDF')}\n\n{err_msg[:500]}",
                    )
                except Exception:  # pylint: disable=W0718
                    logger.exception("Failed to export map")
                    QMessageBox.critical(
                        self, self._tr("Error"),
                        self._tr("Failed to export map"),
                    )

    def export_to_image(self: HasFormWidgets) -> None:
        """Render the map canvas and export to PNG via an external
        reporting script."""
        selected_value = self.paper.currentData()
        if selected_value == 'A0':
            self._render_and_export('4', include_situation=True)
        elif selected_value == 'A3':
            self._render_and_export('3')
        else:
            QMessageBox.critical(
                self, "Error",
                "Please select a paper size",
            )
