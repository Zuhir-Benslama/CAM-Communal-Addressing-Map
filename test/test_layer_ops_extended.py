"""Extended tests for mixins/layer_ops_mixin.py covering uncovered methods."""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from test.helpers import setup_gui_mocks


class TestLayerOpsMixinExtended(unittest.TestCase):
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
        self.mixin.menu = MagicMock()
        self.mixin.num_val = MagicMock()
        self.mixin.identify_tool = MagicMock()
        self.mixin.ref_identify_tool = MagicMock()
        self.mixin.measure_tool = MagicMock()
        self.mixin.sat_view = None
        self.mixin.rast = None
        self.mixin._current_layer_name = lambda: ''
        self.mixin._last_loaded_tab = None
        self.mixin._last_feature_id = None
        self.mixin._last_feature_wkt = None
        self.mixin._geometry_ready = None
        self.mixin._reconnect_context_menu = MagicMock()

    # ------------------------------------------------------------------
    # _load_tab_styles
    # ------------------------------------------------------------------

    def test_load_tab_styles_valid_layer_tuple_success(self):
        layer = MagicMock()
        layer.loadNamedStyle.return_value = (True, 'ok')
        with patch.object(self.mod.QgsProject, 'instance') as mock_inst:
            mock_inst.return_value.mapLayersByName.return_value = [layer]
            self.mod.LayerOpsMixin._load_tab_styles(
                [{'label': 'Roads', 'style': 'road.qml'}],
                '/tmp/styles',
            )
        layer.loadNamedStyle.assert_called_once()

    def test_load_tab_styles_valid_layer_tuple_failure(self):
        layer = MagicMock()
        layer.loadNamedStyle.return_value = (False, 'error msg')
        with patch.object(self.mod.QgsProject, 'instance') as mock_inst:
            mock_inst.return_value.mapLayersByName.return_value = [layer]
            self.mod.LayerOpsMixin._load_tab_styles(
                [{'label': 'Roads', 'style': 'road.qml'}],
                '/tmp/styles',
            )
        layer.loadNamedStyle.assert_called_once()

    def test_load_tab_styles_non_tuple_result(self):
        layer = MagicMock()
        layer.loadNamedStyle.return_value = 'unexpected_string'
        with patch.object(self.mod.QgsProject, 'instance') as mock_inst:
            mock_inst.return_value.mapLayersByName.return_value = [layer]
            self.mod.LayerOpsMixin._load_tab_styles(
                [{'label': 'Roads', 'style': 'road.qml'}],
                '/tmp/styles',
            )
        layer.loadNamedStyle.assert_called_once()

    def test_load_tab_styles_layer_not_found(self):
        with patch.object(self.mod.QgsProject, 'instance') as mock_inst:
            mock_inst.return_value.mapLayersByName.return_value = []
            self.mod.LayerOpsMixin._load_tab_styles(
                [{'label': 'NonExistent', 'style': 'style.qml'}],
                '/tmp/styles',
            )

    def test_load_tab_styles_multiple_layers(self):
        layer1 = MagicMock()
        layer1.loadNamedStyle.return_value = (True, '')
        layer2 = MagicMock()
        layer2.loadNamedStyle.return_value = (False, 'err')
        with patch.object(self.mod.QgsProject, 'instance') as mock_inst:
            mock_inst.return_value.mapLayersByName.side_effect = [
                [layer1],
                [layer2],
            ]
            self.mod.LayerOpsMixin._load_tab_styles(
                [{'label': 'A', 'style': 'a.qml'}, {'label': 'B', 'style': 'b.qml'}],
                '/styles',
            )
        layer1.loadNamedStyle.assert_called_once()
        layer2.loadNamedStyle.assert_called_once()

    def test_load_tab_styles_empty_data_list(self):
        with patch.object(self.mod.QgsProject, 'instance') as mock_inst:
            self.mod.LayerOpsMixin._load_tab_styles([], '/tmp/styles')
            mock_inst.return_value.mapLayersByName.assert_not_called()

    # ------------------------------------------------------------------
    # _current_ops_layer
    # ------------------------------------------------------------------

    def test_current_ops_layer_returns_empty_when_no_attr(self):
        del self.mixin._current_layer_name
        result = self.mixin._current_ops_layer()
        self.assertEqual(result, '')

    def test_current_ops_layer_returns_empty_string(self):
        self.mixin._current_layer_name = lambda: ''
        result = self.mixin._current_ops_layer()
        self.assertEqual(result, '')

    def test_current_ops_layer_returns_layer_name(self):
        self.mixin._current_layer_name = lambda: 'Roads'
        result = self.mixin._current_ops_layer()
        self.assertEqual(result, 'Roads')

    # ------------------------------------------------------------------
    # _handle_ops_tab
    # ------------------------------------------------------------------

    def test_handle_ops_tab_operations_tab_sets_ops_prefix(self):
        self.mixin._show_layers_for_label = MagicMock()
        self.mixin._load_tab_styles = MagicMock()
        root = MagicMock()
        root.children.return_value = []
        with patch.object(self.mod, 'qgis_config') as mock_cfg:
            mock_cfg.return_value = {'other_layers': [{'label': 'Roads'}]}
            self.mixin._handle_ops_tab(root, 'Operations', 'Roads')
        self.mixin._show_layers_for_label.assert_called_once_with(root, 'Roads')
        self.assertEqual(self.mixin._last_loaded_tab, 'ops:Roads')

    def test_handle_ops_tab_non_operations_tab_no_prefix(self):
        self.mixin._show_layers_for_label = MagicMock()
        self.mixin._load_tab_styles = MagicMock()
        root = MagicMock()
        root.children.return_value = []
        with patch.object(self.mod, 'qgis_config') as mock_cfg:
            mock_cfg.return_value = {'other_layers': []}
            self.mixin._handle_ops_tab(root, 'Zones', 'Zones')
        self.assertEqual(self.mixin._last_loaded_tab, 'Zones')

    def test_handle_ops_tab_skips_load_when_same_tab(self):
        self.mixin._show_layers_for_label = MagicMock()
        self.mixin._load_tab_styles = MagicMock()
        self.mixin._last_loaded_tab = 'ops:Roads'
        root = MagicMock()
        root.children.return_value = []
        with patch.object(self.mod, 'qgis_config') as mock_cfg:
            mock_cfg.return_value = {'other_layers': []}
            self.mixin._handle_ops_tab(root, 'Operations', 'Roads')
        self.mixin._load_tab_styles.assert_not_called()

    # ------------------------------------------------------------------
    # _handle_default_tab
    # ------------------------------------------------------------------

    def _make_fake_ltl(self, layer):
        FakeLTL = type(
            'FakeLTL', (), {'setItemVisibilityChecked': lambda self, v: None}
        )
        node = FakeLTL()
        node.layer = lambda: layer
        return node

    def test_handle_default_tab_hides_panels_and_numbering(self):
        layer_r = MagicMock()
        layer_r.name.return_value = 'Roads'
        layer_r.isEditable.return_value = False
        layer_z = MagicMock()
        layer_z.name.return_value = 'Zones'
        layer_z.isEditable.return_value = False
        layer_p = MagicMock()
        layer_p.name.return_value = 'Panels'
        layer_p.isEditable.return_value = False
        layer_n = MagicMock()
        layer_n.name.return_value = 'Numbering'
        layer_n.isEditable.return_value = False
        nodes = [self._make_fake_ltl(lyr) for lyr in (layer_r, layer_z, layer_p, layer_n)]
        root = MagicMock()
        root.children.return_value = nodes
        with patch.object(self.mod, 'QgsLayerTreeLayer', type(nodes[0])):
            self.mixin._handle_default_tab(root)

    def test_handle_default_tab_rollbacks_editable_layers(self):
        layer = MagicMock()
        layer.name.return_value = 'Roads'
        layer.isEditable.return_value = True
        node = self._make_fake_ltl(layer)
        root = MagicMock()
        root.children.return_value = [node]
        with patch.object(self.mod, 'QgsLayerTreeLayer', type(node)):
            self.mixin._handle_default_tab(root)
        layer.rollBack.assert_called_once()
        layer.commitChanges.assert_called_once()

    def test_handle_default_tab_skips_non_layer_nodes(self):
        root = MagicMock()
        root.children.return_value = ['not_a_layer_node']
        FakeLTL = type('FakeLTL', (), {})
        with patch.object(self.mod, 'QgsLayerTreeLayer', FakeLTL):
            self.mixin._handle_default_tab(root)

    # ------------------------------------------------------------------
    # on_opt_selected
    # ------------------------------------------------------------------

    def test_on_opt_selected_empty_layer_calls_default_tab(self):
        self.mixin._current_layer_name = lambda: ''
        self.mixin.menu.tabText.return_value = 'General'
        canvas = MagicMock()
        self.mixin.iface.mapCanvas.return_value = canvas
        self.mixin._handle_default_tab = MagicMock()
        self.mixin._handle_ops_tab = MagicMock()
        self.mixin.on_opt_selected(0)
        self.mixin._handle_default_tab.assert_called_once()
        self.mixin._handle_ops_tab.assert_not_called()

    def test_on_opt_selected_with_layer_calls_ops_tab(self):
        self.mixin._current_layer_name = lambda: 'Roads'
        self.mixin.menu.tabText.return_value = 'Operations'
        canvas = MagicMock()
        self.mixin.iface.mapCanvas.return_value = canvas
        self.mixin._handle_ops_tab = MagicMock()
        self.mixin._handle_default_tab = MagicMock()
        self.mixin.on_opt_selected(0)
        self.mixin._handle_ops_tab.assert_called_once()
        self.mixin._handle_default_tab.assert_not_called()

    def test_on_opt_selected_resets_tools(self):
        self.mixin._current_layer_name = lambda: ''
        self.mixin.menu.tabText.return_value = 'Tab'
        self.mixin._handle_default_tab = MagicMock()
        self.mixin.on_opt_selected(0)
        self.mixin.identify_tool.unset_map_tool.assert_called_once()
        self.mixin.ref_identify_tool.unset_map_tool.assert_called_once()
        self.mixin.measure_tool.clear.assert_called_once()

    def test_on_opt_selected_clears_type_plan(self):
        self.mixin._current_layer_name = lambda: ''
        self.mixin.menu.tabText.return_value = 'Tab'
        self.mixin._handle_default_tab = MagicMock()
        self.mixin.type_plan = 'old'
        self.mixin.on_opt_selected(0)
        self.assertEqual(self.mixin.type_plan, '')

    def test_on_opt_selected_refreshes_canvas(self):
        self.mixin._current_layer_name = lambda: ''
        self.mixin.menu.tabText.return_value = 'Tab'
        self.mixin._handle_default_tab = MagicMock()
        canvas = MagicMock()
        self.mixin.iface.mapCanvas.return_value = canvas
        self.mixin.on_opt_selected(0)
        canvas.refresh.assert_called_once()

    # ------------------------------------------------------------------
    # on_feature_added
    # ------------------------------------------------------------------

    def _setup_feature_added(self, zone_case=1):
        layer = MagicMock()
        layer.name.return_value = 'Roads'
        layer.isEditable.return_value = True
        feature = MagicMock()
        feature.isValid.return_value = True
        feature.__getitem__ = lambda self_, k: 'uuid-1234'
        feature.__setitem__ = lambda self_, k, v: None
        feature.geometry.return_value.asWkt.return_value = 'POINT(5 5)'
        layer.getFeature.return_value = feature
        self.mixin.iface.activeLayer.return_value = layer
        self.mixin._check_geometry_in_zone = MagicMock(return_value=zone_case)
        self.mixin.menu.currentIndex.return_value = 0
        self.mixin.menu.tabText.return_value = 'other'
        self.mixin._current_layer_name = lambda: 'Roads'
        inner_canvas = MagicMock()
        self.mixin.iface.mapCanvas.return_value = inner_canvas
        return layer, feature, inner_canvas

    def test_on_feature_added_deletes_when_outside_zone(self):
        layer, _feature, _ = self._setup_feature_added(zone_case=0)
        del_feature = MagicMock()
        del_feature.isValid.return_value = True
        layer.getFeature.return_value = del_feature
        self.mixin.on_feature_added(1)
        layer.deleteFeature.assert_called_once()

    def test_on_feature_added_saves_when_inside_zone(self):
        layer, feature, _ = self._setup_feature_added(zone_case=1)
        layer.getFeature.return_value = feature
        self.mixin.on_feature_added(1)
        self.assertEqual(self.mixin._last_feature_id, 'uuid-1234')
        self.assertEqual(self.mixin._last_feature_wkt, 'POINT(5 5)')
        layer.commitChanges.assert_called_once()

    def test_on_feature_added_unsets_canvas_tool_when_saved(self):
        layer, feature, inner_canvas = self._setup_feature_added(zone_case=2)
        layer.getFeature.return_value = feature
        self.mixin.on_feature_added(1)
        inner_canvas.unsetMapTool.assert_called()

    def test_on_feature_added_sets_geometry_ready(self):
        layer, feature, _ = self._setup_feature_added(zone_case=1)
        layer.getFeature.return_value = feature
        self.mixin.on_feature_added(1)
        self.assertEqual(self.mixin._geometry_ready, 'Roads')

    def test_on_feature_added_skips_invalid_feature(self):
        layer = MagicMock()
        layer.isEditable.return_value = True
        feature = MagicMock()
        feature.isValid.return_value = False
        layer.getFeature.return_value = feature
        self.mixin.iface.activeLayer.return_value = layer
        self.mixin.on_feature_added(1)
        layer.deleteFeature.assert_not_called()

    def test_on_feature_added_skips_when_layer_not_editable(self):
        layer = MagicMock()
        layer.isEditable.return_value = False
        self.mixin.iface.activeLayer.return_value = layer
        self.mixin.on_feature_added(1)

    def test_on_feature_added_skips_when_no_active_layer(self):
        self.mixin.iface.activeLayer.return_value = None
        self.mixin.on_feature_added(1)

    def test_on_feature_added_numbering_tab_focuses_num_val(self):
        layer, feature, _ = self._setup_feature_added(zone_case=1)
        layer.getFeature.return_value = feature
        self.mixin.menu.tabText.return_value = 'numbering'
        self.mixin.on_feature_added(1)
        self.mixin.num_val.setFocus.assert_called_once()

    def test_on_feature_added_numbering_layer_focuses_num_val(self):
        layer, feature, _ = self._setup_feature_added(zone_case=1)
        layer.getFeature.return_value = feature
        self.mixin._current_layer_name = lambda: 'numbering'
        self.mixin.on_feature_added(1)
        self.mixin.num_val.setFocus.assert_called_once()

    def test_on_feature_added_del_feature_invalid_skips_delete(self):
        layer, _feature, _ = self._setup_feature_added(zone_case=0)
        del_feature = MagicMock()
        del_feature.isValid.return_value = False
        layer.getFeature.return_value = del_feature
        self.mixin.on_feature_added(1)
        layer.deleteFeature.assert_not_called()

    def test_on_feature_added_disconnects_feature_added_signal(self):
        layer, feature, _ = self._setup_feature_added(zone_case=1)
        layer.getFeature.return_value = feature
        self.mixin.on_feature_added(1)
        layer.featureAdded.disconnect.assert_called_once()

    # ------------------------------------------------------------------
    # on_geometry_changed
    # ------------------------------------------------------------------

    def _make_geo_layer(self, name='Roads'):
        layer = MagicMock()
        layer.name.return_value = name
        layer.isEditable.return_value = True
        feature = MagicMock()
        feature.isValid.return_value = True
        feature.__getitem__ = lambda self_, k: 'uuid-db'
        feature.geometry.return_value.asWkt.return_value = 'POINT(3 3)'
        layer.getFeature.return_value = feature
        self.mixin.iface.activeLayer.return_value = layer
        self.mixin._check_geometry_in_zone = MagicMock(return_value=1)
        return layer, feature

    def test_on_geometry_changed_rollbacks_when_outside_zone(self):
        layer = MagicMock()
        layer.name.return_value = 'Roads'
        layer.isEditable.return_value = True
        feature = MagicMock()
        feature.isValid.return_value = True
        feature.geometry.return_value.asWkt.return_value = 'POINT(50 50)'
        layer.getFeature.return_value = feature
        self.mixin.iface.activeLayer.return_value = layer
        self.mixin._check_geometry_in_zone = MagicMock(return_value=0)
        with patch.object(self.mod, 'QMessageBox') as mock_msgbox:
            self.mixin.on_geometry_changed(1)
        layer.rollBack.assert_called_once()
        mock_msgbox.warning.assert_called_once()

    def test_on_geometry_changed_updates_db_when_valid(self):
        _layer, _feature = self._make_geo_layer()
        mock_session = MagicMock()
        mock_model = MagicMock()
        mock_models = MagicMock()
        mock_models.Road = mock_model
        with (
            patch.object(self.mod, '_models', mock_models),
            patch.object(self.mod, 'get_session', return_value=mock_session),
            patch.object(self.mod, 'qgis_config') as mock_cfg,
        ):
            mock_cfg.return_value = {'mapper': [{'layer': 'Roads', 'model': 'Road'}]}
            self.mixin.on_geometry_changed(1)
        mock_model.update.assert_called_once()

    def test_on_geometry_changed_handles_sqlalchemy_error(self):
        _layer, _feature = self._make_geo_layer()
        from sqlalchemy.exc import SQLAlchemyError

        mock_session = MagicMock()
        mock_model = MagicMock()
        mock_model.update.side_effect = SQLAlchemyError('db failure')
        mock_models = MagicMock()
        mock_models.Road = mock_model
        with (
            patch.object(self.mod, '_models', mock_models),
            patch.object(self.mod, 'get_session', return_value=mock_session),
            patch.object(self.mod, 'qgis_config') as mock_cfg,
            patch.object(self.mod, 'QMessageBox') as mock_msgbox,
        ):
            mock_cfg.return_value = {'mapper': [{'layer': 'Roads', 'model': 'Road'}]}
            self.mixin.on_geometry_changed(1)
        mock_msgbox.critical.assert_called_once()

    def test_on_geometry_changed_skips_invalid_feature(self):
        layer = MagicMock()
        layer.isEditable.return_value = True
        feature = MagicMock()
        feature.isValid.return_value = False
        layer.getFeature.return_value = feature
        self.mixin.iface.activeLayer.return_value = layer
        self.mixin._check_geometry_in_zone = MagicMock()
        self.mixin.on_geometry_changed(1)
        self.mixin._check_geometry_in_zone.assert_not_called()

    def test_on_geometry_changed_skips_when_not_editable(self):
        layer = MagicMock()
        layer.isEditable.return_value = False
        self.mixin.iface.activeLayer.return_value = layer
        self.mixin.on_geometry_changed(1)

    def test_on_geometry_changed_skips_when_no_layer(self):
        self.mixin.iface.activeLayer.return_value = None
        self.mixin.on_geometry_changed(1)

    def test_on_geometry_changed_skips_non_matching_mapper(self):
        layer = MagicMock()
        layer.isEditable.return_value = True
        feature = MagicMock()
        feature.isValid.return_value = True
        feature.__getitem__ = lambda self_, k: 'id-val'
        feature.geometry.return_value.asWkt.return_value = 'POINT(5 5)'
        layer.getFeature.return_value = feature
        self.mixin.iface.activeLayer.return_value = layer
        self.mixin._check_geometry_in_zone = MagicMock(return_value=1)
        with patch.object(self.mod, 'qgis_config') as mock_cfg:
            mock_cfg.return_value = {'mapper': [{'layer': 'Zones', 'model': 'Zone'}]}
            self.mixin.on_geometry_changed(1)

    def test_on_geometry_changed_session_always_closed(self):
        _layer, _feature = self._make_geo_layer()
        from sqlalchemy.exc import SQLAlchemyError

        mock_session = MagicMock()
        mock_model = MagicMock()
        mock_model.update.side_effect = SQLAlchemyError('fail')
        mock_models = MagicMock()
        mock_models.Road = mock_model
        with (
            patch.object(self.mod, '_models', mock_models),
            patch.object(self.mod, 'get_session', return_value=mock_session),
            patch.object(self.mod, 'qgis_config') as mock_cfg,
            patch.object(self.mod, 'QMessageBox'),
        ):
            mock_cfg.return_value = {'mapper': [{'layer': 'Roads', 'model': 'Road'}]}
            self.mixin.on_geometry_changed(1)
        mock_session.close.assert_called()

    def test_on_geometry_changed_null_mapper_list(self):
        layer = MagicMock()
        layer.isEditable.return_value = True
        feature = MagicMock()
        feature.isValid.return_value = True
        feature.geometry.return_value.asWkt.return_value = 'POINT(5 5)'
        layer.getFeature.return_value = feature
        self.mixin.iface.activeLayer.return_value = layer
        self.mixin._check_geometry_in_zone = MagicMock(return_value=1)
        with patch.object(self.mod, 'qgis_config') as mock_cfg:
            mock_cfg.return_value = {'mapper': None}
            self.mixin.on_geometry_changed(1)


if __name__ == '__main__':
    unittest.main()
