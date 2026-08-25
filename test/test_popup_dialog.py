"""Tests for gui/popup_dialog.py — module-level helpers and PopupDialog methods."""

import importlib
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

from .helpers import get_qapp, setup_gui_mocks


def _load_module():
    setup_gui_mocks()
    spec = importlib.util.spec_from_file_location(
        'plans_adressage.gui.popup_dialog',
        'gui/popup_dialog.py',
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules['plans_adressage.gui.popup_dialog'] = mod
    spec.loader.exec_module(mod)
    parent = sys.modules.get('plans_adressage.gui')
    if parent is not None:
        parent.popup_dialog = mod
    return mod


def _make_mock_dialog(**overrides):
    """Build a mock PopupDialog with all widget attributes the helpers touch."""
    d = MagicMock()
    d._tr_locale = 'en'
    d.layer_name_value = 'zone'
    d.layer_name_key = 'zones'
    d.attribute = 'rec-1'
    d.iface = MagicMock()
    d._current_form_data = {}
    d.ref_identify_tool = None
    d._ref_layer = ''
    d._ref_id = ''

    # Zone widgets
    d._combo_zone_type = MagicMock()
    d._combo_zone_type.currentData = MagicMock(return_value='residential')
    d._field_zone_name = MagicMock()
    d._field_zone_name.text = MagicMock(return_value='Zone A')

    # Road widgets
    d._combo_road_type = MagicMock()
    d._combo_road_type.currentData = MagicMock(return_value='avenue')
    d._field_road_name = MagicMock()
    d._field_road_name.text = MagicMock(return_value='Main St')

    # Org widgets
    d._combo_org_cat = MagicMock()
    d._combo_org_cat.currentData = MagicMock(return_value='health')
    d._combo_org_type = MagicMock()
    d._combo_org_type.currentData = MagicMock(return_value='hospital')
    d._field_org_name = MagicMock()
    d._field_org_name.text = MagicMock(return_value='CHU')

    # City / subdivision widgets
    d._combo_subd_type = MagicMock()
    d._combo_subd_type.currentData = MagicMock(return_value='cite')
    d._field_subd_name = MagicMock()
    d._field_subd_name.text = MagicMock(return_value='Cite 500')

    # Numbering widgets
    d._combo_road_ref = MagicMock()
    d._combo_road_ref.currentData = MagicMock(return_value='roads')
    d._field_num_val = MagicMock()
    d._field_num_val.text = MagicMock(return_value='42')
    d._field_repetition = MagicMock()
    d._field_repetition.text = MagicMock(return_value='bis')
    d._combo_num_state = MagicMock()
    d._combo_num_state.currentData = MagicMock(return_value='booked')
    d._combo_activity_cat = MagicMock()
    d._combo_activity_cat.currentData = MagicMock(return_value='residential')
    d._combo_activity_type = MagicMock()
    d._combo_activity_type.currentData = MagicMock(return_value='house')

    # Panel widgets
    d._combo_mount_status = MagicMock()
    d._combo_mount_status.currentData = MagicMock(return_value='mounted')
    d._combo_panel_ref = MagicMock()
    d._combo_panel_ref.currentData = MagicMock(return_value='roads')

    # Buttons
    d._btn_select_ref = MagicMock()
    d._btn_select_panel_ref = MagicMock()

    for k, v in overrides.items():
        setattr(d, k, v)
    return d


def _make_wired_dialog(mod, **overrides):
    """Build a mock dialog with _collect_form_data wired to the real module dispatch."""
    d = _make_mock_dialog(**overrides)
    d._collect_form_data = lambda pk: mod.PopupDialog._collect_form_data(d, pk)
    d._on_save = lambda pk: mod.PopupDialog._on_save(d, pk)
    d._on_select_ref = lambda: mod.PopupDialog._on_select_ref(d)
    d._on_select_panel_ref = lambda: mod.PopupDialog._on_select_panel_ref(d)
    d._start_ref_selection = lambda name='': mod.PopupDialog._start_ref_selection(
        d, name
    )
    d._set_combo_by_data = lambda combo, val: mod.PopupDialog._set_combo_by_data(
        combo, val
    )
    d._on_reference_selected = lambda fid, ln: mod.PopupDialog._on_reference_selected(
        d, fid, ln
    )
    return d


# ======================================================================
# _PAGES registry
# ======================================================================


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestPageRegistry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()

    def test_registry_keys(self):
        expected = {'zone', 'roads', 'org', 'city', 'num', 'pan'}
        self.assertEqual(set(self.mod._PAGES.keys()), expected)

    def test_stack_indices_are_contiguous(self):
        indices = sorted(spec.stack_index for spec in self.mod._PAGES.values())
        self.assertEqual(indices, [0, 1, 2, 3, 4, 5])

    def test_set_values_map_correct_functions(self):
        self.assertIs(self.mod._PAGES['zone'].set_values, self.mod._set_zone_values)
        self.assertIs(self.mod._PAGES['roads'].set_values, self.mod._set_road_values)
        self.assertIs(self.mod._PAGES['org'].set_values, self.mod._set_org_values)
        self.assertIs(self.mod._PAGES['city'].set_values, self.mod._set_city_values)
        self.assertIs(self.mod._PAGES['num'].set_values, self.mod._set_num_values)
        self.assertIs(self.mod._PAGES['pan'].set_values, self.mod._set_pan_values)

    def test_collect_map_correct_functions(self):
        self.assertIs(self.mod._PAGES['zone'].collect, self.mod._collect_zone_data)
        self.assertIs(self.mod._PAGES['roads'].collect, self.mod._collect_road_data)
        self.assertIs(self.mod._PAGES['org'].collect, self.mod._collect_org_data)
        self.assertIs(self.mod._PAGES['city'].collect, self.mod._collect_city_data)
        self.assertIs(self.mod._PAGES['num'].collect, self.mod._collect_num_data)
        self.assertIs(self.mod._PAGES['pan'].collect, self.mod._collect_pan_data)

    def test_update_hooks_callable(self):
        for key, spec in self.mod._PAGES.items():
            with self.subTest(key=key):
                self.assertTrue(callable(spec.update))


# ======================================================================
# _set_*_values helpers
# ======================================================================


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestSetZoneValues(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()

    def test_sets_type_and_name(self):
        d = _make_mock_dialog()
        self.mod._set_zone_values(d, {'type': 'industrial', 'name': 'Zone B'})
        d._set_combo_by_data.assert_called_with(d._combo_zone_type, 'industrial')
        d._field_zone_name.setText.assert_called_with('Zone B')

    def test_empty_name_skips_set_text(self):
        d = _make_mock_dialog()
        self.mod._set_zone_values(d, {'type': 'residential', 'name': ''})
        d._field_zone_name.setText.assert_not_called()

    def test_none_name_skips_set_text(self):
        d = _make_mock_dialog()
        self.mod._set_zone_values(d, {'type': 'residential'})
        d._field_zone_name.setText.assert_not_called()

    def test_none_type_passes_none(self):
        d = _make_mock_dialog()
        self.mod._set_zone_values(d, {'name': 'Only Name'})
        d._set_combo_by_data.assert_called_with(d._combo_zone_type, None)
        d._field_zone_name.setText.assert_called_with('Only Name')

    def test_empty_data(self):
        d = _make_mock_dialog()
        self.mod._set_zone_values(d, {})
        d._set_combo_by_data.assert_called_with(d._combo_zone_type, None)
        d._field_zone_name.setText.assert_not_called()


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestSetRoadValues(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()

    def test_sets_type_and_name(self):
        d = _make_mock_dialog()
        self.mod._set_road_values(d, {'type': 'boulevard', 'name': 'Rue 1'})
        d._set_combo_by_data.assert_called_with(d._combo_road_type, 'boulevard')
        d._field_road_name.setText.assert_called_with('Rue 1')

    def test_empty_name_skips(self):
        d = _make_mock_dialog()
        self.mod._set_road_values(d, {'type': 'avenue', 'name': ''})
        d._field_road_name.setText.assert_not_called()

    def test_none_name_skips(self):
        d = _make_mock_dialog()
        self.mod._set_road_values(d, {'type': 'avenue'})
        d._field_road_name.setText.assert_not_called()


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestSetOrgValues(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()

    def test_sets_category_type_and_name(self):
        d = _make_mock_dialog()
        data = {'category': 'edu', 'type': 'school', 'name': 'Lycée'}
        self.mod._set_org_values(d, data)
        d._set_combo_by_data.assert_any_call(d._combo_org_cat, 'edu')
        d._set_combo_by_data.assert_any_call(d._combo_org_type, 'school')
        d._field_org_name.setText.assert_called_with('Lycée')

    def test_empty_name_skips(self):
        d = _make_mock_dialog()
        self.mod._set_org_values(d, {'category': 'c', 'type': 't', 'name': ''})
        d._field_org_name.setText.assert_not_called()

    def test_none_name_skips(self):
        d = _make_mock_dialog()
        self.mod._set_org_values(d, {'category': 'c', 'type': 't'})
        d._field_org_name.setText.assert_not_called()

    def test_empty_data(self):
        d = _make_mock_dialog()
        self.mod._set_org_values(d, {})
        d._set_combo_by_data.assert_any_call(d._combo_org_cat, None)
        d._set_combo_by_data.assert_any_call(d._combo_org_type, None)
        d._field_org_name.setText.assert_not_called()


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestSetCityValues(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()

    def test_sets_type_and_name(self):
        d = _make_mock_dialog()
        self.mod._set_city_values(d, {'type': 'cite', 'name': 'Cite 100'})
        d._set_combo_by_data.assert_called_with(d._combo_subd_type, 'cite')
        d._field_subd_name.setText.assert_called_with('Cite 100')

    def test_none_name_skips(self):
        d = _make_mock_dialog()
        self.mod._set_city_values(d, {'type': 'cite'})
        d._field_subd_name.setText.assert_not_called()

    def test_empty_data(self):
        d = _make_mock_dialog()
        self.mod._set_city_values(d, {})
        d._set_combo_by_data.assert_called_with(d._combo_subd_type, None)
        d._field_subd_name.setText.assert_not_called()


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestSetNumValues(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()

    def test_sets_all_fields(self):
        d = _make_mock_dialog()
        data = {
            'refType': 'roads',
            'number': '7',
            'repetition': 'ter',
            'state': 'planned',
            'activityCat': 'com',
            'activityType': 'shop',
        }
        self.mod._set_num_values(d, data)
        d._set_combo_by_data.assert_any_call(d._combo_road_ref, 'roads')
        d._field_num_val.setText.assert_called_with('7')
        d._field_repetition.setText.assert_called_with('ter')
        d._set_combo_by_data.assert_any_call(d._combo_num_state, 'planned')
        d._set_combo_by_data.assert_any_call(d._combo_activity_cat, 'com')
        d._set_combo_by_data.assert_any_call(d._combo_activity_type, 'shop')

    def test_empty_number_skips(self):
        d = _make_mock_dialog()
        self.mod._set_num_values(d, {'number': '', 'repetition': ''})
        d._field_num_val.setText.assert_not_called()
        d._field_repetition.setText.assert_not_called()

    def test_none_number_skips(self):
        d = _make_mock_dialog()
        self.mod._set_num_values(d, {})
        d._field_num_val.setText.assert_not_called()
        d._field_repetition.setText.assert_not_called()

    def test_repetition_only_when_number_present(self):
        d = _make_mock_dialog()
        self.mod._set_num_values(d, {'number': '3', 'repetition': 'bis'})
        d._field_num_val.setText.assert_called_with('3')
        d._field_repetition.setText.assert_called_with('bis')


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestSetPanValues(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()

    def test_sets_both_combos(self):
        d = _make_mock_dialog()
        self.mod._set_pan_values(d, {'mountStatus': 'planned', 'refType': 'roads'})
        d._set_combo_by_data.assert_any_call(d._combo_mount_status, 'planned')
        d._set_combo_by_data.assert_any_call(d._combo_panel_ref, 'roads')

    def test_empty_data_passes_none(self):
        d = _make_mock_dialog()
        self.mod._set_pan_values(d, {})
        d._set_combo_by_data.assert_any_call(d._combo_mount_status, None)
        d._set_combo_by_data.assert_any_call(d._combo_panel_ref, None)


# ======================================================================
# _collect_*_data helpers
# ======================================================================


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestCollectZoneData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()

    def test_returns_type_and_name(self):
        d = _make_mock_dialog()
        result = self.mod._collect_zone_data(d)
        self.assertEqual(result, {'type': 'residential', 'name': 'Zone A'})


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestCollectRoadData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()

    def test_returns_type_and_name(self):
        d = _make_mock_dialog()
        result = self.mod._collect_road_data(d)
        self.assertEqual(result, {'type': 'avenue', 'name': 'Main St'})


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestCollectOrgData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()

    def test_returns_category_type_and_name(self):
        d = _make_mock_dialog()
        result = self.mod._collect_org_data(d)
        self.assertEqual(
            result, {'category': 'health', 'type': 'hospital', 'name': 'CHU'}
        )

    def test_has_all_three_keys(self):
        d = _make_mock_dialog()
        result = self.mod._collect_org_data(d)
        self.assertEqual(set(result.keys()), {'category', 'type', 'name'})


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestCollectCityData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()

    def test_returns_type_and_name(self):
        d = _make_mock_dialog()
        result = self.mod._collect_city_data(d)
        self.assertEqual(result, {'type': 'cite', 'name': 'Cite 500'})


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestCollectNumData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()

    def test_returns_all_six_fields(self):
        d = _make_mock_dialog()
        result = self.mod._collect_num_data(d)
        expected = {
            'refType': 'roads',
            'number': '42',
            'repetition': 'bis',
            'state': 'booked',
            'activityCat': 'residential',
            'activityType': 'house',
        }
        self.assertEqual(result, expected)

    def test_has_all_expected_keys(self):
        d = _make_mock_dialog()
        result = self.mod._collect_num_data(d)
        self.assertEqual(
            set(result.keys()),
            {'refType', 'number', 'repetition', 'state', 'activityCat', 'activityType'},
        )


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestCollectPanData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()

    def test_returns_both_fields(self):
        d = _make_mock_dialog()
        result = self.mod._collect_pan_data(d)
        self.assertEqual(result, {'mountStatus': 'mounted', 'refType': 'roads'})


# ======================================================================
# PopupDialog._set_combo_by_data
# ======================================================================


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestSetComboByData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()

    def _make_combo(self, items):
        """Create a mock combo with findData support."""
        combo = MagicMock()
        data_map = {v: i for i, v in enumerate(items)}
        combo.findData = MagicMock(side_effect=lambda v: data_map.get(v, -1))
        combo.setCurrentIndex = MagicMock()
        return combo

    def test_value_found_sets_index(self):
        combo = self._make_combo(['a', 'b', 'c'])
        self.mod.PopupDialog._set_combo_by_data(combo, 'b')
        combo.findData.assert_called_with('b')
        combo.setCurrentIndex.assert_called_with(1)

    def test_value_not_found_no_change(self):
        combo = self._make_combo(['a', 'b', 'c'])
        self.mod.PopupDialog._set_combo_by_data(combo, 'z')
        combo.findData.assert_called_with('z')
        combo.setCurrentIndex.assert_not_called()

    def test_none_value_no_change(self):
        combo = self._make_combo(['a', 'b'])
        self.mod.PopupDialog._set_combo_by_data(combo, None)
        combo.findData.assert_not_called()
        combo.setCurrentIndex.assert_not_called()

    def test_empty_string_value_no_change(self):
        combo = self._make_combo(['a', 'b'])
        self.mod.PopupDialog._set_combo_by_data(combo, '')
        combo.findData.assert_not_called()
        combo.setCurrentIndex.assert_not_called()

    def test_first_item(self):
        combo = self._make_combo(['x', 'y', 'z'])
        self.mod.PopupDialog._set_combo_by_data(combo, 'x')
        combo.setCurrentIndex.assert_called_with(0)

    def test_last_item(self):
        combo = self._make_combo(['x', 'y', 'z'])
        self.mod.PopupDialog._set_combo_by_data(combo, 'z')
        combo.setCurrentIndex.assert_called_with(2)


# ======================================================================
# PopupDialog._collect_form_data
# ======================================================================


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestCollectFormData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()

    def _make_instance(self):
        return _make_wired_dialog(self.mod)

    def test_zone_key(self):
        d = self._make_instance()
        result = d._collect_form_data('zone')
        self.assertEqual(result['type'], 'residential')
        self.assertEqual(result['name'], 'Zone A')

    def test_roads_key(self):
        d = self._make_instance()
        result = d._collect_form_data('roads')
        self.assertEqual(result['type'], 'avenue')
        self.assertEqual(result['name'], 'Main St')

    def test_org_key(self):
        d = self._make_instance()
        result = d._collect_form_data('org')
        self.assertEqual(result['category'], 'health')
        self.assertEqual(result['type'], 'hospital')
        self.assertEqual(result['name'], 'CHU')

    def test_city_key(self):
        d = self._make_instance()
        result = d._collect_form_data('city')
        self.assertEqual(result['type'], 'cite')
        self.assertEqual(result['name'], 'Cite 500')

    def test_num_key(self):
        d = self._make_instance()
        result = d._collect_form_data('num')
        self.assertEqual(result['number'], '42')
        self.assertEqual(result['repetition'], 'bis')

    def test_pan_key(self):
        d = self._make_instance()
        result = d._collect_form_data('pan')
        self.assertEqual(result['mountStatus'], 'mounted')
        self.assertEqual(result['refType'], 'roads')

    def test_unknown_key_returns_empty_dict(self):
        d = self._make_instance()
        result = d._collect_form_data('nonexistent')
        self.assertEqual(result, {})


# ======================================================================
# PopupDialog._on_save
# ======================================================================


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestOnSave(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()

    def test_zone_dispatches_to_update_zone(self):
        with patch.object(self.mod._PAGES['zone'], 'update') as mock_uq:
            d = _make_wired_dialog(self.mod, layer_name_value='zone')
            d._on_save('zone')
            mock_uq.assert_called_once_with(d)
            self.assertEqual(d._current_form_data['type'], 'residential')

    def test_roads_dispatches_to_update_road(self):
        with patch.object(self.mod._PAGES['roads'], 'update') as mock_ur:
            d = _make_wired_dialog(self.mod, layer_name_value='roads')
            d._on_save('roads')
            mock_ur.assert_called_once_with(d)
            self.assertEqual(d._current_form_data['type'], 'avenue')

    def test_org_dispatches_to_update_organization(self):
        with patch.object(self.mod._PAGES['org'], 'update') as mock_uo:
            d = _make_wired_dialog(self.mod, layer_name_value='org')
            d._on_save('org')
            mock_uo.assert_called_once_with(d)
            self.assertEqual(d._current_form_data['category'], 'health')

    def test_city_dispatches_to_update_subdivision(self):
        with patch.object(self.mod._PAGES['city'], 'update') as mock_us:
            d = _make_wired_dialog(self.mod, layer_name_value='city')
            d._on_save('city')
            mock_us.assert_called_once_with(d)
            self.assertEqual(d._current_form_data['type'], 'cite')

    def test_num_dispatches_to_update_numbering(self):
        with patch.object(self.mod._PAGES['num'], 'update') as mock_un:
            d = _make_wired_dialog(self.mod, layer_name_value='num')
            d._on_save('num')
            mock_un.assert_called_once_with(d)
            self.assertEqual(d._current_form_data['number'], '42')

    def test_pan_dispatches_to_update_panel(self):
        with patch.object(self.mod._PAGES['pan'], 'update') as mock_up:
            d = _make_wired_dialog(self.mod, layer_name_value='pan')
            d._on_save('pan')
            mock_up.assert_called_once_with(d)
            self.assertEqual(d._current_form_data['mountStatus'], 'mounted')

    def test_unknown_key_no_handler(self):
        d = _make_wired_dialog(self.mod, layer_name_value='zone')
        d._on_save('unknown_key')
        self.assertEqual(d._current_form_data, {})


# ======================================================================
# PopupDialog._on_select_ref / _on_select_panel_ref
# ======================================================================


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestOnSelectRef(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()

    def test_reads_road_ref_and_starts_selection(self):
        d = _make_wired_dialog(self.mod)
        with patch.object(d, '_start_ref_selection') as mock_start:
            d._on_select_ref()
            mock_start.assert_called_once_with('roads')

    def test_reads_panel_ref_and_starts_selection(self):
        d = _make_wired_dialog(self.mod)
        with patch.object(d, '_start_ref_selection') as mock_start:
            d._on_select_panel_ref()
            mock_start.assert_called_once_with('roads')


# ======================================================================
# PopupDialog._start_ref_selection
# ======================================================================


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestStartRefSelection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()
        cls._ident_mod = types.ModuleType('plans_adressage.gui.identify_tool')
        cls._ident_cls = type(
            'IdentifyTool',
            (),
            {
                'MODE_REF': 'ref',
                '__init__': lambda self, canvas, mode=None: None,
                'set_iface': lambda self, iface: None,
                'set_active_layer': lambda self, layer: None,
                'ref_selected': MagicMock(),
            },
        )
        cls._ident_mod.IdentifyTool = cls._ident_cls
        sys.modules['plans_adressage.gui.identify_tool'] = cls._ident_mod
        parent = sys.modules.get('plans_adressage.gui')
        if parent is not None:
            parent.identify_tool = cls._ident_mod

    @classmethod
    def tearDownClass(cls):
        sys.modules.pop('plans_adressage.gui.identify_tool', None)

    @patch('plans_adressage.gui.identify_tool.IdentifyTool')
    @patch('plans_adressage.gui.popup_dialog.QgsProject')
    def test_with_layer_found(self, mock_qgs_project, mock_identify_tool):
        d = _make_wired_dialog(self.mod)
        mock_layer = MagicMock()
        mock_qgs_project.instance.return_value.mapLayersByName.return_value = [
            mock_layer
        ]

        d._start_ref_selection('SomeLayer')

        d.iface.setActiveLayer.assert_any_call(mock_layer)
        mock_identify_tool.assert_called_once()
        self.assertIsNotNone(d.ref_identify_tool)

    @patch('plans_adressage.gui.popup_dialog.QgsProject')
    @patch('plans_adressage.gui.popup_dialog.QMessageBox')
    @patch(
        'plans_adressage.gui.popup_dialog.get_string', side_effect=lambda s, loc=None: s
    )
    def test_empty_layer_name_shows_error(
        self, _gs, mock_qmessagebox, mock_qgs_project
    ):
        d = _make_wired_dialog(self.mod)
        mock_qgs_project.instance.return_value.mapLayersByName.return_value = [
            MagicMock()
        ]

        d._start_ref_selection('')

        mock_qmessagebox.critical.assert_called_once()

    @patch('plans_adressage.gui.popup_dialog.QgsProject')
    def test_with_layer_not_found(self, mock_qgs_project):
        d = _make_wired_dialog(self.mod)
        mock_qgs_project.instance.return_value.mapLayersByName.return_value = []

        d._start_ref_selection('MissingLayer')

        d.iface.setActiveLayer.assert_not_called()

    @patch('plans_adressage.gui.identify_tool.IdentifyTool')
    @patch('plans_adressage.gui.popup_dialog.QgsProject')
    def test_sets_active_layer_for_layer_name_key(
        self, mock_qgs_project, mock_identify_tool
    ):
        d = _make_wired_dialog(self.mod, layer_name_key='numbering')
        ref_layer = MagicMock()
        key_layer = MagicMock()
        mock_qgs_project.instance.return_value.mapLayersByName.side_effect = (
            lambda name: [ref_layer] if name == 'roads' else [key_layer]
        )

        d._start_ref_selection('roads')

        calls = d.iface.setActiveLayer.call_args_list
        self.assertEqual(calls[0], unittest.mock.call(ref_layer))
        self.assertEqual(calls[1], unittest.mock.call(key_layer))


# ======================================================================
# PopupDialog._on_reference_selected
# ======================================================================


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestOnReferenceSelected(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        cls.mod = _load_module()

    def test_stores_ref_id_and_layer(self):
        d = _make_wired_dialog(self.mod)
        d._on_reference_selected(42, 'roads')
        self.assertEqual(d._ref_id, '42')
        self.assertEqual(d._ref_layer, 'roads')

    def test_converts_non_string_id(self):
        d = _make_wired_dialog(self.mod)
        d._on_reference_selected(99.5, 'facilities')
        self.assertEqual(d._ref_id, '99.5')
        self.assertEqual(d._ref_layer, 'facilities')


if __name__ == '__main__':
    unittest.main()
