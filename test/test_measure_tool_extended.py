"""Extended tests for gui/measure_tool.py covering uncovered methods."""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from test.helpers import get_qapp, setup_gui_mocks


def _make_point(x, y):
    """Create a mock point with numeric x()/y() methods."""
    p = MagicMock()
    p.x.return_value = x
    p.y.return_value = y
    return p


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestMeasureToolInit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.measure_tool',
            'gui/measure_tool.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.measure_tool'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.canvas = MagicMock()
        self.iface = MagicMock()
        self.tool = self.mod.MeasureTool(self.canvas, self.iface)

    def test_canvas_stored(self):
        self.assertIs(self.tool.canvas, self.canvas)

    def test_iface_stored(self):
        self.assertIs(self.tool.iface, self.iface)

    def test_points_initialized_empty(self):
        self.assertEqual(self.tool.points, [])

    def test_markers_initialized_empty(self):
        self.assertEqual(self.tool.markers, [])

    def test_labels_initialized_empty(self):
        self.assertEqual(self.tool.labels, [])

    def test_paused_initialized_false(self):
        self.assertFalse(self.tool.paused)

    def test_da_created(self):
        self.assertIsNotNone(self.tool.da)

    def test_rubber_band_created(self):
        self.assertIsNotNone(self.tool.rubber_band)


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestMeasureToolCanvasRelease(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.measure_tool',
            'gui/measure_tool.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.measure_tool'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.canvas = MagicMock()
        self.iface = MagicMock()
        self.tool = self.mod.MeasureTool(self.canvas, self.iface)
        self.tool.da.measureLine = MagicMock(return_value=10.5)

    def _make_event(self):
        return MagicMock()

    def test_release_paused_returns_early(self):
        self.tool.paused = True
        self.tool.toMapCoordinates = MagicMock(return_value=_make_point(1, 2))
        self.tool.canvasReleaseEvent(self._make_event())
        self.assertEqual(len(self.tool.points), 0)

    def test_release_first_click_adds_one_point_and_marker(self):
        self.tool.toMapCoordinates = MagicMock(return_value=_make_point(1, 2))
        self.tool.canvasReleaseEvent(self._make_event())
        self.assertEqual(len(self.tool.points), 1)
        self.assertEqual(len(self.tool.markers), 1)

    def test_release_second_click_adds_second_point(self):
        self.tool.toMapCoordinates = MagicMock(
            side_effect=[
                _make_point(1, 2),
                _make_point(3, 4),
            ]
        )
        self.tool.canvasReleaseEvent(self._make_event())
        self.tool.canvasReleaseEvent(self._make_event())
        self.assertEqual(len(self.tool.points), 2)
        self.assertEqual(len(self.tool.markers), 2)

    def test_release_second_click_shows_rubber_band(self):
        self.tool.toMapCoordinates = MagicMock(
            side_effect=[
                _make_point(1, 2),
                _make_point(3, 4),
            ]
        )
        self.tool.canvasReleaseEvent(self._make_event())
        self.tool.canvasReleaseEvent(self._make_event())
        self.tool.rubber_band.show.assert_called()

    def test_release_second_click_pushes_total_message(self):
        self.tool.toMapCoordinates = MagicMock(
            side_effect=[
                _make_point(1, 2),
                _make_point(3, 4),
            ]
        )
        self.tool.canvasReleaseEvent(self._make_event())
        self.tool.canvasReleaseEvent(self._make_event())
        self.iface.messageBar().pushMessage.assert_called()

    def test_release_multiple_clicks_accumulates_points(self):
        points = [_make_point(i, i * 2) for i in range(5)]
        self.tool.toMapCoordinates = MagicMock(side_effect=points)
        for _ in range(5):
            self.tool.canvasReleaseEvent(self._make_event())
        self.assertEqual(len(self.tool.points), 5)
        self.assertEqual(len(self.tool.markers), 5)

    def test_release_adds_distance_label(self):
        self.tool.toMapCoordinates = MagicMock(
            side_effect=[
                _make_point(0, 0),
                _make_point(3, 4),
            ]
        )
        self.tool.canvasReleaseEvent(self._make_event())
        self.tool.canvasReleaseEvent(self._make_event())
        self.assertTrue(
            len(self.tool.labels) > 0 or self.tool.canvas.scene().addItem.called
        )

    def test_release_first_click_resets_rubber_band(self):
        self.tool.toMapCoordinates = MagicMock(return_value=_make_point(1, 2))
        self.tool.canvasReleaseEvent(self._make_event())
        self.tool.rubber_band.reset.assert_called()


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestMeasureToolCanvasMove(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.measure_tool',
            'gui/measure_tool.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.measure_tool'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.canvas = MagicMock()
        self.iface = MagicMock()
        self.tool = self.mod.MeasureTool(self.canvas, self.iface)
        self.tool.da.measureLine = MagicMock(return_value=5.0)

    def test_move_paused_returns_early(self):
        self.tool.paused = True
        self.tool.canvasMoveEvent(MagicMock())
        self.tool.rubber_band.removeLastPoint.assert_not_called()

    def test_move_no_points_returns_early(self):
        self.tool.points = []
        self.tool.canvasMoveEvent(MagicMock())
        self.tool.rubber_band.removeLastPoint.assert_not_called()

    def test_move_with_points_updates_rubber_band(self):
        self.tool.toMapCoordinates = MagicMock(
            side_effect=[
                _make_point(0, 0),
                _make_point(3, 4),
            ]
        )
        self.tool.canvasReleaseEvent(MagicMock())
        self.tool.canvasMoveEvent(MagicMock())
        self.tool.rubber_band.removeLastPoint.assert_called()
        self.tool.rubber_band.addPoint.assert_called()

    def test_move_shows_tooltip(self):
        self.tool.toMapCoordinates = MagicMock(
            side_effect=[
                _make_point(0, 0),
                _make_point(3, 4),
            ]
        )
        self.tool.canvasReleaseEvent(MagicMock())
        with patch.object(self.mod.QToolTip, 'showText') as mock_tt:
            self.tool.canvasMoveEvent(MagicMock())
        mock_tt.assert_called_once()


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestMeasureToolKeyPress(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.measure_tool',
            'gui/measure_tool.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.measure_tool'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.canvas = MagicMock()
        self.iface = MagicMock()
        self.tool = self.mod.MeasureTool(self.canvas, self.iface)
        self.tool.da.measureLine = MagicMock(return_value=10.0)

    def _make_key_event(self, key_value):
        event = MagicMock()
        event.key.return_value = key_value
        return event

    def test_key_r_clears_and_shows_restart_message(self):
        self.tool.points = [MagicMock(), MagicMock()]
        self.tool.markers = [MagicMock()]
        self.tool.labels = [MagicMock()]
        event = self._make_key_event(82)  # Key_R
        self.tool.keyPressEvent(event)
        self.assertEqual(len(self.tool.points), 0)
        self.assertEqual(len(self.tool.markers), 0)
        self.assertEqual(len(self.tool.labels), 0)
        self.iface.messageBar().pushMessage.assert_called()

    def test_key_e_clears_and_unsets_tool(self):
        self.tool.points = [MagicMock()]
        event = self._make_key_event(69)  # Key_E
        self.tool.keyPressEvent(event)
        self.assertEqual(len(self.tool.points), 0)
        self.canvas.unsetMapTool.assert_called_once_with(self.tool)

    def test_key_e_shows_finish_message(self):
        event = self._make_key_event(69)
        self.tool.keyPressEvent(event)
        self.iface.messageBar().pushMessage.assert_called()

    def test_key_p_toggles_pause_on(self):
        event = self._make_key_event(80)  # Key_P
        self.assertFalse(self.tool.paused)
        self.tool.keyPressEvent(event)
        self.assertTrue(self.tool.paused)

    def test_key_p_toggles_pause_off(self):
        self.tool.paused = True
        event = self._make_key_event(80)
        self.tool.keyPressEvent(event)
        self.assertFalse(self.tool.paused)

    def test_key_p_shows_status_message(self):
        event = self._make_key_event(80)
        self.tool.keyPressEvent(event)
        self.iface.messageBar().pushMessage.assert_called()


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestMeasureToolClear(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.measure_tool',
            'gui/measure_tool.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.measure_tool'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.canvas = MagicMock()
        self.iface = MagicMock()
        self.tool = self.mod.MeasureTool(self.canvas, self.iface)

    def test_clear_empties_points(self):
        self.tool.points = [MagicMock(), MagicMock()]
        self.tool.clear()
        self.assertEqual(self.tool.points, [])

    def test_clear_empties_markers(self):
        self.tool.markers = [MagicMock(), MagicMock()]
        self.tool.clear()
        self.assertEqual(self.tool.markers, [])

    def test_clear_empties_labels(self):
        self.tool.labels = [MagicMock()]
        self.tool.clear()
        self.assertEqual(self.tool.labels, [])

    def test_clear_removes_markers_from_scene(self):
        marker = MagicMock()
        self.tool.markers = [marker]
        self.tool.clear()
        self.canvas.scene().removeItem.assert_any_call(marker)

    def test_clear_removes_labels_from_scene(self):
        label = MagicMock()
        self.tool.labels = [label]
        self.tool.clear()
        self.canvas.scene().removeItem.assert_any_call(label)

    def test_clear_resets_rubber_band(self):
        self.tool.clear()
        self.tool.rubber_band.reset.assert_called()

    def test_clear_disconnects_signals(self):
        self.tool.clear()
        self.canvas.extentsChanged.disconnect.assert_called()
        self.canvas.scaleChanged.disconnect.assert_called()

    def test_clear_reconnects_signals(self):
        self.tool.clear()
        self.canvas.extentsChanged.connect.assert_called()
        self.canvas.scaleChanged.connect.assert_called()

    def test_clear_works_when_already_empty(self):
        self.tool.points = []
        self.tool.markers = []
        self.tool.labels = []
        self.tool.clear()
        self.assertEqual(self.tool.points, [])
        self.assertEqual(self.tool.markers, [])
        self.assertEqual(self.tool.labels, [])


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestMeasureToolUnsetMapTool(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.measure_tool',
            'gui/measure_tool.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.measure_tool'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.canvas = MagicMock()
        self.iface = MagicMock()
        self.tool = self.mod.MeasureTool(self.canvas, self.iface)

    def test_unset_map_tool_calls_clear(self):
        self.tool.points = [MagicMock()]
        self.tool.unset_map_tool()
        self.assertEqual(self.tool.points, [])

    def test_unset_map_tool_unsets_from_canvas(self):
        self.tool.unset_map_tool()
        self.canvas.unsetMapTool.assert_called_once_with(self.tool)


if __name__ == '__main__':
    unittest.main()
