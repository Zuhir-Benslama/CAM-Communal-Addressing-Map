"""Tests for app.users.repository."""

import unittest
from unittest.mock import MagicMock, patch


class TestLoadSessionCookie(unittest.TestCase):
    @patch('app.users.repository.toml')
    def test_loads_cookie(self, mock_toml):
        mock_toml.load.return_value = {'Session': {'uid': 'abc123', 'cookie': 'xyz789'}}
        from app.users.repository import load_session_cookie

        result = load_session_cookie()
        self.assertEqual(result['Session']['uid'], 'abc123')

    @patch('app.users.repository.Path')
    def test_returns_none_on_missing_file(self, mock_path):
        mock_path.return_value.open.side_effect = FileNotFoundError
        from app.users.repository import load_session_cookie

        result = load_session_cookie()
        self.assertIsNone(result)


class TestGetUserLocation(unittest.TestCase):
    @patch('app.users.repository.get_current_user')
    def test_returns_none_when_no_user(self, mock_user):
        mock_user.return_value = None
        from app.users.repository import get_user_location

        result = get_user_location()
        self.assertIsNone(result)

    @patch('app.users.repository.get_commune_wkt', return_value='POINT(0 0)')
    @patch('app.users.repository._get_authenticated_user')
    def test_returns_wkt(self, mock_auth, mock_wkt):
        mock_auth.return_value = {'commune_id': 42}
        from app.users.repository import get_user_location

        result = get_user_location()
        self.assertEqual(result, 'POINT(0 0)')

    @patch('app.users.repository.get_commune_wkt', return_value=None)
    @patch('app.users.repository._get_authenticated_user')
    def test_returns_none_when_no_row(self, mock_auth, mock_wkt):
        mock_auth.return_value = {'commune_id': 42}
        from app.users.repository import get_user_location

        result = get_user_location()
        self.assertIsNone(result)

    @patch('app.users.repository._get_authenticated_user')
    def test_returns_none_when_no_commune_id(self, mock_auth):
        mock_auth.return_value = {'commune_code': '1601'}
        from app.users.repository import get_user_location

        result = get_user_location()
        self.assertIsNone(result)


class TestCreateCookie(unittest.TestCase):
    @patch('app.users.repository.toml')
    @patch('app.users.repository.os.fdopen')
    @patch('app.users.repository.os.open')
    def test_creates_file(self, mock_open, mock_fdopen, mock_toml):
        from app.users.repository import create_cookie

        create_cookie('test_cookie', 'uid123')
        mock_toml.dump.assert_called_once()
        mock_open.assert_called_once()

    @patch('app.users.repository.os.fdopen')
    @patch('app.users.repository.os.open')
    def test_raises_on_permission_error(self, mock_open, mock_fdopen):
        mock_open.side_effect = PermissionError
        from app.users.repository import create_cookie

        with self.assertRaises(PermissionError):
            create_cookie('test_cookie', 'uid123')


class TestQgisConfig(unittest.TestCase):
    def test_returns_cached_config(self):
        from app.users.repository import reset_qgis_config_cache

        reset_qgis_config_cache()

    @patch('app.users.repository.Path')
    def test_returns_config(self, mock_path):
        mock_file = MagicMock()
        mock_file.__enter__ = lambda s: mock_file
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_path.return_value.open.return_value = mock_file
        mock_file.read.return_value = '{"layers": []}'

        with patch('app.users.repository.json') as mock_json:
            mock_json.load.return_value = {'layers': []}
            from app.users.repository import qgis_config, reset_qgis_config_cache

            reset_qgis_config_cache()
            result = qgis_config()
            self.assertIsNotNone(result)


class TestFindActiveSessionUser(unittest.TestCase):
    def test_returns_user_when_found(self):
        from app.users.repository import find_active_session_user

        mock_session = MagicMock()
        mock_user = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_user
        )
        result = find_active_session_user(mock_session, 'uid123', 'cookie123')
        self.assertIs(result, mock_user)

    def test_returns_none_when_not_found(self):
        from app.users.repository import find_active_session_user

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        result = find_active_session_user(mock_session, 'uid123', 'cookie123')
        self.assertIsNone(result)


class TestGetCommuneByCode(unittest.TestCase):
    def test_returns_none_when_no_code(self):
        from app.users.repository import _get_commune_by_code

        self.assertIsNone(_get_commune_by_code(None))
        self.assertIsNone(_get_commune_by_code(''))
        self.assertIsNone(_get_commune_by_code('abc'))

    @patch('app.users.repository._load_localites')
    def test_returns_commune(self, mock_load):
        mock_load.return_value = [{'commune_code': 1601, 'name': 'Alger'}]
        from app.users.repository import _get_commune_by_code

        result = _get_commune_by_code(1601)
        self.assertIsNotNone(result)

    @patch('app.users.repository._load_localites')
    def test_returns_none_when_not_found(self, mock_load):
        mock_load.return_value = [{'commune_code': 1601, 'name': 'Alger'}]
        from app.users.repository import _get_commune_by_code

        result = _get_commune_by_code(9999)
        self.assertIsNone(result)


class TestLoadLocalites(unittest.TestCase):
    @patch('app.shared.geo.COMMUNES_JSON', '/fake/communes.json')
    @patch('app.shared.geo.json')
    @patch('app.shared.geo.Path')
    def test_loads_localites(self, mock_path, mock_json):
        mock_json.load.return_value = {'1': {'commune_code': 1601}}
        from app.users.repository import _load_localites

        result = _load_localites()
        self.assertEqual(len(result), 1)

    @patch('app.shared.geo.COMMUNES_JSON', '/nonexistent/communes.json')
    def test_returns_empty_on_error(self):
        from app.users.repository import _load_localites

        result = _load_localites()
        self.assertEqual(result, [])


class TestLoadSessionCookieExtended(unittest.TestCase):
    @patch('app.users.repository.Path')
    def test_returns_none_on_toml_decode_error(self, mock_path):
        import toml

        mock_path.return_value.open.side_effect = toml.TomlDecodeError('', '', 0)
        from app.users.repository import load_session_cookie

        result = load_session_cookie()
        self.assertIsNone(result)

    @patch('app.users.repository.Path')
    def test_returns_none_on_os_error(self, mock_path):
        mock_path.return_value.open.side_effect = OSError('read failed')
        from app.users.repository import load_session_cookie

        result = load_session_cookie()
        self.assertIsNone(result)


class TestGetCurrentUser(unittest.TestCase):
    @patch('app.users.repository.toml')
    def test_returns_none_when_no_cookie_data(self, mock_toml):
        mock_toml.load.return_value = None
        from app.users.repository import get_current_user

        result = get_current_user()
        self.assertIsNone(result)

    @patch('app.users.repository.toml')
    def test_returns_none_when_no_session_key(self, mock_toml):
        mock_toml.load.return_value = {}
        from app.users.repository import get_current_user

        result = get_current_user()
        self.assertIsNone(result)

    @patch('app.users.repository.toml')
    def test_returns_none_when_cookie_missing(self, mock_toml):
        mock_toml.load.return_value = {'Session': {'uid': 'abc'}}
        from app.users.repository import get_current_user

        result = get_current_user()
        self.assertIsNone(result)

    @patch('app.users.repository.toml')
    def test_returns_none_when_uid_missing(self, mock_toml):
        mock_toml.load.return_value = {'Session': {'cookie': 'tok'}}
        from app.users.repository import get_current_user

        result = get_current_user()
        self.assertIsNone(result)

    @patch('app.users.repository.toml')
    @patch('app.users.repository.get_session')
    def test_returns_none_when_user_not_found(self, mock_session_fn, mock_toml):
        mock_toml.load.return_value = {'Session': {'cookie': 'tok', 'uid': 'abc'}}
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session_fn.return_value = mock_session
        from app.users.repository import get_current_user

        result = get_current_user()
        self.assertIsNone(result)
        mock_session.close.assert_called_once()

    @patch('app.users.repository.WILAYAS_JSON', '/nonexistent/wilayas.json')
    @patch('app.users.repository.toml')
    @patch('app.users.repository.get_session')
    @patch('app.users.repository._get_commune_by_code', return_value=None)
    def test_returns_user_with_wilaya_load_error(
        self, mock_commune, mock_session_fn, mock_toml
    ):
        mock_toml.load.return_value = {'Session': {'cookie': 'tok', 'uid': 'abc'}}
        user = MagicMock()
        user.commune_code = '1601'
        user.wilaya_code = 16
        user.first_name = 'Test'
        user.last_name = 'User'
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = user
        mock_session_fn.return_value = mock_session
        from app.users.repository import get_current_user

        result = get_current_user()
        self.assertIsNotNone(result)
        self.assertEqual(result['wilaya'], '')

    @patch('app.users.repository.toml')
    @patch('app.users.repository.get_session')
    @patch('app.users.repository._get_commune_by_code')
    def test_returns_user_with_commune_fallback_fr(
        self, mock_commune, mock_session_fn, mock_toml
    ):
        mock_toml.load.return_value = {'Session': {'cookie': 'tok', 'uid': 'abc'}}
        user = MagicMock()
        user.commune_code = '1601'
        user.wilaya_code = None
        user.first_name = 'Test'
        user.last_name = 'User'
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = user
        mock_session_fn.return_value = mock_session
        mock_commune.return_value = {
            'commune_code': 1601,
            'commune_ar': None,
            'commune_fr': 'Alger',
        }
        from app.users.repository import get_current_user

        result = get_current_user()
        self.assertEqual(result['commune'], 'Alger')

    @patch('app.users.repository.toml')
    @patch('app.users.repository.get_session')
    @patch('app.users.repository._get_commune_by_code')
    def test_returns_user_with_no_commune(
        self, mock_commune, mock_session_fn, mock_toml
    ):
        mock_toml.load.return_value = {'Session': {'cookie': 'tok', 'uid': 'abc'}}
        user = MagicMock()
        user.commune_code = None
        user.wilaya_code = None
        user.first_name = 'Test'
        user.last_name = 'User'
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = user
        mock_session_fn.return_value = mock_session
        mock_commune.return_value = None
        from app.users.repository import get_current_user

        result = get_current_user()
        self.assertIsNotNone(result)
        self.assertEqual(result['commune'], '')

    @patch('app.users.repository.toml')
    @patch('app.users.repository.get_session')
    @patch('app.users.repository._get_commune_by_code')
    @patch('app.users.repository.json')
    def test_returns_user_with_wilaya_name_loaded(
        self, mock_json, mock_commune, mock_session_fn, mock_toml
    ):
        mock_toml.load.return_value = {'Session': {'cookie': 'tok', 'uid': 'abc'}}
        user = MagicMock()
        user.commune_code = '1601'
        user.wilaya_code = 16
        user.first_name = 'Test'
        user.last_name = 'User'
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = user
        mock_session_fn.return_value = mock_session
        mock_commune.return_value = {'commune_ar': 'الجزائر', 'commune_fr': None}
        json_file = MagicMock()
        json_file.__enter__ = lambda s: json_file
        json_file.__exit__ = MagicMock(return_value=False)
        with patch('app.users.repository.Path') as mock_path_cls:
            mock_path_cls.return_value.open.return_value = json_file
            mock_json.load.return_value = {
                '16': {'wilaya_ar': 'الجزائر'},
                '31': {'wilaya_ar': 'وهران'},
            }
            from app.users.repository import get_current_user

            result = get_current_user()
        self.assertEqual(result['wilaya'], 'الجزائر')
        self.assertEqual(result['commune'], 'الجزائر')


class TestQgisConfigExtended(unittest.TestCase):
    @patch('app.users.repository.Path')
    def test_returns_cached_config(self, mock_path_cls):
        from app.users.repository import qgis_config, reset_qgis_config_cache

        reset_qgis_config_cache()
        mock_file = MagicMock()
        mock_file.__enter__ = lambda s: mock_file
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_path_cls.return_value.open.return_value = mock_file

        with patch('app.users.repository.json') as mock_json:
            mock_json.load.return_value = {'key': 'value'}
            first = qgis_config()
            second = qgis_config()
            self.assertIs(first, second)
            self.assertEqual(mock_json.load.call_count, 1)

    @patch('app.users.repository.Path')
    def test_raises_on_file_not_found(self, mock_path_cls):
        from app.users.repository import qgis_config, reset_qgis_config_cache

        reset_qgis_config_cache()
        mock_path_cls.return_value.open.side_effect = FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            qgis_config()

    @patch('app.users.repository.Path')
    def test_raises_on_json_decode_error(self, mock_path_cls):
        import json as _json

        from app.users.repository import qgis_config, reset_qgis_config_cache

        reset_qgis_config_cache()
        mock_file = MagicMock()
        mock_file.__enter__ = lambda s: mock_file
        mock_file.__exit__ = MagicMock(return_value=False)
        mock_path_cls.return_value.open.return_value = mock_file

        with patch('app.users.repository.json') as mock_json:
            mock_json.JSONDecodeError = _json.JSONDecodeError
            mock_json.load.side_effect = _json.JSONDecodeError('err', '', 0)
            with self.assertRaises(_json.JSONDecodeError):
                qgis_config()


class TestGetAuthenticatedUser(unittest.TestCase):
    @patch('app.users.repository.get_current_user')
    def test_returns_none_when_no_user(self, mock_user):
        mock_user.return_value = None
        from app.users.repository import _get_authenticated_user

        result = _get_authenticated_user()
        self.assertIsNone(result)

    @patch('app.users.repository._get_commune_by_code')
    @patch('app.users.repository.get_current_user')
    def test_returns_commune(self, mock_user, mock_commune):
        mock_user.return_value = {'commune_code': '1601'}
        mock_commune.return_value = {'commune_code': 1601, 'name': 'Alger'}
        from app.users.repository import _get_authenticated_user

        result = _get_authenticated_user()
        self.assertIsNotNone(result)
