"""Tests for app.core.migration."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock

from app.core.migration import (
    COLUMN_MAP,
    GEOMETRY_TYPES,
    NEW_TABLES,
    register_geometry,
    create_spatial_index,
    migrate_database,
)


class TestColumnMap(unittest.TestCase):
    def test_has_expected_tables(self):
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

    def test_each_table_maps_old_to_new_columns(self):
        for _table, mapping in COLUMN_MAP.items():
            self.assertIsInstance(mapping, dict)
            for old_col, new_col in mapping.items():
                self.assertIsInstance(old_col, str)
                self.assertIsInstance(new_col, str)


class TestNewTables(unittest.TestCase):
    def test_has_all_spatial_tables(self):
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

    def test_ddl_is_string(self):
        for _table, ddl in NEW_TABLES.items():
            self.assertIsInstance(ddl, str)
            self.assertIn('CREATE TABLE', ddl)


class TestGeometryTypes(unittest.TestCase):
    def test_has_all_spatial_entities(self):
        expected = {
            'zone',
            'subdivision',
            'road',
            'organization',
            'numbering',
            'panel_sign',
        }
        self.assertEqual(set(GEOMETRY_TYPES.keys()), expected)

    def test_each_has_tuple_of_4(self):
        for table, config in GEOMETRY_TYPES.items():
            self.assertEqual(len(config), 4, f'{table} should have 4 elements')
            self.assertIn(config[0], ('POLYGON', 'LINESTRING', 'POINT'))
            self.assertEqual(config[1], 4326)


class TestRegisterGeometry(unittest.TestCase):
    def test_validates_table_name(self):
        conn = MagicMock()
        with self.assertRaises(ValueError):
            register_geometry(conn, '123invalid', 'geometry', ('POINT', 4326, 2, 1))

    def test_validates_column_name(self):
        conn = MagicMock()
        with self.assertRaises(ValueError):
            register_geometry(conn, 'valid_table', 'bad-col!', ('POINT', 4326, 2, 1))

    def test_calls_execute(self):
        conn = MagicMock()
        register_geometry(conn, 'roads', 'geometry', ('LINESTRING', 4326, 2, 2))
        conn.execute.assert_called_once()


class TestCreateSpatialIndex(unittest.TestCase):
    def test_validates_names(self):
        conn = MagicMock()
        with self.assertRaises(ValueError):
            create_spatial_index(conn, 'DROP TABLE', 'geometry')

    def test_calls_execute(self):
        conn = MagicMock()
        create_spatial_index(conn, 'roads', 'geometry')
        conn.execute.assert_called_once()


class TestMigrateDatabase(unittest.TestCase):
    def test_raises_if_output_exists(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            path = f.name
        try:
            with self.assertRaises(FileExistsError):
                migrate_database('/nonexistent_old.db', path)
        finally:
            os.unlink(path)
