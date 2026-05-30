"""Tests for gui/entity_list_dialog.py."""
import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from .helpers import setup_gui_mocks, get_qapp


def _make_dialog_class():
    """Load and return the EntityListDialog module."""
    app = get_qapp()
    if app is None:
        return None, None
    setup_gui_mocks()
    spec = importlib.util.spec_from_file_location(
        'plans_adressage.gui.entity_list_dialog',
        'gui/entity_list_dialog.py',
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules['plans_adressage.gui.entity_list_dialog'] = mod
    spec.loader.exec_module(mod)
    return app, mod


@unittest.skipIf(get_qapp() is None, 'PyQt5 not available')
class TestEntityListDialog(unittest.TestCase):
    """Test EntityListDialog creation and basic pagination."""

    @classmethod
    def setUpClass(cls):
        cls.app, cls.mod = _make_dialog_class()

    def setUp(self):
        self.dialog = self.mod.EntityListDialog('Road', 'roads', parent=None)

    def test_dialog_created(self):
        self.assertIsNotNone(self.dialog)

    def test_dialog_title_set(self):
        title = self.dialog.windowTitle()
        self.assertIsNotNone(title)

    def test_initial_page_zero(self):
        self.assertEqual(self.dialog._page, 0)

    def test_page_size_constant(self):
        self.assertEqual(self.dialog.PAGE_SIZE, 50)

    def test_next_page_increases_page(self):
        self.dialog._total_records = 100
        self.dialog._next_page()
        self.assertEqual(self.dialog._page, 1)

    def test_prev_page_decreases_page(self):
        self.dialog._page = 2
        self.dialog._total_records = 100
        self.dialog._prev_page()
        self.assertEqual(self.dialog._page, 1)

    def test_prev_page_stops_at_zero(self):
        self.dialog._page = 0
        self.dialog._prev_page()
        self.assertEqual(self.dialog._page, 0)

    def test_next_page_does_not_exceed_total(self):
        self.dialog._total_records = 30
        self.dialog._page = 0
        self.dialog._next_page()
        self.assertEqual(self.dialog._page, 0)

    def test_populate_table_returns_early_for_unknown_model(self):
        dialog = self.mod.EntityListDialog('NonExistent', 'test', parent=None)
        self.assertEqual(dialog._total_records, 0)

    def test_prev_button_disabled_at_first_page(self):
        self.assertFalse(self.dialog._prev_btn.isEnabled())

    def test_next_button_disabled_when_no_more_records(self):
        self.assertFalse(self.dialog._next_btn.isEnabled())

    def test_session_closed_after_init(self):
        session = self.mod.get_session()
        self.assertTrue(session.close.called)


@unittest.skipIf(get_qapp() is None, 'PyQt5 not available')
class TestEntityListDialogWithData(unittest.TestCase):
    """Test EntityListDialog populate_table with mocked DB records."""

    @classmethod
    def setUpClass(cls):
        cls.app, cls.mod = _make_dialog_class()

    def _make_record(self, value='A1', state='active'):
        record = MagicMock()
        record.value = value
        record.state = state
        return record

    def _make_dialog(self, records, total_count=None):
        mock_session = MagicMock()
        if total_count is not None:
            mock_session.query.return_value.count.return_value = total_count
        else:
            mock_session.query.return_value.count.return_value = len(records)
        mock_all = (mock_session.query.return_value.offset
                    .return_value.limit.return_value.all)
        mock_all.return_value = records

        patcher = patch.object(self.mod, 'get_session',
                               return_value=mock_session)
        patcher.start()
        self.addCleanup(patcher.stop)

        return self.mod.EntityListDialog('Road', 'roads', parent=None)

    def test_populate_table_sets_row_count(self):
        dialog = self._make_dialog([self._make_record() for _ in range(3)])
        self.assertEqual(dialog.table.rowCount(), 3)

    def test_populate_table_sets_column_count(self):
        dialog = self._make_dialog([self._make_record()])
        self.assertEqual(dialog.table.columnCount(), 2)

    def test_populate_table_sets_total_label(self):
        dialog = self._make_dialog([self._make_record()], total_count=42)
        self.assertIn('42', dialog._total_label.text())

    def test_populate_table_sets_page_label(self):
        dialog = self._make_dialog(
            [self._make_record() for _ in range(60)],
            total_count=60,
        )
        self.assertIn('1 / 2', dialog._page_label.text())

    def test_populate_table_sets_page_label_single_page(self):
        dialog = self._make_dialog([self._make_record()], total_count=1)
        self.assertIn('1 / 1', dialog._page_label.text())

    def test_next_enabled_with_more_pages(self):
        dialog = self._make_dialog(
            [self._make_record() for _ in range(100)],
            total_count=100,
        )
        self.assertTrue(dialog._next_btn.isEnabled())

    def test_next_disabled_on_last_page(self):
        dialog = self._make_dialog(
            [self._make_record() for _ in range(50)],
            total_count=50,
        )
        self.assertFalse(dialog._next_btn.isEnabled())

    def test_prev_disabled_on_first_page_with_data(self):
        dialog = self._make_dialog([self._make_record()], total_count=1)
        self.assertFalse(dialog._prev_btn.isEnabled())

    def test_populate_table_na_fallback_on_none_value(self):
        record = MagicMock()
        del record.value
        del record.state
        dialog = self._make_dialog([record], total_count=1)
        item = dialog.table.item(0, 0)
        self.assertIsNotNone(item)
        self.assertEqual(item.text(), 'N/A')

    def test_populate_table_empty_results(self):
        dialog = self._make_dialog([], total_count=0)
        self.assertEqual(dialog.table.rowCount(), 0)

    def test_session_closed(self):
        mock_session = MagicMock()
        mock_session.query.return_value.count.return_value = 0
        mock_all = (mock_session.query.return_value.offset
                    .return_value.limit.return_value.all)
        mock_all.return_value = []

        patcher = patch.object(self.mod, 'get_session',
                               return_value=mock_session)
        patcher.start()
        self.addCleanup(patcher.stop)

        self.mod.EntityListDialog('Road', 'roads', parent=None)
        mock_session.close.assert_called_once()

    def test_pagination_next_page_with_data(self):
        records = [self._make_record(value=str(i)) for i in range(60)]
        dialog = self._make_dialog(records, total_count=60)
        dialog._next_page()
        self.assertEqual(dialog._page, 1)

    def test_pagination_does_not_overflow(self):
        records = [self._make_record(value=str(i)) for i in range(60)]
        dialog = self._make_dialog(records, total_count=60)
        dialog._page = 1
        dialog._next_page()
        self.assertEqual(dialog._page, 1)

    def test_pagination_prev_page_with_data(self):
        records = [self._make_record(value=str(i)) for i in range(60)]
        dialog = self._make_dialog(records, total_count=60)
        dialog._page = 1
        dialog._prev_page()
        self.assertEqual(dialog._page, 0)


if __name__ == '__main__':
    unittest.main()
