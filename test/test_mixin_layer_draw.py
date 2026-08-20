"""Tests for mixins.layer_draw_mixin."""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from test.helpers import setup_gui_mocks


class TestLayerDrawMixin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.mixins.layer_draw_mixin',
            'mixins/layer_draw_mixin.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.mixins.layer_draw_mixin'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.mixin = self.mod.LayerDrawMixin()
        self.mixin._tr = lambda s: s
        self.mixin.iface = MagicMock()
        self.mixin.on_feature_added = MagicMock()
        self.mixin.on_edition_release = MagicMock()
        self.mixin._current_layer_name = MagicMock(return_value='Panels')

    def test_start_drawing(self):
        self.mixin._draw_handler = MagicMock()
        self.mixin.start_drawing()
        self.mixin._draw_handler.assert_called_once_with('Panels')

    def test_draw_handler(self):
        with (
            patch.object(self.mod, 'start_editing_layer') as mock_start,
            patch.object(self.mod, 'QgsProject') as mock_project,
        ):
            mock_layer = MagicMock()
            mock_project.instance.return_value.mapLayersByName.return_value = [
                mock_layer
            ]
            self.mixin._draw_handler('Panels')
            mock_start.assert_called_once()
            mock_layer.featureAdded.connect.assert_called_once()

    def test_draw_handler_no_layer(self):
        with (
            patch.object(self.mod, 'start_editing_layer') as mock_start,
            patch.object(self.mod, 'QgsProject') as mock_project,
        ):
            mock_project.instance.return_value.mapLayersByName.return_value = []
            self.mixin._draw_handler('NonExistent')
            mock_start.assert_not_called()
