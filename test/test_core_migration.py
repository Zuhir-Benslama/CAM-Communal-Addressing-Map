"""Tests for app.core.migration.migrate_database (end-to-end integration)."""

import os
import sqlite3
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from app.core.migration import NEW_TABLES, migrate_database


_LEGACY_TABLES = (
    'user',
    'refpoly',
    'refpolychild',
    'RefLine',
    'reforg',
    'Numerotation',
    'Pannautage',
)


def _make_old_db(path):
    """Create a legacy-format DB with all expected tables under *path*."""
    conn = sqlite3.connect(path)
    for tbl in _LEGACY_TABLES:
        conn.execute(f'CREATE TABLE "{tbl}" (pkuid INTEGER)')
    conn.commit()
    conn.close()


class TestMigrateDatabase(unittest.TestCase):
    def test_raises_if_output_exists(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            path = f.name
        try:
            with self.assertRaises(FileExistsError):
                migrate_database('/nonexistent_old.db', path)
        finally:
            os.unlink(path)

    def test_full_migration_user_data(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as of:
            old_path = of.name
        new_path = old_path + '_new.db'
        try:
            oc = sqlite3.connect(old_path)
            oc.execute("""
                CREATE TABLE user (
                    id TEXT, username TEXT, first_name TEXT,
                    last_name TEXT, password TEXT, active INTEGER,
                    wilaya_code INTEGER, commune_code TEXT,
                    api_key TEXT, email TEXT, phone TEXT
                )
            """)
            oc.execute(
                'INSERT INTO user VALUES '
                "('u1','alice','Alice','A','pw',1,16,'comm',NULL,NULL,NULL)"
            )
            for tbl in (
                'refpoly',
                'refpolychild',
                'RefLine',
                'reforg',
                'Numerotation',
                'Pannautage',
            ):
                oc.execute(f'CREATE TABLE "{tbl}" (pkuid INTEGER)')
            oc.commit()
            oc.close()

            with (
                patch('app.core.migration.init_spatialite'),
                patch('app.core.migration._register_geometry_columns'),
                patch('app.core.migration._create_spatial_indexes'),
            ):
                migrate_database(old_path, new_path)

            nc = sqlite3.connect(new_path)
            rows = nc.execute('SELECT * FROM user ORDER BY id').fetchall()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][1], 'alice')
            nc.close()
        finally:
            if os.path.exists(old_path):
                os.unlink(old_path)
            if os.path.exists(new_path):
                os.unlink(new_path)

    def test_migration_with_auth_path(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as of:
            old_path = of.name
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as af:
            auth_path = af.name
        new_path = old_path + '_new.db'
        try:
            ac = sqlite3.connect(auth_path)
            ac.execute(
                'CREATE TABLE user (id TEXT, username TEXT, '
                'first_name TEXT, last_name TEXT, password TEXT, '
                'active INTEGER, wilaya_code INTEGER, commune_code TEXT, '
                'api_key TEXT, email TEXT, phone TEXT)'
            )
            ac.execute(
                'INSERT INTO user VALUES '
                "('u2','bob','Bob','B','pw2',1,16,'c',NULL,NULL,NULL)"
            )
            ac.commit()
            ac.close()

            oc = sqlite3.connect(old_path)
            oc.execute("""
                CREATE TABLE user (
                    id TEXT, username TEXT, first_name TEXT,
                    last_name TEXT, password TEXT, active INTEGER,
                    wilaya_code INTEGER, commune_code TEXT,
                    api_key TEXT, email TEXT, phone TEXT
                )
            """)
            for tbl in (
                'refpoly',
                'refpolychild',
                'RefLine',
                'reforg',
                'Numerotation',
                'Pannautage',
            ):
                oc.execute(f'CREATE TABLE "{tbl}" (pkuid INTEGER)')
            oc.commit()
            oc.close()

            with (
                patch('app.core.migration.init_spatialite'),
                patch('app.core.migration._register_geometry_columns'),
                patch('app.core.migration._create_spatial_indexes'),
            ):
                migrate_database(old_path, new_path, auth_path)

            nc = sqlite3.connect(new_path)
            rows = nc.execute('SELECT * FROM user').fetchall()
            self.assertTrue(len(rows) >= 1)
            nc.close()
        finally:
            for p in (old_path, new_path, auth_path):
                if os.path.exists(p):
                    os.unlink(p)

    def test_migration_closes_connections_on_error(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as of:
            old_path = of.name
        new_path = old_path + '_new.db'
        try:
            _make_old_db(old_path)

            with (
                patch(
                    'app.core.migration.init_spatialite',
                    side_effect=RuntimeError('boom'),
                ),
                self.assertRaises(RuntimeError),
            ):
                migrate_database(old_path, new_path)
        finally:
            for p in (old_path, new_path):
                if os.path.exists(p):
                    os.unlink(p)

    def test_migrate_database_sets_pragmas(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as of:
            old_path = of.name
        new_path = old_path + '_new.db'
        try:
            _make_old_db(old_path)

            with (
                patch('app.core.migration.init_spatialite'),
                patch('app.core.migration._register_geometry_columns'),
                patch('app.core.migration._create_spatial_indexes'),
            ):
                migrate_database(old_path, new_path)

            nc = sqlite3.connect(new_path)
            journal = nc.execute('PRAGMA journal_mode').fetchone()[0]
            nc.close()
            self.assertEqual(journal, 'wal')
        finally:
            for p in (old_path, new_path):
                if os.path.exists(p):
                    os.unlink(p)

    def test_new_tables_created(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as of:
            old_path = of.name
        new_path = old_path + '_new.db'
        try:
            _make_old_db(old_path)

            with (
                patch('app.core.migration.init_spatialite'),
                patch('app.core.migration._register_geometry_columns'),
                patch('app.core.migration._create_spatial_indexes'),
            ):
                migrate_database(old_path, new_path)

            nc = sqlite3.connect(new_path)
            tables = {
                r[0]
                for r in nc.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            nc.close()
            for expected in NEW_TABLES:
                self.assertIn(expected, tables)
        finally:
            for p in (old_path, new_path):
                if os.path.exists(p):
                    os.unlink(p)

    def test_auth_path_none_is_skipped(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as of:
            old_path = of.name
        new_path = old_path + '_new.db'
        try:
            _make_old_db(old_path)

            with (
                patch('app.core.migration.init_spatialite'),
                patch('app.core.migration._register_geometry_columns'),
                patch('app.core.migration._create_spatial_indexes'),
            ):
                migrate_database(old_path, new_path, auth_path=None)
            self.assertTrue(os.path.exists(new_path))
        finally:
            for p in (old_path, new_path):
                if os.path.exists(p):
                    os.unlink(p)

    def test_spatialite_init_called(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as of:
            old_path = of.name
        new_path = old_path + '_new.db'
        try:
            _make_old_db(old_path)

            mock_init = MagicMock()
            with (
                patch('app.core.migration.init_spatialite', mock_init),
                patch('app.core.migration._register_geometry_columns'),
                patch('app.core.migration._create_spatial_indexes'),
            ):
                migrate_database(old_path, new_path)
            mock_init.assert_called_once()
        finally:
            for p in (old_path, new_path):
                if os.path.exists(p):
                    os.unlink(p)

    def test_old_closed_in_finally(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as of:
            old_path = of.name
        new_path = old_path + '_new.db'
        try:
            _make_old_db(old_path)

            with (
                patch('app.core.migration.init_spatialite'),
                patch('app.core.migration._register_geometry_columns'),
                patch('app.core.migration._create_spatial_indexes'),
            ):
                migrate_database(old_path, new_path)
            self.assertTrue(os.path.exists(new_path))
        finally:
            for p in (old_path, new_path):
                if os.path.exists(p):
                    os.unlink(p)

    def test_migration_logs_completion(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as of:
            old_path = of.name
        new_path = old_path + '_new.db'
        try:
            _make_old_db(old_path)

            with (
                patch('app.core.migration.init_spatialite'),
                patch('app.core.migration._register_geometry_columns'),
                patch('app.core.migration._create_spatial_indexes'),
                self.assertLogs('app.core.migration', level='INFO') as cm,
            ):
                migrate_database(old_path, new_path)
            self.assertTrue(any('Migration complete' in m for m in cm.output))
        finally:
            for p in (old_path, new_path):
                if os.path.exists(p):
                    os.unlink(p)


if __name__ == '__main__':
    unittest.main()
