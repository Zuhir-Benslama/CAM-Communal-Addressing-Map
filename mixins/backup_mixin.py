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
        """Atomically replace *destination* with a copy of *source*."""
        temp = destination + '.tmp'
        try:
            shutil.copy2(source, temp)
            os.replace(temp, destination)
        except (OSError, shutil.Error):
            if os.path.exists(temp):
                os.remove(temp)
            raise

    def restore_database(self: HasTranslation) -> None:
        """Restore the database from a user-selected backup file.

        The connection pool is reset afterwards so the engine picks up the
        new file on the next access.
        """
        file_dialog_open = QFileDialog(self)
        file_dialog_open.setDirectory(PLUGIN_DIR)
        file_dialog_open.setOption(QFileDialog.DontUseNativeDialog)
        file_dialog_open.setWindowTitle(self._tr('Select SQLite/SpatiaLite File'))
        file_dialog_open.setNameFilter(
            'SQLite/SpatiaLite Files (*.sqlite *.db *.sqlite3);;All Files (*)'
        )

        file_dialog_open.setStyleSheet(get_dialog_qss(current_theme()))

        if file_dialog_open.exec():
            source_path = file_dialog_open.selectedFiles()[0]
        else:
            QMessageBox.warning(self, self._tr('Warning'), self._tr('No file selected'))
            return

        with open(source_path, 'rb') as f:
            header = f.read(16)
        if header[:16] != b'SQLite format 3\x00':
            QMessageBox.critical(
                self,
                self._tr('Error'),
                self._tr('Selected file is not a valid SQLite database'),
            )
            return

        self._replace_db_file(source_path, DATABASE_FILE)
        reset_connection_pool()

        QMessageBox.information(
            self,
            self._tr('Success'),
            self._tr('Database restored from %s') % os.path.basename(source_path),
        )

    def backup(self: HasTranslation) -> None:
        """Backup the database to a user-chosen location."""
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
        """Import an old-format database, migrating it to the current schema.

        The user selects an old SQLite file and optionally a companion
        ``auth.sqlite``.  A migrated copy replaces the current database.
        """
        file_dialog = QFileDialog(self)
        file_dialog.setDirectory(PLUGIN_DIR)
        file_dialog.setOption(QFileDialog.DontUseNativeDialog)
        file_dialog.setWindowTitle(self._tr('Select Old Database File'))
        file_dialog.setNameFilter(
            'SQLite/SpatiaLite Files (*.sqlite *.db *.sqlite3);;All Files (*)'
        )
        file_dialog.setStyleSheet(get_dialog_qss(current_theme()))

        if file_dialog.exec():
            old_path = file_dialog.selectedFiles()[0]
        else:
            QMessageBox.warning(self, self._tr('Warning'), self._tr('No file selected'))
            return

        with open(old_path, 'rb') as f:
            header = f.read(16)
        if header[:16] != b'SQLite format 3\x00':
            QMessageBox.critical(
                self,
                self._tr('Error'),
                self._tr('Selected file is not a valid SQLite database'),
            )
            return

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
        auth_path = None
        if reply == QMessageBox.Yes:
            auth_dialog = QFileDialog(self)
            auth_dialog.setDirectory(PLUGIN_DIR)
            auth_dialog.setOption(QFileDialog.DontUseNativeDialog)
            auth_dialog.setWindowTitle(self._tr('Select auth.sqlite'))
            auth_dialog.setNameFilter('SQLite Files (*.sqlite *.db);;All Files (*)')
            auth_dialog.setStyleSheet(get_dialog_qss(current_theme()))
            if auth_dialog.exec():
                auth_path = auth_dialog.selectedFiles()[0]
                with open(auth_path, 'rb') as f:
                    header = f.read(16)
                if header[:16] != b'SQLite format 3\x00':
                    QMessageBox.critical(
                        self,
                        self._tr('Error'),
                        self._tr('Selected auth file is not valid'),
                    )
                    return
            else:
                QMessageBox.warning(
                    self,
                    self._tr('Warning'),
                    self._tr('No auth file selected — continuing without it'),
                )

        fd, temp_path = tempfile.mkstemp(suffix='.sqlite')
        os.close(fd)
        try:
            migrate_database(old_path, temp_path, auth_path)
        except Exception as e:  # pylint: disable=W0718
            logger.exception('Migration failed')
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            QMessageBox.critical(
                self,
                self._tr('Error'),
                self._tr('Migration failed: %s') % str(e),
            )
            return

        try:
            self._replace_db_file(temp_path, DATABASE_FILE)
        except (OSError, shutil.Error) as e:
            logger.exception('Failed to replace database')
            QMessageBox.critical(
                self,
                self._tr('Error'),
                self._tr('Failed to replace current database: %s') % str(e),
            )
            return
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

        reset_connection_pool()

        QMessageBox.information(
            self,
            self._tr('Success'),
            self._tr('Database imported and migrated successfully'),
        )
