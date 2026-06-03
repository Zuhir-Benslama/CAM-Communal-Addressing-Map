"""Tests for mixins/chart_mixin.py."""

import importlib
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from .helpers import setup_gui_mocks


class TestChartMixin(unittest.TestCase):
    """Test ChartMixin chart generation and layer visibility."""

    @classmethod
    def setUpClass(cls):
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.mixins.chart_mixin',
            'mixins/chart_mixin.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.mixins.chart_mixin'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.mod.CHART_SVG = os.path.join(self.tmpdir, 'chart.svg')
        self.mod.LAYER_PANELS = 'Panels'
        self.mod.LAYER_NUMBERING = 'Numbering'

        self.mixin = self.mod.ChartMixin()
        self.mixin._tr = lambda s: s
        self.mixin.type_plan = None
        self.mixin.type_to_hide = None
        self.mixin.iface = MagicMock()

        self.session_mock = MagicMock()
        self.session_mock.query.return_value.group_by.return_value.all.return_value = [
            ('installed', 5),
            ('planned', 3),
        ]
        self.session_mock.close = MagicMock()

        session_patch = patch.object(
            self.mod, 'get_session', return_value=self.session_mock
        )
        self._session_patch = session_patch.start()

    def tearDown(self):
        self._session_patch.stop()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_panel_chart_queries_and_renders(self):
        with patch.object(self.mod, 'refresh_all_layers'):
            self.mixin.panel_chart()
        self.assertEqual(self.mixin.type_plan, 'Panels')
        self.assertEqual(self.mixin.type_to_hide, 'Numbering')
        self.session_mock.query.assert_called_once()
        self.session_mock.close.assert_called_once()

    def test_numbering_chart_queries_and_renders(self):
        with patch.object(self.mod, 'refresh_all_layers'):
            self.mixin.numbering_chart()
        self.assertEqual(self.mixin.type_plan, 'Numbering')
        self.assertEqual(self.mixin.type_to_hide, 'Panels')
        self.session_mock.query.assert_called_once()
        self.session_mock.close.assert_called_once()

    def test_get_zone_chart_with_data(self):
        dist_mock = MagicMock(return_value=[('type_a', 10), ('type_b', 5)])
        with patch.object(
            self.mod,
            'get_zone_distribution',
            dist_mock,
        ):
            self.mixin.get_zone_chart(16)
            dist_mock.assert_called_once_with(16)

    def test_get_zone_chart_no_data(self):
        dist_mock = MagicMock(return_value=[])
        with patch.object(
            self.mod,
            'get_zone_distribution',
            dist_mock,
        ):
            self.mixin.get_zone_chart(16)
            dist_mock.assert_called_once_with(16)

    def test_render_bar_chart_creates_file(self):
        results = [('A', 10), ('B', 5)]
        self.mod._render_bar_chart(results, 'X', 'Y', 'Test')
        self.assertTrue(os.path.exists(self.mod.CHART_SVG))

    def test_toggle_layer_visibility_hides(self):
        mock_layer = MagicMock()
        mock_layer.id.return_value = 'layer_id'
        mock_node = MagicMock()

        qgis_project = MagicMock()
        (qgis_project.instance.return_value.mapLayersByName.return_value) = [mock_layer]
        (
            qgis_project.instance.return_value.layerTreeRoot.return_value.findLayer.return_value
        ) = mock_node

        with patch.object(self.mod, 'QgsProject', qgis_project):
            self.mod._toggle_layer_visibility('test_layer', False)
            mock_node.setItemVisibilityChecked.assert_called_once_with(False)

    def test_toggle_layer_visibility_shows(self):
        mock_layer = MagicMock()
        mock_layer.id.return_value = 'layer_id'
        mock_node = MagicMock()

        qgis_project = MagicMock()
        (qgis_project.instance.return_value.mapLayersByName.return_value) = [mock_layer]
        (
            qgis_project.instance.return_value.layerTreeRoot.return_value.findLayer.return_value
        ) = mock_node

        with patch.object(self.mod, 'QgsProject', qgis_project):
            self.mod._toggle_layer_visibility('test_layer', True)
            mock_node.setItemVisibilityChecked.assert_called_once_with(True)


if __name__ == '__main__':
    unittest.main()
