"""Tests for mixins/symbol_export_mixin.py."""
import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from .helpers import setup_gui_mocks


class TestSymbolExportMixin(unittest.TestCase):
    """Test SymbolExportMixin layout/SVG/PNG export methods."""

    @classmethod
    def setUpClass(cls):
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.mixins.symbol_export_mixin',
            'mixins/symbol_export_mixin.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.mixins.symbol_export_mixin'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.mixin = self.mod.SymbolExportMixin()
        self.mixin._tr = lambda s: s
        self.mixin.type_plan = 'ترقيم'
        self.mixin.type_to_hide = 'لوحات'
        self.mixin.sat_view = 'Satellite View'
        self.mixin.rast = None
        self.mixin.iface = MagicMock()
        self.mixin.iface.mapCanvas.return_value.rotation.return_value = 0.0
        self.mixin.iface.mapCanvas.return_value.extent.return_value = MagicMock()
        self.mixin.iface.mapCanvas.return_value.mapSettings.return_value.scale.return_value = 500

    def _make_project(self, layer_names=None):
        if layer_names is None:
            layer_names = ['بلديتي', 'ترقيم', 'لوحات']
        layers = {}
        for name in layer_names:
            l = MagicMock()
            l.name.return_value = name
            layers[name] = l
        project = MagicMock()
        project.mapLayers.return_value = layers
        return project

    def _make_scene_rect(self, val=300.0):
        r = MagicMock()
        r.right.return_value = val
        r.bottom.return_value = val
        r.height.return_value = val
        return r

    # --- symbols() ---

    def test_symbols_returns_none_when_type_plan_missing(self):
        self.mixin.type_plan = None
        result = self.mixin.symbols()
        self.assertIsNone(result)

    def test_symbols_returns_none_when_type_to_hide_missing(self):
        self.mixin.type_to_hide = None
        result = self.mixin.symbols()
        self.assertIsNone(result)

    def test_symbols_returns_path_on_success(self):
        project = self._make_project()
        scene_rect = self._make_scene_rect()
        with patch.object(self.mod, 'QgsProject') as mock_qp, \
             patch.object(self.mod, 'QgsPrintLayout'), \
             patch.object(self.mod, 'QgsLayoutItemMap') as mock_map, \
             patch.object(self.mod, 'QgsLayoutItemLegend') as mock_legend, \
             patch.object(self.mod, 'QgsLayoutExporter') as mock_exporter:
            mock_qp.instance.return_value = project
            mock_map.return_value.sceneBoundingRect.return_value = scene_rect
            mock_legend.return_value.sceneBoundingRect.return_value = scene_rect
            mock_exporter.Success = 0
            mock_exporter.return_value.exportToSvg.return_value = 0
            result = self.mixin.symbols()
            self.assertEqual(result, self.mod.SYMBOLS_SVG)

    def test_symbols_returns_none_on_export_failure(self):
        project = self._make_project()
        scene_rect = self._make_scene_rect()
        with patch.object(self.mod, 'QgsProject') as mock_qp, \
             patch.object(self.mod, 'QgsPrintLayout'), \
             patch.object(self.mod, 'QgsLayoutItemMap') as mock_map, \
             patch.object(self.mod, 'QgsLayoutItemLegend') as mock_legend, \
             patch.object(self.mod, 'QgsLayoutExporter') as mock_exporter:
            mock_qp.instance.return_value = project
            mock_map.return_value.sceneBoundingRect.return_value = scene_rect
            mock_legend.return_value.sceneBoundingRect.return_value = scene_rect
            mock_exporter.Success = 0
            mock_exporter.return_value.exportToSvg.return_value = 1
            result = self.mixin.symbols()
            self.assertIsNone(result)

    def test_symbols_hides_layers_in_to_hide_list(self):
        project = self._make_project(['بلديتي', 'ترقيم', 'لوحات', 'Satellite View'])
        scene_rect = self._make_scene_rect()
        with patch.object(self.mod, 'QgsProject') as mock_qp, \
             patch.object(self.mod, 'QgsPrintLayout'), \
             patch.object(self.mod, 'QgsLayoutItemMap') as mock_map, \
             patch.object(self.mod, 'QgsLayoutItemLegend') as mock_legend, \
             patch.object(self.mod, 'QgsLayoutExporter') as mock_exporter:
            mock_qp.instance.return_value = project
            mock_map.return_value.sceneBoundingRect.return_value = scene_rect
            mock_legend.return_value.sceneBoundingRect.return_value = scene_rect
            mock_exporter.Success = 0
            mock_exporter.return_value.exportToSvg.return_value = 0
            self.mixin.symbols()
            call_args = mock_map.return_value.setLayers.call_args
            self.assertIsNotNone(call_args)
            passed_layers = call_args[0][0]
            passed_names = [l.name() for l in passed_layers]
            self.assertNotIn('لوحات', passed_names)
            self.assertNotIn('Satellite View', passed_names)
            self.assertIn('ترقيم', passed_names)

    # --- map_situation() ---

    def test_map_situation_exports_with_sat_view(self):
        project = MagicMock()
        layer1 = MagicMock()
        layer1.renderer.return_value.clone.return_value = MagicMock()
        layer1.clone.return_value = MagicMock()
        project.mapLayersByName = MagicMock(side_effect=lambda name: {
            self.mod.LAYER_MUNICIPALITY: [layer1],
            'Satellite View': [MagicMock()],
        }.get(name, []))

        with patch.object(self.mod, 'QgsProject') as mock_qp, \
             patch.object(self.mod, 'QgsFillSymbol'), \
             patch.object(self.mod, 'QgsLayout'), \
             patch.object(self.mod, 'QgsLayoutItemMap'), \
             patch.object(self.mod, 'QgsLayoutExporter'):
            mock_qp.instance.return_value = project
            self.mixin.sat_view = 'Satellite View'
            self.mixin.rast = None
            self.mixin.map_situation()

    def test_map_situation_exports_with_rast_when_no_sat_view(self):
        project = MagicMock()
        layer1 = MagicMock()
        layer1.renderer.return_value.clone.return_value = MagicMock()
        layer1.clone.return_value = MagicMock()
        project.mapLayersByName = MagicMock(side_effect=lambda name: {
            self.mod.LAYER_MUNICIPALITY: [layer1],
            'raster_layer': [MagicMock()],
        }.get(name, []))

        with patch.object(self.mod, 'QgsProject') as mock_qp, \
             patch.object(self.mod, 'QgsFillSymbol'), \
             patch.object(self.mod, 'QgsLayout'), \
             patch.object(self.mod, 'QgsLayoutItemMap'), \
             patch.object(self.mod, 'QgsLayoutExporter'):
            mock_qp.instance.return_value = project
            self.mixin.sat_view = None
            self.mixin.rast = 'raster_layer'
            self.mixin.map_situation()

    def test_map_situation_logs_warning_when_no_base_layer(self):
        project = MagicMock()
        layer1 = MagicMock()
        layer1.renderer.return_value.clone.return_value = MagicMock()
        layer1.clone.return_value = MagicMock()
        project.mapLayersByName = MagicMock(side_effect=lambda name: {
            self.mod.LAYER_MUNICIPALITY: [layer1],
        }.get(name, []))

        with patch.object(self.mod, 'QgsProject') as mock_qp, \
             patch.object(self.mod, 'logger') as mock_logger:
            mock_qp.instance.return_value = project
            self.mixin.sat_view = None
            self.mixin.rast = None
            self.mixin.map_situation()
            mock_logger.warning.assert_called_once()

    # --- north() ---

    def test_north_exports_svg(self):
        project = MagicMock()
        with patch.object(self.mod, 'QgsProject') as mock_qp, \
             patch.object(self.mod, 'QgsPrintLayout'), \
             patch.object(self.mod, 'QgsLayoutItemPage'), \
             patch.object(self.mod, 'QgsLayoutItemPicture'), \
             patch.object(self.mod, 'QgsApplication'), \
             patch.object(self.mod, 'QgsLayoutExporter'):
            mock_qp.instance.return_value = project
            self.mixin.north()

    def test_north_uses_canvas_rotation(self):
        project = MagicMock()
        with patch.object(self.mod, 'QgsProject') as mock_qp, \
             patch.object(self.mod, 'QgsPrintLayout'), \
             patch.object(self.mod, 'QgsLayoutItemPage'), \
             patch.object(self.mod, 'QgsLayoutItemPicture') as mock_pic, \
             patch.object(self.mod, 'QgsApplication'), \
             patch.object(self.mod, 'QgsLayoutExporter'):
            mock_qp.instance.return_value = project
            self.mixin.iface.mapCanvas.return_value.rotation.return_value = 45.0
            self.mixin.north()
            mock_pic.return_value.setRotation.assert_called_once_with(45.0)

    # --- scale() ---

    def test_scale_uses_kilometers_when_scale_large(self):
        project = MagicMock()
        self.mixin.iface.mapCanvas.return_value.mapSettings.return_value.scale.return_value = 10000
        with patch.object(self.mod, 'QgsProject') as mock_qp, \
             patch.object(self.mod, 'QgsPrintLayout'), \
             patch.object(self.mod, 'QgsLayoutItemPage'), \
             patch.object(self.mod, 'QgsLayoutItemMap'), \
             patch.object(self.mod, 'QgsLayoutItemScaleBar') as mock_bar, \
             patch.object(self.mod, 'QgsBasicNumericFormat'), \
             patch.object(self.mod, 'QgsLayoutExporter'):
            mock_qp.instance.return_value = project
            self.mixin.scale()
            mock_bar.return_value.setUnits.assert_called_once_with(
                self.mod.QgsUnitTypes.DistanceKilometers)
            mock_bar.return_value.setUnitLabel.assert_called_once_with('كم')

    def test_scale_uses_meters_when_scale_small(self):
        project = MagicMock()
        with patch.object(self.mod, 'QgsProject') as mock_qp, \
             patch.object(self.mod, 'QgsPrintLayout'), \
             patch.object(self.mod, 'QgsLayoutItemPage'), \
             patch.object(self.mod, 'QgsLayoutItemMap'), \
             patch.object(self.mod, 'QgsLayoutItemScaleBar') as mock_bar, \
             patch.object(self.mod, 'QgsBasicNumericFormat'), \
             patch.object(self.mod, 'QgsLayoutExporter'):
            mock_qp.instance.return_value = project
            self.mixin.scale()
            mock_bar.return_value.setUnits.assert_called_once_with(
                self.mod.QgsUnitTypes.DistanceMeters)
            mock_bar.return_value.setUnitLabel.assert_called_once_with('م')

    def test_scale_exports_svg(self):
        project = MagicMock()
        with patch.object(self.mod, 'QgsProject') as mock_qp, \
             patch.object(self.mod, 'QgsPrintLayout'), \
             patch.object(self.mod, 'QgsLayoutItemPage'), \
             patch.object(self.mod, 'QgsLayoutItemMap'), \
             patch.object(self.mod, 'QgsLayoutItemScaleBar'), \
             patch.object(self.mod, 'QgsBasicNumericFormat'), \
             patch.object(self.mod, 'QgsLayoutExporter') as mock_exporter:
            mock_qp.instance.return_value = project
            self.mixin.scale()
            mock_exporter.return_value.exportToSvg.assert_called_once()


if __name__ == '__main__':
    unittest.main()
