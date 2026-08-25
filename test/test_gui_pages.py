"""Tests for gui/pages/ — page builder functions."""

import importlib
import sys
import types
import unittest
from typing import Any, ClassVar
from unittest.mock import MagicMock

from .helpers import get_qapp, _qt_widgets_module, setup_gui_mocks


def _ensure_package_hierarchy(qwidget_cls: Any, qvboxlayout_cls: Any) -> None:
    if 'plans_adressage' not in sys.modules:
        sys.modules['plans_adressage'] = MagicMock()
    if 'plans_adressage.gui' not in sys.modules:
        sys.modules['plans_adressage.gui'] = MagicMock()
    if 'plans_adressage.gui.pages' not in sys.modules:
        _pkg = types.ModuleType('plans_adressage.gui.pages')
        _pkg.__path__ = ['gui/pages']
        _pkg.__package__ = 'plans_adressage.gui.pages'
        sys.modules['plans_adressage.gui.pages'] = _pkg
    _dialog_helpers = MagicMock()

    def _make_section_frame(max_width=None):
        w = qwidget_cls()
        w.setObjectName('sectionFrame')
        qvboxlayout_cls(w)
        return w

    _dialog_helpers.make_section_frame = _make_section_frame
    _dialog_helpers.add_form_row = MagicMock(return_value=MagicMock())
    sys.modules['plans_adressage.gui.dialog_helpers'] = _dialog_helpers


def _load_page_module(module_path, package) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(  # type: ignore[attr-defined]
        f'{package}.{module_path.split("/")[-1].replace(".py", "")}',
        module_path,
    )
    mod = importlib.util.module_from_spec(spec)  # type: ignore[attr-defined]
    mod.__package__ = package
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestBuildAddUserPage(unittest.TestCase):
    """Test gui/pages/add_user_page.py — build_add_user_page."""

    qt: ClassVar[Any]
    app: ClassVar[Any]
    mod: ClassVar[Any]
    _prev_qtwidgets: ClassVar[Any]

    @classmethod
    def setUpClass(cls) -> None:
        setup_gui_mocks()
        cls.qt = _qt_widgets_module()
        if cls.qt is None:
            raise unittest.SkipTest('No real Qt widgets module available')
        cls.app = get_qapp()
        cls._prev_qtwidgets = sys.modules.get('qgis.PyQt.QtWidgets')
        sys.modules['qgis.PyQt.QtWidgets'] = cls.qt
        _ensure_package_hierarchy(cls.qt.QWidget, cls.qt.QVBoxLayout)
        cls.mod = _load_page_module(
            'gui/pages/add_user_page.py',
            'plans_adressage.gui.pages',
        )

    @classmethod
    def tearDownClass(cls) -> None:
        if cls._prev_qtwidgets is None:
            sys.modules.pop('qgis.PyQt.QtWidgets', None)
        else:
            sys.modules['qgis.PyQt.QtWidgets'] = cls._prev_qtwidgets

    def _make_mock_dialog(self) -> Any:
        dialog = type('MockDialog', (), {})()
        dialog._page_stack = self.qt.QStackedWidget()
        dialog._main_stack = self.qt.QStackedWidget()
        dialog._held_widgets = []
        return dialog

    def test_build_adds_page_to_stack(self) -> None:
        dialog = self._make_mock_dialog()
        self.mod.build_add_user_page(dialog)
        page = dialog._page_stack.widget(0)
        self.assertIsNotNone(page)
        self.assertEqual(page.objectName(), 'add_usr')

    def test_build_appends_page_to_held_widgets(self) -> None:
        dialog = self._make_mock_dialog()
        self.mod.build_add_user_page(dialog)
        self.assertGreater(len(dialog._held_widgets), 0)

    def test_build_creates_text_fields(self) -> None:
        dialog = self._make_mock_dialog()
        self.mod.build_add_user_page(dialog)
        self.assertIsNotNone(dialog._field_fname)
        self.assertEqual(dialog._field_fname.objectName(), 'fname')
        self.assertIsNotNone(dialog._field_lname)
        self.assertIsNotNone(dialog._field_email)
        self.assertIsNotNone(dialog._field_pnum)
        self.assertIsNotNone(dialog._field_uname)
        self.assertIsNotNone(dialog._field_pwd)

    def test_build_password_echo_mode(self) -> None:
        dialog = self._make_mock_dialog()
        self.mod.build_add_user_page(dialog)
        self.assertEqual(
            dialog._field_pwd.echoMode(),
            self.qt.QLineEdit.EchoMode.Password,
        )

    def test_build_creates_combos(self) -> None:
        dialog = self._make_mock_dialog()
        self.mod.build_add_user_page(dialog)
        self.assertIsNotNone(dialog.wilaya_list)
        self.assertEqual(dialog.wilaya_list.objectName(), 'wilaya_list')
        self.assertIsNotNone(dialog.commune_of_wilaya)

    def test_build_creates_buttons(self) -> None:
        dialog = self._make_mock_dialog()
        self.mod.build_add_user_page(dialog)
        self.assertIsNotNone(dialog._btn_cancel_add)
        self.assertEqual(dialog._btn_cancel_add.objectName(), 'abort_uc')
        self.assertIsNotNone(dialog._btn_save_add)
        self.assertEqual(dialog._btn_save_add.objectName(), 'submit_usr')


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestBuildSettingsPage(unittest.TestCase):
    """Test gui/pages/settings_page.py — build_settings_page."""

    qt: ClassVar[Any]
    app: ClassVar[Any]
    mod: ClassVar[Any]
    _prev_qtwidgets: ClassVar[Any]

    @classmethod
    def setUpClass(cls) -> None:
        setup_gui_mocks()
        cls.qt = _qt_widgets_module()
        if cls.qt is None:
            raise unittest.SkipTest('No real Qt widgets module available')
        cls.app = get_qapp()
        cls._prev_qtwidgets = sys.modules.get('qgis.PyQt.QtWidgets')
        sys.modules['qgis.PyQt.QtWidgets'] = cls.qt
        _ensure_package_hierarchy(cls.qt.QWidget, cls.qt.QVBoxLayout)
        cls.mod = _load_page_module(
            'gui/pages/settings_page.py',
            'plans_adressage.gui.pages',
        )

    @classmethod
    def tearDownClass(cls) -> None:
        if cls._prev_qtwidgets is None:
            sys.modules.pop('qgis.PyQt.QtWidgets', None)
        else:
            sys.modules['qgis.PyQt.QtWidgets'] = cls._prev_qtwidgets

    def _make_mock_dialog(self) -> Any:
        dialog = type('MockDialog', (), {})()
        dialog._page_stack = self.qt.QStackedWidget()
        dialog._main_stack = self.qt.QStackedWidget()
        dialog._held_widgets = []
        return dialog

    def test_build_adds_scroll_area_to_stack(self) -> None:
        dialog = self._make_mock_dialog()
        self.mod.build_settings_page(dialog)
        widget = dialog._main_stack.widget(0)
        self.assertIsNotNone(widget)
        self.assertEqual(widget.objectName(), 'settingsTab')

    def test_build_appends_to_held_widgets(self) -> None:
        dialog = self._make_mock_dialog()
        self.mod.build_settings_page(dialog)
        self.assertGreaterEqual(len(dialog._held_widgets), 3)

    def test_build_creates_action_combo(self) -> None:
        dialog = self._make_mock_dialog()
        self.mod.build_settings_page(dialog)
        self.assertIsNotNone(dialog._combo_action)
        self.assertEqual(dialog._combo_action.objectName(), '_action_combo')

    def test_build_creates_paper_combo_hidden(self) -> None:
        dialog = self._make_mock_dialog()
        self.mod.build_settings_page(dialog)
        self.assertIsNotNone(dialog._combo_paper)
        self.assertFalse(dialog._combo_paper.isVisible())

    def test_build_creates_save_action_button(self) -> None:
        dialog = self._make_mock_dialog()
        self.mod.build_settings_page(dialog)
        self.assertIsNotNone(dialog._btn_save_action)
        self.assertEqual(dialog._btn_save_action.objectName(), 'print')

    def test_build_creates_feature_combo(self) -> None:
        dialog = self._make_mock_dialog()
        self.mod.build_settings_page(dialog)
        self.assertIsNotNone(dialog.feature_combo)
        self.assertEqual(dialog.feature_combo.objectName(), 'feature_combo')

    def test_build_creates_subtype_combo_editable(self) -> None:
        dialog = self._make_mock_dialog()
        self.mod.build_settings_page(dialog)
        self.assertIsNotNone(dialog.subtype_combo)
        self.assertTrue(dialog.subtype_combo.isEditable())

    def test_build_creates_new_type_field(self) -> None:
        dialog = self._make_mock_dialog()
        self.mod.build_settings_page(dialog)
        self.assertIsNotNone(dialog._field_new_type)
        self.assertEqual(dialog._field_new_type.objectName(), 'new_type')

    def test_build_creates_save_new_type_button(self) -> None:
        dialog = self._make_mock_dialog()
        self.mod.build_settings_page(dialog)
        self.assertIsNotNone(dialog._btn_save_new_type)
        self.assertEqual(dialog._btn_save_new_type.objectName(), 'add_type_btn')

    def test_build_creates_theme_and_locale_combos(self) -> None:
        dialog = self._make_mock_dialog()
        self.mod.build_settings_page(dialog)
        self.assertIsNotNone(dialog._combo_theme)
        self.assertEqual(dialog._combo_theme.objectName(), '_theme_combo')
        self.assertIsNotNone(dialog._combo_locale)
        self.assertEqual(dialog._combo_locale.objectName(), '_locale_combo')

    def test_build_creates_section_frames(self) -> None:
        dialog = self._make_mock_dialog()
        self.mod.build_settings_page(dialog)
        frames = [
            w
            for w in dialog._held_widgets
            if hasattr(w, 'objectName') and w.objectName() == 'sectionFrame'
        ]
        self.assertGreaterEqual(len(frames), 3)
