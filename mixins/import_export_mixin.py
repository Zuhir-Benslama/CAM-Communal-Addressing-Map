"""Import/export mixin for rendering maps to PNG."""
# mypy: disable-error-code="attr-defined"

from __future__ import annotations

import json
import logging
import subprocess
from datetime import datetime
from typing import Any, ClassVar

from qgis.core import QgsMapRendererSequentialJob, QgsMapSettings
from qgis.PyQt.QtCore import QSize
from qgis.PyQt.QtWidgets import QApplication, QMessageBox

from ..app.shared.utils import run_reporting_script
from ..constants import (
    MAP_PNG,
    TMP_JSON,
    validate_text,
)
from ..layer.refresh import refresh_all_layers
from ._protocols import HasExportContext, HasFormWidgets

logger = logging.getLogger(__name__)

EXPORT_MAP_SIZE = QSize(2200, 2200)


class ImportExportMixin:
    """Mixin for exporting map canvases and invoking external
    reporting scripts."""

    # Async render state (class-level defaults; shadowed per instance).
    _export_in_progress: ClassVar[bool] = False
    _render_job: ClassVar[Any] = None
    _export_method: ClassVar[str | None] = None

    def _validate_export_ready(self: HasExportContext) -> bool:
        if not (self.type_plan and self.type_to_hide):
            QMessageBox.critical(
                self,
                self._tr('Error'),
                self._tr(
                    'Numbering map or Panel map\nYou must select the map type to print'
                ),
            )
            return False
        return True

    def _start_map_render(
        self: HasExportContext,
    ) -> QgsMapRendererSequentialJob | None:
        """Prepare map settings and start an asynchronous render job.

        The job runs in the background; :meth:`_on_map_render_finished`
        continues the export when it completes. Returns None on failure.
        """
        if not self.north() or not self.scale():
            return None

        refresh_all_layers(self.iface)

        canvas = self.iface.mapCanvas()
        canvas.refreshAllLayers()
        QApplication.processEvents()
        extent = canvas.extent()
        extent.scale(1.1)

        map_settings = canvas.mapSettings()
        map_settings.setExtent(extent)
        map_settings.setOutputSize(EXPORT_MAP_SIZE)
        map_settings.setFlag(QgsMapSettings.Flag.Antialiasing, True)

        render_job = QgsMapRendererSequentialJob(map_settings)
        self._render_job = render_job  # keep alive until finished
        render_job.start()
        return render_job

    def _build_export_data(self: HasExportContext) -> dict | None:
        canvas = self.iface.mapCanvas()
        current_scale = canvas.scale()
        now = datetime.now().astimezone()
        if self.current_user is None:
            logger.error('No current user for export data')
            return None
        first = self.current_user.get('first_name', '') or ''
        last = self.current_user.get('last_name', '') or ''
        return {
            'type_plan': self.type_plan,
            'date': now.strftime('%Y/%m/%d %H:%M'),
            'by': validate_text(f'{first} {last}'.strip()),
            'wilaya': self.current_user.get('wilaya'),
            'commune': self.current_user.get('commune'),
            'zone': validate_text(self.current_user.get('commune', '')),
            'scale': f'1:{round(current_scale)}',
            'num_plan': self.type_plan,
            'output_dir': self._output_dir,
        }

    def _write_export_json(self: HasExportContext, data: dict) -> bool:
        try:
            with open(TMP_JSON, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except (OSError, TypeError):
            logger.exception('Error saving JSON data to %s', TMP_JSON)
            QMessageBox.critical(
                self,
                self._tr('Error'),
                self._tr('Failed to write export data'),
            )
            return False
        else:
            return True

    def _validate_export_data(self: HasExportContext, data: dict) -> bool:
        required_keys = ('type_plan', 'num_plan', 'scale', 'by', 'date')
        missing = [k for k in required_keys if k not in data]
        if missing:
            logger.error('Missing keys in export data: %s', missing)
            QMessageBox.critical(
                self,
                self._tr('Error'),
                self._tr('Internal error: missing export data'),
            )
            return False
        return True

    def _invoke_reporting_script(self: HasExportContext, _method: str) -> None:
        try:
            run_reporting_script(_method)
            QMessageBox.information(
                self,
                self._tr('Success'),
                self._tr('Map saved to your documents'),
            )
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr.strip() if e.stderr else '(no output)'
            logger.exception(
                'Map export failed (exit %d): %s',
                e.returncode,
                err_msg,
            )
            QMessageBox.critical(
                self,
                self._tr('Error'),
                f'{self._tr("Failed to generate map PDF")}\n\n{err_msg[:500]}',
            )
        except OSError:
            logger.exception('Failed to invoke reporting script')
            QMessageBox.critical(
                self,
                self._tr('Error'),
                self._tr('Failed to export map'),
            )

    def _render_and_export(
        self: HasExportContext,
        _method: str,
        include_situation: bool = False,
    ) -> None:
        if self._export_in_progress:
            logger.info('Map export already in progress; ignoring request')
            return
        if not self._validate_export_ready():
            return

        if include_situation and not self.map_situation():
            return

        job = self._start_map_render()
        if job is None:
            return

        self._export_in_progress = True
        self._export_method = _method
        job.jobFinished.connect(self._on_map_render_finished)

    def _on_map_render_finished(self: HasExportContext) -> None:
        """Continue (and reset) the export once the render job completes."""
        try:
            self._finish_render_and_export()
        finally:
            self._export_in_progress = False
            self._render_job = None
            self._export_method = None

    def _finish_render_and_export(self: HasExportContext) -> None:
        """Save the rendered image and hand off to the reporting script."""
        job = self._render_job
        if job is None:
            return

        rendered_image = job.renderedImage()
        if not rendered_image.save(MAP_PNG, 'png'):
            logger.error('Failed to save rendered map to %s', MAP_PNG)
            return

        if not self.symbols():
            return

        data = self._build_export_data()
        if data is None or not self._validate_export_data(data):
            return

        if not self._write_export_json(data):
            return

        self._invoke_reporting_script(self._export_method or '')

    def export_to_image(self: HasFormWidgets) -> None:
        selected_value = self.paper.currentData()
        if selected_value == 'A0':
            self._render_and_export('4', include_situation=True)
        elif selected_value == 'A3':
            self._render_and_export('3')
        else:
            QMessageBox.critical(
                self,
                self._tr('Error'),
                self._tr('Please select a paper size'),
            )
