"""Tests for gui/main_dialog.py — MainDialog."""
import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from .helpers import get_qapp, make_mock_iface, setup_gui_mocks


def _stub_widgets(target, names):
    """Set MagicMock attributes on the target unconditionally."""
    for name in names:
        setattr(target, name, MagicMock())


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestMainDialogCore(unittest.TestCase):
    """Test MainDialog core methods defined in main_dialog.py."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.main_dialog',
            'gui/main_dialog.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.main_dialog'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def _make_raw(self):
        """Create a raw MainDialog instance without calling __init__."""
        dialog = self.mod.MainDialog.__new__(self.mod.MainDialog)
        dialog.iface = make_mock_iface()
        dialog._tr_locale = 'ar'
        dialog._current_theme = 'dark'
        dialog._combo_proxies = {}
        dialog._field_proxies = {}
        dialog.router = MagicMock()
        dialog.menu = MagicMock()
        dialog.form_stack = MagicMock()
        dialog._bridge = MagicMock()
        return dialog

    def _real_combo(self):
        """Return a fresh _ComboProxy from the loaded module."""
        return self.mod._ComboProxy()

    def _real_field(self):
        """Return a fresh _FieldProxy from the loaded module."""
        return self.mod._FieldProxy()

    def test_current_layer_name_returns_first_by_default(self):
        dialog = self._make_raw()
        layer_sel = self._real_combo()
        dialog._combo_proxies['layer_selector'] = layer_sel
        self.assertEqual(dialog._current_layer_name(), "Zones")

    def test_current_layer_name_returns_by_index(self):
        dialog = self._make_raw()
        layer_sel = self._real_combo()
        dialog._combo_proxies['layer_selector'] = layer_sel
        for idx, expected in enumerate(
            ["Zones", "Roads", "Facilities",
             "Subdivisions", "Numbering", "Panels"]):
            layer_sel.setCurrentIndex(idx)
            self.assertEqual(dialog._current_layer_name(), expected)

    def test_current_layer_name_fallback_on_bad_index(self):
        dialog = self._make_raw()
        layer_sel = self._real_combo()
        dialog._combo_proxies['layer_selector'] = layer_sel
        layer_sel.setCurrentIndex(99)
        self.assertEqual(dialog._current_layer_name(), "Zones")

    def test_tr_delegates_to_get_string(self):
        dialog = self._make_raw()
        result = dialog._tr("Hello")
        self.assertEqual(result, "Hello")

    def test_translate_internal_combos_sets_item_texts(self):
        dialog = self._make_raw()
        layer_sel = self._real_combo()
        theme_combo = self._real_combo()
        layer_sel.addItem("Zones", "Zones")
        layer_sel.addItem("Roads", "Roads")
        layer_sel.addItem("Facilities", "Facilities")
        layer_sel.addItem("Subdivisions", "Subdivisions")
        layer_sel.addItem("Numbering", "Numbering")
        layer_sel.addItem("Panels", "Panels")
        theme_combo.addItem("dark", "dark")
        theme_combo.addItem("light", "light")
        dialog._combo_proxies['layer_selector'] = layer_sel
        dialog._combo_proxies['_theme_combo'] = theme_combo
        dialog._translate_internal_combos()
        for i in range(6):
            self.assertEqual(layer_sel.itemText(i), layer_sel.itemData(i))

    def test_init_state_resets_tool_state(self):
        dialog = self._make_raw()
        dialog._init_state()
        self.assertIsNone(dialog.sat_view)
        self.assertIsNone(dialog.rast)
        self.assertIsNone(dialog.ln)
        self.assertEqual(dialog.type_plan, "")
        self.assertEqual(dialog.type_to_hide, "")
        self.assertIsNone(dialog.measure_tool)
        self.assertIsNone(dialog.identify_tool)
        self.assertIsNone(dialog.ref_identify_tool)
        self.assertIsNone(dialog.popup_dialog)
        self.assertIsNone(dialog.current_user)
        self.assertEqual(dialog.update_object, {})
        self.assertEqual(dialog.update_only_form, {})

    def test_apply_theme_sets_stylesheet(self):
        dialog = self._make_raw()
        dialog.setStyleSheet = MagicMock()
        dialog.apply_theme()
        dialog.setStyleSheet.assert_called_once()

    def test_on_layer_changed_sets_form_stack(self):
        dialog = self._make_raw()
        dialog.form_stack.setCurrentIndex = MagicMock()
        dialog.menu.currentWidget.return_value.objectName.return_value = 'tab_ops'
        dialog.menu.currentIndex.return_value = 2
        dialog.on_opt_selected = MagicMock()
        dialog._on_layer_changed(2)
        dialog.form_stack.setCurrentIndex.assert_called_once_with(2)
        dialog.on_opt_selected.assert_called_once_with(2)

    def test_on_layer_changed_skips_opt_for_non_ops_tab(self):
        dialog = self._make_raw()
        dialog.form_stack.setCurrentIndex = MagicMock()
        dialog.menu.currentWidget.return_value.objectName.return_value = 'tab'
        dialog.on_opt_selected = MagicMock()
        dialog._on_layer_changed(1)
        dialog.form_stack.setCurrentIndex.assert_called_once_with(1)
        dialog.on_opt_selected.assert_not_called()

    def test_on_layer_changed_handles_no_current_widget(self):
        dialog = self._make_raw()
        dialog.form_stack.setCurrentIndex = MagicMock()
        dialog.menu.currentWidget.return_value = None
        dialog.on_opt_selected = MagicMock()
        dialog._on_layer_changed(0)
        dialog.form_stack.setCurrentIndex.assert_called_once_with(0)

    def test_init_theme_locale_creates_theme_combo(self):
        dialog = self._make_raw()
        dialog._combo_proxies['_theme_combo'] = self._real_combo()
        dialog._combo_proxies['_locale_combo'] = self._real_combo()
        with patch.object(self.mod, 'QSettings') as mock_qs, \
             patch.object(self.mod, 'AVAILABLE_LOCALES',
                          [("ar", "Arabic"), ("fr", "Français"), ("en", "English")]):
            mock_qs.return_value.value.return_value = ''
            dialog._init_theme_locale()
        self.assertGreater(dialog._combo_proxies['_theme_combo'].count(), 0)
        self.assertGreater(dialog._combo_proxies['_locale_combo'].count(), 0)

    def test_on_theme_changed_saves_and_applies(self):
        dialog = self._make_raw()
        theme_combo = self._real_combo()
        theme_combo.addItem("dark", "dark")
        theme_combo.addItem("light", "light")
        theme_combo.setCurrentIndex(0)
        dialog._combo_proxies['_theme_combo'] = theme_combo
        dialog.apply_theme = MagicMock()
        with patch.object(self.mod, 'QSettings') as mock_qs:
            theme_combo.setCurrentIndex(1)
            dialog._on_theme_changed(1)
            self.assertEqual(dialog._current_theme, 'light')
            dialog.apply_theme.assert_called_once()
            mock_qs.return_value.setValue.assert_called_once()

    def test_on_locale_changed_skips_empty_code(self):
        dialog = self._make_raw()
        dialog._on_locale_changed(0)

    @patch('plans_adressage.gui.main_dialog.fill_panel_reference')
    @patch('plans_adressage.gui.main_dialog.fill_road_reference')
    @patch('plans_adressage.gui.main_dialog.fill_activity_category')
    @patch('plans_adressage.gui.main_dialog.fill_org_category')
    @patch('plans_adressage.gui.main_dialog.fill_numbering_state')
    @patch('plans_adressage.gui.main_dialog.fill_mounting_status')
    @patch('plans_adressage.gui.main_dialog.fill_subdivision_type')
    @patch('plans_adressage.gui.main_dialog.fill_zone_type')
    @patch('plans_adressage.gui.main_dialog.fill_road_type')
    @patch('plans_adressage.gui.main_dialog.fill_wilayas_list')
    @patch('plans_adressage.gui.main_dialog.fill_paper')
    def test_on_locale_changed_updates_tr_locale(
        self,
        _fill_paper, _fill_wilayas, _fill_road_type, _fill_zone_type,
        _fill_subd_type, _fill_mount, _fill_num, _fill_org_cat,
        _fill_act_cat, _fill_road_ref, _fill_panel_ref,
    ):
        dialog = self._make_raw()
        locale_combo = self._real_combo()
        locale_combo.addItem("French", "fr")
        locale_combo.setCurrentIndex(0)
        dialog._combo_proxies['_locale_combo'] = locale_combo
        for name in ('wilaya_list', 'type_road', 'zone_type', 'subd_type',
                      'mount_status', 'num_state', 'road_ref', 'panel_ref',
                      'org_cat', 'activity_cat'):
            dialog._combo_proxies[name] = self._real_combo()
        dialog._combo_proxies['paper'] = self._real_combo()
        dialog._translate_internal_combos = MagicMock()
        with patch.object(self.mod, 'QSettings'), \
             patch.object(self.mod, 'clear_i18n_cache'), \
             patch.object(self.mod, 'apply_widget_texts'):
            dialog._on_locale_changed(1)
        self.assertEqual(dialog._tr_locale, 'fr')

    @patch('plans_adressage.gui.main_dialog.fill_panel_reference')
    @patch('plans_adressage.gui.main_dialog.fill_road_reference')
    @patch('plans_adressage.gui.main_dialog.fill_activity_category')
    @patch('plans_adressage.gui.main_dialog.fill_org_category')
    @patch('plans_adressage.gui.main_dialog.fill_numbering_state')
    @patch('plans_adressage.gui.main_dialog.fill_mounting_status')
    @patch('plans_adressage.gui.main_dialog.fill_subdivision_type')
    @patch('plans_adressage.gui.main_dialog.fill_zone_type')
    @patch('plans_adressage.gui.main_dialog.fill_road_type')
    @patch('plans_adressage.gui.main_dialog.fill_wilayas_list')
    @patch('plans_adressage.gui.main_dialog.fill_paper')
    def test_on_locale_changed_sets_rtl_for_ar(
        self,
        _fill_paper, _fill_wilayas, _fill_road_type, _fill_zone_type,
        _fill_subd_type, _fill_mount, _fill_num, _fill_org_cat,
        _fill_act_cat, _fill_road_ref, _fill_panel_ref,
    ):
        dialog = self._make_raw()
        locale_combo = self._real_combo()
        locale_combo.addItem("Arabic", "ar")
        locale_combo.setCurrentIndex(0)
        dialog._combo_proxies['_locale_combo'] = locale_combo
        with patch.object(
            self.mod.QApplication, 'setLayoutDirection',
        ) as mock_dir, \
             patch.object(self.mod, 'QSettings'), \
             patch.object(self.mod, 'clear_i18n_cache'), \
             patch.object(self.mod, 'apply_widget_texts'):
            dialog._on_locale_changed(1)
        mock_dir.assert_called_once_with(
            self.mod.Qt.LayoutDirection.RightToLeft,
        )

    @patch('plans_adressage.gui.main_dialog.fill_panel_reference')
    @patch('plans_adressage.gui.main_dialog.fill_road_reference')
    @patch('plans_adressage.gui.main_dialog.fill_activity_category')
    @patch('plans_adressage.gui.main_dialog.fill_org_category')
    @patch('plans_adressage.gui.main_dialog.fill_numbering_state')
    @patch('plans_adressage.gui.main_dialog.fill_mounting_status')
    @patch('plans_adressage.gui.main_dialog.fill_subdivision_type')
    @patch('plans_adressage.gui.main_dialog.fill_zone_type')
    @patch('plans_adressage.gui.main_dialog.fill_road_type')
    @patch('plans_adressage.gui.main_dialog.fill_wilayas_list')
    @patch('plans_adressage.gui.main_dialog.fill_paper')
    def test_on_locale_changed_sets_ltr_for_fr(
        self,
        _fill_paper, _fill_wilayas, _fill_road_type, _fill_zone_type,
        _fill_subd_type, _fill_mount, _fill_num, _fill_org_cat,
        _fill_act_cat, _fill_road_ref, _fill_panel_ref,
    ):
        dialog = self._make_raw()
        locale_combo = self._real_combo()
        locale_combo.addItem("French", "fr")
        locale_combo.setCurrentIndex(0)
        dialog._combo_proxies['_locale_combo'] = locale_combo
        with patch.object(
            self.mod.QApplication, 'setLayoutDirection',
        ) as mock_dir, \
             patch.object(self.mod, 'QSettings'), \
             patch.object(self.mod, 'clear_i18n_cache'), \
             patch.object(self.mod, 'apply_widget_texts'):
            dialog._on_locale_changed(1)
        mock_dir.assert_called_once_with(
            self.mod.Qt.LayoutDirection.LeftToRight,
        )

    @patch('plans_adressage.gui.main_dialog.fill_panel_reference')
    @patch('plans_adressage.gui.main_dialog.fill_road_reference')
    @patch('plans_adressage.gui.main_dialog.fill_activity_category')
    @patch('plans_adressage.gui.main_dialog.fill_org_category')
    @patch('plans_adressage.gui.main_dialog.fill_numbering_state')
    @patch('plans_adressage.gui.main_dialog.fill_mounting_status')
    @patch('plans_adressage.gui.main_dialog.fill_subdivision_type')
    @patch('plans_adressage.gui.main_dialog.fill_zone_type')
    @patch('plans_adressage.gui.main_dialog.fill_road_type')
    @patch('plans_adressage.gui.main_dialog.fill_wilayas_list')
    @patch('plans_adressage.gui.main_dialog.fill_paper')
    def test_on_locale_changed_refills_combos(
        self,
        _fill_paper, _fill_wilayas, _fill_road_type, _fill_zone_type,
        _fill_subd_type, _fill_mount, _fill_num, _fill_org_cat,
        _fill_act_cat, _fill_road_ref, _fill_panel_ref,
    ):
        dialog = self._make_raw()
        locale_combo = self._real_combo()
        locale_combo.addItem("French", "fr")
        locale_combo.setCurrentIndex(0)
        dialog._combo_proxies['_locale_combo'] = locale_combo
        for name in ('wilaya_list', 'type_road', 'zone_type', 'subd_type',
                      'mount_status', 'num_state', 'road_ref', 'panel_ref',
                      'org_cat', 'activity_cat'):
            dialog._combo_proxies[name] = self._real_combo()
        dialog._combo_proxies['paper'] = self._real_combo()
        dialog._translate_internal_combos = MagicMock()
        with patch.object(self.mod, 'QSettings'), \
             patch.object(self.mod, 'clear_i18n_cache'), \
             patch.object(self.mod, 'apply_widget_texts'):
            dialog._on_locale_changed(1)
            _fill_paper.assert_called_once()
            _fill_wilayas.assert_called_once()
            _fill_road_type.assert_called_once()
            _fill_zone_type.assert_called_once()
            _fill_subd_type.assert_called_once()
            _fill_mount.assert_called_once()
            _fill_num.assert_called_once()
            _fill_org_cat.assert_called_once()
            _fill_act_cat.assert_called_once()
            _fill_road_ref.assert_called_once()
            _fill_panel_ref.assert_called_once()

    def test_on_action_changed_triggers_chart(self):
        dialog = self._make_raw()
        action_combo = self._real_combo()
        action_combo.addItem("Panels Map", "panels_map")
        action_combo.setCurrentIndex(0)
        dialog._combo_proxies['_action_combo'] = action_combo
        dialog._combo_proxies['paper'] = self._real_combo()
        dialog.panel_chart = MagicMock()
        dialog.numbering_chart = MagicMock()
        dialog._on_action_changed(0)
        dialog.panel_chart.assert_called_once()

    def test_on_action_changed_numbering_map(self):
        dialog = self._make_raw()
        action_combo = self._real_combo()
        action_combo.addItem("Numbering Map", "num_map")
        action_combo.setCurrentIndex(0)
        dialog._combo_proxies['_action_combo'] = action_combo
        dialog._combo_proxies['paper'] = self._real_combo()
        dialog.panel_chart = MagicMock()
        dialog.numbering_chart = MagicMock()
        dialog._on_action_changed(0)
        dialog.numbering_chart.assert_called_once()

    def test_save_new_type_with_activity(self):
        dialog = self._make_raw()
        feature_combo = self._real_combo()
        feature_combo.addItem("Activity", "_ACTIVITY")
        feature_combo.setCurrentIndex(0)
        subtype_combo = self._real_combo()
        subtype_combo.addItem("School", "school")
        dialog._combo_proxies['feature_combo'] = feature_combo
        dialog._combo_proxies['subtype_combo'] = subtype_combo
        dialog._field_proxies['new_type'] = self._real_field()
        self.mod._ACTIVITY_KEY = '_ACTIVITY'
        dialog.clear_i18n_cache = MagicMock()
        with patch.object(self.mod, 'save_new_type', return_value=True), \
             patch.object(self.mod, 'fill_subtype_combo'), \
             patch.object(self.mod, 'clear_i18n_cache'):
            dialog._save_new_type()


if __name__ == '__main__':
    unittest.main()
