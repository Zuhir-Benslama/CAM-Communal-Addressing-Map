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

    # ------------------------------------------------------------------
    # _run_init_steps
    # ------------------------------------------------------------------

    def test_run_init_steps_runs_all(self) -> None:
        calls = []
        steps = [
            ('a', lambda: calls.append('a')),
            ('b', lambda: calls.append('b')),
        ]
        self.assertIsNone(self.main_dialog._run_init_steps(steps))
        self.assertEqual(calls, ['a', 'b'])

    def test_run_init_steps_logs_and_reraises(self) -> None:
        def boom():
            raise ValueError('x')

        steps = [('a', boom)]
        with (
            patch.object(self.main_dialog.logger, 'exception') as mock_exc,
            self.assertRaises(ValueError),
        ):
            self.main_dialog._run_init_steps(steps)
        mock_exc.assert_called_once_with('Init step %r failed', 'a')

    # ------------------------------------------------------------------
    # _on_submit
    # ------------------------------------------------------------------

    def test_on_submit_dispatches_action(self) -> None:
        dialog = self._make_raw()
        handler = MagicMock()
        dialog._submit_dispatch = {self.main_dialog.Action.DRAW: handler}
        dialog._on_submit(self.main_dialog.Action.DRAW)
        handler.assert_called_once()

    def test_on_submit_accepts_string(self) -> None:
        dialog = self._make_raw()
        handler = MagicMock()
        dialog._submit_dispatch = {self.main_dialog.Action.DRAW: handler}
        dialog._on_submit('draw')
        handler.assert_called_once()

    def test_on_submit_ignores_unknown_string(self) -> None:
        dialog = self._make_raw()
        dialog._submit_dispatch = {}
        self.assertIsNone(dialog._on_submit('no_such_action'))

    def test_on_submit_unknown_action_logs(self) -> None:
        dialog = self._make_raw()
        dialog._submit_dispatch = {}
        with patch.object(self.main_dialog.logger, 'error') as mock_err:
            dialog._on_submit(self.main_dialog.Action.DRAW)
        mock_err.assert_called_once()

    # ------------------------------------------------------------------
    # _switch_page
    # ------------------------------------------------------------------

    def test_switch_page_finds_and_activates(self) -> None:
        dialog = self._make_raw()
        page = MagicMock()
        dialog._page_stack = MagicMock()
        dialog._page_stack.findChild.return_value = page
        dialog._switch_page('login')
        dialog._page_stack.setCurrentWidget.assert_called_once_with(page)

    def test_switch_page_logs_when_missing(self) -> None:
        dialog = self._make_raw()
        dialog._page_stack = MagicMock()
        dialog._page_stack.findChild.return_value = None
        with patch.object(self.main_dialog.logger, 'warning') as mock_warn:
            dialog._switch_page('nope')
        mock_warn.assert_called()

    # ------------------------------------------------------------------
    # _toggle_settings
    # ------------------------------------------------------------------

    def test_toggle_settings_shows_settings(self) -> None:
        dialog = self._make_raw()
        dialog._settings_visible = False
        dialog._main_stack = MagicMock()
        dialog._main_stack.findChild.return_value = MagicMock()
        dialog._toggle_settings()
        self.assertTrue(dialog._settings_visible)
        dialog._main_stack.setCurrentWidget.assert_called_once()

    def test_toggle_settings_hides_when_visible(self) -> None:
        dialog = self._make_raw()
        dialog._settings_visible = True
        dialog._main_stack = MagicMock()
        dialog._main_stack.findChild.return_value = MagicMock()
        dialog._toggle_settings()
        self.assertFalse(dialog._settings_visible)

    # ------------------------------------------------------------------
    # _restore_layout_direction
    # ------------------------------------------------------------------

    def test_restore_layout_direction(self) -> None:
        dialog = self._make_raw()
        dialog._previous_layout_dir = MagicMock()
        with patch.object(
            self.main_dialog.QApplication, 'setLayoutDirection'
        ) as mock_set:
            dialog._restore_layout_direction()
        mock_set.assert_called_once_with(dialog._previous_layout_dir)

    # ------------------------------------------------------------------
    # _default_layer_keys / _layer_key_map
    # ------------------------------------------------------------------

    def test_default_layer_keys(self) -> None:
        self.assertEqual(
            self.main_dialog.MainDialog._default_layer_keys(),
            ['zone', 'road', 'org', 'city', 'num', 'pan'],
        )

    def test_layer_key_map_when_no_stack(self) -> None:
        dialog = self._make_raw()
        dialog._form_stack = None
        self.assertEqual(
            dialog._layer_key_map(),
            ['zone', 'road', 'org', 'city', 'num', 'pan'],
        )

    def test_layer_key_map_derives_from_stack(self) -> None:
        dialog = self._make_raw()

        def make_widget(name):
            w = MagicMock()
            w.objectName.return_value = name
            return w

        stack = MagicMock()
        stack.count.return_value = 3
        stack.widget.side_effect = [
            make_widget('zoneForm'),
            make_widget('roadForm'),
            make_widget('plain'),
        ]
        dialog._form_stack = stack
        self.assertEqual(dialog._layer_key_map(), ['zone', 'road', 'plain'])

    # ------------------------------------------------------------------
    # _validate_layer_maps
    # ------------------------------------------------------------------

    def test_validate_layer_maps_ok(self) -> None:
        dialog = self._make_raw()
        stack = MagicMock()
        stack.count.return_value = 6
        dialog._form_stack = stack
        self.assertIsNone(dialog._validate_layer_maps())

    def test_validate_layer_maps_no_stack(self) -> None:
        dialog = self._make_raw()
        dialog._form_stack = None
        self.assertIsNone(dialog._validate_layer_maps())

    def test_validate_layer_maps_raises_on_mismatch(self) -> None:
        dialog = self._make_raw()
        stack = MagicMock()
        stack.count.return_value = 3
        dialog._form_stack = stack
        with self.assertRaises(AssertionError):
            dialog._validate_layer_maps()

    # ------------------------------------------------------------------
    # _setup_i18n / _setup_widget_aliases
    # ------------------------------------------------------------------

    def test_setup_i18n_clears_button_texts(self) -> None:
        dialog = self._make_raw()
        for b in ('_btn_draw', '_btn_select', '_btn_edit', '_btn_measure'):
            setattr(dialog, b, MagicMock())
        with (
            patch.object(self.main_dialog, 'clear_i18n_cache') as mock_clear,
            patch.object(self.main_dialog, 'translate_internal_combos') as mock_tr,
        ):
            dialog._setup_i18n()
        dialog._btn_draw.setText.assert_called_once_with('')
        mock_clear.assert_called_once()
        mock_tr.assert_called_once_with(dialog)

    def test_setup_widget_aliases_assigns_attributes(self) -> None:
        dialog = self._make_raw()
        source_names = [
            '_combo_map_options',
            '_field_username',
            '_field_password',
            '_field_fname',
            '_field_lname',
            '_field_email',
            '_field_pnum',
            '_field_uname',
            '_field_pwd',
            '_label_username',
            '_combo_paper',
            '_combo_zone_type',
            '_field_nom_zone',
            '_combo_type_road',
            '_field_road_name',
            '_combo_org_cat',
            '_combo_org_type',
            '_field_org_name',
            '_combo_subd_type',
            '_field_subd_name',
            '_combo_road_ref',
            '_field_num_val',
            '_field_repetition',
            '_combo_num_state',
            '_combo_activity_cat',
            '_combo_activity_type',
            '_combo_mount_status',
            '_combo_panel_ref',
        ]
        for name in source_names:
            setattr(dialog, name, MagicMock())
        dialog._setup_widget_aliases()
        self.assertIs(dialog.map_options, dialog._combo_map_options)
        self.assertIs(dialog.username, dialog._field_username)
        self.assertIs(dialog.panel_ref, dialog._combo_panel_ref)

    # ------------------------------------------------------------------
    # _populate_dispatch
    # ------------------------------------------------------------------

    def test_populate_dispatch_maps_actions(self) -> None:
        dialog = self._make_raw()
        dialog.login_user = MagicMock()
        dialog._populate_dispatch()
        self.assertEqual(
            dialog._submit_dispatch[self.main_dialog.Action.LOGIN],
            dialog.login_user,
        )
        self.assertEqual(
            dialog._submit_dispatch[self.main_dialog.Action.LIST_ROADS],
            dialog.list_road_entries,
        )

    # ------------------------------------------------------------------
    # _on_feature_changed
    # ------------------------------------------------------------------

    def test_on_feature_changed_non_string_ignored(self) -> None:
        dialog = self._make_raw()
        dialog.feature_combo = self.QComboBox()
        dialog.feature_combo.addItem('x', None)
        dialog._label_subtype = MagicMock()
        dialog._field_new_type = MagicMock()
        dialog.subtype_combo = MagicMock()
        with patch.object(self.main_dialog, 'fill_subtype_combo') as mock_fill:
            dialog._on_feature_changed(0)
        mock_fill.assert_not_called()

    def test_on_feature_changed_activity(self) -> None:
        dialog = self._make_raw()
        dialog.feature_combo = self.QComboBox()
        dialog.feature_combo.addItem('Activity', 'Activities')
        dialog.feature_combo.setCurrentIndex(0)
        dialog._label_subtype = MagicMock()
        dialog._field_new_type = MagicMock()
        dialog.subtype_combo = MagicMock()
        with (
            patch.object(self.main_dialog, 'ACTIVITY_KEY', 'Activities'),
            patch.object(self.main_dialog, 'fill_subtype_combo') as mock_fill,
        ):
            dialog._on_feature_changed(0)
        dialog._label_subtype.setVisible.assert_called_once_with(True)
        dialog._field_new_type.setVisible.assert_called_once_with(True)
        mock_fill.assert_called_once()

    def test_on_feature_changed_non_activity(self) -> None:
        dialog = self._make_raw()
        dialog.feature_combo = self.QComboBox()
        dialog.feature_combo.addItem('Road', 'road')
        dialog.feature_combo.setCurrentIndex(0)
        dialog._label_subtype = MagicMock()
        dialog._field_new_type = MagicMock()
        dialog.subtype_combo = MagicMock()
        with patch.object(self.main_dialog, 'fill_subtype_combo'):
            dialog._on_feature_changed(0)
        dialog._label_subtype.setVisible.assert_called_once_with(False)
        dialog._field_new_type.setVisible.assert_called_once_with(False)

    # ------------------------------------------------------------------
    # _save_new_type failure path
    # ------------------------------------------------------------------

    def test_save_new_type_shows_warning_on_failure(self) -> None:
        dialog = self._make_raw()
        dialog.feature_combo = self.QComboBox()
        dialog.feature_combo.addItem('Road', 'road')
        dialog.feature_combo.setCurrentIndex(0)
        dialog.subtype_combo = self.QComboBox()
        dialog.subtype_combo.addItem('Local', 'local')
        dialog._field_new_type = self.QLineEdit()
        with (
            patch.object(self.main_dialog, 'save_new_type_to_json', return_value=False),
            patch.object(self.main_dialog.QMessageBox, 'warning') as mock_warn,
        ):
            dialog._save_new_type()
        mock_warn.assert_called_once()

    # ------------------------------------------------------------------
    # _setup_map_canvas / disconnect_map_canvas
    # ------------------------------------------------------------------

    def test_setup_map_canvas_wires_signals(self) -> None:
        dialog = self._make_raw()
        canvas = dialog.iface.mapCanvas()
        dialog._setup_map_canvas()
        canvas.setContextMenuPolicy.assert_called_once_with(
            self.main_dialog.Qt.ContextMenuPolicy.CustomContextMenu
        )
        canvas.customContextMenuRequested.connect.assert_called_once_with(
            dialog.on_edition_release
        )
        canvas.mapToolSet.connect.assert_called_once_with(dialog._on_map_tool_changed)

    def test_disconnect_map_canvas(self) -> None:
        dialog = self._make_raw()
        canvas = dialog.iface.mapCanvas()
        dialog.disconnect_map_canvas()
        canvas.customContextMenuRequested.disconnect.assert_called_once_with(
            dialog.on_edition_release
        )
        canvas.mapToolSet.disconnect.assert_called_once_with(
            dialog._on_map_tool_changed
        )

    def test_disconnect_map_canvas_suppresses_errors(self) -> None:
        dialog = self._make_raw()
        canvas = dialog.iface.mapCanvas()
        canvas.customContextMenuRequested.disconnect.side_effect = TypeError
        canvas.mapToolSet.disconnect.side_effect = RuntimeError
        self.assertIsNone(dialog.disconnect_map_canvas())

    # ------------------------------------------------------------------
    # _connect_signals
    # ------------------------------------------------------------------

    def _wire_connect_signals_widgets(self, dialog) -> None:
        names = [
            '_btn_sign_in',
            '_btn_add_user',
            '_btn_restore_db',
            '_btn_save_add',
            '_btn_cancel_add',
            '_btn_gear',
            '_btn_draw',
            '_btn_select',
            '_btn_edit',
            '_btn_measure',
            '_combo_layer_selector',
            'wilaya_list',
            '_combo_org_cat',
            '_combo_activity_cat',
            'feature_combo',
            '_combo_action',
            '_combo_theme',
            '_combo_locale',
            '_btn_save_zone',
            '_btn_save_road',
            '_btn_save_org',
            '_btn_save_city',
            '_btn_save_num',
            '_btn_save_pan',
            '_btn_save_action',
            '_btn_save_new_type',
            '_btn_list_roads',
            '_btn_list_orgs',
            '_btn_list_cities',
            '_btn_list_nums',
            '_btn_list_panels',
            '_btn_select_road_ref',
            '_btn_select_panel_ref',
        ]
        for name in names:
            setattr(dialog, name, MagicMock())

    def test_connect_signals_wires_login(self) -> None:
        dialog = self._make_raw()
        self._wire_connect_signals_widgets(dialog)
        dialog._connect_signals()
        dialog._btn_sign_in.clicked.connect.assert_called_once()

    def test_connect_signals_wires_all_buttons(self) -> None:
        dialog = self._make_raw()
        self._wire_connect_signals_widgets(dialog)
        dialog._connect_signals()
        for name in (
            '_btn_add_user',
            '_btn_restore_db',
            '_btn_save_add',
            '_btn_cancel_add',
            '_btn_gear',
            '_btn_draw',
            '_btn_select',
            '_btn_edit',
            '_btn_measure',
            '_btn_save_zone',
            '_btn_save_road',
            '_btn_save_org',
            '_btn_save_city',
            '_btn_save_num',
            '_btn_save_pan',
            '_btn_save_action',
            '_btn_save_new_type',
            '_btn_list_roads',
            '_btn_list_orgs',
            '_btn_list_cities',
            '_btn_list_nums',
            '_btn_list_panels',
            '_btn_select_road_ref',
            '_btn_select_panel_ref',
        ):
            getattr(dialog, name).clicked.connect.assert_called_once()

    def test_connect_signals_wires_combos(self) -> None:
        dialog = self._make_raw()
        self._wire_connect_signals_widgets(dialog)
        dialog._connect_signals()
        for name in (
            '_combo_layer_selector',
            'wilaya_list',
            '_combo_org_cat',
            '_combo_activity_cat',
            'feature_combo',
            '_combo_action',
            '_combo_theme',
            '_combo_locale',
        ):
            getattr(dialog, name).currentIndexChanged.connect.assert_called_once()


if __name__ == '__main__':
    unittest.main()
