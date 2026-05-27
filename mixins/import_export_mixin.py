"""Import/export mixin for rendering maps to PNG."""
# mypy: disable-error-code="attr-defined,func-returns-value"

from __future__ import annotations

import json
import logging

from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsMapSettings, QgsMapRendererParallelJob

from ..constants import MAP_PNG, TMP_JSON, validate_text
from ._protocols import (
    HasUiWidgets, HasExportContext,
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

        canvas = self.iface.mapCanvas()
        extent = canvas.extent()
        extent.scale(1.1)

        map_settings = QgsMapSettings()
        map_settings.setLayers(canvas.layers())
        map_settings.setExtent(extent)
        map_settings.setOutputSize(EXPORT_MAP_SIZE)
        map_settings.setFlag(
            QgsMapSettings.Flag.UseAdvancedEffects, True,
        )
        map_settings.setDestinationCrs(
            canvas.mapSettings().destinationCrs(),
        )

        render_job = QgsMapRendererParallelJob(map_settings)
        render_job.start()
        render_job.waitForFinished()

        rendered_image = render_job.renderedImage()

        if rendered_image.save(MAP_PNG, "png"):
            current_scale = canvas.scale()
            symb = self.symbols()
            if symb:
                export_data = {
                    'type_plan': self.type_plan,
                    'date': self.dateEdit.date().toString("yyyy/MM/dd"),
                    'by': validate_text(self.lineEdit_by.text()),
                    'wilaya': self.current_user.get('wilaya'),
                    'commune': self.current_user.get('commune'),
                    'zone': validate_text(self.lineEdit_type.text()),
                    'num_plan': validate_text(self.lineEdit_nummokh.text()),
                    'scale': f"1:{round(current_scale)}",
                }
                try:
                    with open(TMP_JSON, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, ensure_ascii=False, indent=4)
                except (IOError, OSError) as e:
                    logger.error("Error saving JSON file: %s", e)

                QMessageBox.information(
                    self, self._tr("Success"),
                    self._tr("Your file has been saved to your documents"),
                )

    def export_to_image(self: HasUiWidgets) -> None:
        """Render the map canvas and export to PNG via an external
        reporting script."""
        selected_value = self.paper.currentData()
        if selected_value == 'A0':
            self._render_and_export('4', include_situation=True)
        elif selected_value == 'A3':
            self._render_and_export('3')
