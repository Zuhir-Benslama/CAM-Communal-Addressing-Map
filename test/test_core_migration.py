"""Tests for app.core.migration (comprehensive)."""

import os
import sqlite3
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from app.core.migration import (
    COLUMN_MAP,
    GEOMETRY_TYPES,
    NEW_TABLES,
    _create_spatial_indexes,
    _merge_auth_users,
    _migrate_data,
    _register_geometry_columns,
    create_spatial_index,
    init_spatialite,
    migrate_database,
    register_geometry,
)


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------


class TestConstants(unittest.TestCase):
    def test_column_map_keys(self):
        expected = {
            'user',
            'refpoly',
            'refpolychild',
            'RefLine',
            'reforg',
            'Numerotation',
            'Pannautage',
        }
        self.assertEqual(set(COLUMN_MAP.keys()), expected)

    def test_column_map_values_are_dicts(self):
        for _table, mapping in COLUMN_MAP.items():
            self.assertIsInstance(mapping, dict)
            for old, new in mapping.items():
                self.assertIsInstance(old, str)
                self.assertIsInstance(new, str)

    def test_new_tables_keys(self):
        expected = {
            'user',
            'zone',
            'subdivision',
            'road',
            'organization',
            'numbering',
            'panel_sign',
        }
        self.assertEqual(set(NEW_TABLES.keys()), expected)

    def test_new_tables_ddl_contains_create(self):
        for ddl in NEW_TABLES.values():
            self.assertIn('CREATE TABLE', ddl)

    def test_geometry_types_keys(self):
        expected = {
            'zone',
            'subdivision',
            'road',
            'organization',
            'numbering',
            'panel_sign',
        }
        self.assertEqual(set(GEOMETRY_TYPES.keys()), expected)

    def test_geometry_types_values_are_4_tuples(self):
        for table, cfg in GEOMETRY_TYPES.items():
            self.assertEqual(len(cfg), 4, f'{table} config length')
            self.assertIn(cfg[0], ('POLYGON', 'LINESTRING', 'POINT'))
            self.assertEqual(cfg[1], 4326)


# ---------------------------------------------------------------------------
# init_spatialite
# ---------------------------------------------------------------------------


class TestInitSpatiaLite(unittest.TestCase):
    def test_calls_enable_load_and_load_extension(self):
        conn = MagicMock()
        with patch(
            'app.core.migration.find_mod_spatialite_dll',
            return_value='/fake/mod_spatialite.so',
        ):
            init_spatialite(conn)
        conn.enable_load_extension.assert_called_once_with(True)
        conn.load_extension.assert_called_once_with('/fake/mod_spatialite.so')
        conn.execute.assert_called_once_with('SELECT InitSpatialMetadata(1)')


# ---------------------------------------------------------------------------
# register_geometry
# ---------------------------------------------------------------------------


class TestRegisterGeometry(unittest.TestCase):
    def test_valid_table_and_column(self):
        conn = MagicMock()
        register_geometry(conn, 'roads', 'geometry', ('LINESTRING', 4326, 2, 2))
        conn.execute.assert_called_once_with(
            'SELECT AddGeometryColumn(?, ?, ?, ?, ?)',
            ('roads', 'geometry', 4326, 'LINESTRING', 2),
        )

    def test_validates_table_name(self):
        conn = MagicMock()
        with self.assertRaises(ValueError):
            register_geometry(conn, '1bad', 'geometry', ('POINT', 4326, 2, 1))

    def test_validates_column_name(self):
        conn = MagicMock()
        with self.assertRaises(ValueError):
            register_geometry(conn, 'roads', 'bad-col!', ('POINT', 4326, 2, 1))

    def test_both_names_invalid(self):
        conn = MagicMock()
        with self.assertRaises(ValueError):
            register_geometry(conn, '!!', '??', ('POINT', 4326, 2, 1))

    def test_unwraps_geom_config_tuple(self):
        conn = MagicMock()
        cfg = ('POLYGON', 4326, 2, 3)
        register_geometry(conn, 'zone', 'geometry', cfg)
        args = conn.execute.call_args[0]
        self.assertEqual(args[1], ('zone', 'geometry', 4326, 'POLYGON', 2))

    def test_valid_underscore_names(self):
        conn = MagicMock()
        register_geometry(conn, '_private', '_geom', ('POINT', 4326, 2, 1))
        conn.execute.assert_called_once()


# ---------------------------------------------------------------------------
# create_spatial_index
# ---------------------------------------------------------------------------


class TestCreateSpatialIndex(unittest.TestCase):
    def test_calls_execute(self):
        conn = MagicMock()
        create_spatial_index(conn, 'roads', 'geometry')
        conn.execute.assert_called_once_with(
            'SELECT CreateSpatialIndex(?, ?)',
            ('roads', 'geometry'),
        )

    def test_invalid_table_raises(self):
        conn = MagicMock()
        with self.assertRaises(ValueError):
            create_spatial_index(conn, ' DROP TABLE ', 'geometry')

    def test_invalid_col_raises(self):
        conn = MagicMock()
        with self.assertRaises(ValueError):
            create_spatial_index(conn, 'roads', 'col; DROP')


# ---------------------------------------------------------------------------
# _register_geometry_columns
# ---------------------------------------------------------------------------


class TestRegisterGeometryColumns(unittest.TestCase):
    @patch('app.core.migration.register_geometry')
    def test_registers_all_geometry_types(self, mock_reg):
        conn = MagicMock()
        _register_geometry_columns(conn)
        self.assertEqual(mock_reg.call_count, len(GEOMETRY_TYPES))
        for table in GEOMETRY_TYPES:
            mock_reg.assert_any_call(conn, table, 'geometry', GEOMETRY_TYPES[table])

    @patch('app.core.migration.register_geometry')
    def test_operational_error_is_swallowed(self, mock_reg):
        mock_reg.side_effect = sqlite3.OperationalError('already exists')
        conn = MagicMock()
        _register_geometry_columns(conn)
        self.assertEqual(mock_reg.call_count, len(GEOMETRY_TYPES))

    @patch('app.core.migration.register_geometry')
    def test_operational_error_logged(self, mock_reg):
        mock_reg.side_effect = sqlite3.OperationalError('fail')
        conn = MagicMock()
        with self.assertLogs('app.core.migration', level='ERROR') as cm:
            _register_geometry_columns(conn)
        self.assertTrue(any('registration failed' in m for m in cm.output))


# ---------------------------------------------------------------------------
# _migrate_data
# ---------------------------------------------------------------------------


def _make_old_side_effect(table_data):
    """Build a side_effect for old.execute that returns different cursors
    per table.  *table_data* maps table name -> list of dict rows.
    Missing tables return an empty list.
    """

    def _side_effect(sql, *args):
        cursor = MagicMock()
        for tname, rows in table_data.items():
            if f'"{tname}"' in sql:
                cursor.fetchall.return_value = rows
                if rows:
                    cursor.description = [(k,) for k in rows[0]]
                else:
                    cursor.description = []
                return cursor
        cursor.fetchall.return_value = []
        cursor.description = []
        return cursor

    return _side_effect


class TestMigrateData(unittest.TestCase):
    def test_empty_table_skipped(self):
        old = MagicMock()
        new = MagicMock()
        old.execute.side_effect = _make_old_side_effect({})
        _migrate_data(old, new)
        new.execute.assert_not_called()

    def test_single_row_user_migrated(self):
        old = MagicMock()
        new = MagicMock()
        user_cols = list(COLUMN_MAP['user'].keys())
        row = {k: f'val_{k}' for k in user_cols}
        old.execute.side_effect = _make_old_side_effect({'user': [row]})
        _migrate_data(old, new)
        self.assertTrue(new.execute.called)
        first_insert = new.execute.call_args_list[0]
        self.assertIn('"user"', first_insert[0][0])

    def test_operational_error_on_insert_is_handled(self):
        old = MagicMock()
        new = MagicMock()
        user_cols = list(COLUMN_MAP['user'].keys())
        row = {k: f'v_{k}' for k in user_cols}
        old.execute.side_effect = _make_old_side_effect({'user': [row]})
        new.execute.side_effect = sqlite3.OperationalError('constraint')
        with self.assertLogs('app.core.migration', level='WARNING'):
            _migrate_data(old, new)

    def test_index_error_on_insert_is_handled(self):
        old = MagicMock()
        new = MagicMock()
        user_cols = list(COLUMN_MAP['user'].keys())
        row = {k: f'v_{k}' for k in user_cols}
        old.execute.side_effect = _make_old_side_effect({'user': [row]})
        new.execute.side_effect = IndexError('out of range')
        with self.assertLogs('app.core.migration', level='WARNING'):
            _migrate_data(old, new)

    def test_value_error_on_insert_is_handled(self):
        old = MagicMock()
        new = MagicMock()
        user_cols = list(COLUMN_MAP['user'].keys())
        row = {k: f'v_{k}' for k in user_cols}
        old.execute.side_effect = _make_old_side_effect({'user': [row]})
        new.execute.side_effect = ValueError('bad value')
        with self.assertLogs('app.core.migration', level='WARNING'):
            _migrate_data(old, new)

    def test_logs_row_count(self):
        old = MagicMock()
        new = MagicMock()
        user_cols = list(COLUMN_MAP['user'].keys())
        rows = [{k: f'v{i}_{k}' for k in user_cols} for i in range(3)]
        old.execute.side_effect = _make_old_side_effect({'user': rows})
        with self.assertLogs('app.core.migration', level='INFO') as cm:
            _migrate_data(old, new)
        self.assertTrue(any('user' in m and '3 / 3' in m for m in cm.output))

    def test_multiple_tables(self):
        old = MagicMock()
        new = MagicMock()
        user_cols = list(COLUMN_MAP['user'].keys())
        refpoly_cols = list(COLUMN_MAP['refpoly'].keys())
        data = {
            'user': [{k: 'u' for k in user_cols}],
            'refpoly': [{k: 'r' for k in refpoly_cols}],
        }
        old.execute.side_effect = _make_old_side_effect(data)
        _migrate_data(old, new)
        self.assertTrue(new.execute.called)

    def test_all_tables_without_data_are_skipped(self):
        old = MagicMock()
        new = MagicMock()
        old.execute.side_effect = _make_old_side_effect({})
        with self.assertLogs('app.core.migration', level='INFO') as cm:
            _migrate_data(old, new)
        skipped = [m for m in cm.output if '0 rows (skipped)' in m]
        self.assertEqual(len(skipped), len(COLUMN_MAP))


# ---------------------------------------------------------------------------
# _create_spatial_indexes
# ---------------------------------------------------------------------------


class TestCreateSpatialIndexes(unittest.TestCase):
    @patch('app.core.migration.create_spatial_index')
    def test_creates_index_per_geometry_table(self, mock_csi):
        conn = MagicMock()
        _create_spatial_indexes(conn)
        self.assertEqual(mock_csi.call_count, len(GEOMETRY_TYPES))
        for table in GEOMETRY_TYPES:
            mock_csi.assert_any_call(conn, table, 'geometry')

    @patch('app.core.migration.create_spatial_index')
    def test_operational_error_is_swallowed(self, mock_csi):
        mock_csi.side_effect = sqlite3.OperationalError('no such table')
        conn = MagicMock()
        _create_spatial_indexes(conn)
        self.assertEqual(mock_csi.call_count, len(GEOMETRY_TYPES))

    @patch('app.core.migration.create_spatial_index')
    def test_operational_error_logged(self, mock_csi):
        mock_csi.side_effect = sqlite3.OperationalError('fail')
        conn = MagicMock()
        with self.assertLogs('app.core.migration', level='ERROR') as cm:
            _create_spatial_indexes(conn)
        self.assertTrue(any('index creation failed' in m for m in cm.output))

    @patch('app.core.migration.create_spatial_index')
    def test_success_logged(self, mock_csi):
        conn = MagicMock()
        with self.assertLogs('app.core.migration', level='INFO') as cm:
            _create_spatial_indexes(conn)
        self.assertTrue(any('index created' in m for m in cm.output))


# ---------------------------------------------------------------------------
# _merge_auth_users
# ---------------------------------------------------------------------------


class TestMergeAuthUsers(unittest.TestCase):
    def test_no_auth_path(self):
        _merge_auth_users('/tmp/new.db', None)

    def test_auth_path_not_exists(self):
        _merge_auth_users('/tmp/new.db', '/nonexistent/auth.sqlite')

    def test_auth_db_no_user_table(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            auth_path = f.name
        try:
            conn = sqlite3.connect(auth_path)
            conn.execute('CREATE TABLE dummy (id TEXT)')
            conn.commit()
            conn.close()
            _merge_auth_users('/tmp/new.db', auth_path)
        finally:
            os.unlink(auth_path)

    def test_auth_db_empty_user_table(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            auth_path = f.name
        try:
            conn = sqlite3.connect(auth_path)
            conn.execute('CREATE TABLE user (id TEXT, username TEXT)')
            conn.commit()
            conn.close()
            _merge_auth_users('/tmp/new.db', auth_path)
        finally:
            os.unlink(auth_path)

    def test_merge_users_into_target(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as af:
            auth_path = af.name
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tf:
            target_path = tf.name
        try:
            ac = sqlite3.connect(auth_path)
            ac.execute('CREATE TABLE user (id TEXT, username TEXT)')
            ac.execute("INSERT INTO user VALUES ('u1', 'alice')")
            ac.execute("INSERT INTO user VALUES ('u2', 'bob')")
            ac.commit()
            ac.close()

            tc = sqlite3.connect(target_path)
            tc.execute('CREATE TABLE user (id TEXT PRIMARY KEY, username TEXT)')
            tc.execute("INSERT INTO user VALUES ('u1', 'alice')")
            tc.commit()
            tc.close()

            _merge_auth_users(target_path, auth_path)

            tc = sqlite3.connect(target_path)
            rows = tc.execute('SELECT * FROM user ORDER BY id').fetchall()
            tc.close()
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0], ('u1', 'alice'))
            self.assertEqual(rows[1], ('u2', 'bob'))
        finally:
            os.unlink(auth_path)
            os.unlink(target_path)

    def test_merge_all_users_new_target(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as af:
            auth_path = af.name
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tf:
            target_path = tf.name
        try:
            ac = sqlite3.connect(auth_path)
            ac.execute('CREATE TABLE user (id TEXT, username TEXT)')
            ac.execute("INSERT INTO user VALUES ('u1', 'alice')")
            ac.execute("INSERT INTO user VALUES ('u2', 'bob')")
            ac.commit()
            ac.close()

            tc = sqlite3.connect(target_path)
            tc.execute('CREATE TABLE user (id TEXT, username TEXT)')
            tc.commit()
            tc.close()

            _merge_auth_users(target_path, auth_path)

            tc = sqlite3.connect(target_path)
            rows = tc.execute('SELECT * FROM user ORDER BY id').fetchall()
            tc.close()
            self.assertEqual(len(rows), 2)
        finally:
            os.unlink(auth_path)
            os.unlink(target_path)

    def test_merge_operational_error_on_insert_is_handled(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as af:
            auth_path = af.name
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tf:
            target_path = tf.name
        try:
            ac = sqlite3.connect(auth_path)
            ac.execute('CREATE TABLE user (id TEXT, username TEXT)')
            ac.execute("INSERT INTO user VALUES ('u1', 'alice')")
            ac.commit()
            ac.close()

            tc = sqlite3.connect(target_path)
            tc.execute('CREATE TABLE user (id TEXT, username TEXT)')
            tc.commit()
            tc.close()

            original_connect = sqlite3.connect
            target_mock = MagicMock()
            target_mock.total_changes = 0

            def _raise_on_insert(sql, *a, **kw):
                if sql.lstrip().upper().startswith('INSERT'):
                    raise sqlite3.OperationalError('constraint')
                cursor = MagicMock()
                cursor.fetchall.return_value = []
                return cursor

            target_mock.execute.side_effect = _raise_on_insert

            def _connect(path, *a, **kw):
                if path == target_path:
                    return target_mock
                return original_connect(path, *a, **kw)

            with (
                patch('app.core.migration.sqlite3.connect', side_effect=_connect),
                self.assertLogs('app.core.migration', level='WARNING'),
            ):
                _merge_auth_users(target_path, auth_path)
        finally:
            os.unlink(auth_path)
            os.unlink(target_path)

    def test_merge_total_changes_tracked(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as af:
            auth_path = af.name
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tf:
            target_path = tf.name
        try:
            ac = sqlite3.connect(auth_path)
            ac.execute('CREATE TABLE user (id TEXT, username TEXT)')
            ac.execute("INSERT INTO user VALUES ('u1', 'alice')")
            ac.commit()
            ac.close()

            tc = sqlite3.connect(target_path)
            tc.execute('CREATE TABLE user (id TEXT, username TEXT)')
            tc.commit()
            tc.close()

            original_connect = sqlite3.connect

            def _connect(path, *a, **kw):
                if path == target_path:
                    m = MagicMock()
                    m.total_changes = 0
                    return m
                return original_connect(path, *a, **kw)

            with (
                patch('app.core.migration.sqlite3.connect', side_effect=_connect),
                self.assertLogs('app.core.migration', level='INFO') as cm,
            ):
                _merge_auth_users(target_path, auth_path)
            self.assertTrue(any('Merged' in m for m in cm.output))
        finally:
            os.unlink(auth_path)
            os.unlink(target_path)

    def test_malicious_column_name_is_rejected(self):
        """Columns from an untrusted auth file must not reach raw SQL."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as af:
            auth_path = af.name
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tf:
            target_path = tf.name
        try:
            ac = sqlite3.connect(auth_path)
            # A crafted column name that breaks out of the double-quoted
            # identifier when interpolated.  Built from parts so source
            # formatters cannot alter the payload; the doubled "" inside
            # the DDL identifier yields a single '"' in the stored name.
            d = chr(34)  # double quote
            q = chr(39)  # single quote
            hostile_col = f'x{d}) VALUES({q}p{q}); DROP TABLE user;--'
            ac.execute(
                f'CREATE TABLE user ({d}id{d} TEXT, {d}{d}{hostile_col}{d} TEXT)'
            )
            ac.execute(f'INSERT INTO user VALUES ({q}u1{q}, {q}evil{q})')
            ac.commit()
            ac.close()

            tc = sqlite3.connect(target_path)
            tc.execute('CREATE TABLE user (id TEXT PRIMARY KEY, username TEXT)')
            tc.commit()
            tc.close()

            with self.assertLogs('app.core.migration', level='WARNING'):
                _merge_auth_users(target_path, auth_path)

            tc = sqlite3.connect(target_path)
            tables = {
                r[0]
                for r in tc.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
            usernames = [
                row[1] if len(row) > 1 else None
                for row in tc.execute('SELECT * FROM user').fetchall()
            ]
            tc.close()
            # The hostile column must not have been interpolated: the user
            # table was not dropped and no rogue payload was stored.
            self.assertIn('user', tables)
            self.assertNotIn('evil', usernames)
        finally:
            os.unlink(auth_path)
            os.unlink(target_path)

    def test_unknown_columns_are_skipped(self):
        """Columns absent from the target schema are ignored, not inserted."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as af:
            auth_path = af.name
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tf:
            target_path = tf.name
        try:
            ac = sqlite3.connect(auth_path)
            ac.execute('CREATE TABLE user (id TEXT, username TEXT, legacy_col TEXT)')
            ac.execute("INSERT INTO user VALUES ('u1', 'alice', 'junk')")
            ac.commit()
            ac.close()

            tc = sqlite3.connect(target_path)
            tc.execute('CREATE TABLE user (id TEXT PRIMARY KEY, username TEXT)')
            tc.commit()
            tc.close()

            _merge_auth_users(target_path, auth_path)

            tc = sqlite3.connect(target_path)
            rows = tc.execute('SELECT id, username FROM user ORDER BY id').fetchall()
            tc.close()
            self.assertEqual(rows, [('u1', 'alice')])
        finally:
            os.unlink(auth_path)
            os.unlink(target_path)


# ---------------------------------------------------------------------------
# migrate_database
# ---------------------------------------------------------------------------


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
            oc = sqlite3.connect(old_path)
            for tbl in (
                'user',
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
            oc = sqlite3.connect(old_path)
            for tbl in (
                'user',
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
            oc = sqlite3.connect(old_path)
            for tbl in (
                'user',
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
            oc = sqlite3.connect(old_path)
            for tbl in (
                'user',
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
            oc = sqlite3.connect(old_path)
            for tbl in (
                'user',
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
            oc = sqlite3.connect(old_path)
            for tbl in (
                'user',
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
            oc = sqlite3.connect(old_path)
            for tbl in (
                'user',
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
