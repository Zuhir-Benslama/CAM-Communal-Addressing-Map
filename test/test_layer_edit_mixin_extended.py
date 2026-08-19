"""Extended tests for mixins.layer_edit_mixin covering all public methods."""

import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.exc import SQLAlchemyError
from test.helpers import setup_gui_mocks

LAYER_PANELS = 'panels'
LAYER_ROADS = 'roads'
LAYER_FACILITIES = 'facilities'
LAYER_SUBDIVISIONS = 'subdivisions'
LAYER_ZONES = 'zones'
LAYER_NUMBERING = 'numbering'


class _MixinHarness:
    """Create a LayerEditMixin instance with every required mock attribute."""

    def __init__(self, mod):
        self.mixin = mod.LayerEditMixin()
        self.mixin._tr = lambda s: s
        self.mixin.iface = MagicMock()
        self.mixin._last_feature_wkt = None
        self.mixin._last_feature_id = None
        self.mixin._geometry_ready = None
        self.mixin.ref_identify_tool = MagicMock()
        self.mixin.ref_identify_tool.get_id.return_value = {
            'layer_name': LAYER_ROADS,
            'id': 'ref-1',
        }
        self.mixin.measure_tool = None
        self.mixin._current_layer_name = MagicMock(return_value='roads')
        self.mixin.on_geometry_changed = MagicMock()
        self.mixin._draw_handler = MagicMock()

        self.mixin.road_name = MagicMock()
        self.mixin.road_name.text.return_value = 'Road 1'
        self.mixin.road_decision = MagicMock()
        self.mixin.type_road = MagicMock()
        self.mixin.type_road.currentData.return_value = 'avenue'

        self.mixin.nom_zone = MagicMock()
        self.mixin.nom_zone.text.return_value = 'Zone A'
        self.mixin.zone_type = MagicMock()
        self.mixin.zone_type.currentData.return_value = 'residential'

        self.mixin.org_name = MagicMock()
        self.mixin.org_name.text.return_value = 'Org 1'
        self.mixin.org_cat = MagicMock()
        self.mixin.org_cat.currentData.return_value = 'edu'
        self.mixin.org_type = MagicMock()
        self.mixin.org_type.currentData.return_value = 'school'

        self.mixin.subd_name = MagicMock()
        self.mixin.subd_name.text.return_value = 'Subd 1'
        self.mixin.subd_type = MagicMock()
        self.mixin.subd_type.currentData.return_value = 'cite'

        self.mixin.mount_status = MagicMock()
        self.mixin.mount_status.currentData.return_value = 'pole'

        self.mixin.num_val = MagicMock()
        self.mixin.num_val.text.return_value = '42'
        self.mixin.repetition = MagicMock()
        self.mixin.repetition.text.return_value = '1'
        self.mixin.num_state = MagicMock()
        self.mixin.num_state.currentData.return_value = 'active'
        self.mixin.activity_cat = MagicMock()
        self.mixin.activity_cat.currentData.return_value = 'cat1'
        self.mixin.activity_type = MagicMock()
        self.mixin.activity_type.currentData.return_value = 'type1'


class TestUpdateHandler(unittest.TestCase):
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
        self.h = _MixinHarness(self.mod)

    @patch('plans_adressage.mixins.layer_edit_mixin.QgsProject')
    @patch('plans_adressage.mixins.layer_edit_mixin.update_layer')
    def test_no_layers_found(self, mock_update, mock_proj):
        mock_proj.instance.return_value.mapLayersByName.return_value = []
        self.h.mixin._update_handler('Nonexistent')
        mock_update.assert_not_called()

    @patch('plans_adressage.mixins.layer_edit_mixin.QgsProject')
    @patch('plans_adressage.mixins.layer_edit_mixin.update_layer')
    def test_layers_found_connects_signal(self, mock_update, mock_proj):
        layer = MagicMock()
        mock_proj.instance.return_value.mapLayersByName.return_value = [layer]
        self.h.mixin._update_handler('roads')
        layer.geometryChanged.connect.assert_called_once_with(
            self.h.mixin.on_geometry_changed,
        )
        mock_update.assert_called_once_with(self.h.mixin.iface, 'roads')

    @patch('plans_adressage.mixins.layer_edit_mixin.QgsProject')
    @patch('plans_adressage.mixins.layer_edit_mixin.update_layer')
    def test_disconnect_before_connect(self, mock_update, mock_proj):
        layer = MagicMock()
        mock_proj.instance.return_value.mapLayersByName.return_value = [layer]
        self.h.mixin._update_handler('roads')
        layer.geometryChanged.disconnect.assert_called_once()
        layer.geometryChanged.connect.assert_called_once()

    @patch('plans_adressage.mixins.layer_edit_mixin.QgsProject')
    @patch('plans_adressage.mixins.layer_edit_mixin.update_layer')
    def test_disconnect_type_error_suppressed(self, mock_update, mock_proj):
        layer = MagicMock()
        layer.geometryChanged.disconnect.side_effect = TypeError
        mock_proj.instance.return_value.mapLayersByName.return_value = [layer]
        self.h.mixin._update_handler('roads')
        layer.geometryChanged.connect.assert_called_once()
        mock_update.assert_called_once()


class TestStartEditing(unittest.TestCase):
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
        self.h = _MixinHarness(self.mod)

    def test_calls_update_handler_with_current_layer(self):
        self.h.mixin._update_handler = MagicMock()
        self.h.mixin.start_editing()
        self.h.mixin._update_handler.assert_called_once_with('roads')


class TestGetGeometryAndId(unittest.TestCase):
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
        self.h = _MixinHarness(self.mod)

    def test_both_none(self):
        self.h.mixin._last_feature_wkt = None
        self.h.mixin._last_feature_id = None
        self.assertEqual(self.h.mixin._get_geometry_and_id('entity'), (None, None))

    def test_wkt_missing(self):
        self.h.mixin._last_feature_wkt = None
        self.h.mixin._last_feature_id = 'pk-1'
        self.assertEqual(self.h.mixin._get_geometry_and_id('entity'), (None, None))

    def test_id_missing(self):
        self.h.mixin._last_feature_wkt = 'POINT(0 0)'
        self.h.mixin._last_feature_id = None
        self.assertEqual(self.h.mixin._get_geometry_and_id('entity'), (None, None))

    def test_both_present(self):
        self.h.mixin._last_feature_wkt = 'POINT(1 2)'
        self.h.mixin._last_feature_id = 'pk-99'
        self.assertEqual(
            self.h.mixin._get_geometry_and_id('entity'),
            ('POINT(1 2)', 'pk-99'),
        )

    def test_empty_strings_treated_as_missing(self):
        self.h.mixin._last_feature_wkt = ''
        self.h.mixin._last_feature_id = ''
        self.assertEqual(self.h.mixin._get_geometry_and_id('entity'), (None, None))


class TestShowSuccess(unittest.TestCase):
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
        self.h = _MixinHarness(self.mod)

    @patch('plans_adressage.mixins.layer_edit_mixin.QMessageBox')
    def test_calls_information(self, mock_msg):
        self.h.mixin._show_success('it worked')
        mock_msg.information.assert_called_once_with(
            self.h.mixin,
            'Success',
            'it worked',
        )


class TestShowError(unittest.TestCase):
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
        self.h = _MixinHarness(self.mod)

    @patch('plans_adressage.mixins.layer_edit_mixin.QMessageBox')
    def test_calls_critical(self, mock_msg):
        self.h.mixin._show_error('boom')
        mock_msg.critical.assert_called_once_with(
            self.h.mixin,
            'Error',
            'boom',
        )


class TestMakeLocaleKwargs(unittest.TestCase):
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
        self.h = _MixinHarness(self.mod)

    @patch('plans_adressage.mixins.layer_edit_mixin.current_locale', return_value='ar')
    def test_arabic_returns_empty(self, _):
        self.assertEqual(self.h.mixin._make_locale_kwargs('name', 'val'), {})

    @patch('plans_adressage.mixins.layer_edit_mixin.current_locale', return_value='fr')
    def test_french(self, _):
        self.assertEqual(
            self.h.mixin._make_locale_kwargs('name', 'val'), {'name_fr': 'val'}
        )

    @patch('plans_adressage.mixins.layer_edit_mixin.current_locale', return_value='en')
    def test_english(self, _):
        self.assertEqual(
            self.h.mixin._make_locale_kwargs('road_name', 'A'), {'road_name_en': 'A'}
        )


class TestAddZone(unittest.TestCase):
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
        self.h = _MixinHarness(self.mod)

    def test_wrong_geometry_ready(self):
        self.h.mixin._geometry_ready = 'wrong'
        self.h.mixin.add_zone()

    def test_no_geometry_or_id(self):
        self.h.mixin._geometry_ready = LAYER_ZONES
        self.h.mixin._last_feature_wkt = None
        self.h.mixin.add_zone()

    @patch('plans_adressage.mixins.layer_edit_mixin.add_zone')
    @patch(
        'plans_adressage.mixins.layer_edit_mixin.validate_text',
        side_effect=lambda v, **kw: v,
    )
    def test_success(self, mock_validate, mock_add):
        self.h.mixin._geometry_ready = LAYER_ZONES
        self.h.mixin._last_feature_wkt = 'POLYGON((0 0,1 0,1 1,0 1,0 0))'
        self.h.mixin._last_feature_id = 'pk-1'
        self.h.mixin._make_locale_kwargs = MagicMock(return_value={})
        self.h.mixin.add_zone()
        mock_add.assert_called_once()
        self.assertIn('geometry_wkt', mock_add.call_args.kwargs)

    @patch(
        'plans_adressage.mixins.layer_edit_mixin.add_zone',
        side_effect=SQLAlchemyError('db'),
    )
    @patch(
        'plans_adressage.mixins.layer_edit_mixin.validate_text',
        side_effect=lambda v, **kw: v,
    )
    def test_sqlalchemy_error(self, mock_validate, mock_add):
        self.h.mixin._geometry_ready = LAYER_ZONES
        self.h.mixin._last_feature_wkt = 'POLYGON((0 0,1 0,1 1,0 1,0 0))'
        self.h.mixin._last_feature_id = 'pk-1'
        self.h.mixin._make_locale_kwargs = MagicMock(return_value={})
        with patch.object(self.h.mixin, '_show_error') as mock_err:
            self.h.mixin.add_zone()
            mock_err.assert_called_once()


class TestAddRoad(unittest.TestCase):
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
        self.h = _MixinHarness(self.mod)

    def test_wrong_geometry_ready(self):
        self.h.mixin._geometry_ready = 'wrong'
        self.h.mixin.add_road()

    def test_no_geometry_or_id(self):
        self.h.mixin._geometry_ready = LAYER_ROADS
        self.h.mixin._last_feature_wkt = None
        self.h.mixin.add_road()

    @patch('plans_adressage.mixins.layer_edit_mixin.add_road')
    @patch(
        'plans_adressage.mixins.layer_edit_mixin.validate_text',
        side_effect=lambda v, **kw: v,
    )
    def test_success(self, mock_validate, mock_add):
        self.h.mixin._geometry_ready = LAYER_ROADS
        self.h.mixin._last_feature_wkt = 'LINESTRING(0 0,1 1)'
        self.h.mixin._last_feature_id = 'pk-2'
        self.h.mixin._make_locale_kwargs = MagicMock(return_value={})
        self.h.mixin.add_road()
        mock_add.assert_called_once()
        self.assertIn('road_name', mock_add.call_args.kwargs)

    @patch(
        'plans_adressage.mixins.layer_edit_mixin.add_road',
        side_effect=SQLAlchemyError('db'),
    )
    @patch(
        'plans_adressage.mixins.layer_edit_mixin.validate_text',
        side_effect=lambda v, **kw: v,
    )
    def test_sqlalchemy_error(self, mock_validate, mock_add):
        self.h.mixin._geometry_ready = LAYER_ROADS
        self.h.mixin._last_feature_wkt = 'LINESTRING(0 0,1 1)'
        self.h.mixin._last_feature_id = 'pk-2'
        self.h.mixin._make_locale_kwargs = MagicMock(return_value={})
        with patch.object(self.h.mixin, '_show_error') as mock_err:
            self.h.mixin.add_road()
            mock_err.assert_called_once()


class TestAddOrganization(unittest.TestCase):
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
        self.h = _MixinHarness(self.mod)

    def test_wrong_geometry_ready(self):
        self.h.mixin._geometry_ready = 'wrong'
        self.h.mixin.add_organization()

    def test_no_geometry_or_id(self):
        self.h.mixin._geometry_ready = LAYER_FACILITIES
        self.h.mixin._last_feature_wkt = None
        self.h.mixin.add_organization()

    @patch('plans_adressage.mixins.layer_edit_mixin.add_organization')
    @patch(
        'plans_adressage.mixins.layer_edit_mixin.validate_text',
        side_effect=lambda v, **kw: v,
    )
    def test_success(self, mock_validate, mock_add):
        self.h.mixin._geometry_ready = LAYER_FACILITIES
        self.h.mixin._last_feature_wkt = 'POLYGON((0 0,1 0,1 1,0 1,0 0))'
        self.h.mixin._last_feature_id = 'pk-3'
        self.h.mixin._make_locale_kwargs = MagicMock(return_value={})
        self.h.mixin.add_organization()
        mock_add.assert_called_once()

    @patch(
        'plans_adressage.mixins.layer_edit_mixin.add_organization',
        side_effect=SQLAlchemyError('db'),
    )
    @patch(
        'plans_adressage.mixins.layer_edit_mixin.validate_text',
        side_effect=lambda v, **kw: v,
    )
    def test_sqlalchemy_error(self, mock_validate, mock_add):
        self.h.mixin._geometry_ready = LAYER_FACILITIES
        self.h.mixin._last_feature_wkt = 'POLYGON((0 0,1 0,1 1,0 1,0 0))'
        self.h.mixin._last_feature_id = 'pk-3'
        self.h.mixin._make_locale_kwargs = MagicMock(return_value={})
        with patch.object(self.h.mixin, '_show_error') as mock_err:
            self.h.mixin.add_organization()
            mock_err.assert_called_once()


class TestAddCity(unittest.TestCase):
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
        self.h = _MixinHarness(self.mod)

    def test_wrong_geometry_ready(self):
        self.h.mixin._geometry_ready = 'wrong'
        self.h.mixin.add_city()

    def test_no_geometry_or_id(self):
        self.h.mixin._geometry_ready = LAYER_SUBDIVISIONS
        self.h.mixin._last_feature_wkt = None
        self.h.mixin.add_city()

    @patch('plans_adressage.mixins.layer_edit_mixin.add_subdivision')
    @patch(
        'plans_adressage.mixins.layer_edit_mixin.validate_text',
        side_effect=lambda v, **kw: v,
    )
    def test_success(self, mock_validate, mock_add):
        self.h.mixin._geometry_ready = LAYER_SUBDIVISIONS
        self.h.mixin._last_feature_wkt = 'POLYGON((0 0,1 0,1 1,0 1,0 0))'
        self.h.mixin._last_feature_id = 'pk-4'
        self.h.mixin._make_locale_kwargs = MagicMock(return_value={})
        self.h.mixin.add_city()
        mock_add.assert_called_once()

    @patch(
        'plans_adressage.mixins.layer_edit_mixin.add_subdivision',
        side_effect=SQLAlchemyError('db'),
    )
    @patch(
        'plans_adressage.mixins.layer_edit_mixin.validate_text',
        side_effect=lambda v, **kw: v,
    )
    def test_sqlalchemy_error(self, mock_validate, mock_add):
        self.h.mixin._geometry_ready = LAYER_SUBDIVISIONS
        self.h.mixin._last_feature_wkt = 'POLYGON((0 0,1 0,1 1,0 1,0 0))'
        self.h.mixin._last_feature_id = 'pk-4'
        self.h.mixin._make_locale_kwargs = MagicMock(return_value={})
        with patch.object(self.h.mixin, '_show_error') as mock_err:
            self.h.mixin.add_city()
            mock_err.assert_called_once()


class TestAddPanel(unittest.TestCase):
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
        self.h = _MixinHarness(self.mod)

    def test_wrong_geometry_ready(self):
        self.h.mixin._geometry_ready = 'wrong'
        self.h.mixin.add_panel()

    def test_no_ref_data(self):
        self.h.mixin._geometry_ready = LAYER_PANELS
        self.h.mixin.ref_identify_tool.get_id.return_value = None
        self.h.mixin.add_panel()

    def test_no_geometry_or_id(self):
        self.h.mixin._geometry_ready = LAYER_PANELS
        self.h.mixin.ref_identify_tool.get_id.return_value = {
            'layer_name': LAYER_ROADS,
            'id': 'ref-1',
        }
        self.h.mixin._last_feature_wkt = None
        self.h.mixin.add_panel()

    @patch('plans_adressage.mixins.layer_edit_mixin.add_panel_sign')
    def test_success_with_measure_tool(self, mock_add):
        self.h.mixin._geometry_ready = LAYER_PANELS
        self.h.mixin._last_feature_wkt = 'POINT(3 4)'
        self.h.mixin._last_feature_id = 'pk-5'
        self.h.mixin.ref_identify_tool.get_id.return_value = {
            'layer_name': LAYER_ROADS,
            'id': 'r-1',
        }
        self.h.mixin.measure_tool = MagicMock()
        self.h.mixin.show_confirm_dialog = MagicMock()
        self.h.mixin.add_panel()
        mock_add.assert_called_once()
        self.h.mixin.ref_identify_tool.unset_map_tool.assert_called_once()
        self.h.mixin._draw_handler.assert_called_once_with(LAYER_PANELS)
        self.h.mixin.show_confirm_dialog.assert_called_once()

    @patch('plans_adressage.mixins.layer_edit_mixin.add_panel_sign')
    def test_success_without_measure_tool(self, mock_add):
        self.h.mixin._geometry_ready = LAYER_PANELS
        self.h.mixin._last_feature_wkt = 'POINT(3 4)'
        self.h.mixin._last_feature_id = 'pk-5'
        self.h.mixin.ref_identify_tool.get_id.return_value = {
            'layer_name': LAYER_ROADS,
            'id': 'r-1',
        }
        self.h.mixin.measure_tool = None
        with patch.object(self.h.mixin, '_show_success') as mock_suc:
            self.h.mixin.add_panel()
            mock_suc.assert_called_once_with('Panel added successfully')

    @patch(
        'plans_adressage.mixins.layer_edit_mixin.add_panel_sign',
        side_effect=ValueError('bad'),
    )
    def test_error_path(self, mock_add):
        self.h.mixin._geometry_ready = LAYER_PANELS
        self.h.mixin._last_feature_wkt = 'POINT(3 4)'
        self.h.mixin._last_feature_id = 'pk-5'
        self.h.mixin.ref_identify_tool.get_id.return_value = {
            'layer_name': LAYER_ROADS,
            'id': 'r-1',
        }
        self.h.mixin.measure_tool = None
        with patch.object(self.h.mixin, '_show_error') as mock_err:
            self.h.mixin.add_panel()
            mock_err.assert_called_once()
        self.h.mixin.ref_identify_tool.unset_map_tool.assert_called_once()
        self.h.mixin._draw_handler.assert_called_once_with(LAYER_PANELS)

    @patch('plans_adressage.mixins.layer_edit_mixin.add_panel_sign')
    def test_ref_facilities(self, mock_add):
        self.h.mixin._geometry_ready = LAYER_PANELS
        self.h.mixin._last_feature_wkt = 'POINT(3 4)'
        self.h.mixin._last_feature_id = 'pk-5'
        self.h.mixin.ref_identify_tool.get_id.return_value = {
            'layer_name': LAYER_FACILITIES,
            'id': 'f-1',
        }
        self.h.mixin.measure_tool = None
        self.h.mixin.add_panel()
        call_kwargs = mock_add.call_args.kwargs
        self.assertEqual(call_kwargs['organization_id'], 'f-1')
        self.assertIsNone(call_kwargs['road_id'])
        self.assertIsNone(call_kwargs['subdivision_id'])

    @patch('plans_adressage.mixins.layer_edit_mixin.add_panel_sign')
    def test_ref_subdivisions(self, mock_add):
        self.h.mixin._geometry_ready = LAYER_PANELS
        self.h.mixin._last_feature_wkt = 'POINT(3 4)'
        self.h.mixin._last_feature_id = 'pk-5'
        self.h.mixin.ref_identify_tool.get_id.return_value = {
            'layer_name': LAYER_SUBDIVISIONS,
            'id': 's-1',
        }
        self.h.mixin.measure_tool = None
        self.h.mixin.add_panel()
        call_kwargs = mock_add.call_args.kwargs
        self.assertEqual(call_kwargs['subdivision_id'], 's-1')
        self.assertIsNone(call_kwargs['road_id'])
        self.assertIsNone(call_kwargs['organization_id'])


class TestAddNumbering(unittest.TestCase):
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
        self.h = _MixinHarness(self.mod)

    def test_wrong_geometry_ready(self):
        self.h.mixin._geometry_ready = 'wrong'
        self.h.mixin.add_numbering()

    def test_no_geometry_or_id(self):
        self.h.mixin._geometry_ready = LAYER_NUMBERING
        self.h.mixin._last_feature_wkt = None
        self.h.mixin.add_numbering()

    @patch(
        'plans_adressage.mixins.layer_edit_mixin.validate_text',
        side_effect=lambda v, **kw: v,
    )
    @patch('plans_adressage.mixins.layer_edit_mixin.add_numbering')
    def test_ref_is_road(self, mock_add, mock_val):
        self.h.mixin._geometry_ready = LAYER_NUMBERING
        self.h.mixin._last_feature_wkt = 'POINT(1 2)'
        self.h.mixin._last_feature_id = 'pk-6'
        self.h.mixin.ref_identify_tool.get_id.return_value = {
            'layer_name': LAYER_ROADS,
            'id': 'r-10',
        }
        self.h.mixin.measure_tool = None
        self.h.mixin.add_numbering()
        mock_add.assert_called_once()
        call_kwargs = mock_add.call_args.kwargs
        self.assertEqual(call_kwargs['road_id'], 'r-10')
        self.assertIsNone(call_kwargs['subdivision_id'])

    @patch(
        'plans_adressage.mixins.layer_edit_mixin.validate_text',
        side_effect=lambda v, **kw: v,
    )
    @patch('plans_adressage.mixins.layer_edit_mixin.add_numbering')
    def test_ref_is_subdivision(self, mock_add, mock_val):
        self.h.mixin._geometry_ready = LAYER_NUMBERING
        self.h.mixin._last_feature_wkt = 'POINT(1 2)'
        self.h.mixin._last_feature_id = 'pk-6'
        self.h.mixin.ref_identify_tool.get_id.return_value = {
            'layer_name': LAYER_SUBDIVISIONS,
            'id': 's-10',
        }
        self.h.mixin.measure_tool = None
        self.h.mixin.add_numbering()
        mock_add.assert_called_once()
        call_kwargs = mock_add.call_args.kwargs
        self.assertEqual(call_kwargs['subdivision_id'], 's-10')
        self.assertIsNone(call_kwargs['road_id'])

    @patch(
        'plans_adressage.mixins.layer_edit_mixin.validate_text',
        side_effect=lambda v, **kw: v,
    )
    @patch('plans_adressage.mixins.layer_edit_mixin.add_numbering')
    def test_no_ref_data(self, mock_add, mock_val):
        self.h.mixin._geometry_ready = LAYER_NUMBERING
        self.h.mixin._last_feature_wkt = 'POINT(1 2)'
        self.h.mixin._last_feature_id = 'pk-6'
        self.h.mixin.ref_identify_tool.get_id.return_value = None
        self.h.mixin.measure_tool = None
        self.h.mixin.add_numbering()
        mock_add.assert_not_called()

    @patch(
        'plans_adressage.mixins.layer_edit_mixin.validate_text',
        side_effect=lambda v, **kw: v,
    )
    @patch('plans_adressage.mixins.layer_edit_mixin.add_numbering')
    def test_with_measure_tool(self, mock_add, mock_val):
        self.h.mixin._geometry_ready = LAYER_NUMBERING
        self.h.mixin._last_feature_wkt = 'POINT(1 2)'
        self.h.mixin._last_feature_id = 'pk-6'
        self.h.mixin.ref_identify_tool.get_id.return_value = {
            'layer_name': LAYER_ROADS,
            'id': 'r-10',
        }
        self.h.mixin.measure_tool = MagicMock()
        self.h.mixin.show_confirm_dialog = MagicMock()
        self.h.mixin.add_numbering()
        self.h.mixin.show_confirm_dialog.assert_called_once()
        call_kwargs = self.h.mixin.show_confirm_dialog.call_args.kwargs
        self.assertIs(call_kwargs['yes_callback'], self.h.mixin.measure_tool.clear)

    @patch(
        'plans_adressage.mixins.layer_edit_mixin.validate_text',
        side_effect=lambda v, **kw: v,
    )
    @patch(
        'plans_adressage.mixins.layer_edit_mixin.add_numbering',
        side_effect=TypeError('bad'),
    )
    def test_error_path(self, mock_add, mock_val):
        self.h.mixin._geometry_ready = LAYER_NUMBERING
        self.h.mixin._last_feature_wkt = 'POINT(1 2)'
        self.h.mixin._last_feature_id = 'pk-6'
        self.h.mixin.ref_identify_tool.get_id.return_value = {
            'layer_name': LAYER_ROADS,
            'id': 'r-10',
        }
        self.h.mixin.measure_tool = None
        with patch.object(self.h.mixin, '_show_error') as mock_err:
            self.h.mixin.add_numbering()
            mock_err.assert_called_once()

    def test_ref_identify_tool_raises_type_error(self):
        self.h.mixin._geometry_ready = LAYER_NUMBERING
        self.h.mixin._last_feature_wkt = 'POINT(1 2)'
        self.h.mixin._last_feature_id = 'pk-6'
        self.h.mixin.ref_identify_tool.get_id.side_effect = TypeError('broken')
        self.h.mixin.measure_tool = None
        with patch.object(self.h.mixin, '_show_error'):
            self.h.mixin.add_numbering()
        self.h.mixin.num_val.setFocus.assert_called_once()
        self.h.mixin.num_val.clear.assert_called_once()
        self.h.mixin._draw_handler.assert_called_once_with(LAYER_NUMBERING)


class TestShowConfirmDialog(unittest.TestCase):
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
        self.h = _MixinHarness(self.mod)

    @patch('plans_adressage.mixins.layer_edit_mixin.QMessageBox')
    def test_yes_calls_yes_callback(self, mock_msg_cls):
        mock_msg_cls.Yes = 1
        mock_msg_cls.No = 2
        mock_msg_cls.Question = 4
        instance = mock_msg_cls.return_value
        instance.exec.return_value = 1
        yes_cb = MagicMock()
        result = self.h.mixin.show_confirm_dialog('T', 'M', yes_callback=yes_cb)
        self.assertTrue(result)
        yes_cb.assert_called_once()

    @patch('plans_adressage.mixins.layer_edit_mixin.QMessageBox')
    def test_no_calls_no_callback(self, mock_msg_cls):
        mock_msg_cls.Yes = 1
        mock_msg_cls.No = 2
        mock_msg_cls.Question = 4
        instance = mock_msg_cls.return_value
        instance.exec.return_value = 2
        no_cb = MagicMock()
        result = self.h.mixin.show_confirm_dialog('T', 'M', no_callback=no_cb)
        self.assertFalse(result)
        no_cb.assert_called_once()

    @patch('plans_adressage.mixins.layer_edit_mixin.QMessageBox')
    def test_no_callback_none(self, mock_msg_cls):
        mock_msg_cls.Yes = 1
        mock_msg_cls.No = 2
        mock_msg_cls.Question = 4
        instance = mock_msg_cls.return_value
        instance.exec.return_value = 2
        result = self.h.mixin.show_confirm_dialog('T', 'M')
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
