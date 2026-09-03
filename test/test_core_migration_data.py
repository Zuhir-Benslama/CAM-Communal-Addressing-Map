"""Tests for app.core.migration data migration and spatial index helpers."""

import sqlite3
import unittest
from unittest.mock import MagicMock, patch

from app.core.migration import (
    COLUMN_MAP,
    GEOMETRY_TYPES,
    _create_spatial_indexes,
    _migrate_data,
)


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


if __name__ == '__main__':
    unittest.main()
