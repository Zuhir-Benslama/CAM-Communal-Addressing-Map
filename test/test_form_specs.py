"""Tests for gui.form_specs — shared form field specs."""

import unittest

from qgis.PyQt.QtWidgets import QComboBox, QLabel, QLineEdit, QPushButton  # noqa: F401

from test.helpers import setup_gui_mocks


def _load_module():
    setup_gui_mocks()
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        'plans_adressage.gui.form_specs',
        'gui/form_specs.py',
    )
    mod = importlib.util.module_from_spec(spec)
    sys_modules = __import__('sys').modules
    sys_modules['plans_adressage.gui.form_specs'] = mod
    spec.loader.exec_module(mod)
    return mod


class TestFormSpecs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def test_six_entity_row_lists(self):
        for name in (
            'ZONE_ROWS',
            'ROAD_ROWS',
            'ORG_ROWS',
            'CITY_ROWS',
            'NUM_ROWS',
            'PAN_ROWS',
        ):
            with self.subTest(name=name):
                rows = getattr(self.mod, name)
                self.assertGreaterEqual(len(rows), 2)

    def test_kinds_are_valid(self):
        for rows in (
            self.mod.ZONE_ROWS,
            self.mod.ROAD_ROWS,
            self.mod.ORG_ROWS,
            self.mod.CITY_ROWS,
            self.mod.NUM_ROWS,
            self.mod.PAN_ROWS,
        ):
            for row in rows:
                with self.subTest(row=row):
                    self.assertIn(row.kind, ('combo', 'text', 'button'))

    def test_non_button_rows_have_both_attrs_and_label(self):
        for rows in (
            self.mod.ZONE_ROWS,
            self.mod.ROAD_ROWS,
            self.mod.ORG_ROWS,
            self.mod.CITY_ROWS,
            self.mod.NUM_ROWS,
            self.mod.PAN_ROWS,
        ):
            for row in rows:
                if row.kind == 'button':
                    continue
                with self.subTest(row=row):
                    self.assertTrue(row.main_attr)
                    self.assertTrue(row.popup_attr)
                    self.assertTrue(row.label)
                    self.assertTrue(row.obj_name)

    def test_button_rows_have_no_obj_name_or_label_obj(self):
        for rows in (self.mod.NUM_ROWS, self.mod.PAN_ROWS):
            buttons = [row for row in rows if row.kind == 'button']
            self.assertTrue(buttons)
            for row in buttons:
                with self.subTest(row=row):
                    self.assertEqual(row.obj_name, '')
                    self.assertEqual(row.label_obj, '')
                    self.assertTrue(row.main_attr)
                    self.assertTrue(row.popup_attr)


if __name__ == '__main__':
    unittest.main()
