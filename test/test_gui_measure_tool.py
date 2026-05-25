"""Tests for gui/measure_tool.py."""
import importlib
import sys
import unittest
from unittest.mock import MagicMock

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
        self.canvas.getCoordinateTransform.return_value.transform.return_value = MagicMock()
        self.iface = MagicMock()
        self.tool = self.mod.MeasureTool(self.canvas, self.iface)
        self.tool.toMapCoordinates = MagicMock(return_value=MagicMock())

    def test_tool_created(self):
        self.assertIsNotNone(self.tool)

    def test_initial_points_empty(self):
        self.assertEqual(self.tool.points, [])

    def test_initial_paused_false(self):
        self.assertFalse(self.tool.paused)

    def test_rubber_band_created(self):
        self.assertIsNotNone(self.tool.rubber_band)

    def test_initial_markers_empty(self):
        self.assertEqual(self.tool.markers, [])

    def test_initial_labels_empty(self):
        self.assertEqual(self.tool.labels, [])

    def test_clear_empties_all_state(self):
        self.tool.points = [MagicMock()]
        self.tool.markers = [MagicMock()]
        self.tool.labels = [MagicMock()]
        self.tool.clear()
        self.assertEqual(self.tool.points, [])
        self.assertEqual(self.tool.markers, [])
        self.assertEqual(self.tool.labels, [])

    def test_unset_map_tool_calls_clear_and_unset(self):
        self.tool.unset_map_tool()
        self.canvas.unsetMapTool.assert_called_once_with(self.tool)

    def test_canvas_release_event_paused_returns_early(self):
        self.tool.paused = True
        self.tool.canvasReleaseEvent(MagicMock())
        self.assertEqual(len(self.tool.points), 0)

    def test_canvas_release_first_click_adds_point_and_marker(self):
        event = MagicMock()
        self.tool.toMapCoordinates.return_value = MagicMock()
        self.tool.canvasReleaseEvent(event)
        self.assertEqual(len(self.tool.points), 1)
        self.assertEqual(len(self.tool.markers), 1)

    def test_key_press_r_clears_and_shows_message(self):
        event = MagicMock()
        event.key.return_value = 82  # Qt.Key_R
        self.tool.points = [MagicMock(), MagicMock()]
        self.tool.markers = [MagicMock()]
        self.tool.keyPressEvent(event)
        self.assertEqual(len(self.tool.points), 0)
        self.iface.messageBar().pushMessage.assert_called()

    def test_key_press_e_clears_and_unset_tool(self):
        event = MagicMock()
        event.key.return_value = 69  # Qt.Key_E
        self.tool.points = [MagicMock()]
        self.tool.keyPressEvent(event)
        self.assertEqual(len(self.tool.points), 0)
        self.canvas.unsetMapTool.assert_called_once_with(self.tool)

    def test_key_press_p_toggles_pause(self):
        event = MagicMock()
        event.key.return_value = 80  # Qt.Key_P
        self.assertFalse(self.tool.paused)
        self.tool.keyPressEvent(event)
        self.assertTrue(self.tool.paused)
        self.tool.keyPressEvent(event)
        self.assertFalse(self.tool.paused)

    def test_deactivate_clears_state(self):
        self.tool.points = [[1, 2]]
        self.tool.markers = [MagicMock()]
        self.tool.labels = [MagicMock()]
        self.tool.deactivate()
        self.assertEqual(self.tool.points, [])
        self.assertEqual(self.tool.markers, [])
        self.assertEqual(self.tool.labels, [])


if __name__ == '__main__':
    unittest.main()
