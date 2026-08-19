"""Tests for gui.pages.login_page — build_login_page."""

import importlib
import sys
import types
import unittest
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


def _load_login_module():
    setup_gui_mocks()
    _ensure_packages()

    qt = sys.modules['qgis.PyQt.QtWidgets']
    widget_names = (
        'QLabel',
        'QPushButton',
        'QLineEdit',
        'QComboBox',
        'QFormLayout',
        'QHBoxLayout',
        'QVBoxLayout',
        'QWidget',
    )
    orig_qt = {k: getattr(qt, k) for k in widget_names}

    saved_helpers = sys.modules.get('plans_adressage.gui.dialog_helpers')
    hpkg = sys.modules.get('plans_adressage.gui')
    hpkg_dh = getattr(hpkg, 'dialog_helpers', None) if hpkg else None

    helpers_mod = types.ModuleType('plans_adressage.gui.dialog_helpers')
    helpers_mod.__package__ = 'plans_adressage.gui'
    helpers_mod.make_section_frame = lambda max_width=None: MagicMock()
    helpers_mod.add_form_row = MagicMock(return_value=MagicMock())
    sys.modules['plans_adressage.gui.dialog_helpers'] = helpers_mod
    if hpkg:
        hpkg.dialog_helpers = helpers_mod

    for k in widget_names:
        setattr(qt, k, MagicMock(side_effect=lambda *a, **kw: MagicMock()))
    try:
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.pages.login_page',
            'gui/pages/login_page.py',
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


class TestLoginPageModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_login_module()

    def test_module_has_build_login_page(self):
        self.assertTrue(hasattr(self.mod, 'build_login_page'))

    def test_build_login_page_is_callable(self):
        self.assertTrue(callable(self.mod.build_login_page))


class TestBuildLoginPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = _load_login_module()

    def _make_dialog(self) -> Any:
        dialog = type('MockDialog', (), {})()
        dialog._page_stack = MagicMock()
        dialog._held_widgets: list = []
        return dialog

    def test_adds_page_to_page_stack(self):
        dialog = self._make_dialog()
        self.mod.build_login_page(dialog)
        dialog._page_stack.addWidget.assert_called_once()

    def test_appends_page_to_held_widgets(self):
        dialog = self._make_dialog()
        self.mod.build_login_page(dialog)
        self.assertEqual(len(dialog._held_widgets), 1)

    def test_creates_username_field(self):
        dialog = self._make_dialog()
        self.mod.build_login_page(dialog)
        self.assertIsNotNone(dialog._field_username)
        dialog._field_username.setObjectName.assert_called_with('username')

    def test_creates_password_field(self):
        dialog = self._make_dialog()
        self.mod.build_login_page(dialog)
        self.assertIsNotNone(dialog._field_password)
        dialog._field_password.setObjectName.assert_called_with('password')

    def test_password_echo_mode_set(self):
        dialog = self._make_dialog()
        self.mod.build_login_page(dialog)
        dialog._field_password.setEchoMode.assert_called_once()

    def test_creates_map_options_combo(self):
        dialog = self._make_dialog()
        self.mod.build_login_page(dialog)
        self.assertIsNotNone(dialog._combo_map_options)
        dialog._combo_map_options.setObjectName.assert_called_with('map_options')

    def test_creates_sign_in_button(self):
        dialog = self._make_dialog()
        self.mod.build_login_page(dialog)
        self.assertIsNotNone(dialog._btn_sign_in)
        dialog._btn_sign_in.setObjectName.assert_called_with('sign_in_user')

    def test_creates_add_user_button(self):
        dialog = self._make_dialog()
        self.mod.build_login_page(dialog)
        self.assertIsNotNone(dialog._btn_add_user)
        dialog._btn_add_user.setObjectName.assert_called_with('add_u')

    def test_creates_restore_db_button(self):
        dialog = self._make_dialog()
        self.mod.build_login_page(dialog)
        self.assertIsNotNone(dialog._btn_restore_db)
        dialog._btn_restore_db.setObjectName.assert_called_with('restore_db')

    def test_all_expected_attributes_set(self):
        dialog = self._make_dialog()
        self.mod.build_login_page(dialog)
        for attr in (
            '_field_username',
            '_field_password',
            '_combo_map_options',
            '_btn_sign_in',
            '_btn_add_user',
            '_btn_restore_db',
        ):
            self.assertTrue(hasattr(dialog, attr), f'Missing attribute: {attr}')


if __name__ == '__main__':
    unittest.main()
