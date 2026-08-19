"""Extended tests for app.core._schema_migrations — coverage for all
private migration helpers beyond ``_add_column_if_not_exists`` and
``_spatial_index_exists``.
"""

import unittest
from unittest.mock import MagicMock, patch, call

from sqlalchemy.exc import OperationalError, SQLAlchemyError


def _make_engine(mock_conn: MagicMock) -> MagicMock:
    """Return a mock engine whose connect() context manager yields *mock_conn*."""
    engine = MagicMock()
    ctx = engine.connect.return_value
    ctx.__enter__ = MagicMock(return_value=mock_conn)
    ctx.__exit__ = MagicMock(return_value=False)
    return engine


def _pragmas(*col_names: str) -> MagicMock:
    """Return a mock result for PRAGMA table_info(...).fetchall()."""
    result = MagicMock()
    result.fetchall.return_value = [
        (i, name, 'TEXT', 0, None, 0) for i, name in enumerate(col_names)
    ]
    return result


# ── _migrate_missing_columns ──────────────────────────────────────────────


class TestMigrateMissingColumns(unittest.TestCase):
    @patch('app.core._schema_migrations._add_column_if_not_exists')
    def test_calls_add_for_each_missing_column(self, mock_add):
        from app.core._schema_migrations import (
            _migrate_missing_columns,
            _MISSING_COLUMNS,
        )

        engine = _make_engine(MagicMock())
        _migrate_missing_columns(engine)
        self.assertEqual(mock_add.call_count, len(_MISSING_COLUMNS))

    @patch('app.core._schema_migrations._add_column_if_not_exists')
    def test_uses_engine_context_manager(self, mock_add):
        from app.core._schema_migrations import _migrate_missing_columns

        engine = _make_engine(MagicMock())
        _migrate_missing_columns(engine)
        engine.connect.assert_called_once()


# ── _create_spatial_indexes ───────────────────────────────────────────────


class TestCreateSpatialIndexes(unittest.TestCase):
    @patch('app.core._schema_migrations._spatial_index_exists', return_value=True)
    def test_skips_when_index_already_exists(self, mock_exists):
        from app.core._schema_migrations import (
            _create_spatial_indexes,
            _SPATIAL_INDEXES,
        )

        engine = _make_engine(MagicMock())
        _create_spatial_indexes(engine)
        self.assertEqual(mock_exists.call_count, len(_SPATIAL_INDEXES))
        # conn.execute should only be called for the spatial_index_exists checks
        conn = engine.connect().__enter__.return_value
        for c in conn.execute.call_args_list:
            # First positional arg is a text() result — just verify it was the check query
            self.assertIn('spatial_index_enabled', str(c))

    @patch('app.core._schema_migrations._spatial_index_exists', return_value=False)
    def test_creates_index_when_missing(self, mock_exists):
        from app.core._schema_migrations import _create_spatial_indexes

        engine = _make_engine(MagicMock())
        _create_spatial_indexes(engine)
        conn = engine.connect().__enter__.return_value
        self.assertTrue(conn.execute.call_count > 0)
        conn.commit.assert_called()

    @patch('app.core._schema_migrations._spatial_index_exists', return_value=False)
    def test_continues_on_operational_error(self, mock_exists):
        from app.core._schema_migrations import _create_spatial_indexes

        conn = MagicMock()
        conn.execute.side_effect = OperationalError('test', {}, Exception('cause'))
        engine = _make_engine(conn)
        _create_spatial_indexes(engine)
        conn.commit.assert_not_called()

    @patch('app.core._schema_migrations._spatial_index_exists', return_value=False)
    def test_continues_on_sqlalchemy_error(self, mock_exists):
        from app.core._schema_migrations import _create_spatial_indexes

        conn = MagicMock()
        conn.execute.side_effect = SQLAlchemyError('test')
        engine = _make_engine(conn)
        _create_spatial_indexes(engine)


# ── _rename_column_if_needed ──────────────────────────────────────────────


class TestRenameColumnIfNeeded(unittest.TestCase):
    @patch('app.core._schema_migrations.text')
    def test_renames_when_old_exists_and_new_absent(self, mock_text):
        from app.core._schema_migrations import _rename_column_if_needed

        conn = MagicMock()
        _rename_column_if_needed(conn, 'zone', 'pkuid', 'id', {'pkuid', 'other'})
        conn.execute.assert_called_once()
        conn.commit.assert_called_once()

    @patch('app.core._schema_migrations.text')
    def test_skips_when_old_not_in_existing(self, mock_text):
        from app.core._schema_migrations import _rename_column_if_needed

        conn = MagicMock()
        _rename_column_if_needed(conn, 'zone', 'pkuid', 'id', {'other'})
        conn.execute.assert_not_called()

    @patch('app.core._schema_migrations.text')
    def test_skips_when_new_already_exists(self, mock_text):
        from app.core._schema_migrations import _rename_column_if_needed

        conn = MagicMock()
        _rename_column_if_needed(conn, 'zone', 'pkuid', 'id', {'pkuid', 'id'})
        conn.execute.assert_not_called()

    @patch('app.core._schema_migrations.text')
    def test_handles_sqlalchemy_error_on_rename(self, mock_text):
        from app.core._schema_migrations import _rename_column_if_needed

        conn = MagicMock()
        conn.execute.side_effect = SQLAlchemyError('test')
        _rename_column_if_needed(conn, 'zone', 'pkuid', 'id', {'pkuid', 'other'})
        conn.execute.assert_called_once()
        conn.commit.assert_not_called()


# ── _migrate_old_columns ─────────────────────────────────────────────────


class TestMigrateOldColumns(unittest.TestCase):
    @patch('app.core._schema_migrations._rename_column_if_needed')
    def test_iterates_all_tables_and_columns(self, mock_rename):
        from app.core._schema_migrations import (
            _migrate_old_columns,
            _OLD_COLUMN_RENAMES,
        )

        mock_conn = MagicMock()
        mock_conn.execute.return_value = _pragmas('pkuid', 'idLoc')
        engine = _make_engine(mock_conn)
        _migrate_old_columns(engine)
        total_renames = sum(len(v) for v in _OLD_COLUMN_RENAMES.values())
        self.assertEqual(mock_rename.call_count, total_renames)

    @patch('app.core._schema_migrations._rename_column_if_needed')
    def test_passes_correct_existing_cols(self, mock_rename):
        from app.core._schema_migrations import _migrate_old_columns

        mock_conn = MagicMock()
        mock_conn.execute.return_value = _pragmas('pkuid', 'idLoc')
        engine = _make_engine(mock_conn)
        _migrate_old_columns(engine)
        for c in mock_rename.call_args_list:
            existing = c[0][4]  # 5th positional arg
            self.assertIn('pkuid', existing)
            self.assertIn('idLoc', existing)


# ── _create_views ─────────────────────────────────────────────────────────


class TestCreateViews(unittest.TestCase):
    @patch('app.core._schema_migrations.Path')
    def test_returns_early_when_file_missing(self, mock_path_cls):
        from app.core._schema_migrations import _create_views

        mock_path_cls.return_value.exists.return_value = False
        engine = _make_engine(MagicMock())
        _create_views(engine)
        engine.connect.assert_not_called()

    @patch('app.core._schema_migrations.Path')
    def test_executes_statements_from_file(self, mock_path_cls):
        from app.core._schema_migrations import _create_views

        exists_mock = mock_path_cls.return_value.exists
        exists_mock.return_value = True
        open_mock = mock_path_cls.return_value.open.return_value.__enter__
        fake_file = MagicMock()
        fake_file.read.return_value = (
            'CREATE VIEW v1 AS SELECT 1; CREATE VIEW v2 AS SELECT 2;'
        )
        open_mock.return_value = fake_file
        mock_path_cls.return_value.open.return_value.__exit__ = MagicMock(
            return_value=False
        )
        engine = _make_engine(MagicMock())
        _create_views(engine)
        conn = engine.connect().__enter__.return_value
        self.assertEqual(conn.execute.call_count, 2)
        conn.commit.assert_called_once()

    @patch('app.core._schema_migrations.Path')
    def test_skips_blank_statements(self, mock_path_cls):
        from app.core._schema_migrations import _create_views

        exists_mock = mock_path_cls.return_value.exists
        exists_mock.return_value = True
        open_mock = mock_path_cls.return_value.open.return_value.__enter__
        fake_file = MagicMock()
        fake_file.read.return_value = 'CREATE VIEW v1 AS SELECT 1; ;;  ;'
        open_mock.return_value = fake_file
        mock_path_cls.return_value.open.return_value.__exit__ = MagicMock(
            return_value=False
        )
        engine = _make_engine(MagicMock())
        _create_views(engine)
        conn = engine.connect().__enter__.return_value
        self.assertEqual(conn.execute.call_count, 1)

    @patch('app.core._schema_migrations.Path')
    def test_handles_sqlalchemy_error(self, mock_path_cls):
        from app.core._schema_migrations import _create_views

        exists_mock = mock_path_cls.return_value.exists
        exists_mock.return_value = True
        open_mock = mock_path_cls.return_value.open.return_value.__enter__
        fake_file = MagicMock()
        fake_file.read.return_value = 'BAD SQL;'
        open_mock.return_value = fake_file
        mock_path_cls.return_value.open.return_value.__exit__ = MagicMock(
            return_value=False
        )
        conn = MagicMock()
        conn.execute.side_effect = SQLAlchemyError('test')
        engine = _make_engine(conn)
        _create_views(engine)
        conn.commit.assert_not_called()


# ── _migrate_timestamp_columns ────────────────────────────────────────────


class TestMigrateTimestampColumns(unittest.TestCase):
    @patch('app.core._schema_migrations._add_column_if_not_exists')
    def test_calls_add_for_created_at_and_updated_at_per_table(self, mock_add):
        from app.core._schema_migrations import (
            _migrate_timestamp_columns,
            _TIMESTAMP_TABLES,
        )

        engine = _make_engine(MagicMock())
        _migrate_timestamp_columns(engine)
        self.assertEqual(mock_add.call_count, len(_TIMESTAMP_TABLES) * 2)

    @patch('app.core._schema_migrations._add_column_if_not_exists')
    def test_passes_correct_args(self, mock_add):
        from app.core._schema_migrations import (
            _migrate_timestamp_columns,
            _TIMESTAMP_TABLES,
        )

        engine = _make_engine(MagicMock())
        _migrate_timestamp_columns(engine)
        expected_calls = []
        for table in _TIMESTAMP_TABLES:
            expected_calls.append(
                call(mock_add.call_args_list[0][0][0], table, 'created_at', 'DATETIME')
            )
        # Just verify the first call signature pattern
        first_call = mock_add.call_args_list[0]
        self.assertEqual(first_call[0][1], _TIMESTAMP_TABLES[0])
        self.assertEqual(first_call[0][2], 'created_at')
        self.assertEqual(first_call[0][3], 'DATETIME')

    @patch('app.core._schema_migrations._add_column_if_not_exists')
    def test_continues_after_sqlalchemy_error(self, mock_add):
        from app.core._schema_migrations import (
            _migrate_timestamp_columns,
            _TIMESTAMP_TABLES,
        )

        # Fail on the second call (updated_at of first table) so that
        # created_at succeeds and updated_at raises; the except block
        # catches it and the loop moves to the next table.
        side_effects = [MagicMock()] * (len(_TIMESTAMP_TABLES) * 2)
        side_effects[1] = SQLAlchemyError('fail')
        mock_add.side_effect = side_effects
        engine = _make_engine(MagicMock())
        _migrate_timestamp_columns(engine)
        self.assertEqual(mock_add.call_count, len(_TIMESTAMP_TABLES) * 2)


# ── _attach_and_merge_users ──────────────────────────────────────────────


class TestAttachAndMergeUsers(unittest.TestCase):
    @patch('app.core._schema_migrations.text')
    def test_merges_when_missing_users_gt_zero(self, mock_text):
        from app.core._schema_migrations import _attach_and_merge_users

        inner_conn = MagicMock()
        count_result = MagicMock()
        count_result.fetchone.return_value = [3]
        inner_conn.execute.side_effect = [
            MagicMock(),
            count_result,
            MagicMock(),
            MagicMock(),
        ]
        engine = _make_engine(inner_conn)
        _attach_and_merge_users(engine, '/fake/auth.sqlite')
        self.assertEqual(
            inner_conn.execute.call_count, 4
        )  # ATTACH, SELECT, INSERT, DETACH
        inner_conn.commit.assert_called()

    @patch('app.core._schema_migrations.text')
    def test_no_merge_when_missing_users_zero(self, mock_text):
        from app.core._schema_migrations import _attach_and_merge_users

        inner_conn = MagicMock()
        count_result = MagicMock()
        count_result.fetchone.return_value = [0]
        inner_conn.execute.side_effect = [MagicMock(), count_result, MagicMock()]
        engine = _make_engine(inner_conn)
        _attach_and_merge_users(engine, '/fake/auth.sqlite')
        # ATTACH, SELECT count, DETACH — no INSERT, no commit
        inner_conn.commit.assert_not_called()

    @patch('app.core._schema_migrations.text')
    def test_always_detaches_even_on_error(self, mock_text):
        from app.core._schema_migrations import _attach_and_merge_users

        inner_conn = MagicMock()
        # First call (ATTACH) succeeds, second (SELECT count) raises
        inner_conn.execute.side_effect = [
            MagicMock(),
            SQLAlchemyError('fail'),
            MagicMock(),
        ]
        engine = _make_engine(inner_conn)
        # The function has try/finally (no except), so the error propagates
        with self.assertRaises(SQLAlchemyError):
            _attach_and_merge_users(engine, '/fake/auth.sqlite')
        # DETACH was still called via the finally block (3rd call)
        self.assertEqual(inner_conn.execute.call_count, 3)


# ── _rename_migrated_auth ────────────────────────────────────────────────


class TestRenameMigratedAuth(unittest.TestCase):
    @patch('app.core._schema_migrations.Path')
    def test_renames_successfully(self, mock_path_cls):
        from app.core._schema_migrations import _rename_migrated_auth

        _rename_migrated_auth('/fake/auth.sqlite')
        mock_path_cls.assert_any_call('/fake/auth.sqlite')
        mock_path_cls.assert_any_call('/fake/auth.sqlite.migrated')
        mock_path_cls('/fake/auth.sqlite').rename.assert_called_once_with(
            mock_path_cls('/fake/auth.sqlite.migrated')
        )

    @patch('app.core._schema_migrations.Path')
    def test_handles_os_error(self, mock_path_cls):
        from app.core._schema_migrations import _rename_migrated_auth

        mock_path_cls.return_value.rename.side_effect = OSError('denied')
        _rename_migrated_auth('/fake/auth.sqlite')
        mock_path_cls.return_value.rename.assert_called_once()


# ── _migrate_users_from_auth ─────────────────────────────────────────────


class TestMigrateUsersFromAuth(unittest.TestCase):
    @patch('app.core._schema_migrations._rename_migrated_auth')
    @patch('app.core._schema_migrations._attach_and_merge_users')
    @patch('app.core._schema_migrations.Path')
    def test_returns_early_when_no_auth_file(
        self, mock_path_cls, mock_merge, mock_rename
    ):
        from app.core._schema_migrations import _migrate_users_from_auth

        mock_path_cls.return_value.exists.return_value = False
        engine = MagicMock()
        _migrate_users_from_auth(engine)
        mock_merge.assert_not_called()
        mock_rename.assert_not_called()

    @patch('app.core._schema_migrations._rename_migrated_auth')
    @patch('app.core._schema_migrations._attach_and_merge_users')
    @patch('app.core._schema_migrations.Path')
    def test_merges_and_renames_when_file_exists(
        self, mock_path_cls, mock_merge, mock_rename
    ):
        from app.core._schema_migrations import _migrate_users_from_auth

        mock_path_cls.return_value.exists.return_value = True
        engine = MagicMock()
        _migrate_users_from_auth(engine)
        mock_merge.assert_called_once()
        mock_rename.assert_called_once()

    @patch('app.core._schema_migrations._rename_migrated_auth')
    @patch('app.core._schema_migrations._attach_and_merge_users')
    @patch('app.core._schema_migrations.Path')
    def test_returns_on_sqlalchemy_error(self, mock_path_cls, mock_merge, mock_rename):
        from app.core._schema_migrations import _migrate_users_from_auth

        mock_path_cls.return_value.exists.return_value = True
        mock_merge.side_effect = SQLAlchemyError('fail')
        engine = MagicMock()
        _migrate_users_from_auth(engine)
        mock_rename.assert_not_called()

    @patch('app.core._schema_migrations._rename_migrated_auth')
    @patch('app.core._schema_migrations._attach_and_merge_users')
    @patch('app.core._schema_migrations.Path')
    def test_returns_on_os_error(self, mock_path_cls, mock_merge, mock_rename):
        from app.core._schema_migrations import _migrate_users_from_auth

        mock_path_cls.return_value.exists.return_value = True
        mock_merge.side_effect = OSError('fail')
        engine = MagicMock()
        _migrate_users_from_auth(engine)
        mock_rename.assert_not_called()
