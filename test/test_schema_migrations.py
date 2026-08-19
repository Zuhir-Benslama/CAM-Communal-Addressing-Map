"""Tests for app.core._schema_migrations."""

import unittest
from unittest.mock import MagicMock, patch


class TestAddColumnIfNotExists(unittest.TestCase):
    def test_skips_when_table_missing(self):
        from app.core._schema_migrations import _add_column_if_not_exists

        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = [0]
        mock_conn.execute.return_value = mock_result
        _add_column_if_not_exists(mock_conn, 'nonexistent', 'col', 'TEXT')

    def test_skips_when_column_exists(self):
        from app.core._schema_migrations import _add_column_if_not_exists

        mock_conn = MagicMock()
        count_result = MagicMock()
        count_result.fetchone.return_value = [1]
        pragma_result = MagicMock()
        # PRAGMA table_info returns (cid, name, type, notnull, dflt_value, pk)
        pragma_result.fetchall.return_value = [
            (0, 'id', 'TEXT', 0, None, 1),
            (1, 'existing_col', 'TEXT', 0, None, 0),
        ]
        mock_conn.execute.side_effect = [count_result, pragma_result]
        _add_column_if_not_exists(mock_conn, 'table', 'existing_col', 'TEXT')
        self.assertEqual(mock_conn.execute.call_count, 2)

    def test_adds_column_when_missing(self):
        from app.core._schema_migrations import _add_column_if_not_exists

        mock_conn = MagicMock()
        count_result = MagicMock()
        count_result.fetchone.return_value = [1]
        pragma_result = MagicMock()
        pragma_result.fetchall.return_value = [
            (0, 'id', 'TEXT', 0, None, 1),
        ]
        mock_conn.execute.side_effect = [count_result, pragma_result, MagicMock()]
        _add_column_if_not_exists(mock_conn, 'table', 'new_col', 'TEXT')
        self.assertEqual(mock_conn.execute.call_count, 3)

    def test_validates_safe_name(self):
        from app.core._schema_migrations import _add_column_if_not_exists

        mock_conn = MagicMock()
        with self.assertRaises(ValueError):
            _add_column_if_not_exists(mock_conn, '123bad', 'col', 'TEXT')


class TestSpatialIndexExists(unittest.TestCase):
    def test_returns_true_when_found(self):
        from app.core._schema_migrations import _spatial_index_exists

        mock_conn = MagicMock()
        result = MagicMock()
        result.fetchone.return_value = (1,)
        mock_conn.execute.return_value = result
        self.assertTrue(_spatial_index_exists(mock_conn, 'table', 'geometry'))

    def test_returns_false_when_not_found(self):
        from app.core._schema_migrations import _spatial_index_exists

        mock_conn = MagicMock()
        result = MagicMock()
        result.fetchone.return_value = (0,)
        mock_conn.execute.return_value = result
        self.assertFalse(_spatial_index_exists(mock_conn, 'table', 'geometry'))

    def test_returns_false_when_none(self):
        from app.core._schema_migrations import _spatial_index_exists

        mock_conn = MagicMock()
        result = MagicMock()
        result.fetchone.return_value = None
        mock_conn.execute.return_value = result
        self.assertFalse(_spatial_index_exists(mock_conn, 'table', 'geometry'))


class TestMigrateFunctions(unittest.TestCase):
    def test_migrate_missing_columns(self):
        from app.core._schema_migrations import _migrate_missing_columns

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = lambda s: mock_conn
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        _migrate_missing_columns(mock_engine)

    def test_migrate_old_columns(self):
        from app.core._schema_migrations import _migrate_old_columns

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        # PRAGMA returns (cid, name, type, notnull, dflt_value, pk) tuples
        mock_result.fetchall.return_value = [
            (0, 'id', 'TEXT', 0, None, 1),
        ]
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__ = lambda s: mock_conn
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        _migrate_old_columns(mock_engine)

    def test_migrate_timestamp_columns(self):
        from app.core._schema_migrations import _migrate_timestamp_columns

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            (0, 'id', 'TEXT', 0, None, 1),
        ]
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__ = lambda s: mock_conn
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        _migrate_timestamp_columns(mock_engine)

    def test_create_spatial_indexes(self):
        from app.core._schema_migrations import _create_spatial_indexes

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = lambda s: mock_conn
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
        _create_spatial_indexes(mock_engine)

    def test_create_views_no_file(self):
        from app.core._schema_migrations import _create_views

        mock_engine = MagicMock()
        with patch('app.core._schema_migrations.Path') as mock_path:
            mock_path.return_value.exists.return_value = False
            _create_views(mock_engine)
