"""Tests for mixins.map_tools_mixin."""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from test.helpers import setup_gui_mocks


class TestMapToolsMixin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.mixins.map_tools_mixin',
            'mixins/map_tools_mixin.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.mixins.map_tools_mixin'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.mixin = self.mod.MapToolsMixin()
        self.mixin._tr = lambda s: s
        self.mixin.identify_tool = None
        self.mixin.ref_identify_tool = None
        self.mixin.measure_tool = None
        self.mixin.iface = MagicMock()

    def test_stop_no_active_layer(self):
        self.mixin.iface.activeLayer.return_value = None
        self.mixin.stop()

    def test_stop_with_identify_tool(self):
        self.mixin.identify_tool = MagicMock()
        self.mixin.iface.activeLayer.return_value = MagicMock()
        self.mixin.stop()
        self.mixin.identify_tool.unset_map_tool.assert_called_once()

    def test_stop_with_ref_identify_tool(self):
        self.mixin.ref_identify_tool = MagicMock()
        self.mixin.iface.activeLayer.return_value = MagicMock()
        self.mixin.stop()
        self.mixin.ref_identify_tool.unset_map_tool.assert_called_once()

    def test_stop_with_measure_tool(self):
        self.mixin.measure_tool = MagicMock()
        self.mixin.iface.activeLayer.return_value = MagicMock()
        self.mixin.stop()
        self.mixin.measure_tool.clear.assert_called_once()

    def test_on_edition_release_calls_stop(self):
        self.mixin.stop = MagicMock()
        self.mixin.on_edition_release(None)
        self.mixin.stop.assert_called_once()

    def test_activate_measure(self):
        with patch.object(self.mod, 'MeasureTool') as MockTool:
            mock_tool = MagicMock()
            MockTool.return_value = mock_tool
            self.mixin.activate_measure()
            self.mixin.iface.mapCanvas().setMapTool.assert_called_with(mock_tool)

    def test_set_default_cursor(self):
        self.mixin.set_default_cursor()
        self.mixin.iface.mapCanvas().setCursor.assert_called_once()

    def test_select_ref_handler(self):
        self.mixin.road_ref = MagicMock()
        self.mixin.road_ref.currentData.return_value = 'roads'
        with (
            patch.object(self.mod, 'QgsProject') as mock_proj,
            patch.object(self.mod, 'IdentifyTool') as MockTool,
        ):
            mock_proj.instance.return_value.mapLayersByName.return_value = [MagicMock()]
            MockTool.return_value = MagicMock()
            self.mixin.select_ref_handler()

    def test_select_ref_handler_empty(self):
        self.mixin.road_ref = MagicMock()
        self.mixin.road_ref.currentData.return_value = ''
        self.mixin.road_ref.currentText.return_value = ''
        with patch.object(self.mod, 'QMessageBox') as mock_msg:
            self.mixin.select_ref_handler()
            mock_msg.critical.assert_called_once()

    def test_start_selecting_no_layers(self):
        self.mixin._current_layer_name = MagicMock(return_value='nonexistent')
        with (
            patch.object(self.mod, 'QgsProject') as mock_proj,
            patch.object(self.mod, 'QMessageBox') as mock_msg,
        ):
            mock_proj.instance.return_value.mapLayersByName.return_value = []
            self.mixin.start_selecting()
            mock_msg.critical.assert_called_once()

    def test_selection_handler(self):
        with patch.object(self.mod, 'IdentifyTool') as MockTool:
            mock_tool = MagicMock()
            MockTool.return_value = mock_tool
            self.mixin._selection_handler(layer=MagicMock())
            self.mixin.iface.mapCanvas().setMapTool.assert_called_with(mock_tool)

    def test_selection_handler_unsets_ref_tool(self):
        self.mixin.ref_identify_tool = MagicMock()
        with patch.object(self.mod, 'IdentifyTool'):
            self.mixin._selection_handler(layer=MagicMock())
        self.mixin.ref_identify_tool.unset_map_tool.assert_called_once()

    def test_start_selecting_success(self):
        layer = MagicMock()
        self.mixin._current_layer_name = MagicMock(return_value='roads')
        with (
            patch.object(self.mod, 'QgsProject') as mock_proj,
            patch.object(self.mod, 'IdentifyTool'),
        ):
            mock_proj.instance.return_value.mapLayersByName.return_value = [layer]
            self.mixin.start_selecting()
            self.mixin.iface.setActiveLayer.assert_called_once_with(layer)
            self.mixin.iface.mapCanvas().setMapTool.assert_called_once()

    def test_reconnect_context_menu(self):
        canvas = self.mixin.iface.mapCanvas()
        self.mixin._reconnect_context_menu()
        canvas.customContextMenuRequested.disconnect.assert_called_once_with(
            self.mixin.on_edition_release,
        )
        canvas.customContextMenuRequested.connect.assert_called_once_with(
            self.mixin.on_edition_release,
        )
        canvas.setContextMenuPolicy.assert_called_once()

    def test_reconnect_context_menu_swallows_disconnect_error(self):
        canvas = self.mixin.iface.mapCanvas()
        canvas.customContextMenuRequested.disconnect.side_effect = TypeError
        self.mixin._reconnect_context_menu()
        canvas.customContextMenuRequested.connect.assert_called_once()

    def test_on_map_tool_changed(self):
        canvas = self.mixin.iface.mapCanvas()
        self.mixin._on_map_tool_changed(None)
        canvas.customContextMenuRequested.connect.assert_called_once()

    def test_on_map_tool_changed_dead_canvas(self):
        self.mixin.iface.mapCanvas.side_effect = RuntimeError('wrapped C/C++ deleted')
        self.mixin._on_map_tool_changed(None)

    def test_select_ref_layer_not_found(self):
        self.mixin.road_ref = MagicMock()
        self.mixin.road_ref.currentData.return_value = 'ghost'
        with patch.object(self.mod, 'QgsProject') as mock_proj:
            mock_proj.instance.return_value.mapLayersByName.return_value = []
            self.mixin._select_ref(self.mixin.road_ref)
        self.mixin.iface.mapCanvas().setCursor.assert_called_once()

    def test_select_panel_ref_handler(self):
        self.mixin.panel_ref = MagicMock()
        self.mixin.panel_ref.currentData.return_value = 'panels'
        with (
            patch.object(self.mod, 'QgsProject') as mock_proj,
            patch.object(self.mod, 'IdentifyTool'),
        ):
            mock_proj.instance.return_value.mapLayersByName.return_value = [
                MagicMock(),
            ]
            self.mixin.select_panel_ref_handler()
