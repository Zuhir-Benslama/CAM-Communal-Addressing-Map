"""Tests for app.users.repository."""

import unittest
from unittest.mock import MagicMock, patch, mock_open


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

    @patch('app.users.repository.sqlite3')
    @patch('app.users.repository._get_authenticated_user')
    def test_returns_wkt(self, mock_auth, mock_sqlite):
        mock_auth.return_value = {'commune_id': 42}
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ['POINT(0 0)']
        mock_conn.execute.return_value = mock_cursor
        mock_sqlite.connect.return_value.__enter__ = lambda s: mock_conn
        mock_sqlite.connect.return_value.__exit__ = MagicMock(return_value=False)
        from app.users.repository import get_user_location

        result = get_user_location()
        self.assertEqual(result, 'POINT(0 0)')

    @patch('app.users.repository.sqlite3')
    @patch('app.users.repository._get_authenticated_user')
    def test_returns_none_on_sqlite_error(self, mock_auth, mock_sqlite):
        mock_auth.return_value = {'commune_id': 42}
        import sqlite3

        mock_sqlite.connect.side_effect = sqlite3.Error('db locked')
        mock_sqlite.Error = sqlite3.Error
        from app.users.repository import get_user_location

        result = get_user_location()
        self.assertIsNone(result)

    @patch('app.users.repository.sqlite3')
    @patch('app.users.repository._get_authenticated_user')
    def test_returns_none_when_no_row(self, mock_auth, mock_sqlite):
        mock_auth.return_value = {'commune_id': 42}
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.execute.return_value = mock_cursor
        mock_sqlite.connect.return_value.__enter__ = lambda s: mock_conn
        mock_sqlite.connect.return_value.__exit__ = MagicMock(return_value=False)
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
    def test_creates_file(self, mock_toml):
        with patch('builtins.open', mock_open()):
            from app.users.repository import create_cookie

            with patch('app.users.repository.Path'):
                create_cookie('test_cookie', 'uid123')
                mock_toml.dump.assert_called_once()

    @patch('app.users.repository.Path')
    def test_raises_on_permission_error(self, mock_path_cls):
        mock_path_cls.return_value.open.side_effect = PermissionError
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
    @patch('app.users.repository.json')
    @patch('app.users.repository.Path')
    def test_loads_localites(self, mock_path, mock_json):
        mock_json.load.return_value = {'1': {'commune_code': 1601}}
        from app.users.repository import _load_localites

        result = _load_localites()
        self.assertEqual(len(result), 1)

    @patch('app.users.repository.Path')
    def test_returns_empty_on_error(self, mock_path):
        mock_path.return_value.open.side_effect = FileNotFoundError
        from app.users.repository import _load_localites

        result = _load_localites()
        self.assertEqual(result, [])


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
