"""Tests for gui/measure_tool.py."""
import importlib
import sys
import unittest
from unittest.mock import MagicMock, PropertyMock

from .helpers import setup_gui_mocks, get_qapp


@unittest.skipIf(get_qapp() is None, 'PyQt5 not available')
class TestMeasureTool(unittest.TestCase):
    """Test MeasureTool creation and measurement functionality."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.measure_tool', 'gui/measure_tool.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.measure_tool'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.canvas = MagicMock()
        self.iface = MagicMock()
        self.tool = self.mod.MeasureTool(self.canvas, self.iface)

    def test_tool_created(self):
        self.assertIsNotNone(self.tool)

    def test_initial_points_empty(self):
        self.assertEqual(self.tool.points, [])

    def test_initial_paused_false(self):
        self.assertFalse(self.tool.paused)

    def test_reset_clears_points(self):
        self.tool.points = [[1, 2], [3, 4]]
        self.tool.markers = [MagicMock()]
        self.tool.labels = [MagicMock()]
        self.tool.reset()
        self.assertEqual(self.tool.points, [])
        self.assertEqual(self.tool.markers, [])

    def test_measure_deactivated_clears_state(self):
        self.tool.points = [[1, 2]]
        self.tool.markers = [MagicMock()]
        self.tool.deactivate()
        self.assertEqual(self.tool.points, [])
        self.assertEqual(self.tool.markers, [])


if __name__ == '__main__':
    unittest.main()
