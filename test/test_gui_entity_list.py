"""Tests for gui/entity_list_dialog.py (QML-backed version)."""
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
            setattr(parent, 'entity_list_dialog', cls.mod)

    def setUp(self):
        self.dialog = self.mod.EntityListDialog('Road', 'roads', parent=None)

    def test_dialog_created(self):
        self.assertIsNotNone(self.dialog)

    def test_window_title_set(self):
        title = self.dialog.windowTitle()
        self.assertIsNotNone(title)

    def test_bridge_created(self):
        self.assertIsNotNone(self.dialog._bridge)

    def test_bridge_page_size_default(self):
        self.assertEqual(self.dialog._bridge._page_size, 50)

    def test_bridge_page_starts_at_zero(self):
        self.assertEqual(self.dialog._bridge._page, 0)

    def test_quick_widget_created(self):
        self.assertIsNotNone(self.dialog._quick_widget)

    def test_qml_root_accessible(self):
        self.assertIsNotNone(self.dialog._qml_root)

    def test_bridge_next_page_increases_page(self):
        self.dialog._bridge._total_records = 100
        self.dialog._bridge._page = 0
        self.dialog._bridge.nextPage()
        self.assertEqual(self.dialog._bridge._page, 1)

    def test_bridge_prev_page_decreases_page(self):
        self.dialog._bridge._total_records = 100
        self.dialog._bridge._page = 2
        self.dialog._bridge.prevPage()
        self.assertEqual(self.dialog._bridge._page, 1)

    def test_bridge_prev_page_stops_at_zero(self):
        self.dialog._bridge._total_records = 100
        self.dialog._bridge._page = 0
        self.dialog._bridge.prevPage()
        self.assertEqual(self.dialog._bridge._page, 0)

    def test_bridge_next_page_does_not_exceed_total(self):
        self.dialog._bridge._total_records = 30
        self.dialog._bridge._page = 0
        self.dialog._bridge.nextPage()
        self.assertEqual(self.dialog._bridge._page, 0)

    def test_bridge_next_page_on_last_page_stays(self):
        self.dialog._bridge._total_records = 50
        self.dialog._bridge._page = 0
        self.dialog._bridge.nextPage()
        self.assertEqual(self.dialog._bridge._page, 0)


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
            setattr(parent, 'entity_list_dialog', cls.mod)

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

    def test_set_page_data_called_on_populate(self):
        """_populate_table pushes data to QML via setPageData."""
        dialog = self._make_dialog([MagicMock() for _ in range(3)])
        call_args = dialog._qml_root.setPageData.call_args
        self.assertIsNotNone(call_args)
        data = call_args[0][0]
        self.assertIn('rows', data)
        self.assertIn('fields', data)
        self.assertIn('labels', data)
        self.assertIn('total', data)
        self.assertIn('page', data)
        self.assertIn('pageSize', data)

    def test_set_page_data_has_correct_row_count(self):
        dialog = self._make_dialog([MagicMock() for _ in range(3)])
        data = dialog._qml_root.setPageData.call_args[0][0]
        self.assertEqual(len(data['rows']), 3)

    def test_set_page_data_total_matches(self):
        dialog = self._make_dialog([MagicMock() for _ in range(5)],
                                   total_count=42)
        data = dialog._qml_root.setPageData.call_args[0][0]
        self.assertEqual(data['total'], 42)

    def test_set_page_data_page_zero_on_init(self):
        dialog = self._make_dialog([MagicMock()])
        data = dialog._qml_root.setPageData.call_args[0][0]
        self.assertEqual(data['page'], 0)

    def test_set_page_data_page_size_constant(self):
        dialog = self._make_dialog([MagicMock()])
        data = dialog._qml_root.setPageData.call_args[0][0]
        self.assertEqual(data['pageSize'], 50)

    def test_bridge_page_state_updated_after_populate(self):
        dialog = self._make_dialog([MagicMock()], total_count=100)
        self.assertEqual(dialog._bridge._total_records, 100)

    def test_bridge_model_name_stored(self):
        dialog = self._make_dialog([MagicMock()])
        self.assertEqual(dialog.model_name, 'Road')

    def test_bridge_unknown_model_returns_empty_data(self):
        with patch.object(self.mod, 'get_session') as mock_gs:
            mock_session = MagicMock()
            mock_gs.return_value = mock_session
            dialog = self.mod.EntityListDialog(
                'NonExistent', 'test', parent=None)
            data = dialog._qml_root.setPageData.call_args[0][0]
            self.assertEqual(data['total'], 0)
            self.assertEqual(len(data['rows']), 0)

    def test_bridge_prev_disabled_at_first_page_by_data(self):
        dialog = self._make_dialog([MagicMock()], total_count=1)
        data = dialog._qml_root.setPageData.call_args[0][0]
        self.assertEqual(data['page'], 0)

    def test_bridge_next_enabled_with_more_pages(self):
        dialog = self._make_dialog(
            [MagicMock() for _ in range(50)], total_count=100)
        data = dialog._qml_root.setPageData.call_args[0][0]
        self.assertEqual(data['page'], 0)

    def test_session_closed_after_init(self):
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
        dialog = self._make_dialog(
            [MagicMock() for _ in range(60)], total_count=60)
        dialog._bridge.nextPage()
        self.assertEqual(dialog._bridge._page, 1)

    def test_pagination_does_not_overflow(self):
        dialog = self._make_dialog(
            [MagicMock() for _ in range(60)], total_count=60)
        dialog._bridge._page = 1
        dialog._bridge.nextPage()
        self.assertEqual(dialog._bridge._page, 1)

    def test_pagination_prev_page_with_data(self):
        dialog = self._make_dialog(
            [MagicMock() for _ in range(60)], total_count=60)
        dialog._bridge._page = 1
        dialog._bridge.prevPage()
        self.assertEqual(dialog._bridge._page, 0)


if __name__ == '__main__':
    unittest.main()
