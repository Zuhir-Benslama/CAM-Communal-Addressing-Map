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

    def test_no_layers_found(self):
        with (
            patch.object(self.mod, 'QgsProject') as mock_proj,
            patch.object(self.mod, 'update_layer') as mock_update,
        ):
            mock_proj.instance.return_value.mapLayersByName.return_value = []
            self.h.mixin._update_handler('Nonexistent')
            mock_update.assert_not_called()

    def test_layers_found_connects_signal(self):
        with (
            patch.object(self.mod, 'QgsProject') as mock_proj,
            patch.object(self.mod, 'update_layer') as mock_update,
        ):
            layer = MagicMock()
            mock_proj.instance.return_value.mapLayersByName.return_value = [layer]
            self.h.mixin._update_handler('roads')
            layer.geometryChanged.connect.assert_called_once_with(
                self.h.mixin.on_geometry_changed,
            )
            mock_update.assert_called_once_with(self.h.mixin.iface, 'roads')

    def test_disconnect_before_connect(self):
        with (
            patch.object(self.mod, 'QgsProject') as mock_proj,
            patch.object(self.mod, 'update_layer'),
        ):
            layer = MagicMock()
            mock_proj.instance.return_value.mapLayersByName.return_value = [layer]
            self.h.mixin._update_handler('roads')
            layer.geometryChanged.disconnect.assert_called_once()
            layer.geometryChanged.connect.assert_called_once()

    def test_disconnect_type_error_suppressed(self):
        with (
            patch.object(self.mod, 'QgsProject') as mock_proj,
            patch.object(self.mod, 'update_layer') as mock_update,
        ):
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

    def test_calls_information(self):
        with patch.object(self.mod, 'QMessageBox') as mock_msg:
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

    def test_calls_critical(self):
        with patch.object(self.mod, 'QMessageBox') as mock_msg:
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

    def test_arabic_returns_empty(self):
        with patch.object(self.mod, 'current_locale', return_value='ar'):
            self.assertEqual(self.h.mixin._make_locale_kwargs('name', 'val'), {})

    def test_french(self):
        with patch.object(self.mod, 'current_locale', return_value='fr'):
            self.assertEqual(
                self.h.mixin._make_locale_kwargs('name', 'val'), {'name_fr': 'val'}
            )

    def test_english(self):
        with patch.object(self.mod, 'current_locale', return_value='en'):
            self.assertEqual(
                self.h.mixin._make_locale_kwargs('road_name', 'A'),
                {'road_name_en': 'A'},
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

    def test_success(self):
        with (
            patch.object(self.mod, 'add_zone') as mock_add,
            patch.object(self.mod, 'validate_text', side_effect=lambda v, **kw: v),
        ):
            self.h.mixin._geometry_ready = LAYER_ZONES
            self.h.mixin._last_feature_wkt = 'POLYGON((0 0,1 0,1 1,0 1,0 0))'
            self.h.mixin._last_feature_id = 'pk-1'
            self.h.mixin._make_locale_kwargs = MagicMock(return_value={})
            self.h.mixin.add_zone()
            mock_add.assert_called_once()
            self.assertIn('geometry_wkt', mock_add.call_args.kwargs)

    def test_sqlalchemy_error(self):
        with (
            patch.object(self.mod, 'add_zone', side_effect=SQLAlchemyError('db')),
            patch.object(self.mod, 'validate_text', side_effect=lambda v, **kw: v),
        ):
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

    def test_success(self):
        with (
            patch.object(self.mod, 'add_road') as mock_add,
            patch.object(self.mod, 'validate_text', side_effect=lambda v, **kw: v),
        ):
            self.h.mixin._geometry_ready = LAYER_ROADS
            self.h.mixin._last_feature_wkt = 'LINESTRING(0 0,1 1)'
            self.h.mixin._last_feature_id = 'pk-2'
            self.h.mixin._make_locale_kwargs = MagicMock(return_value={})
            self.h.mixin.add_road()
            mock_add.assert_called_once()
            self.assertIn('road_name', mock_add.call_args.kwargs)

    def test_sqlalchemy_error(self):
        with (
            patch.object(self.mod, 'add_road', side_effect=SQLAlchemyError('db')),
            patch.object(self.mod, 'validate_text', side_effect=lambda v, **kw: v),
        ):
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

    def test_success(self):
        with (
            patch.object(self.mod, 'add_organization') as mock_add,
            patch.object(self.mod, 'validate_text', side_effect=lambda v, **kw: v),
        ):
            self.h.mixin._geometry_ready = LAYER_FACILITIES
            self.h.mixin._last_feature_wkt = 'POLYGON((0 0,1 0,1 1,0 1,0 0))'
            self.h.mixin._last_feature_id = 'pk-3'
            self.h.mixin._make_locale_kwargs = MagicMock(return_value={})
            self.h.mixin.add_organization()
            mock_add.assert_called_once()

    def test_sqlalchemy_error(self):
        with (
            patch.object(
                self.mod, 'add_organization', side_effect=SQLAlchemyError('db')
            ),
            patch.object(self.mod, 'validate_text', side_effect=lambda v, **kw: v),
        ):
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

    def test_success(self):
        with (
            patch.object(self.mod, 'add_subdivision') as mock_add,
            patch.object(self.mod, 'validate_text', side_effect=lambda v, **kw: v),
        ):
            self.h.mixin._geometry_ready = LAYER_SUBDIVISIONS
            self.h.mixin._last_feature_wkt = 'POLYGON((0 0,1 0,1 1,0 1,0 0))'
            self.h.mixin._last_feature_id = 'pk-4'
            self.h.mixin._make_locale_kwargs = MagicMock(return_value={})
            self.h.mixin.add_city()
            mock_add.assert_called_once()

    def test_sqlalchemy_error(self):
        with (
            patch.object(
                self.mod, 'add_subdivision', side_effect=SQLAlchemyError('db')
            ),
            patch.object(self.mod, 'validate_text', side_effect=lambda v, **kw: v),
        ):
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

    def test_success_with_measure_tool(self):
        with patch.object(self.mod, 'add_panel_sign') as mock_add:
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

    def test_success_without_measure_tool(self):
        with patch.object(self.mod, 'add_panel_sign'):
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

    def test_error_path(self):
        with patch.object(self.mod, 'add_panel_sign', side_effect=ValueError('bad')):
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

    def test_ref_facilities(self):
        with patch.object(self.mod, 'add_panel_sign') as mock_add:
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

    def test_ref_subdivisions(self):
        with patch.object(self.mod, 'add_panel_sign') as mock_add:
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

    def test_ref_is_road(self):
        with (
            patch.object(self.mod, 'validate_text', side_effect=lambda v, **kw: v),
            patch.object(self.mod, 'add_numbering') as mock_add,
        ):
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

    def test_ref_is_subdivision(self):
        with (
            patch.object(self.mod, 'validate_text', side_effect=lambda v, **kw: v),
            patch.object(self.mod, 'add_numbering') as mock_add,
        ):
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

    def test_no_ref_data(self):
        with (
            patch.object(self.mod, 'validate_text', side_effect=lambda v, **kw: v),
            patch.object(self.mod, 'add_numbering') as mock_add,
        ):
            self.h.mixin._geometry_ready = LAYER_NUMBERING
            self.h.mixin._last_feature_wkt = 'POINT(1 2)'
            self.h.mixin._last_feature_id = 'pk-6'
            self.h.mixin.ref_identify_tool.get_id.return_value = None
            self.h.mixin.measure_tool = None
            self.h.mixin.add_numbering()
            mock_add.assert_not_called()

    def test_with_measure_tool(self):
        with (
            patch.object(self.mod, 'validate_text', side_effect=lambda v, **kw: v),
            patch.object(self.mod, 'add_numbering'),
        ):
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

    def test_error_path(self):
        with (
            patch.object(self.mod, 'validate_text', side_effect=lambda v, **kw: v),
            patch.object(self.mod, 'add_numbering', side_effect=TypeError('bad')),
        ):
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
        # No supported reference was bound: the value the user typed must
        # not be wiped and no success path may run.
        self.h.mixin.num_val.setFocus.assert_not_called()
        self.h.mixin.num_val.clear.assert_not_called()
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

    def test_yes_calls_yes_callback(self):
        with patch.object(self.mod, 'QMessageBox') as mock_msg_cls:
            mock_msg_cls.Yes = 1
            mock_msg_cls.No = 2
            mock_msg_cls.Question = 4
            instance = mock_msg_cls.return_value
            instance.exec.return_value = 1
            yes_cb = MagicMock()
            result = self.h.mixin.show_confirm_dialog('T', 'M', yes_callback=yes_cb)
            self.assertTrue(result)
            yes_cb.assert_called_once()

    def test_no_calls_no_callback(self):
        with patch.object(self.mod, 'QMessageBox') as mock_msg_cls:
            mock_msg_cls.Yes = 1
            mock_msg_cls.No = 2
            mock_msg_cls.Question = 4
            instance = mock_msg_cls.return_value
            instance.exec.return_value = 2
            no_cb = MagicMock()
            result = self.h.mixin.show_confirm_dialog('T', 'M', no_callback=no_cb)
            self.assertFalse(result)
            no_cb.assert_called_once()

    def test_no_callback_none(self):
        with patch.object(self.mod, 'QMessageBox') as mock_msg_cls:
            mock_msg_cls.Yes = 1
            mock_msg_cls.No = 2
            mock_msg_cls.Question = 4
            instance = mock_msg_cls.return_value
            instance.exec.return_value = 2
            result = self.h.mixin.show_confirm_dialog('T', 'M')
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
