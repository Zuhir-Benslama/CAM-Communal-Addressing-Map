"""Tests for gui/main_dialog.py — MainDialog."""
import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from .helpers import setup_gui_mocks, make_mock_iface, get_qapp


def _stub_widgets(target, names):
    """Set MagicMock attributes on the target unconditionally."""
    for name in names:
        setattr(target, name, MagicMock())


@unittest.skipIf(get_qapp() is None, 'PyQt5 not available')
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
        return dialog

    def test_current_layer_name_returns_first_by_default(self):
        dialog = self._make_raw()
        _stub_widgets(dialog, ['layer_selector'])
        dialog.layer_selector.currentIndex.return_value = 0
        self.assertEqual(dialog._current_layer_name(), "Zones")

    def test_current_layer_name_returns_by_index(self):
        dialog = self._make_raw()
        _stub_widgets(dialog, ['layer_selector'])
        for idx, expected in enumerate(
            ["Zones", "Roads", "Facilities",
             "Subdivisions", "Numbering", "Panels"]):
            dialog.layer_selector.currentIndex.return_value = idx
            self.assertEqual(dialog._current_layer_name(), expected)

    def test_current_layer_name_fallback_on_bad_index(self):
        dialog = self._make_raw()
        _stub_widgets(dialog, ['layer_selector'])
        dialog.layer_selector.currentIndex.return_value = 99
        self.assertEqual(dialog._current_layer_name(), "Zones")

    def test_tr_delegates_to_get_string(self):
        dialog = self._make_raw()
        result = dialog._tr("Hello")
        self.assertEqual(result, "Hello")

    def test_translate_internal_combos_sets_item_texts(self):
        dialog = self._make_raw()
        _stub_widgets(dialog, ['layer_selector', '_theme_combo'])
        dialog._theme_combo.count.return_value = 2
        dialog._theme_combo.itemData.side_effect = ['dark', 'light']
        dialog._translate_internal_combos()
        self.assertEqual(dialog.layer_selector.setItemText.call_count, 6)
        self.assertEqual(dialog._theme_combo.setItemText.call_count, 2)

    def test_init_state_resets_tool_state(self):
        dialog = self._make_raw()
        dialog.dateEdit = MagicMock()
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
        dialog.dateEdit.setDate.assert_called_once()

    def test_apply_theme_sets_stylesheet(self):
        dialog = self._make_raw()
        dialog.setStyleSheet = MagicMock()
        dialog.apply_theme()
        dialog.setStyleSheet.assert_called_once()

    def test_set_button_roles_assigns_primary(self):
        dialog = self._make_raw()
        btn = MagicMock()
        btn.objectName.return_value = 'submit_road'
        btn.minimumHeight.return_value = 0
        dialog.findChildren = MagicMock(return_value=[btn])
        dialog._set_button_roles()
        btn.setProperty.assert_any_call('role', 'primary')

    def test_set_button_roles_assigns_danger(self):
        dialog = self._make_raw()
        btn = MagicMock()
        btn.objectName.return_value = 'abort_uc'
        btn.minimumHeight.return_value = 0
        dialog.findChildren = MagicMock(return_value=[btn])
        dialog._set_button_roles()
        btn.setProperty.assert_any_call('role', 'danger')

    def test_set_button_roles_assigns_tool(self):
        dialog = self._make_raw()
        btn = MagicMock()
        btn.objectName.return_value = 'draw_btn'
        btn.minimumHeight.return_value = 0
        dialog.findChildren = MagicMock(return_value=[btn])
        dialog._set_button_roles()
        btn.setProperty.assert_any_call('role', 'tool')

    def test_set_button_roles_assigns_ghost(self):
        dialog = self._make_raw()
        btn = MagicMock()
        btn.objectName.return_value = 'unknown_btn'
        btn.minimumHeight.return_value = 0
        dialog.findChildren = MagicMock(return_value=[btn])
        dialog._set_button_roles()
        btn.setProperty.assert_any_call('role', 'ghost')

    def test_apply_ui_polish_sets_properties(self):
        dialog = self._make_raw()
        for m in ('setObjectName', 'setSizeGripEnabled', 'setMinimumSize',
                  'setMaximumSize', 'width', 'resize'):
            setattr(dialog, m, MagicMock())
        dialog.width.return_value = 640
        dialog.router = MagicMock()
        dialog.groupBox = MagicMock()
        dialog.menu = MagicMock()
        tab_bar_mock = MagicMock()
        dialog.menu.tabBar = MagicMock(return_value=tab_bar_mock)
        dialog._set_button_roles = MagicMock()
        _stub_widgets(dialog, ['toolbar_frame', 'frame_8', 'frame_9',
                                'label_feature', 'label_type',
                                'label_subtype'])
        dialog.findChildren = MagicMock(return_value=[])
        dialog._apply_ui_polish()
        dialog.setObjectName.assert_called_once_with('rnaMainDialog')
        dialog.setSizeGripEnabled.assert_called_once_with(True)
        dialog.setMinimumSize.assert_called_once_with(640, 680)
        dialog._set_button_roles.assert_called_once()

    def test_on_layer_changed_sets_form_stack(self):
        dialog = self._make_raw()
        _stub_widgets(dialog, ['form_stack', 'menu'])
        (dialog.menu.currentWidget.return_value
         .objectName.return_value) = 'tab_ops'
        dialog.menu.currentIndex.return_value = 2
        dialog.on_opt_selected = MagicMock()
        dialog._on_layer_changed(2)
        dialog.form_stack.setCurrentIndex.assert_called_once_with(2)
        dialog.on_opt_selected.assert_called_once_with(2)

    def test_on_layer_changed_skips_opt_for_non_ops_tab(self):
        dialog = self._make_raw()
        _stub_widgets(dialog, ['form_stack', 'menu'])
        (dialog.menu.currentWidget.return_value
         .objectName.return_value) = 'tab_settings'
        dialog.on_opt_selected = MagicMock()
        dialog._on_layer_changed(1)
        dialog.form_stack.setCurrentIndex.assert_called_once_with(1)
        dialog.on_opt_selected.assert_not_called()

    def test_on_layer_changed_handles_no_current_widget(self):
        dialog = self._make_raw()
        _stub_widgets(dialog, ['form_stack', 'menu'])
        dialog.menu.currentWidget.return_value = None
        dialog.on_opt_selected = MagicMock()
        dialog._on_layer_changed(0)
        dialog.form_stack.setCurrentIndex.assert_called_once_with(0)

    def test_setup_settings_ui_creates_theme_combo(self):
        dialog = self._make_raw()
        _stub_widgets(dialog, ['scrollAreaWidgetContents_2'])
        mock_combo = MagicMock()
        mock_combo.findData.return_value = -1
        with patch.object(self.mod, 'QSettings') as mock_qs, \
             patch.object(self.mod, 'QGroupBox', return_value=MagicMock()), \
             patch.object(self.mod, 'QComboBox', return_value=mock_combo), \
             patch.object(self.mod, 'QLabel', return_value=MagicMock()), \
             patch.object(self.mod, 'QVBoxLayout', return_value=MagicMock()), \
             patch.object(self.mod, 'QHBoxLayout', return_value=MagicMock()):
            mock_qs.return_value.value.return_value = ''
            dialog.setup_settings_ui()
        self.assertIsNotNone(dialog._theme_combo)
        self.assertIsNotNone(dialog._locale_combo)
        self.assertIsNotNone(dialog._settings_group)

    def test_on_theme_changed_saves_and_applies(self):
        dialog = self._make_raw()
        _stub_widgets(dialog, ['_theme_combo'])
        dialog._theme_combo.currentData.return_value = 'light'
        dialog.apply_theme = MagicMock()
        with patch.object(self.mod, 'QSettings') as mock_qs:
            dialog._on_theme_changed(1)
            self.assertEqual(dialog._current_theme, 'light')
            dialog.apply_theme.assert_called_once()
            mock_qs.return_value.setValue.assert_called_once()

    def test_on_locale_changed_skips_empty_code(self):
        dialog = self._make_raw()
        _stub_widgets(dialog, ['_locale_combo'])
        dialog._locale_combo.currentData.return_value = ''
        dialog._on_locale_changed(0)

    def test_on_locale_changed_updates_tr_locale(self):
        dialog = self._make_raw()
        _stub_widgets(dialog, ['_locale_combo', 'wilaya_list', 'type_road',
                                'zone_type', 'subd_type', 'mount_status',
                                'num_state', 'road_ref', 'panel_ref', 'paper',
                                'org_cat', 'activity_cat'])
        dialog._locale_combo.currentData.return_value = 'fr'
        dialog._translate_internal_combos = MagicMock()
        with patch.object(self.mod, 'QSettings'), \
             patch.object(self.mod, 'clear_i18n_cache'), \
             patch.object(self.mod, 'apply_widget_texts'), \
             patch.object(self.mod, 'fill_wilayas_list'), \
             patch.object(self.mod, 'fill_road_type'), \
             patch.object(self.mod, 'fill_zone_type'), \
             patch.object(self.mod, 'fill_subdivision_type'), \
             patch.object(self.mod, 'fill_mounting_status'), \
             patch.object(self.mod, 'fill_numbering_state'), \
             patch.object(self.mod, 'fill_road_reference'), \
             patch.object(self.mod, 'fill_panel_reference'), \
             patch.object(self.mod, 'fill_paper'), \
             patch.object(self.mod, 'fill_org_category'), \
             patch.object(self.mod, 'fill_activity_category'):
            dialog._on_locale_changed(1)
        self.assertEqual(dialog._tr_locale, 'fr')

    def test_on_locale_changed_sets_rtl_for_ar(self):
        dialog = self._make_raw()
        _stub_widgets(dialog,
                      ['_locale_combo', 'layer_selector', '_theme_combo',
                       'wilaya_list', 'type_road', 'zone_type',
                       'subd_type', 'mount_status', 'num_state',
                       'road_ref', 'panel_ref', 'paper',
                       'org_cat', 'activity_cat'])
        dialog._locale_combo.currentData.return_value = 'ar'
        with patch.object(
            self.mod.QApplication, 'setLayoutDirection',
        ) as mock_dir, \
             patch.object(self.mod, 'QSettings'), \
             patch.object(self.mod, 'clear_i18n_cache'), \
             patch.object(self.mod, 'apply_widget_texts'), \
             patch.object(self.mod, 'fill_wilayas_list'):
            dialog._on_locale_changed(1)
        mock_dir.assert_called_once_with(self.mod.Qt.RightToLeft)

    def test_on_locale_changed_sets_ltr_for_fr(self):
        dialog = self._make_raw()
        _stub_widgets(dialog,
                      ['_locale_combo', 'layer_selector', '_theme_combo',
                       'wilaya_list', 'type_road', 'zone_type',
                       'subd_type', 'mount_status', 'num_state',
                       'road_ref', 'panel_ref', 'paper',
                       'org_cat', 'activity_cat'])
        dialog._locale_combo.currentData.return_value = 'fr'
        with patch.object(
            self.mod.QApplication, 'setLayoutDirection',
        ) as mock_dir, \
             patch.object(self.mod, 'QSettings'), \
             patch.object(self.mod, 'clear_i18n_cache'), \
             patch.object(self.mod, 'apply_widget_texts'), \
             patch.object(self.mod, 'fill_wilayas_list'):
            dialog._on_locale_changed(1)
        mock_dir.assert_called_once_with(self.mod.Qt.LeftToRight)

    def test_on_locale_changed_refills_combos(self):
        dialog = self._make_raw()
        _stub_widgets(dialog, ['_locale_combo', 'wilaya_list', 'type_road',
                                'zone_type', 'subd_type', 'mount_status',
                                'num_state', 'road_ref', 'panel_ref', 'paper',
                                'org_cat', 'activity_cat'])
        dialog._locale_combo.currentData.return_value = 'fr'
        dialog._translate_internal_combos = MagicMock()
        with patch.object(self.mod, 'QSettings'), \
             patch.object(self.mod, 'clear_i18n_cache'), \
             patch.object(self.mod, 'apply_widget_texts'):
            with patch.object(self.mod, 'fill_wilayas_list') as m1, \
                 patch.object(self.mod, 'fill_road_type') as m2, \
                 patch.object(self.mod, 'fill_zone_type') as m3, \
                 patch.object(self.mod, 'fill_subdivision_type') as m4, \
                 patch.object(self.mod, 'fill_mounting_status') as m5, \
                 patch.object(self.mod, 'fill_numbering_state') as m6, \
                 patch.object(self.mod, 'fill_road_reference') as m7, \
                 patch.object(self.mod, 'fill_panel_reference') as m8, \
                 patch.object(self.mod, 'fill_paper') as m9, \
                 patch.object(self.mod, 'fill_org_category') as m10, \
                 patch.object(self.mod, 'fill_activity_category') as m11:
                dialog._on_locale_changed(1)
                m1.assert_called_once()
                m2.assert_called_once()
                m3.assert_called_once()
                m4.assert_called_once()
                m5.assert_called_once()
                m6.assert_called_once()
                m7.assert_called_once()
                m8.assert_called_once()
                m9.assert_called_once()
                m10.assert_called_once()
                m11.assert_called_once()


if __name__ == '__main__':
    unittest.main()
