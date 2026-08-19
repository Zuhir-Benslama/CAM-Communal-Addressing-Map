"""Tests for app.main."""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from test.helpers import setup_gui_mocks


class TestRNA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.app.main',
            'app/main.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.app.main'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.iface = MagicMock()
        self.plugin = self.mod.RNA(self.iface)

    def test_init_actions_empty(self):
        self.assertEqual(self.plugin.actions, [])

    def test_first_start_is_none(self):
        self.assertIsNone(self.plugin.first_start)

    def test_tr_returns_something(self):
        result = self.plugin.tr('Hello')
        self.assertIsNotNone(result)

    def test_add_action(self):
        action = self.plugin.add_action(
            '/fake/icon.png',
            'Test',
            MagicMock(),
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
        )
        self.assertIsNotNone(action)
        self.assertEqual(len(self.plugin.actions), 1)

    def test_add_action_menu_only(self):
        self.plugin.add_action(
            '/fake/icon.png',
            'Test',
            MagicMock(),
            add_to_menu=True,
            add_to_toolbar=False,
        )
        self.assertEqual(len(self.plugin.actions), 1)

    def test_initGui(self):
        self.plugin.initGui()
        self.assertTrue(self.plugin.first_start)
        self.assertEqual(len(self.plugin.actions), 1)

    def test_unload_removes_actions(self):
        self.plugin.add_action('/fake/icon.png', 'Test', MagicMock())
        self.assertEqual(len(self.plugin.actions), 1)
        self.plugin.unload()
        self.iface.removePluginMenu.assert_called()
        self.iface.removeToolBarIcon.assert_called()

    def test_normalize_dock_width_no_dock(self):
        if hasattr(self.plugin, 'dock_widget'):
            delattr(self.plugin, 'dock_widget')
        self.plugin._normalize_dock_width()

    @patch('plans_adressage.app.main.MainDialog')
    @patch('plans_adressage.app.main.QDockWidget')
    @patch('plans_adressage.app.main.QTimer')
    @patch('plans_adressage.app.main.current_locale', return_value='en')
    @patch('plans_adressage.app.main.get_string', return_value='RNA')
    def test_run_first_start(
        self, mock_str, mock_locale, mock_timer, mock_dock_cls, mock_dlg
    ):
        mock_dock = mock_dock_cls.return_value
        mock_dock.width.return_value = 600
        mock_dock.height.return_value = 400
        self.plugin.first_start = True
        self.plugin.run()
        self.assertFalse(self.plugin.first_start)
        mock_dlg.assert_called_once()

    @patch('plans_adressage.app.main.MainDialog')
    @patch('plans_adressage.app.main.QDockWidget')
    @patch('plans_adressage.app.main.QTimer')
    @patch('plans_adressage.app.main.current_locale', return_value='en')
    @patch('plans_adressage.app.main.get_string', return_value='RNA')
    def test_run_subsequent(
        self, mock_str, mock_locale, mock_timer, mock_dock, mock_dlg
    ):
        self.plugin.first_start = False
        self.plugin.dock_widget = MagicMock()
        self.plugin.dock_widget.width.return_value = 600
        self.plugin.run()
        self.plugin.dock_widget.raise_.assert_called()
        self.plugin.dock_widget.show.assert_called()
