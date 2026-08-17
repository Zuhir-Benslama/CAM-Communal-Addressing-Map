"""Backup, restore, and import mixin for SQLite/SpatiaLite databases."""
# mypy: disable-error-code="attr-defined"

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox

from ..app.core.database import reset_connection_pool
from ..constants import (
    DATABASE_FILE,
    PLUGIN_DIR,
    current_theme,
    get_dialog_qss,
)
from ._protocols import HasTranslation

logger = logging.getLogger(__name__)


class BackupMixin:
    """Mixin for backing up and restoring SQLite/SpatiaLite databases."""

    @staticmethod
    def _replace_db_file(source: str, destination: str) -> None:
        temp = destination + '.tmp'
        try:
            shutil.copy2(source, temp)
            Path(temp).replace(destination)
        except (OSError, shutil.Error):
            if Path(temp).exists():
                Path(temp).unlink()
            raise

    def _select_db_file(
        self: HasTranslation, title: str, name_filter: str
    ) -> str | None:
        dialog = QFileDialog(self)
        dialog.setDirectory(PLUGIN_DIR)
        dialog.setOption(QFileDialog.DontUseNativeDialog)
        dialog.setWindowTitle(self._tr(title))
        dialog.setNameFilter(name_filter)
        dialog.setStyleSheet(get_dialog_qss(current_theme()))
        if dialog.exec():
            return dialog.selectedFiles()[0]
        QMessageBox.warning(self, self._tr('Warning'), self._tr('No file selected'))
        return None

    def _validate_sqlite_header(self: HasTranslation, path: str, label: str) -> bool:
        with open(path, 'rb') as f:
            header = f.read(16)
        if header[:16] != b'SQLite format 3\x00':
            QMessageBox.critical(
                self,
                self._tr('Error'),
                f'Selected {label} is not a valid SQLite database',
            )
            return False
        return True

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def restore_database(self: HasTranslation) -> None:
        source_path = self._select_db_file(
            'Select SQLite/SpatiaLite File',
            'SQLite/SpatiaLite Files (*.sqlite *.db *.sqlite3);;All Files (*)',
        )
        if source_path is None:
            return
        if not self._validate_sqlite_header(source_path, 'file'):
            return

        try:
            self._replace_db_file(source_path, DATABASE_FILE)
            reset_connection_pool()
        except (OSError, shutil.Error) as e:
            logger.exception('Failed to restore database')
            QMessageBox.critical(
                self,
                self._tr('Error'),
                f'Failed to restore database: {e}',
            )
            return

        QMessageBox.information(
            self,
            self._tr('Success'),
            f'Database restored from {Path(source_path).name}',
        )

    def backup(self: HasTranslation) -> None:
        source_path = DATABASE_FILE

        file_dialog_save = QFileDialog(self)
        file_dialog_save.setOption(QFileDialog.DontUseNativeDialog)
        file_dialog_save.setWindowTitle(self._tr('Save Copy As'))
        file_dialog_save.setNameFilter(
            'SQLite/SpatiaLite Files (*.sqlite *.db *.sqlite3);;',
        )
        file_dialog_save.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog_save.setStyleSheet(get_dialog_qss(current_theme()))

        if file_dialog_save.exec():
            destination_path = file_dialog_save.selectedFiles()[0]
        else:
            QMessageBox.warning(self, self._tr('Warning'), self._tr('No file selected'))
            return

        try:
            shutil.copy(source_path, destination_path)
            QMessageBox.information(
                self,
                self._tr('Success'),
                self._tr('File copied successfully'),
            )
        except (OSError, shutil.Error):
            logger.exception('Failed to backup database')
            QMessageBox.critical(
                self, self._tr('Error'), self._tr('Failed to copy file')
            )
