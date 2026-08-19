"""Extended tests for gui/identify_tool.py covering uncovered methods."""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from test.helpers import get_qapp, setup_gui_mocks


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestIdentifyMode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.identify_tool',
            'gui/identify_tool.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.identify_tool'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def test_identify_mode_form_value(self):
        self.assertEqual(self.mod.IdentifyMode.FORM.value, 'form')

    def test_identify_mode_ref_value(self):
        self.assertEqual(self.mod.IdentifyMode.REF.value, 'ref')

    def test_identify_mode_members_count(self):
        self.assertEqual(len(self.mod.IdentifyMode), 2)

    def test_mode_form_class_attr_matches_enum(self):
        self.assertEqual(self.mod.IdentifyTool.MODE_FORM, self.mod.IdentifyMode.FORM)

    def test_mode_ref_class_attr_matches_enum(self):
        self.assertEqual(self.mod.IdentifyTool.MODE_REF, self.mod.IdentifyMode.REF)


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestIdentifyToolInit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.identify_tool',
            'gui/identify_tool.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.identify_tool'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def test_form_mode_init_defaults(self):
        canvas = MagicMock()
        tool = self.mod.IdentifyTool(canvas)
        self.assertEqual(tool.mode, self.mod.IdentifyMode.FORM)
        self.assertIsNone(tool._active_layer)
        self.assertIsNone(tool._iface)
        self.assertIsNone(tool.dlg)

    def test_form_mode_no_ref_attrs(self):
        canvas = MagicMock()
        tool = self.mod.IdentifyTool(canvas)
        self.assertFalse(hasattr(tool, 'feature_id'))

    def test_ref_mode_init_defaults(self):
        canvas = MagicMock()
        tool = self.mod.IdentifyTool(canvas, mode=self.mod.IdentifyMode.REF)
        self.assertEqual(tool.mode, self.mod.IdentifyMode.REF)
        self.assertIsNone(tool.feature_id)
        self.assertIsNone(tool.feature_type)
        self.assertIsNone(tool.feature_name)

    def test_canvas_stored(self):
        canvas = MagicMock()
        tool = self.mod.IdentifyTool(canvas)
        self.assertIs(tool.canvas, canvas)


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestIdentifyToolAccessors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.identify_tool',
            'gui/identify_tool.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.identify_tool'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.canvas = MagicMock()
        self.tool = self.mod.IdentifyTool(self.canvas)

    def test_set_active_layer(self):
        layer = MagicMock()
        self.tool.set_active_layer(layer)
        self.assertIs(self.tool._active_layer, layer)

    def test_get_active_layer(self):
        layer = MagicMock()
        self.tool._active_layer = layer
        self.assertIs(self.tool.get_active_layer(), layer)

    def test_get_active_layer_none(self):
        self.assertIsNone(self.tool.get_active_layer())

    def test_set_iface(self):
        iface = MagicMock()
        self.tool.set_iface(iface)
        self.assertIs(self.tool._iface, iface)

    def test_get_iface(self):
        iface = MagicMock()
        self.tool._iface = iface
        self.assertIs(self.tool.get_iface(), iface)

    def test_get_iface_none(self):
        self.assertIsNone(self.tool.get_iface())

    def test_get_id_with_layer(self):
        layer = MagicMock()
        layer.name.return_value = 'Zones'
        self.tool.feature_id = 'uuid-abc'
        self.tool.set_active_layer(layer)
        result = self.tool.get_id()
        self.assertEqual(result, {'id': 'uuid-abc', 'layer_name': 'Zones'})

    def test_get_id_without_layer(self):
        self.tool.feature_id = 'pk-1'
        result = self.tool.get_id()
        self.assertEqual(result, {'id': 'pk-1', 'layer_name': ''})

    def test_get_id_with_none_id(self):
        layer = MagicMock()
        layer.name.return_value = 'Roads'
        self.tool.set_active_layer(layer)
        self.tool.feature_id = None
        result = self.tool.get_id()
        self.assertEqual(result, {'id': None, 'layer_name': 'Roads'})


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestIdentifyToolCanvasEvents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        # Patch the fake base class to support TopDownAll and identify()
        gui_mod = sys.modules.get('qgis.gui')
        if hasattr(gui_mod.QgsMapToolIdentify, 'TopDownAll') is False:
            gui_mod.QgsMapToolIdentify.TopDownAll = 1
        if not hasattr(gui_mod.QgsMapToolIdentify, 'identify'):
            gui_mod.QgsMapToolIdentify.identify = lambda self, *a: []

        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.identify_tool',
            'gui/identify_tool.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.identify_tool'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.canvas = MagicMock()
        self.tool = self.mod.IdentifyTool(self.canvas)
        self.tool._active_layer = MagicMock()
        self.tool._iface = MagicMock()

    def _make_event(self, button):
        event = MagicMock()
        event.button.return_value = button
        event.x.return_value = 100
        event.y.return_value = 200
        event.globalPos.return_value = MagicMock()
        return event

    def test_canvas_release_left_button_with_results(self):
        event = self._make_event(1)
        fake_result = MagicMock()
        fake_result.mFeature = {'id': 'feat-1', 'fields': MagicMock()}
        self.tool.identify = MagicMock(return_value=[fake_result])
        with patch.object(self.tool, '_build_form_menu') as mock_menu:
            self.tool.canvasReleaseEvent(event)
        mock_menu.assert_called_once()

    def test_canvas_release_left_button_no_results(self):
        event = self._make_event(1)
        self.tool.identify = MagicMock(return_value=[])
        with patch.object(self.tool, '_build_form_menu') as mock_menu:
            self.tool.canvasReleaseEvent(event)
        mock_menu.assert_not_called()

    def test_canvas_release_right_button_unsets_tool(self):
        event = self._make_event(2)
        self.tool.canvasReleaseEvent(event)
        self.canvas.unsetMapTool.assert_called_once_with(self.tool)

    def test_canvas_release_ref_mode_builds_ref_menu(self):
        self.tool.mode = self.mod.IdentifyMode.REF
        event = self._make_event(1)
        fake_result = MagicMock()
        fake_result.mFeature = {'id': 'feat-2', 'fields': MagicMock()}
        self.tool.identify = MagicMock(return_value=[fake_result])
        with patch.object(self.tool, '_build_ref_menu') as mock_menu:
            self.tool.canvasReleaseEvent(event)
        mock_menu.assert_called_once()

    def test_canvas_release_left_calls_identify_with_active_layer(self):
        event = self._make_event(1)
        self.tool.identify = MagicMock(return_value=[])
        self.tool.canvasReleaseEvent(event)
        self.tool.identify.assert_called_once()


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestIdentifyToolUnset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.identify_tool',
            'gui/identify_tool.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.identify_tool'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def test_unset_map_tool(self):
        canvas = MagicMock()
        tool = self.mod.IdentifyTool(canvas)
        tool.unset_map_tool()
        canvas.unsetMapTool.assert_called_once_with(tool)


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestIdentifyToolFormFeature(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.identify_tool',
            'gui/identify_tool.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.identify_tool'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.canvas = MagicMock()
        self.tool = self.mod.IdentifyTool(self.canvas)
        layer = MagicMock()
        layer.name.return_value = 'Roads'
        self.tool.set_active_layer(layer)
        self.tool.set_iface(MagicMock())

    def test_display_or_update_form_feature_creates_dialog(self):
        MockPopup = MagicMock()
        self.tool.dlg = None
        with patch.dict(
            'sys.modules',
            {
                'plans_adressage.gui.popup_dialog': MockPopup,
            },
        ), patch.object(self.mod, 'LAYER_KEY', {'Roads': 'roads_key'}):
            self.tool.display_or_update_form_feature('feat-1')
        self.tool.dlg.show.assert_called_once()
        self.tool.dlg.exec.assert_called_once()

    def test_display_or_update_form_feature_closes_existing_dlg(self):
        old_dlg = MagicMock()
        self.tool.dlg = old_dlg
        MockPopup = MagicMock()
        with patch.dict(
            'sys.modules',
            {
                'plans_adressage.gui.popup_dialog': MockPopup,
            },
        ), patch.object(self.mod, 'LAYER_KEY', {'Roads': 'roads_key'}):
            self.tool.display_or_update_form_feature('feat-2')
        old_dlg.close.assert_called_once()
        self.tool.dlg.show.assert_called_once()


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestIdentifyToolDeleteFeature(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.identify_tool',
            'gui/identify_tool.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.identify_tool'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.canvas = MagicMock()
        self.tool = self.mod.IdentifyTool(self.canvas)
        layer = MagicMock()
        layer.name.return_value = 'Roads'
        self.tool.set_active_layer(layer)

    def test_delete_feature_with_mapper_match(self):
        mock_session = MagicMock()
        query_result = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = (
            query_result
        )
        mock_model = MagicMock()
        self.mod._models = MagicMock()
        self.mod._models.Road = mock_model
        with (
            patch.object(self.mod, 'get_session', return_value=mock_session),
            patch.object(self.mod, 'qgis_config') as mock_cfg,
        ):
            mock_cfg.return_value = {
                'mapper': [{'layer': 'Roads', 'model': 'Road'}],
            }
            self.tool.delete_feature('pk-1')
        query_result.delete.assert_called_once_with(mock_session)
        mock_session.close.assert_called_once()

    def test_delete_feature_unknown_model_returns(self):
        mock_session = MagicMock()
        self.mod._models = MagicMock()
        self.mod._models.Unknown = None
        with (
            patch.object(self.mod, 'get_session', return_value=mock_session),
            patch.object(self.mod, 'qgis_config') as mock_cfg,
        ):
            mock_cfg.return_value = {
                'mapper': [{'layer': 'Roads', 'model': 'Unknown'}],
            }
            self.tool.delete_feature('pk-1')
        mock_session.close.assert_called()

    def test_delete_feature_no_mapper_match(self):
        with (
            patch.object(self.mod, 'get_session'),
            patch.object(self.mod, 'qgis_config') as mock_cfg,
        ):
            mock_cfg.return_value = {
                'mapper': [{'layer': 'Zones', 'model': 'Zone'}],
            }
            self.tool.delete_feature('pk-1')
        self.canvas.refresh.assert_called_once()

    def test_delete_feature_starts_editing_and_commits(self):
        layer = self.tool.get_active_layer()
        mock_session = MagicMock()
        mock_model = MagicMock()
        mock_model.query.return_value.filter.return_value.first.return_value = (
            MagicMock()
        )
        self.mod._models = MagicMock()
        self.mod._models.Road = mock_model
        with (
            patch.object(self.mod, 'get_session', return_value=mock_session),
            patch.object(self.mod, 'qgis_config') as mock_cfg,
        ):
            mock_cfg.return_value = {
                'mapper': [{'layer': 'Roads', 'model': 'Road'}],
            }
            self.tool.delete_feature('pk-1')
        layer.startEditing.assert_called_once()
        layer.commitChanges.assert_called_once()
        layer.triggerRepaint.assert_called_once()

    def test_delete_feature_removes_features_by_id(self):
        layer = self.tool.get_active_layer()
        feat = MagicMock()
        feat.id.return_value = 42
        layer.getFeatures.return_value = [feat]
        mock_session = MagicMock()
        mock_model = MagicMock()
        mock_model.query.return_value.filter.return_value.first.return_value = (
            MagicMock()
        )
        self.mod._models = MagicMock()
        self.mod._models.Road = mock_model
        with (
            patch.object(self.mod, 'get_session', return_value=mock_session),
            patch.object(self.mod, 'qgis_config') as mock_cfg,
            patch.object(self.mod, 'QgsFeatureRequest'),
            patch.object(self.mod, 'QgsExpression') as mock_expr,
        ):
            mock_cfg.return_value = {
                'mapper': [{'layer': 'Roads', 'model': 'Road'}],
            }
            mock_expr.quotedValue.return_value = "'pk-1'"
            self.tool.delete_feature('pk-1')
        layer.deleteFeature.assert_called_once_with(42)


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestIdentifyToolLocaleAttr(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.identify_tool',
            'gui/identify_tool.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.identify_tool'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.canvas = MagicMock()
        self.tool = self.mod.IdentifyTool(self.canvas)

    def test_locale_ar_uses_base_name(self):
        feature = MagicMock()
        feature.__getitem__ = lambda f, k: 'المتحف'
        with patch.object(self.mod, 'current_locale', return_value='ar'):
            result = self.tool._locale_feature_attr(feature, 'name')
        self.assertEqual(result, 'المتحف')

    def test_locale_fr_uses_localized_field(self):
        feature = MagicMock()
        feature.__getitem__ = lambda f, k: 'Musée' if k == 'name_fr' else 'Museum'
        feature.fields.return_value.names.return_value = ['name_fr', 'name']
        with patch.object(self.mod, 'current_locale', return_value='fr'):
            result = self.tool._locale_feature_attr(feature, 'name')
        self.assertEqual(result, 'Musée')

    def test_locale_en_uses_localized_field(self):
        feature = MagicMock()
        feature.__getitem__ = lambda f, k: 'Museum' if k == 'name_en' else 'Musée'
        feature.fields.return_value.names.return_value = ['name_en', 'name']
        with patch.object(self.mod, 'current_locale', return_value='en'):
            result = self.tool._locale_feature_attr(feature, 'name')
        self.assertEqual(result, 'Museum')

    def test_locale_fr_falls_back_when_field_empty(self):
        feature = MagicMock()
        feature.__getitem__ = lambda f, k: None if k == 'name_fr' else 'Fallback'
        feature.fields.return_value.names.return_value = ['name_fr', 'name']
        with patch.object(self.mod, 'current_locale', return_value='fr'):
            result = self.tool._locale_feature_attr(feature, 'name')
        self.assertEqual(result, 'Fallback')

    def test_locale_fr_falls_back_when_field_missing(self):
        feature = MagicMock()
        feature.__getitem__ = lambda f, k: 'Value'
        feature.fields.return_value.names.return_value = ['name']
        with patch.object(self.mod, 'current_locale', return_value='fr'):
            result = self.tool._locale_feature_attr(feature, 'name')
        self.assertEqual(result, 'Value')

    def test_locale_feature_attr_type_base(self):
        feature = MagicMock()
        feature.__getitem__ = lambda f, k: 'TypeAr' if k == 'type' else 'TypeFr'
        feature.fields.return_value.names.return_value = ['type_fr', 'type']
        with patch.object(self.mod, 'current_locale', return_value='ar'):
            result = self.tool._locale_feature_attr(feature, 'type')
        self.assertEqual(result, 'TypeAr')


@unittest.skipIf(get_qapp() is None, 'Qt bindings not available')
class TestIdentifyToolFeatureAsRef(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.identify_tool',
            'gui/identify_tool.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.identify_tool'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.canvas = MagicMock()
        self.tool = self.mod.IdentifyTool(self.canvas, mode=self.mod.IdentifyMode.REF)

    def test_feature_as_ref_sets_attributes(self):
        layer = MagicMock()
        layer.name.return_value = 'Facilities'
        self.tool.set_active_layer(layer)
        self.tool.ref_selected = MagicMock()
        self.tool.feature_as_ref('pk-99', 'Building', 'Library')
        self.assertEqual(self.tool.feature_id, 'pk-99')
        self.assertEqual(self.tool.feature_type, 'Building')
        self.assertEqual(self.tool.feature_name, 'Library')

    def test_feature_as_ref_emits_signal(self):
        layer = MagicMock()
        layer.name.return_value = 'Roads'
        self.tool.set_active_layer(layer)
        self.tool.ref_selected = MagicMock()
        self.tool.feature_as_ref('pk-1', 'Street', 'Main')
        self.tool.ref_selected.emit.assert_called_once_with('pk-1', 'Roads')

    def test_feature_as_ref_unsets_canvas_tool(self):
        layer = MagicMock()
        layer.name.return_value = 'Roads'
        self.tool.set_active_layer(layer)
        self.tool.ref_selected = MagicMock()
        self.tool.feature_as_ref('pk-1', 'Type', 'Name')
        self.canvas.unsetMapTool.assert_called_once_with(self.tool)

    def test_feature_as_ref_skips_emit_when_id_none(self):
        layer = MagicMock()
        layer.name.return_value = 'Roads'
        self.tool.set_active_layer(layer)
        self.tool.ref_selected = MagicMock()
        self.tool.feature_as_ref(None, 'Type', 'Name')
        self.tool.ref_selected.emit.assert_not_called()
        self.canvas.unsetMapTool.assert_not_called()

    def test_feature_as_ref_handles_none_layer(self):
        self.tool._active_layer = None
        self.tool.ref_selected = MagicMock()
        self.tool.feature_as_ref('pk-1', 'Type', 'Name')
        self.tool.ref_selected.emit.assert_called_once_with('pk-1', '')


if __name__ == '__main__':
    unittest.main()
