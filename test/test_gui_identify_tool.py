"""Tests for gui/identify_tool.py."""
import importlib
import sys
import unittest
from unittest.mock import MagicMock

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

    def setUp(self):
        self.canvas = MagicMock()
        self.tool = self.mod.IdentifyTool(self.canvas)

    def test_tool_created_form_mode(self):
        self.assertEqual(self.tool.mode, self.mod.IdentifyTool.MODE_FORM)

    def test_tool_ref_mode(self):
        tool = self.mod.IdentifyTool(self.canvas, mode=self.mod.IdentifyTool.MODE_REF)
        self.assertEqual(tool.mode, self.mod.IdentifyTool.MODE_REF)

    def test_set_active_layer(self):
        layer = MagicMock()
        self.tool.set_active_layer(layer)
        self.assertEqual(self.tool._active_layer, layer)

    def test_set_iface(self):
        iface = MagicMock()
        self.tool.set_iface(iface)
        self.assertEqual(self.tool._iface, iface)

    def test_canvas_identify_not_called_without_layer(self):
        self.tool._active_layer = None
        result = self.tool.canvasReleaseEvent(MagicMock())
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
