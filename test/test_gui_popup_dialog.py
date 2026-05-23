"""Tests for gui/popup_dialog.py."""
import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from PyQt5.QtWidgets import QComboBox

from .helpers import setup_gui_mocks, get_qapp


@unittest.skipIf(get_qapp() is None, 'PyQt5 not available')
class TestPopupDialog(unittest.TestCase):
    """Test PopupDialog creation and form population."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.popup_dialog', 'gui/popup_dialog.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.popup_dialog'] = cls.mod
        spec.loader.exec_module(cls.mod)
        parent = sys.modules.get('plans_adressage.gui')
        if parent is not None:
            setattr(parent, 'popup_dialog', cls.mod)

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

    def test_router_initialized(self):
        self.assertIsNotNone(self.dialog.router)

    def test_set_combo_value_by_data(self):
        combo = QComboBox()
        combo.addItem('Display A', 'val_a')
        combo.addItem('Display B', 'val_b')
        self.dialog._set_combo_value(combo, 'val_b')
        self.assertEqual(combo.currentIndex(), 1)

    def test_set_combo_value_by_text_fallback(self):
        combo = QComboBox()
        combo.addItem('Display A', 'val_a')
        combo.addItem('Display B', 'val_b')
        self.dialog._set_combo_value(combo, 'Display A')
        self.assertEqual(combo.currentIndex(), 0)

    def test_set_combo_value_no_match_leaves_index(self):
        combo = QComboBox()
        combo.addItem('Display A', 'val_a')
        self.dialog._set_combo_value(combo, 'nonexistent')
        self.assertEqual(combo.currentIndex(), 0)

    def test_route_switches_to_existing_page(self):
        page = MagicMock()
        page.objectName.return_value = 'test_page'
        self.dialog.router = MagicMock()
        self.dialog.router.findChild.return_value = page
        self.dialog.route('test_page')
        self.dialog.router.setCurrentWidget.assert_called_once_with(page)

    def test_route_ignores_missing_page(self):
        self.dialog.router = MagicMock()
        self.dialog.router.findChild.return_value = None
        self.dialog.route('nonexistent_page')
        self.dialog.router.setCurrentWidget.assert_not_called()

    def test_populate_dispatch_has_all_layers(self):
        expected = {
            self.mod.LAYER_ROADS: self.mod.PopupDialog._populate_road,
            self.mod.LAYER_FACILITIES: self.mod.PopupDialog._populate_facility,
            self.mod.LAYER_SUBDIVISIONS: self.mod.PopupDialog._populate_subdivision,
            self.mod.LAYER_ZONES: self.mod.PopupDialog._populate_zone,
            self.mod.LAYER_NUMBERING: self.mod.PopupDialog._populate_numbering,
            self.mod.LAYER_PANELS: self.mod.PopupDialog._populate_panel,
        }
        for key, handler in expected.items():
            with self.subTest(layer=key):
                self.assertIn(key, self.dialog._POPULATE_DISPATCH)
                self.assertIs(
                    self.dialog._POPULATE_DISPATCH[key], handler,
                )

    @patch('plans_adressage.gui.popup_dialog.get_session')
    def test_set_form_unknown_model_warns_and_continues(self, mock_get_session):
        mock_get_session.return_value = MagicMock()
        with patch('plans_adressage.gui.popup_dialog.qgis_config') as mock_cfg:
            mock_cfg.return_value = {
                'mapper': [{'layer': 'roads', 'model': 'NonExistent'}],
            }
            self.dialog.layer_name_key = 'roads'
            self.dialog.set_form()
            mock_get_session.return_value.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
