"""Tests for gui.ui_fillers."""

import importlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from test.helpers import setup_gui_mocks


def _load_module():
    setup_gui_mocks()
    spec = importlib.util.spec_from_file_location(
        'plans_adressage.gui.ui_fillers',
        'gui/ui_fillers.py',
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules['plans_adressage.gui.ui_fillers'] = mod
    spec.loader.exec_module(mod)
    return mod


class TestUiFillersModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_module()

    def _combo(self):
        combo = MagicMock()
        combo.completer.return_value = MagicMock()
        return combo

    # -- _setup_combo ---------------------------------------------------

    def test_setup_combo_sets_popup_completion(self):
        combo = self._combo()
        self.mod._setup_combo(combo)
        combo.completer().setCompletionMode.assert_called_once()

    def test_setup_combo_no_completer(self):
        combo = MagicMock()
        combo.completer.return_value = None
        self.mod._setup_combo(combo)
        combo.setInsertPolicy.assert_called_once()

    # -- fill_wilayas_list ----------------------------------------------

    def test_fill_wilayas_list(self):
        data = {
            '16': {
                'wilaya_id': 16,
                'wilaya_ar': '\u0627\u0644\u062c\u0632\u0626\u0631',
            },
            '31': {'wilaya_id': 31, 'wilaya_ar': '\u0648\u0647\u0631\u0627\u0646'},
        }
        with (
            patch.object(self.mod, 'wilayas_data', return_value=data),
            patch.object(self.mod, 'current_locale', return_value='en'),
        ):
            combo = self._combo()
            self.mod.fill_wilayas_list(combo)
            combo.clear.assert_called()
            self.assertGreaterEqual(combo.addItem.call_count, 2)

    def test_fill_wilayas_list_empty(self):
        with (
            patch.object(self.mod, 'wilayas_data', return_value={}),
            patch.object(self.mod, 'current_locale', return_value='en'),
        ):
            combo = self._combo()
            self.mod.fill_wilayas_list(combo)
            combo.clear.assert_called()
            self.assertEqual(combo.addItem.call_count, 0)

    def test_fill_wilayas_list_skips_entries_without_code(self):
        data = {
            '1': {'wilaya_ar': 'test'},
            '2': {'wilaya_id': 2, 'wilaya_ar': 'valid'},
        }
        with (
            patch.object(self.mod, 'wilayas_data', return_value=data),
            patch.object(self.mod, 'current_locale', return_value='en'),
        ):
            combo = self._combo()
            self.mod.fill_wilayas_list(combo)
            self.assertEqual(combo.addItem.call_count, 1)

    # -- fill_paper -----------------------------------------------------

    def test_fill_paper(self):
        combo = self._combo()
        self.mod.fill_paper(combo)
        self.assertEqual(combo.addItem.call_count, 2)

    def test_fill_paper_clears_first(self):
        combo = self._combo()
        self.mod.fill_paper(combo)
        combo.clear.assert_called_once()

    # -- _fill_from_json ------------------------------------------------

    def test_fill_from_json(self):
        data = [{'pk': 'a', 'label_fr': 'Alpha', 'label_en': 'Alpha'}]
        combo = self._combo()
        self.mod._fill_from_json(combo, data, 'en')
        combo.clear.assert_called_once()
        combo.addItem.assert_called_once()
        combo.setCurrentIndex.assert_called_with(0)

    def test_fill_from_json_not_list_logs_warning(self):
        combo = self._combo()
        self.mod._fill_from_json(combo, 'not_a_list', 'en')
        combo.clear.assert_called_once()
        combo.addItem.assert_not_called()

    def test_fill_from_json_empty_list(self):
        combo = self._combo()
        self.mod._fill_from_json(combo, [], 'en')
        combo.clear.assert_called_once()
        combo.addItem.assert_not_called()

    # -- fill_commune_of_wilaya -----------------------------------------

    def test_fill_commune_of_wilaya(self):
        dairas = {
            '10': {'wilaya_id': 16},
            '11': {'wilaya_id': 31},
        }
        communes = [
            {
                'daira_id': 10,
                'commune_ar': 'c1',
                'commune_fr': 'Commune 1',
                'commune_code': '1001',
            },
            {
                'daira_id': 11,
                'commune_ar': 'c2',
                'commune_fr': 'Commune 2',
                'commune_code': '2001',
            },
        ]
        with (
            patch.object(self.mod, 'dairas_data', return_value=dairas),
            patch.object(self.mod, 'communes_list', return_value=communes),
            patch.object(self.mod, 'current_locale', return_value='en'),
        ):
            combo = self._combo()
            self.mod.fill_commune_of_wilaya(combo, 16)
            combo.clear.assert_called()
            self.assertEqual(combo.addItem.call_count, 1)

    def test_fill_commune_of_wilaya_arabic_locale(self):
        dairas = {'10': {'wilaya_id': 16}}
        communes = [
            {
                'daira_id': 10,
                'commune_ar': '\u0627\u0644\u0645\u062f\u064a\u0646\u0629',
                'commune_code': '1001',
            },
        ]
        with (
            patch.object(self.mod, 'dairas_data', return_value=dairas),
            patch.object(self.mod, 'communes_list', return_value=communes),
            patch.object(self.mod, 'current_locale', return_value='ar'),
        ):
            combo = self._combo()
            self.mod.fill_commune_of_wilaya(combo, 16)
            self.assertEqual(combo.addItem.call_count, 1)

    def test_fill_commune_of_wilaya_empty_daira_ids(self):
        dairas = {'10': {'wilaya_id': 99}}
        communes = [
            {'daira_id': 10, 'commune_fr': 'C', 'commune_code': '1001'},
        ]
        with (
            patch.object(self.mod, 'dairas_data', return_value=dairas),
            patch.object(self.mod, 'communes_list', return_value=communes),
            patch.object(self.mod, 'current_locale', return_value='en'),
        ):
            combo = self._combo()
            self.mod.fill_commune_of_wilaya(combo, 16)
            self.assertEqual(combo.addItem.call_count, 0)

    def test_fill_commune_of_wilaya_fallback_to_fr(self):
        dairas = {'10': {'wilaya_id': 16}}
        communes = [
            {'daira_id': 10, 'commune_fr': 'FrenchName', 'commune_code': '1001'},
        ]
        with (
            patch.object(self.mod, 'dairas_data', return_value=dairas),
            patch.object(self.mod, 'communes_list', return_value=communes),
            patch.object(self.mod, 'current_locale', return_value='en'),
        ):
            combo = self._combo()
            self.mod.fill_commune_of_wilaya(combo, 16)
            self.assertEqual(combo.addItem.call_count, 1)

    # -- _fill_reference ------------------------------------------------

    def test_fill_road_reference(self):
        combo = self._combo()
        with patch.object(
            self.mod,
            'qgis_config',
            return_value={'refs': [{'label': 'ref_a'}, {'label': 'ref_b'}]},
        ):
            self.mod.fill_road_reference(combo)
            combo.clear.assert_called_once()
            self.assertEqual(combo.addItem.call_count, 2)

    def test_fill_panel_reference(self):
        combo = self._combo()
        with patch.object(
            self.mod, 'qgis_config', return_value={'refs2': [{'label': 'panel_ref'}]}
        ):
            self.mod.fill_panel_reference(combo)
            self.assertEqual(combo.addItem.call_count, 1)

    def test_fill_reference_empty_config(self):
        combo = self._combo()
        with patch.object(self.mod, 'qgis_config', return_value={}):
            self.mod.fill_road_reference(combo)
            combo.clear.assert_called_once()
            combo.addItem.assert_not_called()

    def test_fill_reference_none_value(self):
        combo = self._combo()
        with patch.object(self.mod, 'qgis_config', return_value={'refs': None}):
            self.mod.fill_road_reference(combo)
            combo.addItem.assert_not_called()

    # -- fill_org_category ----------------------------------------------

    def test_fill_org_category(self):
        cats = [('Education', 'edu')]
        with (
            patch.object(self.mod, 'org_categories', return_value=cats),
            patch.object(self.mod, 'current_locale', return_value='en'),
        ):
            combo = self._combo()
            self.mod.fill_org_category(combo)
            combo.clear.assert_called_once()

    def test_fill_org_category_multiple(self):
        cats = [('Education', 'edu'), ('Health', 'health')]
        with (
            patch.object(self.mod, 'org_categories', return_value=cats),
            patch.object(self.mod, 'current_locale', return_value='en'),
        ):
            combo = self._combo()
            self.mod.fill_org_category(combo)
            self.assertEqual(combo.addItem.call_count, 2)

    # -- fill_activity_category -----------------------------------------

    def test_fill_activity_category(self):
        cats = [('Residential', 'res')]
        with (
            patch.object(self.mod, 'activity_categories', return_value=cats),
            patch.object(self.mod, 'current_locale', return_value='en'),
        ):
            combo = self._combo()
            self.mod.fill_activity_category(combo)
            combo.addItem.assert_called()

    def test_fill_activity_category_includes_no_activity(self):
        cats = [('Residential', 'res')]
        with (
            patch.object(self.mod, 'activity_categories', return_value=cats),
            patch.object(self.mod, 'current_locale', return_value='en'),
        ):
            combo = self._combo()
            self.mod.fill_activity_category(combo)
            # NO_ACTIVITY + 1 real category = 2 calls
            self.assertEqual(combo.addItem.call_count, 2)

    # -- fill_activity_type ---------------------------------------------

    def test_fill_activity_type(self):
        types = [('House', 'house')]
        with (
            patch.object(self.mod, 'activity_types_for_category', return_value=types),
            patch.object(self.mod, 'current_locale', return_value='en'),
        ):
            combo = MagicMock()
            self.mod.fill_activity_type(combo, 'residential')
            combo.clear.assert_called_once()

    def test_fill_activity_type_no_activity(self):
        combo = MagicMock()
        with patch.object(self.mod, 'current_locale', return_value='en'):
            self.mod.fill_activity_type(combo, self.mod.NO_ACTIVITY)
            combo.clear.assert_called_once()

    # -- fill_org_type --------------------------------------------------

    def test_fill_org_type(self):
        types = [('School', 'school')]
        with (
            patch.object(self.mod, 'org_types_for_category', return_value=types),
            patch.object(self.mod, 'current_locale', return_value='en'),
        ):
            combo = self._combo()
            self.mod.fill_org_type(combo, 'edu')
            combo.clear.assert_called_once()

    # -- fill_road_type, fill_mounting_status, fill_numbering_state -----

    def test_fill_road_type(self):
        types = [{'pk': 'avenue', 'label_fr': 'Avenue', 'label_en': 'Avenue'}]
        with (
            patch.object(self.mod, 'road_types', return_value=types),
            patch.object(self.mod, 'current_locale', return_value='en'),
        ):
            combo = self._combo()
            self.mod.fill_road_type(combo)
            combo.clear.assert_called_once()

    def test_fill_mounting_status(self):
        statuses = [{'pk': 'mounted', 'label_fr': 'Mont\u00e9', 'label_en': 'Mounted'}]
        with (
            patch.object(self.mod, 'mounting_statuses', return_value=statuses),
            patch.object(self.mod, 'current_locale', return_value='en'),
        ):
            combo = self._combo()
            self.mod.fill_mounting_status(combo)
            combo.clear.assert_called_once()

    def test_fill_numbering_state(self):
        states = [
            {'pk': 'booked', 'label_fr': 'R\u00e9serv\u00e9', 'label_en': 'Booked'}
        ]
        with (
            patch.object(self.mod, 'numbering_states', return_value=states),
            patch.object(self.mod, 'current_locale', return_value='en'),
        ):
            combo = self._combo()
            self.mod.fill_numbering_state(combo)
            combo.clear.assert_called_once()

    # -- fill_feature_combo ---------------------------------------------

    def test_fill_feature_combo(self):
        combo = self._combo()
        self.mod.fill_feature_combo(combo)
        self.assertGreaterEqual(combo.addItem.call_count, 1)

    def test_fill_feature_combo_count(self):
        combo = self._combo()
        self.mod.fill_feature_combo(combo)
        self.assertEqual(combo.addItem.call_count, len(self.mod._MAIN_TYPE_MAP))

    # -- fill_subtype_combo ---------------------------------------------

    def test_fill_subtype_combo_activities(self):
        combo = self._combo()
        with (
            patch.object(self.mod, 'activity_categories', return_value=[('Cat', 'c')]),
            patch.object(self.mod, 'current_locale', return_value='en'),
        ):
            self.mod.fill_subtype_combo(combo, 'Activities')
        combo.clear.assert_called()

    def test_fill_subtype_combo_known_type(self):
        combo = self._combo()
        with (
            patch.object(
                self.mod, 'zone_types', return_value=[{'pk': 'z', 'label_fr': 'Z'}]
            ),
            patch.object(self.mod, 'current_locale', return_value='en'),
        ):
            self.mod.fill_subtype_combo(combo, 'zones')
        combo.clear.assert_called()

    def test_fill_subtype_combo_unknown_clears(self):
        combo = MagicMock()
        self.mod.fill_subtype_combo(combo, 'nonexistent')
        combo.clear.assert_called_once()

    # -- save_new_type --------------------------------------------------

    def test_save_new_type_empty_returns_false(self):
        self.assertFalse(self.mod.save_new_type('', ''))
        self.assertFalse(self.mod.save_new_type('roads', ''))

    def test_save_new_type_activity_no_category_returns_false(self):
        self.assertFalse(self.mod.save_new_type('Activities', 'test'))

    def test_save_new_type_strips_whitespace(self):
        self.assertFalse(self.mod.save_new_type('roads', '   '))

    def test_save_new_type_invalid_main_type(self):
        self.assertFalse(self.mod.save_new_type('InvalidType', 'name'))

    @patch.object(Path, 'open')
    def test_save_new_type_activity_success(self, mock_open):
        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_file

        with patch.object(self.mod.json, 'load', return_value=[]):
            result = self.mod.save_new_type('Activities', 'NewActivity', 'sector')
        self.assertTrue(result)

    @patch.object(Path, 'open')
    def test_save_new_type_roads_success(self, mock_open):
        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_file

        with patch.object(self.mod.json, 'load', return_value=[]):
            result = self.mod.save_new_type('Roads', 'NewRoad')
        self.assertTrue(result)

    @patch.object(Path, 'open', side_effect=OSError('fail'))
    def test_save_new_type_os_error_returns_false(self, _mock_open):
        result = self.mod.save_new_type('Roads', 'NewRoad')
        self.assertFalse(result)

    @patch.object(Path, 'open')
    def test_save_new_type_json_error_returns_false(self, _mock_open):
        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=False)
        _mock_open.return_value = mock_file

        with patch.object(
            self.mod.json, 'load', side_effect=json.JSONDecodeError('err', '', 0)
        ):
            result = self.mod.save_new_type('Roads', 'NewRoad')
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
