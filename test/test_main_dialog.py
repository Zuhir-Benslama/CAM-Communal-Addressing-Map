"""Tests for gui/main_dialog.py — MainDialog."""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from .helpers import get_qapp, get_qt_widget_class, make_mock_iface, setup_gui_mocks


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestMainDialogCore(unittest.TestCase):
    """Test MainDialog core methods defined in main_dialog.py."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        cls.QComboBox = get_qt_widget_class('QComboBox')
        cls.QLineEdit = get_qt_widget_class('QLineEdit')
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
        dialog.router = MagicMock()
        dialog.menu = MagicMock()
        dialog.form_stack = MagicMock()
        dialog._combo_action = self.QComboBox()
        return dialog

    def _add_action_btns(self, dialog):
        dialog._btn_draw = MagicMock()
        dialog._btn_select = MagicMock()
        dialog._btn_edit = MagicMock()
        dialog._btn_measure = MagicMock()

    # ------------------------------------------------------------------
    # _current_layer_name
    # ------------------------------------------------------------------

    def test_current_layer_name_returns_first_by_default(self):
        dialog = self._make_raw()
        dialog._combo_layer_selector = self.QComboBox()
        dialog._combo_layer_selector.addItem('Zones', 'Zones')
        dialog._combo_layer_selector.addItem('Roads', 'Roads')
        self.assertEqual(dialog._current_layer_name(), 'Zones')

    def test_current_layer_name_returns_by_index(self):
        dialog = self._make_raw()
        dialog._combo_layer_selector = self.QComboBox()
        for name in ['Zones', 'Roads', 'Facilities', 'Subdivisions', 'Numbering', 'Panels']:
            dialog._combo_layer_selector.addItem(name, name)
        for idx, expected in enumerate(
            ['Zones', 'Roads', 'Facilities', 'Subdivisions', 'Numbering', 'Panels']
        ):
            dialog._combo_layer_selector.setCurrentIndex(idx)
            self.assertEqual(dialog._current_layer_name(), expected)

    def test_current_layer_name_fallback_on_bad_index(self):
        dialog = self._make_raw()
        dialog._combo_layer_selector = self.QComboBox()
        dialog._combo_layer_selector.addItem('Zones', 'Zones')
        dialog._combo_layer_selector.setCurrentIndex(99)
        self.assertEqual(dialog._current_layer_name(), 'Zones')

    # ------------------------------------------------------------------
    # _tr
    # ------------------------------------------------------------------

    def test_tr_delegates_to_get_string(self):
        dialog = self._make_raw()
        result = dialog._tr('Hello')
        self.assertEqual(result, 'Hello')

    # ------------------------------------------------------------------
    # _translate_internal_combos
    # ------------------------------------------------------------------

    def test_translate_internal_combos_sets_item_texts(self):
        dialog = self._make_raw()
        dialog._tr_locale = 'en'
        dialog._combo_layer_selector = self.QComboBox()
        for _ in range(6):
            dialog._combo_layer_selector.addItem('', '')
        dialog._combo_theme = self.QComboBox()
        dialog._combo_theme.addItem('', 'dark')
        dialog._combo_theme.addItem('', 'light')
        dialog._combo_action = self.QComboBox()
        dialog._combo_action.addItem('', 'report')
        dialog._combo_action.addItem('', 'order')
        dialog._combo_action.addItem('', 'panels_map')
        dialog._combo_action.addItem('', 'num_map')
        dialog._combo_action.addItem('', 'backup')
        dialog._combo_locale = self.QComboBox()
        dialog._combo_locale.addItem('', 'ar')
        dialog._combo_locale.addItem('', 'fr')
        dialog._combo_locale.addItem('', 'en')
        dialog._translate_internal_combos()
        expected_layers = [
            'المناطق', 'الطرق', 'المرافق',
            'التجزئات', 'الترقيم', 'اللوحات',
        ]
        for i, expected in enumerate(expected_layers):
            self.assertEqual(dialog._combo_layer_selector.itemText(i), expected)
        self.assertEqual(dialog._combo_theme.itemText(0), 'داكن')
        self.assertEqual(dialog._combo_theme.itemText(1), 'فاتح')
        expected_actions = [
            'تقرير', 'نموذج طلبية', 'إنشاء خريطة اللوحات',
            'إنشاء خريطة الترقيم', 'إنشاء نسخة احتياطية لقاعدة البيانات',
        ]
        for i, expected in enumerate(expected_actions):
            self.assertEqual(dialog._combo_action.itemText(i), expected)

    # ------------------------------------------------------------------
    # _init_state
    # ------------------------------------------------------------------

    def test_init_state_resets_tool_state(self):
        dialog = self._make_raw()
        dialog._init_state()
        self.assertIsNone(dialog.sat_view)
        self.assertIsNone(dialog.rast)
        self.assertIsNone(dialog.ln)
        self.assertEqual(dialog.type_plan, '')
        self.assertEqual(dialog.type_to_hide, '')
        self.assertIsNone(dialog.measure_tool)
        self.assertIsNone(dialog.identify_tool)
        self.assertIsNone(dialog.ref_identify_tool)
        self.assertIsNone(dialog.popup_dialog)
        self.assertIsNone(dialog.current_user)
        self.assertEqual(dialog.update_object, {})
        self.assertEqual(dialog.update_only_form, {})

    # ------------------------------------------------------------------
    # apply_theme
    # ------------------------------------------------------------------

    def test_apply_theme_sets_stylesheet(self):
        dialog = self._make_raw()
        dialog.setStyleSheet = MagicMock()
        dialog.apply_theme()
        dialog.setStyleSheet.assert_called_once()

    # ------------------------------------------------------------------
    # _on_layer_changed
    # ------------------------------------------------------------------

    def test_on_layer_changed_switches_form_stack_and_updates_map(self):
        dialog = self._make_raw()
        dialog._form_stack = MagicMock()
        dialog.menu = MagicMock()
        dialog.menu.currentIndex.return_value = 0
        dialog.on_opt_selected = MagicMock()
        dialog._update_action_button_texts = MagicMock()
        dialog._combo_layer_selector = self.QComboBox()
        dialog._combo_layer_selector.addItem('Zones', 'Zones')
        dialog._combo_layer_selector.addItem('Roads', 'Roads')
        dialog._combo_layer_selector.addItem('Facilities', 'Facilities')
        dialog._on_layer_changed(2)
        dialog._form_stack.setCurrentIndex.assert_called_once_with(2)
        dialog._update_action_button_texts.assert_called_once_with(2)
        dialog.on_opt_selected.assert_called_once_with(0)

    def test_update_action_button_texts_sets_text_for_each_layer(self):
        dialog = self._make_raw()
        btn_draw = MagicMock()
        btn_select = MagicMock()
        btn_edit = MagicMock()
        btn_measure = MagicMock()
        dialog._btn_draw = btn_draw
        dialog._btn_select = btn_select
        dialog._btn_edit = btn_edit
        dialog._btn_measure = btn_measure
        dialog._tr_locale = 'en'
        for idx, expected_prefix in enumerate(['Draw', 'Select', 'Edit']):
            dialog._update_action_button_texts(idx)
            btn_draw.setText.assert_called()
            btn_select.setText.assert_called()
            btn_edit.setText.assert_called()
            btn_measure.setText.assert_called()

    # ------------------------------------------------------------------
    # _init_theme_locale
    # ------------------------------------------------------------------

    def test_init_theme_locale_creates_combos(self):
        dialog = self._make_raw()
        dialog._combo_theme = self.QComboBox()
        dialog._combo_locale = self.QComboBox()
        with (
            patch.object(self.mod, 'QSettings') as mock_qs,
            patch.object(
                self.mod,
                'AVAILABLE_LOCALES',
                [('ar', 'Arabic'), ('fr', 'Fran\u00e7ais'), ('en', 'English')],
            ),
            patch.object(self.mod, 'THEME_DARK', 'dark'),
            patch.object(self.mod, 'THEME_LIGHT', 'light'),
            patch.object(self.mod, 'DEFAULT_THEME', 'dark'),
        ):
            mock_qs.return_value.value.return_value = ''
            dialog._init_theme_locale()
        self.assertGreater(dialog._combo_theme.count(), 0)
        self.assertGreater(dialog._combo_locale.count(), 0)

    # ------------------------------------------------------------------
    # _on_theme_changed
    # ------------------------------------------------------------------

    def test_on_theme_changed_saves_and_applies(self):
        dialog = self._make_raw()
        dialog._combo_theme = self.QComboBox()
        dialog._combo_theme.addItem('dark', 'dark')
        dialog._combo_theme.addItem('light', 'light')
        dialog.apply_theme = MagicMock()
        with patch.object(self.mod, 'QSettings') as mock_qs:
            dialog._combo_theme.setCurrentIndex(1)
            dialog._on_theme_changed(1)
            self.assertEqual(dialog._current_theme, 'light')
            dialog.apply_theme.assert_called_once()
            mock_qs.return_value.setValue.assert_called_once()

    # ------------------------------------------------------------------
    # _on_locale_changed
    # ------------------------------------------------------------------

    def test_on_locale_changed_skips_empty_code(self):
        dialog = self._make_raw()
        dialog._combo_locale = self.QComboBox()
        dialog._combo_locale.addItem('', '')
        dialog._on_locale_changed(0)

    def _make_locale_combo(self, code='fr', label='French'):
        combo = self.QComboBox()
        combo.addItem(label, code)
        combo.setCurrentIndex(0)
        return combo

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
    @patch('plans_adressage.gui.main_dialog.fill_feature_combo')
    @patch('plans_adressage.gui.main_dialog.fill_paper')
    def test_on_locale_changed_updates_tr_locale(
        self,
        _fill_paper,
        _fill_feature,
        _fill_wilayas,
        _fill_road_type,
        _fill_zone_type,
        _fill_subd_type,
        _fill_mount,
        _fill_num,
        _fill_org_cat,
        _fill_act_cat,
        _fill_road_ref,
        _fill_panel_ref,
    ):
        dialog = self._make_raw()
        dialog._combo_locale = self._make_locale_combo()
        for attr in (
            'wilaya_list',
            '_combo_type_road',
            '_combo_zone_type',
            '_combo_subd_type',
            '_combo_mount_status',
            '_combo_num_state',
            '_combo_road_ref',
            '_combo_panel_ref',
            '_combo_org_cat',
            '_combo_activity_cat',
        ):
            setattr(dialog, attr, self.QComboBox())
        dialog.feature_combo = self.QComboBox()
        dialog._combo_paper = self.QComboBox()
        dialog._combo_layer_selector = self.QComboBox()
        for name in ['Zones', 'Roads', 'Facilities', 'Subdivisions', 'Numbering', 'Panels']:
            dialog._combo_layer_selector.addItem(name, name)
        dialog._combo_theme = self.QComboBox()
        self._add_action_btns(dialog)
        with (
            patch.object(self.mod, 'QSettings'),
            patch.object(self.mod, 'clear_i18n_cache'),
            patch.object(self.mod, 'apply_widget_texts'),
        ):
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
    @patch('plans_adressage.gui.main_dialog.fill_feature_combo')
    @patch('plans_adressage.gui.main_dialog.fill_paper')
    def test_on_locale_changed_sets_rtl_for_ar(
        self,
        _fill_paper,
        _fill_feature,
        _fill_wilayas,
        _fill_road_type,
        _fill_zone_type,
        _fill_subd_type,
        _fill_mount,
        _fill_num,
        _fill_org_cat,
        _fill_act_cat,
        _fill_road_ref,
        _fill_panel_ref,
    ):
        dialog = self._make_raw()
        dialog._combo_locale = self._make_locale_combo(code='ar', label='Arabic')
        dialog._combo_layer_selector = self.QComboBox()
        for name in ['Zones', 'Roads', 'Facilities', 'Subdivisions', 'Numbering', 'Panels']:
            dialog._combo_layer_selector.addItem(name, name)
        dialog._combo_theme = self.QComboBox()
        for attr in (
            'wilaya_list',
            '_combo_type_road',
            '_combo_zone_type',
            '_combo_subd_type',
            '_combo_mount_status',
            '_combo_num_state',
            '_combo_road_ref',
            '_combo_panel_ref',
            '_combo_org_cat',
            '_combo_activity_cat',
        ):
            setattr(dialog, attr, self.QComboBox())
        dialog.feature_combo = self.QComboBox()
        dialog._combo_paper = self.QComboBox()
        self._add_action_btns(dialog)
        with (
            patch.object(
                self.mod.QApplication,
                'setLayoutDirection',
            ) as mock_dir,
            patch.object(self.mod, 'QSettings'),
            patch.object(self.mod, 'clear_i18n_cache'),
            patch.object(self.mod, 'apply_widget_texts'),
        ):
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
    @patch('plans_adressage.gui.main_dialog.fill_feature_combo')
    @patch('plans_adressage.gui.main_dialog.fill_paper')
    def test_on_locale_changed_sets_ltr_for_fr(
        self,
        _fill_paper,
        _fill_feature,
        _fill_wilayas,
        _fill_road_type,
        _fill_zone_type,
        _fill_subd_type,
        _fill_mount,
        _fill_num,
        _fill_org_cat,
        _fill_act_cat,
        _fill_road_ref,
        _fill_panel_ref,
    ):
        dialog = self._make_raw()
        dialog._combo_locale = self._make_locale_combo()
        dialog._combo_layer_selector = self.QComboBox()
        for name in ['Zones', 'Roads', 'Facilities', 'Subdivisions', 'Numbering', 'Panels']:
            dialog._combo_layer_selector.addItem(name, name)
        dialog._combo_theme = self.QComboBox()
        for attr in (
            'wilaya_list',
            '_combo_type_road',
            '_combo_zone_type',
            '_combo_subd_type',
            '_combo_mount_status',
            '_combo_num_state',
            '_combo_road_ref',
            '_combo_panel_ref',
            '_combo_org_cat',
            '_combo_activity_cat',
        ):
            setattr(dialog, attr, self.QComboBox())
        dialog.feature_combo = self.QComboBox()
        dialog._combo_paper = self.QComboBox()
        self._add_action_btns(dialog)
        with (
            patch.object(
                self.mod.QApplication,
                'setLayoutDirection',
            ) as mock_dir,
            patch.object(self.mod, 'QSettings'),
            patch.object(self.mod, 'clear_i18n_cache'),
            patch.object(self.mod, 'apply_widget_texts'),
        ):
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
    @patch('plans_adressage.gui.main_dialog.fill_feature_combo')
    @patch('plans_adressage.gui.main_dialog.fill_paper')
    def test_on_locale_changed_refills_combos(
        self,
        _fill_paper,
        _fill_feature,
        _fill_wilayas,
        _fill_road_type,
        _fill_zone_type,
        _fill_subd_type,
        _fill_mount,
        _fill_num,
        _fill_org_cat,
        _fill_act_cat,
        _fill_road_ref,
        _fill_panel_ref,
    ):
        dialog = self._make_raw()
        dialog._combo_locale = self._make_locale_combo()
        for attr in (
            'wilaya_list',
            '_combo_type_road',
            '_combo_zone_type',
            '_combo_subd_type',
            '_combo_mount_status',
            '_combo_num_state',
            '_combo_road_ref',
            '_combo_panel_ref',
            '_combo_org_cat',
            '_combo_activity_cat',
        ):
            setattr(dialog, attr, self.QComboBox())
        dialog.feature_combo = self.QComboBox()
        dialog._combo_paper = self.QComboBox()
        dialog._combo_layer_selector = self.QComboBox()
        for name in ['Zones', 'Roads', 'Facilities', 'Subdivisions', 'Numbering', 'Panels']:
            dialog._combo_layer_selector.addItem(name, name)
        dialog._combo_theme = self.QComboBox()
        self._add_action_btns(dialog)
        with (
            patch.object(self.mod, 'QSettings'),
            patch.object(self.mod, 'clear_i18n_cache'),
            patch.object(self.mod, 'apply_widget_texts'),
        ):
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

    # ------------------------------------------------------------------
    # _on_action_changed
    # ------------------------------------------------------------------

    def test_on_action_changed_triggers_chart(self):
        dialog = self._make_raw()
        dialog._combo_action = self.QComboBox()
        dialog._combo_action.addItem('Panels Map', 'panels_map')
        dialog._combo_action.setCurrentIndex(0)
        dialog._combo_paper = self.QComboBox()
        dialog.panel_chart = MagicMock()
        dialog.numbering_chart = MagicMock()
        dialog._on_action_changed(0)
        dialog.panel_chart.assert_called_once()

    def test_on_action_changed_numbering_map(self):
        dialog = self._make_raw()
        dialog._combo_action = self.QComboBox()
        dialog._combo_action.addItem('Numbering Map', 'num_map')
        dialog._combo_action.setCurrentIndex(0)
        dialog._combo_paper = self.QComboBox()
        dialog.panel_chart = MagicMock()
        dialog.numbering_chart = MagicMock()
        dialog._on_action_changed(0)
        dialog.numbering_chart.assert_called_once()

    # ------------------------------------------------------------------
    # _save_new_type
    # ------------------------------------------------------------------

    def test_save_new_type_with_activity(self):
        dialog = self._make_raw()
        dialog.feature_combo = self.QComboBox()
        dialog.feature_combo.addItem('Activity', '_ACTIVITY')
        dialog.feature_combo.setCurrentIndex(0)
        dialog.subtype_combo = self.QComboBox()
        dialog.subtype_combo.addItem('School', 'school')
        dialog._field_new_type = self.QLineEdit()
        self.mod._ACTIVITY_KEY = '_ACTIVITY'
        dialog.clear_i18n_cache = MagicMock()
        with (
            patch.object(self.mod, 'save_new_type', return_value=True),
            patch.object(self.mod, 'fill_subtype_combo'),
            patch.object(self.mod, 'clear_i18n_cache'),
        ):
            dialog._save_new_type()


if __name__ == '__main__':
    unittest.main()
