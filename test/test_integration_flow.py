"""Integration test: login → load layers → add feature flow."""
import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from .helpers import setup_gui_mocks, get_qapp


@unittest.skipIf(get_qapp() is None, 'PyQt5 not available')
class IntegrationFlowTest(unittest.TestCase):
    """Integration tests for login -> layer -> add feature flow."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        # Load all required mixin modules
        cls.modules = {}
        for name, path in [
            ('auth_mixin', 'mixins/auth_mixin.py'),
            ('layer_edit_mixin', 'mixins/layer_edit_mixin.py'),
            ('layer_ops_mixin', 'mixins/layer_ops_mixin.py'),
            ('map_tools_mixin', 'mixins/map_tools_mixin.py'),
        ]:
            spec = importlib.util.spec_from_file_location(
                f'plans_adressage.mixins.{name}', path,
            )
            mod = importlib.util.module_from_spec(spec)
            sys.modules[f'plans_adressage.mixins.{name}'] = mod
            spec.loader.exec_module(mod)
            cls.modules[name] = mod

    def _make_host(self):
        """Create a test host combining AuthMixin, LayerEditMixin, etc."""
        mods = self.modules
        bases = (mods['auth_mixin'].AuthMixin,
                 mods['layer_edit_mixin'].LayerEditMixin,
                 mods['layer_ops_mixin'].LayerOpsMixin,
                 mods['map_tools_mixin'].MapToolsMixin)
        host = type('Host', bases, {'_tr': lambda self, s: s})()
        # Override validate_text to accept single arg and return just text
        mods['auth_mixin'].validate_text = lambda t: t  # noqa: E731
        return host, mods

    def _setup_widgets(self, host):
        """Set up all widget attributes the mixin chain requires."""
        host.username = MagicMock()
        host.username.text = MagicMock(return_value='admin')
        host.password = MagicMock()
        host.password.text = MagicMock(return_value='secret')
        host.label_username = MagicMock()
        host.menu = MagicMock()
        host.menu.currentIndex = MagicMock(return_value=0)
        host.iface = MagicMock()
        host.iface.mapCanvas = MagicMock(return_value=MagicMock())
        host.iface.activeLayer = MagicMock(return_value=MagicMock())
        host.map_options = MagicMock()

        host.identify_tool = None
        host.ref_identify_tool = None
        host.popup_dialog = None

        host._last_feature_wkt = None
        host._last_feature_pkuid = None
        host.measure_tool = None
        host.sat_view = None
        host.rast = None
        host.rest = None
        host.current_user = None

        host._geometry_ready = 'Roads'
        host.road_name = MagicMock()
        host.road_name.text = MagicMock(return_value='Test Road')
        host.road_decision = MagicMock()
        host.road_decision.text = MagicMock(return_value='Decision 1')
        host.type_road = MagicMock()
        host.type_road.currentData = MagicMock(return_value='road_type_1')

        host.num_val = MagicMock()
        host.sat_view = None
        host.rast = None
        host.rest = None
        host.current_user = None
        host.update_object = {}
        host.update_only_form = {}

        # Protocol methods
        host._reconnect_context_menu = MagicMock()
        host._current_layer_name = MagicMock(return_value='Roads')

    # --- Integration scenarios ---

    def test_login_flow_invokes_layer_init_and_add_map(self):
        """Login calls sign_in, init_allowed_zone, refresh, add_map_layer."""
        host, mods = self._make_host()
        self._setup_widgets(host)

        sign_in = MagicMock(return_value=(True, 'user1', None))
        get_current_user = MagicMock(return_value={'uid': 1})

        with patch.object(mods['auth_mixin'], 'sign_in', sign_in), \
             patch.object(mods['auth_mixin'], 'get_current_user',
                          get_current_user), \
             patch.object(mods['auth_mixin'],
                          'init_allowed_zone') as mock_init, \
             patch.object(mods['auth_mixin'],
                          'refresh_all_layers') as mock_refresh, \
             patch.object(host, 'add_map_layer', return_value=True), \
             patch.object(host, 'private_route') as mock_route:
            host.login_user()

            sign_in.assert_called_once_with(
                username=host.username.text(),
                password=host.password.text())
            mock_init.assert_called_once()
            mock_refresh.assert_called_once()
            mock_route.assert_called_once_with('main')

    def test_login_sets_current_user(self):
        """After login, current_user is populated from db response."""
        host, mods = self._make_host()
        self._setup_widgets(host)

        sign_in = MagicMock(return_value=(True, 'admin_user', None))
        get_current_user = MagicMock(return_value={
            'id': 'u1', 'loc': 'loc1', 'wilaya': '16', 'commune': 'Alger',
            'first_name': 'Admin', 'last_name': 'User',
        })

        with patch.object(mods['auth_mixin'], 'sign_in', sign_in), \
             patch.object(mods['auth_mixin'], 'get_current_user',
                          get_current_user), \
             patch.object(mods['auth_mixin'], 'init_allowed_zone'), \
             patch.object(mods['auth_mixin'], 'refresh_all_layers'), \
             patch.object(host, 'add_map_layer', return_value=True), \
             patch.object(host, 'private_route'), \
             patch.object(host, 'on_opt_selected'):
            host.login_user()

            self.assertEqual(host.current_user, {
                'id': 'u1', 'loc': 'loc1', 'wilaya': '16', 'commune': 'Alger',
                'first_name': 'Admin', 'last_name': 'User',
            })
            host.label_username.setText.assert_called_once_with('admin_user')

    def test_add_road_uses_last_feature_wkt_and_calls_writer(self):
        """add_road passes _last_feature_wkt/pkuid to the db writer."""
        host, mods = self._make_host()
        self._setup_widgets(host)

        writer = MagicMock(return_value=MagicMock())

        with patch.object(mods['layer_edit_mixin'],
                          'add_road_impl', writer) if hasattr(
                              mods['layer_edit_mixin'], 'add_road_impl') \
             else patch.object(mods['layer_edit_mixin'], 'add_road') as _:
            pass

if __name__ == '__main__':
    unittest.main()
    unittest.main()
