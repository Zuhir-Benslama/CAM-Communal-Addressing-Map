"""Tests for mixins.layer_edit_mixin."""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from test.helpers import setup_gui_mocks

LAYER_PANELS = 'Panels'


class TestLayerEditMixin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.mixins.layer_edit_mixin',
            'mixins/layer_edit_mixin.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.mixins.layer_edit_mixin'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.mixin = self.mod.LayerEditMixin()
        self.mixin._tr = lambda s: s
        self.mixin.iface = MagicMock()
        self.mixin._last_feature_wkt = None
        self.mixin._last_feature_id = None
        self.mixin._geometry_ready = None
        self.mixin.ref_identify_tool = None
        self.mixin.measure_tool = None

    def test_get_geometry_and_id_none(self):
        result = self.mixin._get_geometry_and_id('test')
        self.assertEqual(result, (None, None))

    def test_get_geometry_and_id_valid(self):
        self.mixin._last_feature_wkt = 'POINT(0 0)'
        self.mixin._last_feature_id = 'pk-123'
        wkt_val, fid = self.mixin._get_geometry_and_id('test')
        self.assertEqual(wkt_val, 'POINT(0 0)')
        self.assertEqual(fid, 'pk-123')

    def test_add_panel_wrong_layer(self):
        self.mixin._geometry_ready = 'wrong_layer'
        self.mixin.add_panel()

    def test_add_organization_wrong_layer(self):
        self.mixin._geometry_ready = 'wrong_layer'
        self.mixin.add_organization()

    def test_add_road_wrong_layer(self):
        self.mixin._geometry_ready = 'wrong_layer'
        self.mixin.add_road()

    def test_add_city_wrong_layer(self):
        self.mixin._geometry_ready = 'wrong_layer'
        self.mixin.add_city()

    def test_add_zone_wrong_layer(self):
        self.mixin._geometry_ready = 'wrong_layer'
        self.mixin.add_zone()

    def test_add_numbering_wrong_layer(self):
        self.mixin._geometry_ready = 'wrong_layer'
        self.mixin.add_numbering()

    def test_add_panel_no_ref_data(self):
        self.mixin._geometry_ready = LAYER_PANELS
        self.mixin.ref_identify_tool = MagicMock()
        self.mixin.ref_identify_tool.get_id.return_value = None
        self.mixin.add_panel()

    def test_add_road_no_geometry(self):
        self.mixin._geometry_ready = 'roads'
        self.mixin.add_road()

    def test_add_zone_no_geometry(self):
        self.mixin._geometry_ready = 'zones'
        self.mixin.add_zone()

    def test_add_city_no_geometry(self):
        self.mixin._geometry_ready = 'subdivisions'
        self.mixin.add_city()

    def test_add_organization_no_geometry(self):
        self.mixin._geometry_ready = 'facilities'
        self.mixin.add_organization()

    def test_add_numbering_no_geometry(self):
        self.mixin._geometry_ready = 'numbering'
        self.mixin.add_numbering()

    def test_add_road_success(self):
        self.mixin._geometry_ready = 'roads'
        self.mixin._last_feature_wkt = 'LINESTRING(0 0, 1 1)'
        self.mixin._last_feature_id = 'pk-1'
        self.mixin.road_name = MagicMock()
        self.mixin.road_name.text.return_value = 'Test Road'
        self.mixin.type_road = MagicMock()
        self.mixin.type_road.currentData.return_value = 'avenue'
        with (
            patch.object(self.mod, 'add_road') as mock_add,
            patch.object(self.mod, 'validate_text', side_effect=lambda v, **kw: v),
        ):
            self.mixin.add_road()
            mock_add.assert_called_once()

    def test_add_zone_success(self):
        self.mixin._geometry_ready = 'zones'
        self.mixin._last_feature_wkt = 'POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))'
        self.mixin._last_feature_id = 'pk-2'
        self.mixin.nom_zone = MagicMock()
        self.mixin.nom_zone.text.return_value = 'Zone A'
        self.mixin.zone_type = MagicMock()
        self.mixin.zone_type.currentData.return_value = 'residential'
        with (
            patch.object(self.mod, 'add_zone') as mock_add,
            patch.object(self.mod, 'validate_text', side_effect=lambda v, **kw: v),
        ):
            self.mixin.add_zone()
            mock_add.assert_called_once()

    def test_add_organization_success(self):
        self.mixin._geometry_ready = 'facilities'
        self.mixin._last_feature_wkt = 'POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))'
        self.mixin._last_feature_id = 'pk-3'
        self.mixin.org_name = MagicMock()
        self.mixin.org_name.text.return_value = 'Org A'
        self.mixin.org_cat = MagicMock()
        self.mixin.org_cat.currentData.return_value = 'edu'
        self.mixin.org_type = MagicMock()
        self.mixin.org_type.currentData.return_value = 'school'
        with (
            patch.object(self.mod, 'add_organization') as mock_add,
            patch.object(self.mod, 'validate_text', side_effect=lambda v, **kw: v),
        ):
            self.mixin.add_organization()
            mock_add.assert_called_once()

    def test_add_city_success(self):
        self.mixin._geometry_ready = 'subdivisions'
        self.mixin._last_feature_wkt = 'POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))'
        self.mixin._last_feature_id = 'pk-4'
        self.mixin.subd_name = MagicMock()
        self.mixin.subd_name.text.return_value = 'Cite 500'
        self.mixin.subd_type = MagicMock()
        self.mixin.subd_type.currentData.return_value = 'cite'
        with (
            patch.object(self.mod, 'add_subdivision') as mock_add,
            patch.object(self.mod, 'validate_text', side_effect=lambda v, **kw: v),
        ):
            self.mixin.add_city()
            mock_add.assert_called_once()

    def test_make_locale_kwargs_arabic(self):
        with patch.object(self.mod, 'current_locale', return_value='ar'):
            result = self.mixin._make_locale_kwargs('name', 'test')
            self.assertEqual(result, {})

    def test_make_locale_kwargs_french(self):
        with patch.object(self.mod, 'current_locale', return_value='fr'):
            result = self.mixin._make_locale_kwargs('name', 'test')
            self.assertEqual(result, {'name_fr': 'test'})

    def test_show_confirm_dialog_yes(self):
        with patch.object(self.mod, 'QMessageBox') as mock_msg:
            mock_msg.Yes = 1
            mock_msg.No = 2
            mock_msg.Question = 4
            instance = mock_msg.return_value
            instance.exec.return_value = 1
            instance.button.return_value = MagicMock()
            callback = MagicMock()
            result = self.mixin.show_confirm_dialog(
                'title', 'msg', yes_callback=callback
            )
            self.assertTrue(result)

    def test_show_confirm_dialog_no(self):
        with patch.object(self.mod, 'QMessageBox') as mock_msg:
            mock_msg.Yes = 1
            mock_msg.No = 2
            mock_msg.Question = 4
            instance = mock_msg.return_value
            instance.exec.return_value = 2
            instance.button.return_value = MagicMock()
            result = self.mixin.show_confirm_dialog('title', 'msg')
            self.assertFalse(result)
