"""Tests for gui.dialog_state — init_theme_locale and on_locale_changed."""

import importlib
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

from test.helpers import setup_gui_mocks


def _ensure_constants():
    key = 'plans_adressage.constants'
    mod = sys.modules.get(key)
    if mod is None or not isinstance(getattr(mod, 'AVAILABLE_LOCALES', None), list):
        if mod is None:
            mod = types.ModuleType(key)
        mod.AVAILABLE_LOCALES = [
            ('ar', 'Arabic'),
            ('fr', 'Français'),
            ('en', 'English'),
        ]
        mod.DEFAULT_THEME = 'dark'
        mod.SETTINGS_APP = 'CAM'
        mod.SETTINGS_ORG = 'CAM'
        mod.SETTINGS_KEY_LOCALE = 'locale'
        mod.SETTINGS_KEY_THEME = 'theme'
        mod.THEME_DARK = 'dark'
        mod.THEME_LIGHT = 'light'
        mod.get_theme_qss = lambda t: f'/* {t} */'
        mod.current_theme = lambda: 'dark'
        mod.current_locale = lambda: 'ar'
        sys.modules[key] = mod


def _ensure_widget_texts():
    key = 'plans_adressage.scripts.widget_texts'
    if key not in sys.modules:
        mod = types.ModuleType(key)
        mod.__package__ = 'plans_adressage.scripts'
        mod.get_string = lambda s, loc=None: s if isinstance(s, str) else 'test'
        mod.apply_widget_texts = lambda w, loc: None
        mod.clear_i18n_cache = lambda: None
        sys.modules[key] = mod
    else:
        m = sys.modules[key]
        if not hasattr(m, 'clear_i18n_cache'):
            m.clear_i18n_cache = lambda: None
        if not hasattr(m, 'get_string'):
            m.get_string = lambda s, loc=None: s if isinstance(s, str) else 'test'
        if not hasattr(m, 'apply_widget_texts'):
            m.apply_widget_texts = lambda w, loc: None


def _ensure_ui_fillers():
    key = 'plans_adressage.gui.ui_fillers'
    if key not in sys.modules:
        mod = types.ModuleType(key)
        mod.__package__ = 'plans_adressage.gui'
        for name in (
            'fill_org_category',
            'fill_road_type',
            'fill_road_reference',
            'fill_panel_reference',
            'fill_activity_category',
            'fill_numbering_state',
            'fill_mounting_status',
            'fill_subdivision_type',
            'fill_zone_type',
            'fill_wilayas_list',
            'fill_feature_combo',
            'fill_paper',
            'fill_org_type',
            'fill_activity_type',
        ):
            setattr(mod, name, MagicMock())
        sys.modules[key] = mod


class TestDialogStateModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_gui_mocks()
        _ensure_constants()
        _ensure_widget_texts()
        _ensure_ui_fillers()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.dialog_state',
            'gui/dialog_state.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.dialog_state'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def test_arabic_action_names_not_empty(self):
        self.assertTrue(len(self.mod.ARABIC_ACTION_NAMES) > 0)

    def test_arabic_theme_names_not_empty(self):
        self.assertTrue(len(self.mod.ARABIC_THEME_NAMES) > 0)

    def test_locale_labels_not_empty(self):
        self.assertTrue(len(self.mod.LOCALE_LABELS) > 0)

    def test_layer_translations_not_empty(self):
        self.assertTrue(len(self.mod.LAYER_TRANSLATIONS) > 0)

    def test_apply_theme(self):
        dialog = MagicMock()
        self.mod.apply_theme(dialog)
        dialog.setStyleSheet.assert_called()


class TestInitThemeLocale(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_gui_mocks()
        _ensure_constants()
        _ensure_widget_texts()
        _ensure_ui_fillers()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.dialog_state',
            'gui/dialog_state.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.dialog_state'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def _make_dialog(self, locale='ar'):
        dialog = MagicMock()
        dialog._tr_locale = locale
        dialog._combo_theme = MagicMock()
        dialog._combo_theme.findData.return_value = 0
        dialog._combo_theme.currentData.return_value = 'dark'
        dialog._combo_locale = MagicMock()
        dialog._combo_locale.findData.return_value = 0
        return dialog

    def test_adds_dark_and_light_theme_items(self):
        with patch.object(self.mod, 'QSettings') as MockSettings:
            settings_inst = MagicMock()
            settings_inst.value.return_value = 'dark'
            MockSettings.return_value = settings_inst

            dialog = self._make_dialog()
            self.mod.init_theme_locale(dialog)

            self.assertEqual(dialog._combo_theme.addItem.call_count, 2)

    def test_sets_saved_theme_index(self):
        with patch.object(self.mod, 'QSettings') as MockSettings:
            settings_inst = MagicMock()
            settings_inst.value.return_value = 'dark'
            MockSettings.return_value = settings_inst

            dialog = self._make_dialog()
            self.mod.init_theme_locale(dialog)

            dialog._combo_theme.setCurrentIndex.assert_called_once()

    def test_sets_current_theme_from_combo(self):
        with patch.object(self.mod, 'QSettings') as MockSettings:
            settings_inst = MagicMock()
            settings_inst.value.return_value = 'dark'
            MockSettings.return_value = settings_inst

            dialog = self._make_dialog()
            self.mod.init_theme_locale(dialog)

            self.assertEqual(dialog._current_theme, 'dark')

    def test_adds_locale_items(self):
        with patch.object(self.mod, 'QSettings') as MockSettings:
            settings_inst = MagicMock()
            settings_inst.value.return_value = ''
            MockSettings.return_value = settings_inst

            dialog = self._make_dialog()
            self.mod.init_theme_locale(dialog)

            self.assertEqual(dialog._combo_locale.addItem.call_count, 3)

    def test_sets_saved_locale_index(self):
        with patch.object(self.mod, 'QSettings') as MockSettings:
            settings_inst = MagicMock()
            settings_inst.value.return_value = 'fr'
            MockSettings.return_value = settings_inst

            dialog = self._make_dialog()
            dialog._combo_locale.findData.return_value = 1
            self.mod.init_theme_locale(dialog)

            dialog._combo_locale.setCurrentIndex.assert_called_with(1)

    def test_no_locale_restore_when_empty(self):
        with patch.object(self.mod, 'QSettings') as MockSettings:
            settings_inst = MagicMock()
            settings_inst.value.return_value = ''
            MockSettings.return_value = settings_inst

            dialog = self._make_dialog()
            self.mod.init_theme_locale(dialog)

            dialog._combo_locale.setCurrentIndex.assert_not_called()

    def test_arabic_theme_value_normalized(self):
        with patch.object(self.mod, 'QSettings') as MockSettings:
            settings_inst = MagicMock()
            settings_inst.value.return_value = 'فاتح'
            MockSettings.return_value = settings_inst

            dialog = self._make_dialog()
            self.mod.init_theme_locale(dialog)

            dialog._combo_theme.findData.assert_called_with('light')

    def test_saves_normalized_theme_to_settings(self):
        with patch.object(self.mod, 'QSettings') as MockSettings:
            settings_inst = MagicMock()
            settings_inst.value.return_value = 'فاتح'
            MockSettings.return_value = settings_inst

            dialog = self._make_dialog()
            self.mod.init_theme_locale(dialog)

            settings_inst.setValue.assert_any_call('theme', 'light')


class TestOnLocaleChanged(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_gui_mocks()
        _ensure_constants()
        _ensure_widget_texts()
        _ensure_ui_fillers()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.dialog_state',
            'gui/dialog_state.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.dialog_state'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def _make_dialog(self, locale='fr'):
        dialog = MagicMock()
        dialog._tr_locale = 'ar'
        dialog._combo_locale = MagicMock()
        dialog._combo_locale.currentData.return_value = locale
        dialog._combo_layer_selector = MagicMock()
        dialog._combo_layer_selector.currentIndex.return_value = 0
        dialog._combo_theme = MagicMock()
        dialog._combo_theme.count.return_value = 2
        dialog._combo_theme.itemData.side_effect = lambda i: ['dark', 'light'][i]
        dialog._combo_action = MagicMock()
        dialog._combo_action.count.return_value = 0
        dialog._btn_draw = MagicMock()
        dialog._btn_select = MagicMock()
        dialog._btn_edit = MagicMock()
        dialog._btn_measure = MagicMock()
        dialog.LAYER_INDEX_MAP = ['Zones', 'Roads']
        return dialog

    def test_returns_early_when_code_is_empty(self):
        with (
            patch.object(self.mod, 'QSettings') as MockSettings,
            patch.object(self.mod, 'QApplication'),
            patch.object(self.mod, 'translate_internal_combos') as mock_translate,
        ):
            dialog = self._make_dialog()
            dialog._combo_locale.currentData.return_value = ''
            self.mod.on_locale_changed(dialog, 0)
            MockSettings.return_value.setValue.assert_not_called()
            mock_translate.assert_not_called()

    def test_saves_locale_to_settings(self):
        with (
            patch.object(self.mod, 'QSettings') as MockSettings,
            patch.object(self.mod, 'QApplication'),
            patch.object(self.mod, 'translate_internal_combos'),
        ):
            dialog = self._make_dialog(locale='fr')
            self.mod.on_locale_changed(dialog, 1)
            MockSettings.return_value.setValue.assert_called_with('locale', 'fr')

    def test_updates_tr_locale(self):
        with (
            patch.object(self.mod, 'QSettings'),
            patch.object(self.mod, 'QApplication'),
            patch.object(self.mod, 'translate_internal_combos'),
        ):
            dialog = self._make_dialog(locale='fr')
            self.mod.on_locale_changed(dialog, 1)
            self.assertEqual(dialog._tr_locale, 'fr')

    def test_clears_button_texts(self):
        with (
            patch.object(self.mod, 'QSettings'),
            patch.object(self.mod, 'QApplication'),
            patch.object(self.mod, 'translate_internal_combos'),
        ):
            dialog = self._make_dialog(locale='en')
            self.mod.on_locale_changed(dialog, 2)
            dialog._btn_draw.setText.assert_called_with('')
            dialog._btn_select.setText.assert_called_with('')
            dialog._btn_edit.setText.assert_called_with('')
            dialog._btn_measure.setText.assert_called_with('')

    def test_calls_translate_internal_combos(self):
        with (
            patch.object(self.mod, 'QSettings'),
            patch.object(self.mod, 'QApplication'),
            patch.object(self.mod, 'translate_internal_combos') as mock_translate,
        ):
            dialog = self._make_dialog(locale='fr')
            self.mod.on_locale_changed(dialog, 1)
            mock_translate.assert_called_once_with(dialog)

    def test_sets_rtl_for_arabic(self):
        with (
            patch.object(self.mod, 'QSettings'),
            patch.object(self.mod, 'QApplication') as MockQApp,
            patch.object(self.mod, 'translate_internal_combos'),
        ):
            dialog = self._make_dialog(locale='ar')
            self.mod.on_locale_changed(dialog, 0)
            MockQApp.setLayoutDirection.assert_called_with(
                self.mod.Qt.LayoutDirection.RightToLeft
            )

    def test_sets_ltr_for_non_arabic(self):
        with (
            patch.object(self.mod, 'QSettings'),
            patch.object(self.mod, 'QApplication') as MockQApp,
            patch.object(self.mod, 'translate_internal_combos'),
        ):
            dialog = self._make_dialog(locale='fr')
            self.mod.on_locale_changed(dialog, 1)
            MockQApp.setLayoutDirection.assert_called_with(
                self.mod.Qt.LayoutDirection.LeftToRight
            )

    def test_calls_fill_wilayas_list(self):
        with (
            patch.object(self.mod, 'QSettings'),
            patch.object(self.mod, 'QApplication'),
            patch.object(self.mod, 'translate_internal_combos'),
        ):
            dialog = self._make_dialog(locale='fr')
            self.mod.on_locale_changed(dialog, 1)
            self.mod.fill_wilayas_list.assert_called_with(dialog.wilaya_list)


class TestOnActionChanged(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_gui_mocks()
        _ensure_constants()
        _ensure_widget_texts()
        _ensure_ui_fillers()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.dialog_state',
            'gui/dialog_state.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.dialog_state'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def test_panels_map_shows_paper(self):
        dialog = MagicMock()
        dialog._combo_action.currentData.return_value = 'panels_map'
        self.mod.on_action_changed(dialog, 0)
        dialog._combo_paper.setVisible.assert_called_with(True)
        dialog.panel_chart.assert_called_once()

    def test_num_map_shows_paper(self):
        dialog = MagicMock()
        dialog._combo_action.currentData.return_value = 'num_map'
        self.mod.on_action_changed(dialog, 0)
        dialog._combo_paper.setVisible.assert_called_with(True)
        dialog.numbering_chart.assert_called_once()

    def test_report_hides_paper(self):
        dialog = MagicMock()
        dialog._combo_action.currentData.return_value = 'report'
        self.mod.on_action_changed(dialog, 0)
        dialog._combo_paper.setVisible.assert_called_with(False)


class TestOnSaveAction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_gui_mocks()
        _ensure_constants()
        _ensure_widget_texts()
        _ensure_ui_fillers()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.dialog_state',
            'gui/dialog_state.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.dialog_state'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def test_returns_early_when_no_directory(self):
        with patch.object(self.mod, 'QFileDialog') as MockFileDialog:
            MockFileDialog.getExistingDirectory.return_value = ''
            dialog = MagicMock()
            self.mod.on_save_action(dialog)
            dialog.generate_report.assert_not_called()

    def test_report_action(self):
        with patch.object(self.mod, 'QFileDialog') as MockFileDialog:
            MockFileDialog.getExistingDirectory.return_value = '/tmp/out'
            dialog = MagicMock()
            dialog._combo_action.currentData.return_value = 'report'
            self.mod.on_save_action(dialog)
            self.assertEqual(dialog._output_dir, '/tmp/out')
            dialog.generate_report.assert_called_once()

    def test_order_action(self):
        with patch.object(self.mod, 'QFileDialog') as MockFileDialog:
            MockFileDialog.getExistingDirectory.return_value = '/tmp/out'
            dialog = MagicMock()
            dialog._combo_action.currentData.return_value = 'order'
            self.mod.on_save_action(dialog)
            dialog.purchase_order.assert_called_once()

    def test_panels_map_action(self):
        with patch.object(self.mod, 'QFileDialog') as MockFileDialog:
            MockFileDialog.getExistingDirectory.return_value = '/tmp/out'
            dialog = MagicMock()
            dialog._combo_action.currentData.return_value = 'panels_map'
            self.mod.on_save_action(dialog)
            dialog.panel_chart.assert_called_once()
            dialog.export_to_image.assert_called_once()

    def test_num_map_action(self):
        with patch.object(self.mod, 'QFileDialog') as MockFileDialog:
            MockFileDialog.getExistingDirectory.return_value = '/tmp/out'
            dialog = MagicMock()
            dialog._combo_action.currentData.return_value = 'num_map'
            self.mod.on_save_action(dialog)
            dialog.numbering_chart.assert_called_once()
            dialog.export_to_image.assert_called_once()

    def test_backup_action(self):
        with patch.object(self.mod, 'QFileDialog') as MockFileDialog:
            MockFileDialog.getExistingDirectory.return_value = '/tmp/out'
            dialog = MagicMock()
            dialog._combo_action.currentData.return_value = 'backup'
            self.mod.on_save_action(dialog)
            dialog.backup.assert_called_once()


if __name__ == '__main__':
    unittest.main()
