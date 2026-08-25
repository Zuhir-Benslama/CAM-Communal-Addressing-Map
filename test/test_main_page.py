"""Tests for gui.pages.main_page — build_main_page, _build_form_page, _ICON_DIR."""

import importlib
import sys
import types
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

from .helpers import setup_gui_mocks


def _ensure_packages():
    for name, path in [
        ('plans_adressage.gui', ['gui']),
        ('plans_adressage.gui.pages', ['gui/pages']),
    ]:
        if name not in sys.modules:
            mod = types.ModuleType(name)
            mod.__path__ = path
            mod.__package__ = name
            sys.modules[name] = mod
        else:
            m = sys.modules[name]
            if not hasattr(m, '__path__'):
                m.__path__ = path
            if not hasattr(m, '__package__'):
                m.__package__ = name


def _load_main_module():
    setup_gui_mocks()
    _ensure_packages()

    qt = sys.modules['qgis.PyQt.QtWidgets']
    widget_names = (
        'QLabel',
        'QPushButton',
        'QComboBox',
        'QStackedWidget',
        'QVBoxLayout',
        'QHBoxLayout',
        'QWidget',
    )
    orig_qt = {k: getattr(qt, k) for k in widget_names}

    saved_helpers = sys.modules.get('plans_adressage.gui.dialog_helpers')
    saved_form_pages = sys.modules.get('plans_adressage.gui.pages.form_pages')
    saved_settings = sys.modules.get('plans_adressage.gui.pages.settings_page')
    hpkg = sys.modules.get('plans_adressage.gui')
    hpkg_dh = getattr(hpkg, 'dialog_helpers', None) if hpkg else None
    ppkg = sys.modules.get('plans_adressage.gui.pages')
    ppkg_fp = getattr(ppkg, 'form_pages', None) if ppkg else None
    ppkg_sp = getattr(ppkg, 'settings_page', None) if ppkg else None

    dh_mod = types.ModuleType('plans_adressage.gui.dialog_helpers')
    dh_mod.__package__ = 'plans_adressage.gui'
    dh_mod.make_section_frame = lambda max_width=None: MagicMock()
    dh_mod.add_form_row = MagicMock(return_value=MagicMock())
    sys.modules['plans_adressage.gui.dialog_helpers'] = dh_mod
    if hpkg:
        hpkg.dialog_helpers = dh_mod

    fp_mod = types.ModuleType('plans_adressage.gui.pages.form_pages')
    fp_mod.__package__ = 'plans_adressage.gui.pages'
    for fn in (
        'build_zone_form',
        'build_road_form',
        'build_org_form',
        'build_city_form',
        'build_num_form',
        'build_pan_form',
    ):
        setattr(fp_mod, fn, MagicMock())
    sys.modules['plans_adressage.gui.pages.form_pages'] = fp_mod
    if ppkg:
        ppkg.form_pages = fp_mod

    sp_mod = types.ModuleType('plans_adressage.gui.pages.settings_page')
    sp_mod.__package__ = 'plans_adressage.gui.pages'
    sp_mod.build_settings_page = MagicMock()
    sys.modules['plans_adressage.gui.pages.settings_page'] = sp_mod
    if ppkg:
        ppkg.settings_page = sp_mod

    for k in widget_names:
        setattr(qt, k, MagicMock(side_effect=lambda *a, **kw: MagicMock()))
    try:
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.pages.main_page',
            'gui/pages/main_page.py',
        )
        mod = importlib.util.module_from_spec(spec)
        mod.__package__ = 'plans_adressage.gui.pages'
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod
    finally:
        for k, v in orig_qt.items():
            setattr(qt, k, v)
        if saved_helpers is not None:
            sys.modules['plans_adressage.gui.dialog_helpers'] = saved_helpers
            if hpkg:
                hpkg.dialog_helpers = saved_helpers
        else:
            sys.modules.pop('plans_adressage.gui.dialog_helpers', None)
            if hpkg and hpkg_dh is not None:
                hpkg.dialog_helpers = hpkg_dh
        if saved_form_pages is not None:
            sys.modules['plans_adressage.gui.pages.form_pages'] = saved_form_pages
            if ppkg:
                ppkg.form_pages = saved_form_pages
        else:
            sys.modules.pop('plans_adressage.gui.pages.form_pages', None)
            if ppkg and ppkg_fp is not None:
                ppkg.form_pages = ppkg_fp
        if saved_settings is not None:
            sys.modules['plans_adressage.gui.pages.settings_page'] = saved_settings
            if ppkg:
                ppkg.settings_page = saved_settings
        else:
            sys.modules.pop('plans_adressage.gui.pages.settings_page', None)
            if ppkg and ppkg_sp is not None:
                ppkg.settings_page = ppkg_sp


class TestMainPageModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_main_module()

    def test_module_has_build_main_page(self):
        self.assertTrue(hasattr(self.mod, 'build_main_page'))

    def test_module_has_build_form_page(self):
        self.assertTrue(hasattr(self.mod, '_build_form_page'))

    def test_module_has_icon_dir(self):
        self.assertTrue(hasattr(self.mod, '_ICON_DIR'))

    def test_icon_dir_points_to_resources(self):
        icon_path = Path(self.mod._ICON_DIR)
        self.assertEqual(icon_path.name, 'resources')
        self.assertTrue(icon_path.is_absolute())

    def test_icon_dir_is_sibling_of_gui(self):
        icon_path = Path(self.mod._ICON_DIR)
        self.assertTrue(icon_path.parent.exists())


class TestBuildMainPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_main_module()

    def _make_dialog(self) -> Any:
        dialog = type('MockDialog', (), {})()
        dialog._page_stack = MagicMock()
        dialog._held_widgets = []
        dialog._main_stack = MagicMock()
        return dialog

    def test_adds_page_to_page_stack(self):
        dialog = self._make_dialog()
        self.mod.build_main_page(dialog)
        dialog._page_stack.addWidget.assert_called_once()

    def test_appends_widgets_to_held(self):
        dialog = self._make_dialog()
        self.mod.build_main_page(dialog)
        self.assertGreaterEqual(len(dialog._held_widgets), 2)

    def test_creates_label_username(self):
        dialog = self._make_dialog()
        self.mod.build_main_page(dialog)
        self.assertIsNotNone(dialog._label_username)
        dialog._label_username.setObjectName.assert_called_with('label_username')

    def test_creates_gear_button(self):
        dialog = self._make_dialog()
        self.mod.build_main_page(dialog)
        self.assertIsNotNone(dialog._btn_gear)
        dialog._btn_gear.setObjectName.assert_called_with('gearBtn')

    def test_main_stack_set_current_index(self):
        dialog = self._make_dialog()
        self.mod.build_main_page(dialog)
        dialog._main_stack.setCurrentIndex.assert_called_with(0)


class TestBuildFormPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_main_module()

    def _make_dialog(self) -> Any:
        dialog = type('MockDialog', (), {})()
        dialog._main_stack = MagicMock()
        dialog._held_widgets = []
        return dialog

    def test_creates_combo_layer_selector(self):
        dialog = self._make_dialog()
        self.mod._build_form_page(dialog)
        self.assertIsNotNone(dialog._combo_layer_selector)
        dialog._combo_layer_selector.setObjectName.assert_called_with('layer_selector')

    def test_creates_draw_button(self):
        dialog = self._make_dialog()
        self.mod._build_form_page(dialog)
        self.assertIsNotNone(dialog._btn_draw)
        dialog._btn_draw.setObjectName.assert_called_with('drawBtn')

    def test_creates_select_button(self):
        dialog = self._make_dialog()
        self.mod._build_form_page(dialog)
        self.assertIsNotNone(dialog._btn_select)
        dialog._btn_select.setObjectName.assert_called_with('selectBtn')

    def test_creates_edit_button(self):
        dialog = self._make_dialog()
        self.mod._build_form_page(dialog)
        self.assertIsNotNone(dialog._btn_edit)
        dialog._btn_edit.setObjectName.assert_called_with('editBtn')

    def test_creates_measure_button(self):
        dialog = self._make_dialog()
        self.mod._build_form_page(dialog)
        self.assertIsNotNone(dialog._btn_measure)
        dialog._btn_measure.setObjectName.assert_called_with('mesure_dist')

    def test_creates_form_stack(self):
        dialog = self._make_dialog()
        self.mod._build_form_page(dialog)
        self.assertIsNotNone(dialog._form_stack)

    def test_adds_page_to_main_stack(self):
        dialog = self._make_dialog()
        self.mod._build_form_page(dialog)
        dialog._main_stack.addWidget.assert_called_once()

    def test_appends_widgets_to_held(self):
        dialog = self._make_dialog()
        self.mod._build_form_page(dialog)
        self.assertGreaterEqual(len(dialog._held_widgets), 4)

    def test_draw_button_tooltip(self):
        dialog = self._make_dialog()
        self.mod._build_form_page(dialog)
        dialog._btn_draw.setToolTip.assert_called_with('Draw')

    def test_select_button_tooltip(self):
        dialog = self._make_dialog()
        self.mod._build_form_page(dialog)
        dialog._btn_select.setToolTip.assert_called_with('Select')

    def test_edit_button_tooltip(self):
        dialog = self._make_dialog()
        self.mod._build_form_page(dialog)
        dialog._btn_edit.setToolTip.assert_called_with('Edit')

    def test_measure_button_tooltip(self):
        dialog = self._make_dialog()
        self.mod._build_form_page(dialog)
        dialog._btn_measure.setToolTip.assert_called_with('Measure Distance')


if __name__ == '__main__':
    unittest.main()
