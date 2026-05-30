"""Tests for mixins/auth_mixin.py."""
import importlib
import sys
import unittest
from unittest.mock import MagicMock, patch

from test.helpers import setup_gui_mocks, get_qapp


@unittest.skipIf(get_qapp() is None, 'PyQt5 not available')
class TestAuthMixin(unittest.TestCase):
    """Test auth_mixin login/logout/signup flow."""

    @classmethod
    def setUpClass(cls):
        cls.app = get_qapp()
        setup_gui_mocks()
        spec = importlib.util.spec_from_file_location(
            'plans_adressage.mixins.auth_mixin',
            'mixins/auth_mixin.py',
        )
        cls.mod = importlib.util.module_from_spec(spec)
        sys.modules['plans_adressage.mixins.auth_mixin'] = cls.mod
        spec.loader.exec_module(cls.mod)

    def setUp(self):
        self.mixin = self.mod.AuthMixin()
        self.mixin._tr = lambda s: s
        for attr in ('commune_of_wilaya', 'uname', 'pwd', 'email',
                     'fname', 'lname', 'pnum', 'username', 'password',
                     'label_username', 'wilaya_list', 'org_cat',
                     'org_type', 'activity_cat', 'activity_type'):
            setattr(self.mixin, attr, MagicMock())
        self.mixin.map_options = MagicMock()
        self.mixin.router = MagicMock()
        self.mixin.router.findChild = MagicMock(return_value=MagicMock())
        self.mixin.menu = MagicMock()
        self.mixin.menu.currentIndex = MagicMock(return_value=0)
        for attr in ('identify_tool', 'popup_dialog', 'sat_view', 'rest',
                     'rast', 'iface', 'current_user'):
            setattr(self.mixin, attr, None)
        self.mixin.stop = MagicMock()
        self.mixin.on_opt_selected = MagicMock()

        # Override validate_text to accept a single string argument
        self.mod.validate_text = MagicMock(side_effect=lambda x: (True, x))

    def test_show_error_calls_messagebox(self):
        with patch.object(self.mod, 'QMessageBox') as mock_mb:
            self.mixin._show_error('test error')
            mock_mb.critical.assert_called_once()

    def test_show_info_calls_messagebox(self):
        with patch.object(self.mod, 'QMessageBox') as mock_mb:
            self.mixin._show_info('test info')
            mock_mb.information.assert_called_once()

    def test_submit_add_usr_success(self):
        sign_up = MagicMock(return_value=(True, []))
        with patch.object(self.mod, 'sign_up', sign_up), \
             patch.object(self.mixin, 'public_route') as mock_route:
            self.mixin.submit_add_usr()
            sign_up.assert_called_once()
            mock_route.assert_called_once_with('login')

    def test_submit_add_usr_failure(self):
        sign_up = MagicMock(return_value=(False, ['error1', 'error2']))
        with patch.object(self.mod, 'sign_up', sign_up):
            with patch.object(self.mixin, '_show_error') as mock_err:
                self.mixin.submit_add_usr()
                mock_err.assert_called_once_with('error1\nerror2')

    def test_login_user_success(self):
        sign_in = MagicMock(return_value=(True, 'user1', None))
        get_current_user = MagicMock(return_value={'uid': 1})
        with patch.object(self.mod, 'sign_in', sign_in), \
             patch.object(self.mod, 'get_current_user', get_current_user), \
             patch.object(self.mod, 'init_allowed_zone'), \
             patch.object(self.mod, 'refresh_all_layers'), \
             patch.object(self.mixin, 'add_map_layer', return_value=True), \
             patch.object(self.mixin, 'private_route') as mock_route:
            self.mixin.login_user()
            sign_in.assert_called_once()
            mock_route.assert_called_once_with('main')
            self.mixin.menu.setCurrentIndex.assert_called_once_with(0)

    def test_login_user_auth_ok_map_fails(self):
        sign_in = MagicMock(return_value=(True, 'user1', None))
        with patch.object(self.mod, 'sign_in', sign_in), \
             patch.object(self.mixin, 'add_map_layer', return_value=False), \
             patch.object(self.mixin, '_show_error') as mock_err:
            self.mixin.login_user()
            mock_err.assert_called_once()

    def test_login_user_map_load_failure_does_not_route(self):
        sign_in = MagicMock(return_value=(True, 'user1', None))
        get_current_user = MagicMock(return_value={'uid': 1})
        with patch.object(self.mod, 'sign_in', sign_in), \
             patch.object(self.mod, 'get_current_user', get_current_user), \
             patch.object(self.mod, 'init_allowed_zone',
                          side_effect=RuntimeError('load failed')), \
             patch.object(self.mixin, 'add_map_layer', return_value=True), \
             patch.object(self.mixin, 'private_route') as mock_route, \
             patch.object(self.mixin, '_show_error') as mock_err:
            self.mixin.login_user()
            mock_route.assert_not_called()
            self.mixin.menu.setCurrentIndex.assert_not_called()
            self.mixin.on_opt_selected.assert_not_called()
            mock_err.assert_called_once()

    def test_login_user_wrong_password(self):
        sign_in = MagicMock(return_value=(False, None, 'wrong password'))
        with patch.object(self.mod, 'sign_in', sign_in), \
             patch.object(self.mixin, '_show_error') as mock_err:
            self.mixin.login_user()
            mock_err.assert_called_once_with('wrong password')

    def test_fill_map_options(self):
        qgis_config = MagicMock(return_value={
            'map_layers': [
                {'label': 'Satellite', 'url': 'url1'},
                {'label': 'OSM', 'url': 'url2'},
            ],
        })
        with patch.object(self.mod, 'qgis_config', qgis_config):
            self.mixin.fill_map_options()
            self.mixin.map_options.clear.assert_called_once()
            self.assertEqual(self.mixin.map_options.addItem.call_count, 2)

    def test_add_map_layer_wms(self):
        self.mixin.map_options = MagicMock()
        self.mixin.map_options.currentText = MagicMock(
            return_value='Satellite View 1')
        self.mixin.map_options.currentData = MagicMock(
            return_value='url_value')
        osm_layer = MagicMock()
        osm_layer.isValid = MagicMock(return_value=True)
        with patch.object(self.mod, 'QgsRasterLayer',
                          return_value=osm_layer), \
             patch.object(self.mod, 'QgsProject') as mock_project:
            (mock_project.instance.return_value
             .mapLayersByName.return_value) = []
            result = self.mixin.add_map_layer()
            self.assertTrue(result)
            self.assertEqual(self.mixin.sat_view, 'Satellite View 1')
            self.assertIsNone(self.mixin.rest)

    def test_add_map_layer_wms_already_exists(self):
        self.mixin.map_options = MagicMock()
        self.mixin.map_options.currentText = MagicMock(
            return_value='Satellite View 1')
        self.mixin.map_options.currentData = MagicMock(
            return_value='url_value')
        osm_layer = MagicMock()
        osm_layer.isValid = MagicMock(return_value=True)
        with patch.object(self.mod, 'QgsRasterLayer',
                          return_value=osm_layer), \
             patch.object(self.mod, 'QgsProject') as mock_project:
            mock_project.instance.return_value.mapLayersByName.return_value = [
                'existing']
            result = self.mixin.add_map_layer()
            self.assertTrue(result)
            self.assertEqual(self.mixin.sat_view, 'Satellite View 1')
            self.assertIsNone(self.mixin.rast)
            mock_project.instance.return_value.addMapLayer.assert_not_called()

    def test_add_map_layer_wms_invalid(self):
        self.mixin.map_options = MagicMock()
        self.mixin.map_options.currentText = MagicMock(
            return_value='Satellite View 1')
        self.mixin.map_options.currentData = MagicMock(
            return_value='url_value')
        osm_layer = MagicMock()
        osm_layer.isValid = MagicMock(return_value=False)
        with patch.object(self.mod, 'QgsRasterLayer', return_value=osm_layer):
            result = self.mixin.add_map_layer()
            self.assertFalse(result)

    def test_private_route_finds_page(self):
        self.mixin.router.findChild = MagicMock(return_value=MagicMock())
        self.mixin.private_route('main')
        self.mixin.router.setCurrentWidget.assert_called_once()

    def test_private_route_no_page(self):
        self.mixin.router.findChild = MagicMock(return_value=None)
        self.mixin.private_route('main')
        self.mixin.router.setCurrentWidget.assert_not_called()

    def test_public_route_finds_page(self):
        self.mixin.router.findChild = MagicMock(return_value=MagicMock())
        self.mixin.public_route('login')
        self.mixin.router.setCurrentWidget.assert_called_once()

    def test_public_route_no_page(self):
        self.mixin.router.findChild = MagicMock(return_value=None)
        self.mixin.public_route('login')
        self.mixin.router.setCurrentWidget.assert_not_called()

    def test_closeEvent_with_identify_tool(self):
        event = MagicMock()
        self.mixin.identify_tool = MagicMock()
        self.mixin.identify_tool.dlg = MagicMock()
        self.mixin.popup_dialog = MagicMock()
        self.mixin.router.findChild = MagicMock(return_value=MagicMock())
        with patch.object(self.mod, 'logout') as mock_logout:
            self.mixin.closeEvent(event)
            mock_logout.assert_called_once()
            self.mixin.popup_dialog.close.assert_called_once()
            event.accept.assert_called_once()

    def test_closeEvent_without_identify_tool(self):
        event = MagicMock()
        self.mixin.identify_tool = None
        self.mixin.popup_dialog = None
        self.mixin.router.findChild = MagicMock(return_value=MagicMock())
        with patch.object(self.mod, 'logout') as mock_logout:
            self.mixin.closeEvent(event)
            mock_logout.assert_called_once_with(
                iface=self.mixin.iface, dlg=None)
            event.accept.assert_called_once()

    def test_on_select_wilaya(self):
        with patch.object(
            self.mod, 'fill_commune_of_wilaya'
        ) as mock_fill:
            self.mixin.on_select_wilaya(0)
            mock_fill.assert_called_once()

    def test_on_select_catOrg(self):
        with patch.object(self.mod, 'fill_org_type') as mock_fill:
            self.mixin.on_select_org_cat(0)
            mock_fill.assert_called_once()

    def test_on_select_catAct(self):
        with patch.object(
            self.mod, 'fill_activity_type'
        ) as mock_fill:
            self.mixin.on_select_activity_cat(0)
            mock_fill.assert_called_once()


if __name__ == '__main__':
    unittest.main()
