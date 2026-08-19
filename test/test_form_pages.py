"""Tests for gui.pages.form_pages."""

import importlib
import sys
import unittest
from unittest.mock import MagicMock

from test.helpers import setup_gui_mocks


def _load_module():
    setup_gui_mocks()
    _qtwidgets = sys.modules['qgis.PyQt.QtWidgets']
    _qtwidgets.QLabel = lambda *a, **kw: MagicMock()
    _qtwidgets.QPushButton = lambda *a, **kw: MagicMock()
    spec = importlib.util.spec_from_file_location(
        'plans_adressage.gui.pages.form_pages',
        'gui/pages/form_pages.py',
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules['plans_adressage.gui.pages.form_pages'] = mod
    spec.loader.exec_module(mod)
    return mod


class TestFormPageBuilders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def _make_dialog(self):
        dialog = MagicMock()
        dialog._form_stack = MagicMock()
        dialog._held_widgets = []
        return dialog

    def test_build_zone_form(self):
        dialog = self._make_dialog()
        self.mod.build_zone_form(dialog)
        dialog._form_stack.addWidget.assert_called_once()

    def test_build_road_form(self):
        dialog = self._make_dialog()
        self.mod.build_road_form(dialog)
        dialog._form_stack.addWidget.assert_called_once()

    def test_build_org_form(self):
        dialog = self._make_dialog()
        self.mod.build_org_form(dialog)
        dialog._form_stack.addWidget.assert_called_once()

    def test_build_city_form(self):
        dialog = self._make_dialog()
        self.mod.build_city_form(dialog)
        dialog._form_stack.addWidget.assert_called_once()

    def test_build_num_form(self):
        dialog = self._make_dialog()
        self.mod.build_num_form(dialog)
        dialog._form_stack.addWidget.assert_called_once()

    def test_build_pan_form(self):
        dialog = self._make_dialog()
        self.mod.build_pan_form(dialog)
        dialog._form_stack.addWidget.assert_called_once()


if __name__ == '__main__':
    unittest.main()
