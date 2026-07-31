"""Tests for gui/popup_dialog.py (Qt Widgets version)."""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from .helpers import get_qapp, setup_gui_mocks


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestPopupDialog(unittest.TestCase):
    """Test PopupDialog creation and form population."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.popup_dialog',
            'gui/popup_dialog.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.popup_dialog'] = cls.mod
        spec.loader.exec_module(cls.mod)
        parent = sys.modules.get('plans_adressage.gui')
        if parent is not None:
            parent.popup_dialog = cls.mod

    def setUp(self):
        self.iface = MagicMock()
        self.dialog = self.mod.PopupDialog(
            'test_road',
            'roads',
            'pk_uid',
            self.iface,
        )

    def test_dialog_created(self):
        self.assertIsNotNone(self.dialog)

    def test_layer_name_value_stored(self):
        self.assertEqual(self.dialog.layer_name_value, 'test_road')

    def test_layer_name_key_stored(self):
        self.assertEqual(self.dialog.layer_name_key, 'roads')

    def test_attribute_stored(self):
        self.assertEqual(self.dialog.attribute, 'pk_uid')

    def test_current_form_data_initialized(self):
        self.assertIsInstance(self.dialog._current_form_data, dict)

    def test_populate_dispatch_has_all_layers(self):
        expected_layers = [
            'roads',
            'facilities',
            'subdivisions',
            'zones',
            'numbering',
            'panels',
        ]
        dispatch = self.mod.POPULATE_DISPATCH
        for layer in expected_layers:
            with self.subTest(layer=layer):
                self.assertIn(layer, dispatch)
                self.assertTrue(callable(dispatch[layer]))

    @patch('plans_adressage.gui.popup_dialog.get_session')
    def test_set_form_unknown_model_warns_and_continues(
        self,
        mock_get_session,
    ):
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
