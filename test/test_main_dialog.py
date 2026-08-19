"""Tests for gui/main_dialog.py — MainDialog."""

import importlib
import sys
import unittest
from typing import Any, ClassVar
from unittest.mock import MagicMock, patch

from .helpers import get_qapp, get_qt_widget_class, make_mock_iface, setup_gui_mocks


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestMainDialogCore(unittest.TestCase):
    """Test MainDialog core methods defined in main_dialog.py."""

    app: ClassVar[Any]
    QComboBox: ClassVar[Any]
    QLineEdit: ClassVar[Any]
    main_dialog: ClassVar[Any]
    dialog_state: ClassVar[Any]

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = get_qapp()
        setup_gui_mocks()
        cls.QComboBox = get_qt_widget_class('QComboBox')
        cls.QLineEdit = get_qt_widget_class('QLineEdit')
        cls._load_module('main_dialog')
        cls._load_module('dialog_state')

    @classmethod
    def _load_module(cls, name: str) -> None:
        spec = importlib.util.spec_from_file_location(  # type: ignore[attr-defined]
            f'plans_adressage.gui.{name}',
            f'gui/{name}.py',
        )
        mod = importlib.util.module_from_spec(spec)  # type: ignore[attr-defined]
        sys.modules[f'plans_adressage.gui.{name}'] = mod
        spec.loader.exec_module(mod)
        parent = sys.modules.get('plans_adressage.gui')
        if parent is not None:
            setattr(parent, name, mod)
        setattr(cls, name.replace('.', '_'), mod)

    def _make_raw(self) -> Any:
        """Create a raw MainDialog instance without calling __init__."""
        dialog = self.main_dialog.MainDialog.__new__(self.main_dialog.MainDialog)
        dialog.iface = make_mock_iface()
        dialog._tr_locale = 'ar'
        dialog._current_theme = 'dark'
        dialog.router = MagicMock()
        dialog.menu = MagicMock()
        dialog.form_stack = MagicMock()
        dialog._combo_action = self.QComboBox()
        return dialog

    def _add_action_btns(self, dialog) -> None:
        dialog._btn_draw = MagicMock()
        dialog._btn_select = MagicMock()
        dialog._btn_edit = MagicMock()
        dialog._btn_measure = MagicMock()

    def _make_locale_combo(self, code='fr', label='French') -> Any:
        combo = self.QComboBox()
        combo.addItem(label, code)
        combo.setCurrentIndex(0)
        return combo

    # ------------------------------------------------------------------
    # _current_layer_name
    # ------------------------------------------------------------------

    def test_current_layer_name_returns_first_by_default(self) -> None:
        dialog = self._make_raw()
        dialog._combo_layer_selector = self.QComboBox()
        dialog._combo_layer_selector.addItem('Zones', 'Zones')
        dialog._combo_layer_selector.addItem('Roads', 'Roads')
        self.assertEqual(dialog._current_layer_name(), 'Zones')

    def test_current_layer_name_returns_by_index(self) -> None:
        dialog = self._make_raw()
        dialog._combo_layer_selector = self.QComboBox()
        for name in [
            'Zones',
            'Roads',
            'Facilities',
            'Subdivisions',
            'Numbering',
            'Panels',
        ]:
            dialog._combo_layer_selector.addItem(name, name)
        for idx, expected in enumerate(
            ['Zones', 'Roads', 'Facilities', 'Subdivisions', 'Numbering', 'Panels']
        ):
            dialog._combo_layer_selector.setCurrentIndex(idx)
            self.assertEqual(dialog._current_layer_name(), expected)

    def test_current_layer_name_fallback_on_bad_index(self) -> None:
        dialog = self._make_raw()
        dialog._combo_layer_selector = self.QComboBox()
        dialog._combo_layer_selector.addItem('Zones', 'Zones')
        dialog._combo_layer_selector.setCurrentIndex(99)
        self.assertEqual(dialog._current_layer_name(), 'Zones')

    # ------------------------------------------------------------------
    # _tr
    # ------------------------------------------------------------------

    def test_tr_delegates_to_get_string(self) -> None:
        dialog = self._make_raw()
        result = dialog._tr('Hello')
        self.assertEqual(result, 'Hello')

    # ------------------------------------------------------------------
    # translate_internal_combos (dialog_state)
    # ------------------------------------------------------------------

    def test_translate_internal_combos_sets_item_texts(self) -> None:
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
        dialog.LAYER_INDEX_MAP = self.main_dialog.MainDialog.LAYER_INDEX_MAP
        self.dialog_state.translate_internal_combos(dialog)
        expected_layers = [
            '\u0627\u0644\u0645\u0646\u0627\u0637\u0642',
            '\u0627\u0644\u0637\u0631\u0642',
            '\u0627\u0644\u0645\u0631\u0627\u0641\u0642',
            '\u0627\u0644\u062a\u062c\u0632\u0626\u0627\u062a',
            '\u0627\u0644\u062a\u0631\u0642\u064a\u0645',
            '\u0627\u0644\u0644\u0648\u062d\u0627\u062a',
        ]
        for i, expected in enumerate(expected_layers):
            self.assertEqual(dialog._combo_layer_selector.itemText(i), expected)
        self.assertEqual(dialog._combo_theme.itemText(0), '\u062f\u0627\u0643\u0646')
        self.assertEqual(dialog._combo_theme.itemText(1), '\u0641\u0627\u062a\u062d')
        expected_actions = [
            '\u062a\u0642\u0631\u064a\u0631',
            '\u0646\u0645\u0648\u0630\u062c \u0637\u0644\u0628\u064a\u0629',
            '\u0625\u0646\u0634\u0627\u0621 \u062e\u0631\u064a\u0637\u0629 \u0627\u0644\u0644\u0648\u062d\u0627\u062a',
            '\u0625\u0646\u0634\u0627\u0621 \u062e\u0631\u064a\u0637\u0629 \u0627\u0644\u062a\u0631\u0642\u064a\u0645',
            '\u0625\u0646\u0634\u0627\u0621 \u0646\u0633\u062e\u0629 \u0627\u062d\u062a\u064a\u0627\u0637\u064a\u0629 \u0644\u0642\u0627\u0639\u062f\u0629 \u0627\u0644\u0628\u064a\u0627\u0646\u0627\u062a',
        ]
        for i, expected in enumerate(expected_actions):
            self.assertEqual(dialog._combo_action.itemText(i), expected)

    # ------------------------------------------------------------------
    # _init_state
    # ------------------------------------------------------------------

    def test_init_state_resets_tool_state(self) -> None:
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

    # ------------------------------------------------------------------
    # apply_theme
    # ------------------------------------------------------------------

    def test_apply_theme_sets_stylesheet(self) -> None:
        dialog = self._make_raw()
        dialog.setStyleSheet = MagicMock()
        dialog.apply_theme()
        dialog.setStyleSheet.assert_called_once()

    # ------------------------------------------------------------------
    # _on_layer_changed
    # ------------------------------------------------------------------

    def test_on_layer_changed_switches_form_stack_and_updates_map(self) -> None:
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

    def test_update_action_button_texts_sets_text_for_each_layer(self) -> None:
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
        for idx, _ in enumerate(['Draw', 'Select', 'Edit']):
            dialog._update_action_button_texts(idx)
            btn_draw.setToolTip.assert_called()
            btn_select.setToolTip.assert_called()
            btn_edit.setToolTip.assert_called()
            btn_measure.setToolTip.assert_called()

    # ------------------------------------------------------------------
    # init_theme_locale (dialog_state)
    # ------------------------------------------------------------------

    def test_init_theme_locale_creates_combos(self) -> None:
        dialog = self._make_raw()
        dialog._combo_theme = self.QComboBox()
        dialog._combo_locale = self.QComboBox()
        with (
            patch.object(self.dialog_state, 'QSettings') as mock_qs,
            patch.object(
                self.dialog_state,
                'AVAILABLE_LOCALES',
                [('ar', 'Arabic'), ('fr', 'Fran\u00e7ais'), ('en', 'English')],
            ),
            patch.object(self.dialog_state, 'THEME_DARK', 'dark'),
            patch.object(self.dialog_state, 'THEME_LIGHT', 'light'),
            patch.object(self.dialog_state, 'DEFAULT_THEME', 'dark'),
        ):
            mock_qs.return_value.value.return_value = ''
            self.dialog_state.init_theme_locale(dialog)
        self.assertGreater(dialog._combo_theme.count(), 0)
        self.assertGreater(dialog._combo_locale.count(), 0)

    # ------------------------------------------------------------------
    # on_theme_changed (dialog_state)
    # ------------------------------------------------------------------

    def test_on_theme_changed_saves_and_applies(self) -> None:
        dialog = self._make_raw()
        dialog._combo_theme = self.QComboBox()
        dialog._combo_theme.addItem('dark', 'dark')
        dialog._combo_theme.addItem('light', 'light')
        dialog.apply_theme = MagicMock()
        with patch.object(self.dialog_state, 'QSettings') as mock_qs:
            dialog._combo_theme.setCurrentIndex(1)
            self.dialog_state.on_theme_changed(dialog, 1)
            self.assertEqual(dialog._current_theme, 'light')
            dialog.apply_theme.assert_called_once()
            mock_qs.return_value.setValue.assert_called_once()

    # ------------------------------------------------------------------
    # on_locale_changed (dialog_state)
    # ------------------------------------------------------------------

    def test_on_locale_changed_skips_empty_code(self) -> None:
        dialog = self._make_raw()
        dialog._combo_locale = self.QComboBox()
        dialog._combo_locale.addItem('', '')
        self.dialog_state.on_locale_changed(dialog, 0)

    @patch('plans_adressage.gui.dialog_state.fill_panel_reference')
    @patch('plans_adressage.gui.dialog_state.fill_road_reference')
    @patch('plans_adressage.gui.dialog_state.fill_activity_category')
    @patch('plans_adressage.gui.dialog_state.fill_org_category')
    @patch('plans_adressage.gui.dialog_state.fill_numbering_state')
    @patch('plans_adressage.gui.dialog_state.fill_mounting_status')
    @patch('plans_adressage.gui.dialog_state.fill_subdivision_type')
    @patch('plans_adressage.gui.dialog_state.fill_zone_type')
    @patch('plans_adressage.gui.dialog_state.fill_road_type')
    @patch('plans_adressage.gui.dialog_state.fill_wilayas_list')
    @patch('plans_adressage.gui.dialog_state.fill_feature_combo')
    @patch('plans_adressage.gui.dialog_state.fill_paper')
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
    ) -> None:
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
        for name in [
            'Zones',
            'Roads',
            'Facilities',
            'Subdivisions',
            'Numbering',
            'Panels',
        ]:
            dialog._combo_layer_selector.addItem(name, name)
        dialog._combo_theme = self.QComboBox()
        self._add_action_btns(dialog)
        with (
            patch.object(self.dialog_state, 'QSettings'),
            patch.object(self.dialog_state, 'clear_i18n_cache'),
            patch.object(self.dialog_state, 'apply_widget_texts'),
        ):
            self.dialog_state.on_locale_changed(dialog, 1)
            self.assertEqual(dialog._tr_locale, 'fr')

    @patch('plans_adressage.gui.dialog_state.fill_panel_reference')
    @patch('plans_adressage.gui.dialog_state.fill_road_reference')
    @patch('plans_adressage.gui.dialog_state.fill_activity_category')
    @patch('plans_adressage.gui.dialog_state.fill_org_category')
    @patch('plans_adressage.gui.dialog_state.fill_numbering_state')
    @patch('plans_adressage.gui.dialog_state.fill_mounting_status')
    @patch('plans_adressage.gui.dialog_state.fill_subdivision_type')
    @patch('plans_adressage.gui.dialog_state.fill_zone_type')
    @patch('plans_adressage.gui.dialog_state.fill_road_type')
    @patch('plans_adressage.gui.dialog_state.fill_wilayas_list')
    @patch('plans_adressage.gui.dialog_state.fill_feature_combo')
    @patch('plans_adressage.gui.dialog_state.fill_paper')
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
    ) -> None:
        dialog = self._make_raw()
        dialog._combo_locale = self._make_locale_combo(code='ar', label='Arabic')
        dialog._combo_layer_selector = self.QComboBox()
        for name in [
            'Zones',
            'Roads',
            'Facilities',
            'Subdivisions',
            'Numbering',
            'Panels',
        ]:
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
                self.dialog_state.QApplication,
                'setLayoutDirection',
            ) as mock_dir,
            patch.object(self.dialog_state, 'QSettings'),
            patch.object(self.dialog_state, 'clear_i18n_cache'),
            patch.object(self.dialog_state, 'apply_widget_texts'),
        ):
            self.dialog_state.on_locale_changed(dialog, 1)
        mock_dir.assert_called_once_with(
            self.main_dialog.Qt.LayoutDirection.RightToLeft,
        )

    @patch('plans_adressage.gui.dialog_state.fill_panel_reference')
    @patch('plans_adressage.gui.dialog_state.fill_road_reference')
    @patch('plans_adressage.gui.dialog_state.fill_activity_category')
    @patch('plans_adressage.gui.dialog_state.fill_org_category')
    @patch('plans_adressage.gui.dialog_state.fill_numbering_state')
    @patch('plans_adressage.gui.dialog_state.fill_mounting_status')
    @patch('plans_adressage.gui.dialog_state.fill_subdivision_type')
    @patch('plans_adressage.gui.dialog_state.fill_zone_type')
    @patch('plans_adressage.gui.dialog_state.fill_road_type')
    @patch('plans_adressage.gui.dialog_state.fill_wilayas_list')
    @patch('plans_adressage.gui.dialog_state.fill_feature_combo')
    @patch('plans_adressage.gui.dialog_state.fill_paper')
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
    ) -> None:
        dialog = self._make_raw()
        dialog._combo_locale = self._make_locale_combo()
        dialog._combo_layer_selector = self.QComboBox()
        for name in [
            'Zones',
            'Roads',
            'Facilities',
            'Subdivisions',
            'Numbering',
            'Panels',
        ]:
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
                self.dialog_state.QApplication,
                'setLayoutDirection',
            ) as mock_dir,
            patch.object(self.dialog_state, 'QSettings'),
            patch.object(self.dialog_state, 'clear_i18n_cache'),
            patch.object(self.dialog_state, 'apply_widget_texts'),
        ):
            self.dialog_state.on_locale_changed(dialog, 1)
        mock_dir.assert_called_once_with(
            self.main_dialog.Qt.LayoutDirection.LeftToRight,
        )

    def test_on_locale_changed_refills_combos(self) -> None:
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
        for name in [
            'Zones',
            'Roads',
            'Facilities',
            'Subdivisions',
            'Numbering',
            'Panels',
        ]:
            dialog._combo_layer_selector.addItem(name, name)
        dialog._combo_theme = self.QComboBox()
        self._add_action_btns(dialog)
        with (
            patch.object(self.dialog_state, 'fill_paper'),
            patch.object(self.dialog_state, 'fill_feature_combo'),
            patch.object(self.dialog_state, 'fill_wilayas_list'),
            patch.object(self.dialog_state, 'fill_road_type'),
            patch.object(self.dialog_state, 'fill_zone_type'),
            patch.object(self.dialog_state, 'fill_subdivision_type'),
            patch.object(self.dialog_state, 'fill_mounting_status'),
            patch.object(self.dialog_state, 'fill_numbering_state'),
            patch.object(self.dialog_state, 'fill_org_category'),
            patch.object(self.dialog_state, 'fill_activity_category'),
            patch.object(self.dialog_state, 'fill_road_reference'),
            patch.object(self.dialog_state, 'fill_panel_reference'),
            patch.object(self.dialog_state, 'QSettings'),
            patch.object(self.dialog_state, 'clear_i18n_cache'),
            patch.object(self.dialog_state, 'apply_widget_texts'),
        ):
            self.dialog_state.on_locale_changed(dialog, 1)
            self.dialog_state.fill_paper.assert_called_once()
            self.dialog_state.fill_wilayas_list.assert_called_once()
            self.dialog_state.fill_road_type.assert_called_once()
            self.dialog_state.fill_zone_type.assert_called_once()
            self.dialog_state.fill_subdivision_type.assert_called_once()
            self.dialog_state.fill_mounting_status.assert_called_once()
            self.dialog_state.fill_numbering_state.assert_called_once()
            self.dialog_state.fill_org_category.assert_called_once()
            self.dialog_state.fill_activity_category.assert_called_once()
            self.dialog_state.fill_road_reference.assert_called_once()
            self.dialog_state.fill_panel_reference.assert_called_once()

    # ------------------------------------------------------------------
    # on_action_changed (dialog_state)
    # ------------------------------------------------------------------

    def test_on_action_changed_triggers_chart(self) -> None:
        dialog = self._make_raw()
        dialog._combo_action = self.QComboBox()
        dialog._combo_action.addItem('Panels Map', 'panels_map')
        dialog._combo_action.setCurrentIndex(0)
        dialog._combo_paper = self.QComboBox()
        dialog.panel_chart = MagicMock()
        dialog.numbering_chart = MagicMock()
        self.dialog_state.on_action_changed(dialog, 0)
        dialog.panel_chart.assert_called_once()

    def test_on_action_changed_numbering_map(self) -> None:
        dialog = self._make_raw()
        dialog._combo_action = self.QComboBox()
        dialog._combo_action.addItem('Numbering Map', 'num_map')
        dialog._combo_action.setCurrentIndex(0)
        dialog._combo_paper = self.QComboBox()
        dialog.panel_chart = MagicMock()
        dialog.numbering_chart = MagicMock()
        self.dialog_state.on_action_changed(dialog, 0)
        dialog.numbering_chart.assert_called_once()

    # ------------------------------------------------------------------
    # _save_new_type
    # ------------------------------------------------------------------

    def test_save_new_type_with_activity(self) -> None:
        dialog = self._make_raw()
        dialog.feature_combo = self.QComboBox()
        dialog.feature_combo.addItem('Activity', '_ACTIVITY')
        dialog.feature_combo.setCurrentIndex(0)
        dialog.subtype_combo = self.QComboBox()
        dialog.subtype_combo.addItem('School', 'school')
        dialog._field_new_type = self.QLineEdit()
        dialog.clear_i18n_cache = MagicMock()
        with (
            patch.object(self.main_dialog, 'save_new_type_to_json', return_value=True),
            patch.object(self.main_dialog, 'fill_subtype_combo'),
            patch.object(self.main_dialog, 'clear_i18n_cache'),
        ):
            dialog._save_new_type()


if __name__ == '__main__':
    unittest.main()
