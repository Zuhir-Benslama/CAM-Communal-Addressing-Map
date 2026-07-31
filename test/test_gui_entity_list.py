"""Tests for gui/entity_list_dialog.py (Qt Widgets version)."""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from .helpers import get_qapp, setup_gui_mocks


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestEntityListDialog(unittest.TestCase):
    """Test EntityListDialog creation and basic pagination."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.entity_list_dialog',
            'gui/entity_list_dialog.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.entity_list_dialog'] = cls.mod
        spec.loader.exec_module(cls.mod)
        parent = sys.modules.get('plans_adressage.gui')
        if parent is not None:
            parent.entity_list_dialog = cls.mod

    def setUp(self):
        self.dialog = self.mod.EntityListDialog('Road', 'roads', parent=None)

    def test_dialog_created(self):
        self.assertIsNotNone(self.dialog)

    def test_window_title_set(self):
        title = self.dialog.windowTitle()
        self.assertIsNotNone(title)

    def test_table_created(self):
        self.assertIsNotNone(self.dialog._table)

    def test_page_size_default(self):
        self.assertEqual(self.dialog.PAGE_SIZE, 50)

    def test_page_starts_at_zero(self):
        self.assertEqual(self.dialog._page, 0)

    def test_prev_button_created(self):
        self.assertIsNotNone(self.dialog._btn_prev)

    def test_next_button_created(self):
        self.assertIsNotNone(self.dialog._btn_next)

    def test_next_page_increases_page(self):
        self.dialog._total_records = 100
        self.dialog._page = 0
        self.dialog._on_next()
        self.assertEqual(self.dialog._page, 1)

    def test_prev_page_decreases_page(self):
        self.dialog._total_records = 100
        self.dialog._page = 2
        self.dialog._on_prev()
        self.assertEqual(self.dialog._page, 1)

    def test_prev_page_stops_at_zero(self):
        self.dialog._total_records = 100
        self.dialog._page = 0
        self.dialog._on_prev()
        self.assertEqual(self.dialog._page, 0)

    def test_next_page_does_not_exceed_total(self):
        self.dialog._total_records = 30
        self.dialog._page = 0
        self.dialog._on_next()
        self.assertEqual(self.dialog._page, 0)

    def test_next_page_on_last_page_stays(self):
        self.dialog._total_records = 50
        self.dialog._page = 0
        self.dialog._on_next()
        self.assertEqual(self.dialog._page, 0)


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestEntityListDialogWithData(unittest.TestCase):
    """Test EntityListDialog data flow with mocked DB records."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.entity_list_dialog',
            'gui/entity_list_dialog.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.entity_list_dialog'] = cls.mod
        spec.loader.exec_module(cls.mod)
        parent = sys.modules.get('plans_adressage.gui')
        if parent is not None:
            parent.entity_list_dialog = cls.mod

    def _make_dialog(self, records, total_count=None):
        mock_session = MagicMock()
        if total_count is not None:
            mock_session.query.return_value.count.return_value = total_count
        else:
            mock_session.query.return_value.count.return_value = len(records)
        mock_all = (
            mock_session.query.return_value.offset.return_value.limit.return_value.all
        )
        mock_all.return_value = records

        patcher = patch.object(self.mod, 'get_session', return_value=mock_session)
        patcher.start()
        self.addCleanup(patcher.stop)

        return self.mod.EntityListDialog('Road', 'roads', parent=None)

    def test_rows_populated(self):
        dialog = self._make_dialog([MagicMock() for _ in range(3)])
        self.assertEqual(dialog._table.setRowCount.call_args[0][0], 3)

    def test_total_records_matches(self):
        dialog = self._make_dialog([MagicMock() for _ in range(5)], total_count=42)
        self.assertEqual(dialog._total_records, 42)

    def test_page_zero_on_init(self):
        dialog = self._make_dialog([MagicMock()])
        self.assertEqual(dialog._page, 0)

    def test_page_size_constant(self):
        dialog = self._make_dialog([MagicMock()])
        self.assertEqual(dialog.PAGE_SIZE, 50)

    def test_model_name_stored(self):
        dialog = self._make_dialog([MagicMock()])
        self.assertEqual(dialog.model_name, 'Road')

    def test_unknown_model_returns_empty_table(self):
        with patch.object(self.mod, 'get_session') as mock_gs:
            mock_session = MagicMock()
            mock_gs.return_value = mock_session
            dialog = self.mod.EntityListDialog('NonExistent', 'test', parent=None)
            self.assertEqual(dialog._total_records, 0)
            self.assertEqual(dialog._table.setRowCount.call_args[0][0], 0)

    def test_prev_disabled_at_first_page(self):
        dialog = self._make_dialog([MagicMock()], total_count=1)
        self.assertEqual(dialog._page, 0)

    def test_next_enabled_with_more_pages(self):
        dialog = self._make_dialog([MagicMock() for _ in range(50)], total_count=100)
        self.assertEqual(dialog._page, 0)

    def test_session_closed_after_init(self):
        mock_session = MagicMock()
        mock_session.query.return_value.count.return_value = 0
        mock_all = (
            mock_session.query.return_value.offset.return_value.limit.return_value.all
        )
        mock_all.return_value = []

        patcher = patch.object(self.mod, 'get_session', return_value=mock_session)
        patcher.start()
        self.addCleanup(patcher.stop)

        self.mod.EntityListDialog('Road', 'roads', parent=None)
        mock_session.close.assert_called_once()

    def test_pagination_next_page_with_data(self):
        dialog = self._make_dialog([MagicMock() for _ in range(60)], total_count=60)
        dialog._on_next()
        self.assertEqual(dialog._page, 1)

    def test_pagination_does_not_overflow(self):
        dialog = self._make_dialog([MagicMock() for _ in range(60)], total_count=60)
        dialog._page = 1
        dialog._on_next()
        self.assertEqual(dialog._page, 1)

    def test_pagination_prev_page_with_data(self):
        dialog = self._make_dialog([MagicMock() for _ in range(60)], total_count=60)
        dialog._page = 1
        dialog._on_prev()
        self.assertEqual(dialog._page, 0)


if __name__ == '__main__':
    unittest.main()
