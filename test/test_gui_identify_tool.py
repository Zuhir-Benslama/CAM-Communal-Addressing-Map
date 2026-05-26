"""Tests for gui/identify_tool.py."""
import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from .helpers import setup_gui_mocks, get_qapp


@unittest.skipIf(get_qapp() is None, 'PyQt5 not available')
class TestIdentifyTool(unittest.TestCase):
    """Test IdentifyTool creation and signal handling."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.gui.identify_tool', 'gui/identify_tool.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.gui.identify_tool'] = cls.mod
        spec.loader.exec_module(cls.mod)
        parent = sys.modules.get('plans_adressage.gui')
        if parent is not None:
            setattr(parent, 'identify_tool', cls.mod)

    def setUp(self):
        self.canvas = MagicMock()
        self.tool = self.mod.IdentifyTool(self.canvas)

    def test_tool_created_form_mode(self):
        self.assertEqual(self.tool.mode, self.mod.IdentifyTool.MODE_FORM)

    def test_tool_ref_mode(self):
        tool = self.mod.IdentifyTool(
            self.canvas, mode=self.mod.IdentifyTool.MODE_REF)
        self.assertEqual(tool.mode, self.mod.IdentifyTool.MODE_REF)

    def test_ref_mode_initializes_ref_attrs(self):
        tool = self.mod.IdentifyTool(
            self.canvas, mode=self.mod.IdentifyTool.MODE_REF)
        self.assertIsNone(tool.pkuid)
        self.assertIsNone(tool.type)
        self.assertIsNone(tool.nom)
        self.assertIsNone(tool.ref_name)

    def test_form_mode_does_not_init_ref_attrs(self):
        self.assertIsNone(self.tool.dlg)

    def test_set_active_layer(self):
        layer = MagicMock()
        self.tool.set_active_layer(layer)
        self.assertEqual(self.tool._active_layer, layer)

    def test_get_active_layer(self):
        layer = MagicMock()
        self.tool._active_layer = layer
        self.assertEqual(self.tool.get_active_layer(), layer)

    def test_set_iface(self):
        iface = MagicMock()
        self.tool.set_iface(iface)
        self.assertEqual(self.tool._iface, iface)

    def test_get_iface(self):
        iface = MagicMock()
        self.tool._iface = iface
        self.assertEqual(self.tool.get_iface(), iface)

    def test_set_ref_name(self):
        ref = MagicMock()
        self.tool.set_ref_name(ref)
        self.assertEqual(self.tool.ref_name, ref)

    def test_get_pkuid_returns_dict_with_layer_name(self):
        layer = MagicMock()
        layer.name.return_value = 'Roads'
        self.tool.pkuid = 'abc-123'
        self.tool.set_active_layer(layer)
        result = self.tool.get_pkuid()
        self.assertEqual(result, {'pkuid': 'abc-123', 'layer_name': 'Roads'})

    def test_canvas_identify_not_called_without_layer(self):
        self.tool._active_layer = None
        result = self.tool.canvasReleaseEvent(MagicMock())
        self.assertIsNone(result)

    def test_unset_map_tool(self):
        self.tool.unset_map_tool()
        self.canvas.unsetMapTool.assert_called_once_with(self.tool)

    def test_feature_as_ref_sets_attrs_and_unset(self):
        tool = self.mod.IdentifyTool(
            self.canvas, mode=self.mod.IdentifyTool.MODE_REF)
        tool.ref_name = MagicMock()
        tool.feature_as_ref('pk-1', 'Route', 'Main St')
        self.assertEqual(tool.pkuid, 'pk-1')
        self.assertEqual(tool.type, 'Route')
        self.assertEqual(tool.nom, 'Main St')

    def test_feature_as_ref_skips_unset_when_pkuid_none(self):
        tool = self.mod.IdentifyTool(
            self.canvas, mode=self.mod.IdentifyTool.MODE_REF)
        tool.ref_name = MagicMock()
        tool.feature_as_ref(None, 'Type', 'Name')
        self.canvas.unsetMapTool.assert_not_called()

    def test_locale_feature_attr_arabic_default(self):
        feature = MagicMock()
        feature.__getitem__.return_value = 'شارع'
        with patch('plans_adressage.gui.identify_tool.current_locale',
                   return_value='ar'):
            result = self.tool._locale_feature_attr(feature, 'Nom')
        self.assertEqual(result, 'شارع')

    def test_locale_feature_attr_french_fallback(self):
        feature = MagicMock()
        feature.__getitem__.side_effect = lambda k: 'Rue' if k == 'Nom' else ''
        feature.fields.return_value.names.return_value = ['Nom_fr', 'Nom']
        with patch('plans_adressage.gui.identify_tool.current_locale',
                   return_value='fr'):
            result = self.tool._locale_feature_attr(feature, 'Nom')
        self.assertEqual(result, 'Rue')

    def test_locale_feature_attr_returns_empty_on_missing(self):
        feature = MagicMock()
        feature.__getitem__.return_value = None
        with patch('plans_adressage.gui.identify_tool.current_locale',
                   return_value='ar'):
            result = self.tool._locale_feature_attr(feature, 'Nom')
        self.assertEqual(result, '')

    @patch('plans_adressage.gui.identify_tool.get_session')
    def test_delete_feature_no_mapper_entry_closes_session(
        self, mock_get_session,
    ):
        with patch(
            'plans_adressage.gui.identify_tool.qgis_config'
        ) as mock_cfg:
            mock_cfg.return_value = {'mapper': []}
            layer = MagicMock()
            layer.name.return_value = 'Roads'
            self.tool.set_active_layer(layer)
            self.tool.delete_feature('pk-1')
            mock_get_session.return_value.close.assert_not_called()


if __name__ == '__main__':
    unittest.main()
