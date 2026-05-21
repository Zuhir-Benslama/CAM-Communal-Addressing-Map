"""Tests for gui/entity_list_dialog.py."""
import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from PyQt5.QtWidgets import QApplication

from .helpers import setup_gui_mocks


class TestEntityListDialog(unittest.TestCase):
    """Test EntityListDialog creation and pagination."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.entity_list_dialog',
            'gui/entity_list_dialog.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.entity_list_dialog'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.dialog = self.mod.EntityListDialog('Road', 'roads', parent=None)

    def test_dialog_created(self):
        self.assertIsNotNone(self.dialog)

    def test_dialog_title_set(self):
        title = self.dialog.windowTitle()
        self.assertIsNotNone(title)

    def test_initial_page_zero(self):
        self.assertEqual(self.dialog._page, 0)

    def test_page_size_constant(self):
        self.assertEqual(self.dialog.PAGE_SIZE, 50)

    def test_next_page_increases_page(self):
        self.dialog._total_records = 100
        self.dialog._next_page()
        self.assertEqual(self.dialog._page, 1)

    def test_prev_page_decreases_page(self):
        self.dialog._page = 2
        self.dialog._total_records = 100
        self.dialog._prev_page()
        self.assertEqual(self.dialog._page, 1)

    def test_prev_page_stops_at_zero(self):
        self.dialog._page = 0
        self.dialog._prev_page()
        self.assertEqual(self.dialog._page, 0)


if __name__ == '__main__':
    unittest.main()
