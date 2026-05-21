"""Tests for gui/popup_dialog.py."""
import importlib
import sys
import unittest
from unittest.mock import MagicMock

from PyQt5.QtWidgets import QApplication

from .helpers import setup_gui_mocks


class TestPopupDialog(unittest.TestCase):
    """Test PopupDialog creation and basic behaviour."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.popup_dialog', 'gui/popup_dialog.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.popup_dialog'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.iface = MagicMock()
        self.dialog = self.mod.PopupDialog(
            'test_road', 'roads', 'pk_uid', self.iface,
        )

    def test_dialog_created(self):
        self.assertIsNotNone(self.dialog)

    def test_layer_name_value_stored(self):
        self.assertEqual(self.dialog.layer_name_value, 'test_road')

    def test_layer_name_key_stored(self):
        self.assertEqual(self.dialog.layer_name_key, 'roads')

    def test_attribute_stored(self):
        self.assertEqual(self.dialog.attribute, 'pk_uid')


if __name__ == '__main__':
    unittest.main()
