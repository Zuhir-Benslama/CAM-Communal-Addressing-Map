"""Tests for app.core.migration spatialite geometry helpers."""

import sqlite3
import unittest
from unittest.mock import MagicMock, patch

from app.core.migration import (
    GEOMETRY_TYPES,
    _register_geometry_columns,
    create_spatial_index,
    init_spatialite,
    register_geometry,
)


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


if __name__ == '__main__':
    unittest.main()
