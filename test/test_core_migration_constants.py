"""Tests for app.core.migration constants (COLUMN_MAP, NEW_TABLES, etc.)."""

import unittest

from app.core.migration import COLUMN_MAP, GEOMETRY_TYPES, NEW_TABLES


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


if __name__ == '__main__':
    unittest.main()
