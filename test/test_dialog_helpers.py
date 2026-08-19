"""Tests for gui.dialog_helpers."""

import unittest
from unittest.mock import MagicMock

from test.helpers import setup_gui_mocks

setup_gui_mocks()

import sys as _sys

_qtwidgets = _sys.modules['qgis.PyQt.QtWidgets']
_qtwidgets.QLabel = lambda *a, **kw: MagicMock()
_qtwidgets.QPushButton = lambda *a, **kw: MagicMock()


class TestTabWidget(unittest.TestCase):
    def setUp(self):
        from gui.dialog_helpers import _TabWidget

        self.tw = _TabWidget()

    def test_initial_index(self):
        self.assertEqual(self.tw.currentIndex(), 0)

    def test_set_current_index(self):
        self.tw.setCurrentIndex(2)
        self.assertEqual(self.tw.currentIndex(), 2)

    def test_tab_text_valid(self):
        self.assertEqual(self.tw.tabText(0), 'Operations')
        self.assertEqual(self.tw.tabText(1), 'Report')
        self.assertEqual(self.tw.tabText(2), 'Settings')

    def test_tab_text_out_of_range(self):
        self.assertEqual(self.tw.tabText(5), '')
        self.assertEqual(self.tw.tabText(-1), '')

    def test_count(self):
        self.assertEqual(self.tw.count(), 3)

    def test_current_widget_tab_ops(self):
        self.tw.setCurrentIndex(0)
        self.assertEqual(self.tw.currentWidget, 'tab_ops')

    def test_current_widget_other(self):
        self.tw.setCurrentIndex(1)
        self.assertEqual(self.tw.currentWidget, 'tab')


class TestMakeSectionFrame(unittest.TestCase):
    def test_returns_widget(self):
        from gui.dialog_helpers import make_section_frame

        w = make_section_frame()
        self.assertIsNotNone(w)

    def test_object_name(self):
        from gui.dialog_helpers import make_section_frame

        w = make_section_frame()
        w.setObjectName.assert_called_with('sectionFrame')

    def test_with_max_width(self):
        from gui.dialog_helpers import make_section_frame

        w = make_section_frame(max_width=400)
        self.assertIsNotNone(w)


class TestAddFormRow(unittest.TestCase):
    def test_creates_label_and_adds_row(self):
        from gui.dialog_helpers import add_form_row

        form = MagicMock()
        result = add_form_row(form, 'Test Label', 'test_obj', MagicMock())
        form.addRow.assert_called_once()
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
