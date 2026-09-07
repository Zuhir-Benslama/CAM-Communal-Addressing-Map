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
            # Unknown model: bails out before any session is opened.
            mock_get_session.assert_not_called()

    @patch('plans_adressage.gui.popup_dialog.get_session')
    def test_set_form_no_mapper_entry(self, mock_get_session):
        with patch('plans_adressage.gui.popup_dialog.qgis_config') as mock_cfg:
            mock_cfg.return_value = {'mapper': []}
            self.dialog.layer_name_key = 'roads'
            self.dialog.set_form()
            mock_get_session.assert_not_called()

    @patch('plans_adressage.gui.popup_dialog.get_session')
    def test_set_form_record_not_found(self, mock_get_session):
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_get_session.return_value = mock_session
        mock_model = MagicMock()
        with (
            patch('plans_adressage.gui.popup_dialog.qgis_config') as mock_cfg,
            patch.object(self.mod._models, 'Road', mock_model),
        ):
            mock_cfg.return_value = {
                'mapper': [{'layer': 'roads', 'model': 'Road'}],
            }
            self.dialog.layer_name_key = 'roads'
            self.dialog.set_form()
            mock_session.close.assert_called_once()

    @patch('plans_adressage.gui.popup_dialog.get_session')
    def test_set_form_updates_form_data(self, mock_get_session):
        mock_session = MagicMock()
        record = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = record
        mock_get_session.return_value = mock_session
        mock_model = MagicMock()

        def _populate(dialog, record, locale):
            return {'type': 'residential', 'name': 'Zone A'}

        with (
            patch('plans_adressage.gui.popup_dialog.qgis_config') as mock_cfg,
            patch.object(self.mod._models, 'Zone', mock_model),
            patch.dict(self.mod.POPULATE_DISPATCH, {'zones': _populate}),
        ):
            mock_cfg.return_value = {
                'mapper': [{'layer': 'zones', 'model': 'Zone'}],
            }
            self.dialog.layer_name_key = 'zones'
            self.dialog.layer_name_value = 'zone'
            self.dialog._set_combo_by_data = MagicMock()
            self.dialog._field_zone_name = MagicMock()
            self.dialog._combo_zone_type = MagicMock()
            self.dialog._set_form_values = lambda data: None
            self.dialog.set_form()
            self.assertEqual(self.dialog._current_form_data['type'], 'residential')
            mock_session.close.assert_called_once()

    def test_set_form_values_uses_spec(self):
        spec = self.mod._PAGES['zone']
        d = MagicMock()
        d.layer_name_value = 'zone'
        d._field_zone_name = MagicMock()
        d._combo_zone_type = MagicMock()
        d._set_combo_by_data = MagicMock()
        with patch.object(spec, 'set_values') as mock_set:
            self.mod.PopupDialog._set_form_values(d, {'type': 'x'})
            mock_set.assert_called_once_with(d, {'type': 'x'})

    def test_set_form_values_unknown_key(self):
        d = MagicMock()
        d.layer_name_value = 'unknown_page'
        self.mod.PopupDialog._set_form_values(d, {})

    def test_on_org_cat_changed_fills_types(self):
        d = MagicMock()
        d._combo_org_cat = MagicMock()
        d._combo_org_cat.currentData.return_value = 'health'
        d._combo_org_type = MagicMock()
        with patch('plans_adressage.gui.popup_dialog.fill_org_type') as mock_fill:
            self.mod.PopupDialog._on_org_cat_changed(d, 0)
            mock_fill.assert_called_once_with(d._combo_org_type, 'health')

    def test_on_activity_cat_changed_fills_types(self):
        d = MagicMock()
        d._combo_activity_cat = MagicMock()
        d._combo_activity_cat.currentData.return_value = 'residential'
        d._combo_activity_type = MagicMock()
        with patch('plans_adressage.gui.popup_dialog.fill_activity_type') as mock_fill:
            self.mod.PopupDialog._on_activity_cat_changed(d, 0)
            mock_fill.assert_called_once_with(d._combo_activity_type, 'residential')

    def test_start_ref_selection_with_existing_previous_tool(self):
        previous_tool = MagicMock()
        previous_tool.ref_selected.disconnect = MagicMock()
        previous_tool.unset_map_tool = MagicMock()
        d = MagicMock()
        d.iface = MagicMock()
        d.layer_name_key = 'numbering'
        d.ref_identify_tool = previous_tool
        d._combo_road_ref = MagicMock()
        d._combo_road_ref.currentData.return_value = 'roads'

        mock_layer = MagicMock()
        mock_ident_cls = MagicMock()
        mock_ident_instance = mock_ident_cls.return_value
        mock_ident_instance.ref_selected.connect = MagicMock()

        with (
            patch.object(self.mod, 'QgsProject') as mock_project,
            patch(
                'plans_adressage.gui.identify_tool.IdentifyTool',
                mock_ident_cls,
            ),
        ):
            mock_project.instance.return_value.mapLayersByName.return_value = [
                mock_layer
            ]
            self.mod.PopupDialog._start_ref_selection(d, 'roads')

        previous_tool.ref_selected.disconnect.assert_called_once()
        previous_tool.unset_map_tool.assert_called_once()


if __name__ == '__main__':
    unittest.main()
