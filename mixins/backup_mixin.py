"""Backup and restore mixin for SQLite/SpatiaLite database files."""

import logging
import os
import shutil

from qgis.PyQt.QtWidgets import QMessageBox, QFileDialog

from ..app.core.database import get_auth_engine
from ..constants import (
    PLUGIN_DIR, DATABASE_FILE, AUTH_DATABASE_FILE,
    current_theme, get_dialog_qss,
)

logger = logging.getLogger(__name__)


class BackupMixin:
    """Mixin for backing up and restoring SQLite/SpatiaLite databases."""

    def restore_database(self) -> None:
        """Restore the main database from a user-selected SQLite file."""
        file_dialog_open = QFileDialog(self)
        file_dialog_open.setDirectory(PLUGIN_DIR)
        file_dialog_open.setOption(QFileDialog.DontUseNativeDialog)
        file_dialog_open.setWindowTitle(self._tr("Select SQLite/SpatiaLite File"))
        file_dialog_open.setNameFilter(
            "SQLite/SpatiaLite Files (*.sqlite *.db *.sqlite3);;All Files (*)")

        file_dialog_open.setStyleSheet(get_dialog_qss(current_theme()))

        if file_dialog_open.exec_():
            source_path = file_dialog_open.selectedFiles()[0]
        else:
            QMessageBox.warning(self, self._tr("Warning"), self._tr("No file selected"))
            return

        with open(source_path, 'rb') as f:
            header = f.read(16)
        if header[:16] != b'SQLite format 3\x00':
            QMessageBox.critical(
                self, self._tr("Error"),
                self._tr("Selected file is not a valid SQLite database"),
            )
            return

        destination_path = DATABASE_FILE
        temp_path = destination_path + '.tmp'
        try:
            shutil.copy2(source_path, temp_path)
            os.replace(temp_path, destination_path)
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise
        QMessageBox.information(
            self, self._tr("Success"),
            self._tr("Database restored from %s") % os.path.basename(source_path),
        )

    def restore_auth_database(self) -> None:
        """Ensure the auth database file exists, creating it if needed."""
        auth_path = AUTH_DATABASE_FILE
        if os.path.exists(auth_path):
            QMessageBox.information(
                self, self._tr("Info"),
                self._tr("Auth database already exists"),
            )
        else:
            get_auth_engine()
            QMessageBox.information(
                self, self._tr("Success"),
                self._tr("Auth database created"),
            )

    def backup(self) -> None:
        """Backup the main and auth databases to a user-chosen location."""
        source_path = DATABASE_FILE
        auth_source = AUTH_DATABASE_FILE

        file_dialog_save = QFileDialog(self)
        file_dialog_save.setOption(QFileDialog.DontUseNativeDialog)
        file_dialog_save.setWindowTitle(self._tr("Save Copy As"))
        file_dialog_save.setNameFilter(
            "SQLite/SpatiaLite Files (*.sqlite *.db *.sqlite3);;",
        )
        file_dialog_save.setAcceptMode(QFileDialog.AcceptSave)

        file_dialog_save.setStyleSheet(get_dialog_qss(current_theme()))

        if file_dialog_save.exec_():
            destination_path = file_dialog_save.selectedFiles()[0]
        else:
            QMessageBox.warning(self, self._tr("Warning"), self._tr("No file selected"))
            return

        try:
            shutil.copy(source_path, destination_path)
            if os.path.exists(auth_source):
                base, ext = os.path.splitext(destination_path)
                auth_dest = f"{base}_auth{ext}"
                shutil.copy(auth_source, auth_dest)
            QMessageBox.information(
                self, self._tr("Success"), self._tr("File copied successfully"),
            )
        except Exception as e:
            logger.exception("Failed to backup database: %s", e)
            QMessageBox.critical(self, self._tr("Error"), self._tr("Failed to copy file"))
