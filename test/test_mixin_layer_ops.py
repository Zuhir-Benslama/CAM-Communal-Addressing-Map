"""Tests for mixins.layer_ops_mixin."""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from test.helpers import setup_gui_mocks


class TestLayerOpsMixin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.mixins.layer_ops_mixin',
            'mixins/layer_ops_mixin.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.mixins.layer_ops_mixin'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.mixin = self.mod.LayerOpsMixin()
        self.mixin._tr = lambda s: s
        self.mixin.iface = MagicMock()
        self.mixin.dock_widget = MagicMock()
        self.mixin.dialog = MagicMock()
        self.mixin.tab = MagicMock()
        self.mixin.identify_tool = MagicMock()
        self.mixin.ref_identify_tool = MagicMock()
        self.mixin.measure_tool = MagicMock()
        self.mixin.sat_view = None
        self.mixin.rast = None

    def test_reset_tools(self):
        self.mixin._reset_tools()
        self.mixin.identify_tool.unset_map_tool.assert_called_once()
        self.mixin.ref_identify_tool.unset_map_tool.assert_called_once()
        self.mixin.measure_tool.clear.assert_called_once()

    def test_reset_tools_none_tools(self):
        self.mixin.identify_tool = None
        self.mixin.ref_identify_tool = None
        self.mixin.measure_tool = None
        self.mixin._reset_tools()

    def test_hide_all_tab_layers(self):
        root = MagicMock()
        root.children.return_value = []
        self.mixin._hide_all_tab_layers(root)

    def _make_fake_layer_node(self, layer):
        FakeLTL = type(
            'FakeLTL', (), {'setItemVisibilityChecked': lambda self, v: None}
        )
        node = FakeLTL()
        node.layer = lambda: layer
        return node

    def test_apply_layer_visibility(self):
        layer1 = MagicMock()
        layer1.name.return_value = 'Zones'
        layer1.isEditable.return_value = False
        layer_node = self._make_fake_layer_node(layer1)
        root = MagicMock()
        root.children.return_value = [layer_node]
        with patch.object(self.mod, 'QgsLayerTreeLayer', type(layer_node)):
            result = self.mod.LayerOpsMixin._apply_layer_visibility(
                root, {'Zones'}, 'Zones'
            )
        self.assertEqual(result, layer1)

    def test_apply_layer_visibility_skips_non_layer(self):
        root = MagicMock()
        root.children.return_value = ['not_a_layer_node']
        with patch.object(self.mod, 'QgsLayerTreeLayer', type('FakeLTL', (), {})):
            result = self.mod.LayerOpsMixin._apply_layer_visibility(
                root, {'Zones'}, 'Zones'
            )
        self.assertIsNone(result)

    def test_apply_layer_visibility_skips_none_layer(self):
        layer_node = self._make_fake_layer_node(None)
        root = MagicMock()
        root.children.return_value = [layer_node]
        with patch.object(self.mod, 'QgsLayerTreeLayer', type(layer_node)):
            result = self.mod.LayerOpsMixin._apply_layer_visibility(
                root, {'Zones'}, 'Zones'
            )
        self.assertIsNone(result)

    def test_apply_layer_visibility_rollbacks_editable(self):
        layer1 = MagicMock()
        layer1.name.return_value = 'Zones'
        layer1.isEditable.return_value = True
        layer_node = self._make_fake_layer_node(layer1)
        root = MagicMock()
        root.children.return_value = [layer_node]
        with patch.object(self.mod, 'QgsLayerTreeLayer', type(layer_node)):
            self.mod.LayerOpsMixin._apply_layer_visibility(root, {'Zones'}, 'Zones')
        layer1.rollBack.assert_called_once()
        layer1.commitChanges.assert_called_once()

    def test_show_layers_for_label(self):
        layer1 = MagicMock()
        layer1.name.return_value = 'Zones'
        FakeLTL = type('FakeLTL', (), {})
        layer_node = FakeLTL()
        layer_node.layer = MagicMock(return_value=layer1)
        layer_node.setItemVisibilityChecked = MagicMock()
        root = MagicMock()
        root.children.return_value = [layer_node]
        self.mixin.sat_view = 'Satellite'
        with (
            patch.object(self.mod, 'QgsLayerTreeLayer', FakeLTL),
            patch.object(self.mod, 'qgis_config') as mock_cfg,
        ):
            mock_cfg.return_value = {
                'other_layers': [{'label': 'Zones', 'show_with': ['Panels']}]
            }
            self.mixin._show_layers_for_label(root, 'Zones')
        self.mixin.iface.setActiveLayer.assert_called_once_with(layer1)

    def test_check_geometry_in_zone_point_inside(self):
        with patch.object(self.mod, 'get_user_location') as mock_loc:
            mock_loc.return_value = 'POLYGON((0 0,10 0,10 10,0 10,0 0))'
            result = self.mixin._check_geometry_in_zone('POINT(5 5)')
            self.assertEqual(result, 1)

    def test_check_geometry_in_zone_point_outside(self):
        with patch.object(self.mod, 'get_user_location') as mock_loc:
            mock_loc.return_value = 'POLYGON((0 0,10 0,10 10,0 10,0 0))'
            result = self.mixin._check_geometry_in_zone('POINT(50 50)')
            self.assertEqual(result, 0)

    def test_check_geometry_in_zone_no_location(self):
        with patch.object(self.mod, 'get_user_location') as mock_loc:
            mock_loc.return_value = None
            result = self.mixin._check_geometry_in_zone('POINT(5 5)')
            self.assertEqual(result, 1)

    def test_check_geometry_in_zone_polygon(self):
        with patch.object(self.mod, 'get_user_location') as mock_loc:
            mock_loc.return_value = 'POLYGON((0 0,10 0,10 10,0 10,0 0))'
            result = self.mixin._check_geometry_in_zone(
                'POLYGON((1 1,2 1,2 2,1 2,1 1))'
            )
            self.assertEqual(result, 2)

    def test_check_geometry_in_zone_linestring(self):
        with patch.object(self.mod, 'get_user_location') as mock_loc:
            mock_loc.return_value = 'POLYGON((0 0,10 0,10 10,0 10,0 0))'
            result = self.mixin._check_geometry_in_zone('LINESTRING(1 1,5 5)')
            self.assertEqual(result, 3)

    def test_list_road_entries(self):
        with patch.object(self.mod, 'EntityListDialog') as mock_dlg:
            self.mixin.list_road_entries()
            mock_dlg.assert_called_once()

    def test_list_organizations(self):
        with patch.object(self.mod, 'EntityListDialog') as mock_dlg:
            self.mixin.list_organizations()
            mock_dlg.assert_called_once()

    def test_list_subdivisions(self):
        with patch.object(self.mod, 'EntityListDialog') as mock_dlg:
            self.mixin.list_subdivisions()
            mock_dlg.assert_called_once()

    def test_list_numberings(self):
        with patch.object(self.mod, 'EntityListDialog') as mock_dlg:
            self.mixin.list_numberings()
            mock_dlg.assert_called_once()

    def test_list_panel_signs(self):
        with patch.object(self.mod, 'EntityListDialog') as mock_dlg:
            self.mixin.list_panel_signs()
            mock_dlg.assert_called_once()
