"""Tests for database operations (spatialite, auth, config)."""

import json
import os
import shutil
import unittest
from unittest.mock import MagicMock, patch

from app.core.config import find_mod_spatialite_dll
from app.core.security import hash_password, verify_password
from app.users.repository import (
    _get_authenticated_user,
    create_cookie,
    qgis_config,
)

TMPDIR = os.path.join(os.path.dirname(__file__), '__testtmp__')


def setUpModule() -> None:
    os.makedirs(TMPDIR, exist_ok=True)


def tearDownModule() -> None:
    shutil.rmtree(TMPDIR, ignore_errors=True)


def _clean_tmpdir() -> None:
    if os.path.exists(TMPDIR):
        shutil.rmtree(TMPDIR)
    os.makedirs(TMPDIR, exist_ok=True)


class TestFindModSpatialiteDLL(unittest.TestCase):
    @patch('app.core.config.os.name', 'nt')
    def test_windows_default(self) -> None:
        self.assertEqual(find_mod_spatialite_dll(), 'mod_spatialite.dll')

    @patch('app.core.config.os.name', 'posix')
    @patch('app.core.config.os.uname')
    def test_macos_default(self, mock_uname: MagicMock) -> None:
        mock_uname.return_value.sysname = 'Darwin'
        result = find_mod_spatialite_dll()
        self.assertEqual(result, 'mod_spatialite.dylib')

    @patch('app.core.config.os.path.exists', return_value=False)
    @patch('app.core.config.os.name', 'posix')
    @patch('app.core.config.os.uname')
    def test_linux_default(
        self, mock_uname: MagicMock, _mock_exists: MagicMock
    ) -> None:
        mock_uname.return_value.sysname = 'Linux'
        result = find_mod_spatialite_dll()
        self.assertEqual(result, 'mod_spatialite.so')

    @patch('app.core.config.os.getenv')
    def test_env_var_override(self, mock_getenv: MagicMock) -> None:
        mock_getenv.return_value = '/custom/path/mod_spatialite.so'
        result = find_mod_spatialite_dll()
        self.assertEqual(result, '/custom/path/mod_spatialite.so')
        mock_getenv.assert_called_once_with('MOD_SPATIALITE_DLL')


class TestPasswordFunctions(unittest.TestCase):
    def test_hash_and_verify_roundtrip(self) -> None:
        password = 'test_password_123'
        hashed = hash_password(password)
        self.assertTrue(verify_password(password, hashed))

    def test_verify_wrong_password(self) -> None:
        password = 'correct_password'
        hashed = hash_password(password)
        self.assertFalse(verify_password('wrong_password', hashed))

    def test_hash_is_different_each_time(self) -> None:
        password = 'same_password'
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        self.assertNotEqual(hash1, hash2)


class TestCreateCookie(unittest.TestCase):
    def setUp(self) -> None:
        _clean_tmpdir()

    def test_create_cookie_writes_file(self) -> None:
        cookie_path = os.path.join(TMPDIR, 'cookie.toml')
        with patch('app.users.repository.COOKIE_FILE', cookie_path):
            create_cookie('test_cookie', 'test_uid')
        self.assertTrue(os.path.exists(cookie_path))
        with open(cookie_path, encoding='utf-8') as f:
            data = f.read()
        self.assertIn('test_cookie', data)
        self.assertIn('test_uid', data)


class TestQgisConfig(unittest.TestCase):
    def setUp(self) -> None:
        _clean_tmpdir()

    def test_qgis_config_reads_json(self) -> None:
        expected = {'other_layers': [], 'mapper': {}}
        config_path = os.path.join(TMPDIR, 'qgis_config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(expected, f)
        with patch('app.users.repository.QGIS_CONFIG_FILE', config_path):
            result = qgis_config()
            self.assertEqual(result, expected)


class TestGetAuthenticatedUser(unittest.TestCase):
    def setUp(self) -> None:
        _clean_tmpdir()

    def test_no_cookie_file_returns_none(self) -> None:
        cookie_path = os.path.join(TMPDIR, 'cookie.toml')
        with (
            patch('app.users.repository.COOKIE_FILE', cookie_path),
            patch('app.users.repository.get_session') as mock_session,
        ):
            result = _get_authenticated_user()
            self.assertIsNone(result)
            mock_session.assert_not_called()

    def test_user_not_found_returns_none(self) -> None:
        cookie_path = os.path.join(TMPDIR, 'cookie.toml')
        with open(cookie_path, 'w', encoding='utf-8') as f:
            f.write('[Session]\ncookie = "ck"\nuid = "ui"\n')
        with (
            patch('app.users.repository.COOKIE_FILE', cookie_path),
            patch('app.users.repository.get_session') as mock_session,
        ):
            mock_session_instance = MagicMock()
            mock_session.return_value = mock_session_instance
            mock_query = mock_session_instance.query.return_value
            mock_filter = mock_query.filter.return_value
            mock_filter.first.return_value = None
            result = _get_authenticated_user()
            self.assertIsNone(result)

    def test_commune_not_found_returns_none(self) -> None:
        cookie_path = os.path.join(TMPDIR, 'cookie.toml')
        with open(cookie_path, 'w', encoding='utf-8') as f:
            f.write('[Session]\ncookie = "ck"\nuid = "ui"\n')
        with (
            patch('app.users.repository.COOKIE_FILE', cookie_path),
            patch('app.users.repository.get_session') as mock_session,
            patch('app.users.repository._load_localites', return_value=[]),
        ):
            mock_session_instance = MagicMock()
            mock_session.return_value = mock_session_instance
            mock_session_instance.query.return_value.filter.return_value.first.return_value = MagicMock(
                id='u1',
                api_key='',
                session_token='ck',
                active=True,
                commune_code='unknown',
                wilaya_code=None,
            )
            result = _get_authenticated_user()
            self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
