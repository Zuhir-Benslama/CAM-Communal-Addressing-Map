"""Tests for auth/operations.py — sign up, sign in, logout."""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

os.environ['RNA_JWT_SECRET'] = 'test-secret-key-for-testing-only'

# Mock QGIS modules before importing auth.operations
qgis = MagicMock()
qgis.PyQt = MagicMock()
qgis.PyQt.QtWidgets = MagicMock()
qgis.core = MagicMock()
qgis.core.QgsProject = MagicMock()
qgis.core.QgsMessageLog = MagicMock()
sys.modules['qgis'] = qgis
sys.modules['qgis.PyQt'] = qgis.PyQt
sys.modules['qgis.PyQt.QtWidgets'] = qgis.PyQt.QtWidgets
sys.modules['qgis.core'] = qgis.core

# Now safe to import
from auth.operations import sign_up, sign_in, logout, JWT_SECRET


class TestJWTSecret(unittest.TestCase):
    def test_jwt_secret_reads_from_env(self):
        self.assertEqual(JWT_SECRET, 'test-secret-key-for-testing-only')


class TestSignUp(unittest.TestCase):
    def setUp(self):
        self.mock_spatial_session = MagicMock()
        self.mock_auth_session = MagicMock()
        self.mock_get_session = patch(
            'auth.operations.get_session',
            return_value=self.mock_spatial_session
        ).start()
        self.mock_get_auth_session = patch(
            'auth.operations.get_auth_session',
            return_value=self.mock_auth_session
        ).start()
        self.mock_msgbox_cls = patch(
            'auth.operations.QMessageBox'
        ).start()

    def tearDown(self):
        patch.stopall()

    def test_sign_up_creates_user_in_both_dbs(self):
        with patch('auth.operations.hash_password', return_value='hashed_pw'):
            result = sign_up(
                'newuser', 'secret123', 1, '0555000000',
                'new@test.com', 'New', 'User'
            )
        self.assertTrue(result)
        self.mock_spatial_session.add.assert_called_once()
        self.mock_spatial_session.commit.assert_called_once()
        self.mock_auth_session.add.assert_called_once()
        self.mock_auth_session.commit.assert_called_once()
        self.mock_spatial_session.close.assert_called_once()
        self.mock_auth_session.close.assert_called_once()

    def test_sign_up_validation_error_returns_false(self):
        from marshmallow import ValidationError
        with patch(
            'auth.operations.SignupSchema.load',
            side_effect=ValidationError({'username': ['Required']})
        ):
            result = sign_up('', '', 0, '', '', '', '')
        self.assertFalse(result)
        self.mock_spatial_session.add.assert_not_called()
        # Sessions never opened because validation fails before get_session()
        self.mock_spatial_session.close.assert_not_called()
        self.mock_auth_session.close.assert_not_called()


class TestSignIn(unittest.TestCase):
    def setUp(self):
        self.mock_auth_session = MagicMock()
        self.mock_spatial_session = MagicMock()
        self.mock_get_auth_session = patch(
            'auth.operations.get_auth_session',
            return_value=self.mock_auth_session
        ).start()
        self.mock_get_session = patch(
            'auth.operations.get_session',
            return_value=self.mock_spatial_session
        ).start()
        self.mock_msgbox_cls = patch(
            'auth.operations.QMessageBox'
        ).start()
        self.mock_jwt_encode = patch(
            'auth.operations.jwt.encode', return_value='fake.jwt.token'
        ).start()
        self.label_mock = MagicMock()

    def tearDown(self):
        patch.stopall()

    def _make_user_mock(self, **kwargs):
        user = MagicMock()
        user.password = kwargs.get('password', 'hashed_pw')
        user.username = kwargs.get('username', 'test')
        user.id = kwargs.get('id', 1)
        user.to_dict.return_value = kwargs.get(
            'to_dict', {'id': 1, 'username': 'test'}
        )
        return user

    def test_sign_in_success_returns_true(self):
        mock_user = self._make_user_mock()

        auth_query = self.mock_auth_session.query.return_value
        auth_query.filter_by.return_value.first.return_value = mock_user

        spatial_query = self.mock_spatial_session.query.return_value
        spatial_query.filter_by.return_value.first.return_value = mock_user

        with patch('auth.operations.verify_password', return_value=True):
            result = sign_in('test', 'password', self.label_mock)

        self.assertTrue(result)
        self.label_mock.setText.assert_called_once_with('test')

    def test_sign_in_username_does_not_exist(self):
        auth_query = self.mock_auth_session.query.return_value
        auth_query.filter_by.return_value.first.return_value = None

        result = sign_in('unknown', 'password', self.label_mock)
        self.assertFalse(result)

    def test_sign_in_wrong_password(self):
        mock_user = self._make_user_mock()

        auth_query = self.mock_auth_session.query.return_value
        auth_query.filter_by.return_value.first.return_value = mock_user

        with patch('auth.operations.verify_password', return_value=False):
            result = sign_in('test', 'wrongpass', self.label_mock)
        self.assertFalse(result)

    def test_sign_in_validation_error(self):
        from marshmallow import ValidationError
        with patch(
            'auth.operations.AuthSchema.load',
            side_effect=ValidationError({'USERNAME': ['Required']})
        ):
            result = sign_in('', '', self.label_mock)
        self.assertFalse(result)

    def test_sign_in_exception_triggers_rollback(self):
        self.mock_auth_session.query.side_effect = Exception('DB error')
        result = sign_in('test', 'password', self.label_mock)
        self.assertFalse(result)
        self.mock_auth_session.rollback.assert_called_once()


class TestLogout(unittest.TestCase):
    def setUp(self):
        self.mock_spatial_session = MagicMock()
        self.mock_auth_session = MagicMock()
        self.mock_get_session = patch(
            'auth.operations.get_session',
            return_value=self.mock_spatial_session
        ).start()
        self.mock_get_auth_session = patch(
            'auth.operations.get_auth_session',
            return_value=self.mock_auth_session
        ).start()
        self.mock_toml = patch('auth.operations.toml').start()
        self.mock_iface = MagicMock()

    def tearDown(self):
        patch.stopall()

    def test_logout_clears_cookie_and_closes(self):
        mock_user = MagicMock()
        mock_user.active = True
        self.mock_toml.load.return_value = {
            'Session': {'cookie': 'tok', 'uid': 1}
        }

        spatial_query = self.mock_spatial_session.query.return_value
        spatial_query.filter.return_value.first.return_value = mock_user
        auth_query = self.mock_auth_session.query.return_value
        auth_query.filter.return_value.first.return_value = mock_user

        with patch('builtins.open', MagicMock()):
            logout(self.mock_iface, None)

        self.assertIsNone(mock_user.api_key)
        self.mock_spatial_session.commit.assert_called_once()
        self.mock_auth_session.commit.assert_called_once()
        self.mock_spatial_session.close.assert_called_once()
        self.mock_auth_session.close.assert_called_once()

    def test_logout_no_cookie_skips_clear(self):
        self.mock_toml.load.return_value = {
            'Session': {'cookie': None, 'uid': None}
        }
        with patch('builtins.open', MagicMock()):
            logout(self.mock_iface, None)
        self.mock_spatial_session.query.assert_not_called()

    def test_logout_no_cookie_entry_skips_clear(self):
        self.mock_toml.load.return_value = {}
        with patch('builtins.open', MagicMock()):
            logout(self.mock_iface, None)
        self.mock_spatial_session.query.assert_not_called()


if __name__ == '__main__':
    unittest.main()
