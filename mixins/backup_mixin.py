# mypy: ignore-errors
"""Backup, restore, and import mixin for SQLite/SpatiaLite databases."""

from __future__ import annotations

import logging
import os
import shutil
import tempfile

from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox

from ..app.core.database import reset_connection_pool
from ..app.core.migration import migrate_database
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
            os.replace(temp, destination)
        except (OSError, shutil.Error):
            if os.path.exists(temp):
                os.remove(temp)
            raise

    # ------------------------------------------------------------------
    # Helpers for import_database
    # ------------------------------------------------------------------

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
                self._tr('Selected %s is not a valid SQLite database') % label,
            )
            return False
        return True

    def _select_auth_file(self: HasTranslation) -> str | None:
        reply = QMessageBox.question(
            self,
            self._tr('Import'),
            self._tr(
                'Do you have a companion auth.sqlite file from the old '
                'database?\n\n'
                'This is only needed if user accounts were stored in a '
                'separate file.'
            ),
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return None

        auth_path = self._select_db_file(
            'Select auth.sqlite',
            'SQLite Files (*.sqlite *.db);;All Files (*)',
        )
        if auth_path is None:
            return None
        if not self._validate_sqlite_header(auth_path, 'auth file'):
            return None
        return auth_path

    def _perform_migration(
        self: HasTranslation, old_path: str, temp_path: str, auth_path: str | None
    ) -> bool:
        try:
            migrate_database(old_path, temp_path, auth_path)
            return True
        except Exception as e:  # pylint: disable=W0718
            logger.exception('Migration failed')
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            QMessageBox.critical(
                self,
                self._tr('Error'),
                self._tr('Migration failed: %s') % str(e),
            )
            return False

    def _replace_and_reset(self: HasTranslation, temp_path: str) -> bool:
        try:
            self._replace_db_file(temp_path, DATABASE_FILE)
            reset_connection_pool()
            return True
        except (OSError, shutil.Error) as e:
            logger.exception('Failed to replace database')
            QMessageBox.critical(
                self,
                self._tr('Error'),
                self._tr('Failed to replace current database: %s') % str(e),
            )
            return False
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

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

        self._replace_db_file(source_path, DATABASE_FILE)
        reset_connection_pool()

        QMessageBox.information(
            self,
            self._tr('Success'),
            self._tr('Database restored from %s') % os.path.basename(source_path),
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
        except (OSError, shutil.Error) as e:
            logger.exception('Failed to backup database: %s', e)
            QMessageBox.critical(
                self, self._tr('Error'), self._tr('Failed to copy file')
            )

    def import_database(self: HasTranslation) -> None:
        old_path = self._select_db_file(
            'Select Old Database File',
            'SQLite/SpatiaLite Files (*.sqlite *.db *.sqlite3);;All Files (*)',
        )
        if old_path is None:
            return
        if not self._validate_sqlite_header(old_path, 'file'):
            return

        auth_path = self._select_auth_file()

        fd, temp_path = tempfile.mkstemp(suffix='.sqlite')
        os.close(fd)
        if not self._perform_migration(old_path, temp_path, auth_path):
            return

        if self._replace_and_reset(temp_path):
            QMessageBox.information(
                self,
                self._tr('Success'),
                self._tr('Database imported and migrated successfully'),
            )
