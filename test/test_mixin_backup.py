"""Tests for mixins/backup_mixin.py."""
import importlib
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from test.helpers import setup_gui_mocks, get_qapp


@unittest.skipIf(get_qapp() is None, 'PyQt5 not available')
class TestBackupMixin(unittest.TestCase):
    """Test backup/restore operations."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.mixins.backup_mixin',
            'mixins/backup_mixin.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.mixins.backup_mixin'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.valid_sqlite = os.path.join(self.tmpdir, 'valid.sqlite')
        with open(self.valid_sqlite, 'wb') as f:
            f.write(b'SQLite format 3\x00')
        self.invalid_file = os.path.join(self.tmpdir, 'not_sqlite.txt')
        with open(self.invalid_file, 'w', encoding='utf-8') as f:
            f.write('not a database')

        self.mod.DATABASE_FILE = os.path.join(self.tmpdir, 'main.sqlite')
        self.mod.AUTH_DATABASE_FILE = os.path.join(self.tmpdir, 'auth.sqlite')
        self.mod.PLUGIN_DIR = self.tmpdir

        fake_dialog = MagicMock()
        fake_dialog.exec_ = MagicMock(return_value=MagicMock())
        fake_dialog.selectedFiles = MagicMock(return_value=[self.valid_sqlite])

        self._mock_qfiledialog = MagicMock(return_value=fake_dialog)
        self._mock_qfiledialog_cls = patch.object(
            self.mod, 'QFileDialog', self._mock_qfiledialog,
        )
        self._mock_qfiledialog_cls.start()

        self._mock_qmessagebox = patch.object(
            self.mod, 'QMessageBox', autospec=False,
        )
        mock_qmb = self._mock_qmessagebox.start()
        mock_qmb.critical = MagicMock(side_effect=lambda p, t, m: None)
        mock_qmb.information = MagicMock(side_effect=lambda p, t, m: None)
        mock_qmb.warning = MagicMock(side_effect=lambda p, t, m: None)

        self.host = type('Host', (), {'_tr': lambda self, s: s})()
        self.mixin = self.mod.BackupMixin()
        self.mixin._tr = lambda s: s

    def tearDown(self):
        self._mock_qfiledialog_cls.stop()
        self._mock_qmessagebox.stop()
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_restore_database_valid_file(self):
        self.mixin.restore_database()
        self.assertTrue(os.path.exists(self.mod.DATABASE_FILE))

    def test_restore_database_no_selection(self):
        fake_dialog = MagicMock()
        fake_dialog.exec_ = MagicMock(return_value=None)
        self._mock_qfiledialog.return_value = fake_dialog
        self.mixin.restore_database()
        self.assertFalse(os.path.exists(self.mod.DATABASE_FILE))

    def test_restore_database_invalid_file(self):
        fake_dialog = MagicMock()
        fake_dialog.exec_ = MagicMock(return_value=MagicMock())
        fake_dialog.selectedFiles = MagicMock(return_value=[self.invalid_file])
        self._mock_qfiledialog.return_value = fake_dialog
        self.mixin.restore_database()
        self.assertFalse(os.path.exists(self.mod.DATABASE_FILE))

    def test_restore_auth_exists(self):
        Path(self.mod.AUTH_DATABASE_FILE).touch()
        self.mixin.restore_auth_database()
        self.assertTrue(os.path.exists(self.mod.AUTH_DATABASE_FILE))

    def test_restore_auth_not_exists(self):
        mock_engine = MagicMock()
        with patch.object(self.mod, 'get_auth_engine',
                          return_value=mock_engine):
            self.mixin.restore_auth_database()
            self.mod.get_auth_engine.assert_called_once()

    def test_backup_copies_main_only(self):
        Path(self.mod.DATABASE_FILE).touch()
        dest = os.path.join(self.tmpdir, 'backup.sqlite')
        fake_dialog = MagicMock()
        fake_dialog.exec_ = MagicMock(return_value=MagicMock())
        fake_dialog.selectedFiles = MagicMock(return_value=[dest])
        self._mock_qfiledialog.return_value = fake_dialog
        self.mixin.backup()
        self.assertTrue(os.path.exists(dest))

    def test_backup_copies_both(self):
        Path(self.mod.DATABASE_FILE).touch()
        Path(self.mod.AUTH_DATABASE_FILE).touch()
        dest = os.path.join(self.tmpdir, 'backup.sqlite')
        fake_dialog = MagicMock()
        fake_dialog.exec_ = MagicMock(return_value=MagicMock())
        fake_dialog.selectedFiles = MagicMock(return_value=[dest])
        self._mock_qfiledialog.return_value = fake_dialog
        self.mixin.backup()
        self.assertTrue(os.path.exists(dest))
        auth_dest = os.path.join(self.tmpdir, 'backup_auth.sqlite')
        self.assertTrue(os.path.exists(auth_dest))

    def test_backup_no_selection(self):
        Path(self.mod.DATABASE_FILE).touch()
        fake_dialog = MagicMock()
        fake_dialog.exec_ = MagicMock(return_value=None)
        self._mock_qfiledialog.return_value = fake_dialog
        self.mixin.backup()

    def test_backup_copy_failure(self):
        Path(self.mod.DATABASE_FILE).touch()
        dest = os.path.join(self.tmpdir, 'backup.sqlite')
        fake_dialog = MagicMock()
        fake_dialog.exec_ = MagicMock(return_value=MagicMock())
        fake_dialog.selectedFiles = MagicMock(return_value=[dest])
        self._mock_qfiledialog.return_value = fake_dialog
        with patch('shutil.copy', side_effect=OSError('copy failed')):
            self.mixin.backup()


if __name__ == '__main__':
    unittest.main()
