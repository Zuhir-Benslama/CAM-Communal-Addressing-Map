import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

os.environ['RNA_JWT_SECRET'] = 'test-secret-key-for-testing-only'

qgis = MagicMock()
qgis.PyQt = MagicMock()
qgis.PyQt.QtCore = MagicMock()
qgis.PyQt.QtWidgets = MagicMock()
qgis.core = MagicMock()
qgis.core.QgsProject = MagicMock()
qgis.core.QgsMessageLog = MagicMock()
sys.modules['qgis'] = qgis
sys.modules['qgis.PyQt'] = qgis.PyQt
sys.modules['qgis.PyQt.QtCore'] = qgis.PyQt.QtCore
sys.modules['qgis.PyQt.QtWidgets'] = qgis.PyQt.QtWidgets
sys.modules['qgis.core'] = qgis.core

from app.users.service import sign_up, sign_in, logout  # noqa: E402
from app.core.security import get_jwt_secret  # noqa: E402


class TestJWTSecret(unittest.TestCase):
    def test_jwt_secret_reads_from_env(self):
        self.assertEqual(get_jwt_secret(), 'test-secret-key-for-testing-only')


class TestSignUp(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_get_session = patch(
            'app.users.service.get_session',
            return_value=self.mock_session
        ).start()

    def tearDown(self):
        patch.stopall()

    def test_sign_up_creates_user(self):
        with patch('app.users.service.hash_password',
                    return_value='hashed_pw'):
            ok, errors = sign_up(
                username='newuser', password='secret123',
                affectation_id=1, phone='0555000000',
                email='new@test.com', first_name='New', lastname='User'
            )
        self.assertTrue(ok)
        self.assertIsNone(errors)
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.mock_session.close.assert_called_once()

    def test_sign_up_validation_error_returns_false(self):
        from marshmallow import ValidationError
        with patch(
            'app.users.service.SignupSchema.load',
            side_effect=ValidationError({'username': ['Required']})
        ):
            ok, errors = sign_up(
                username='', password='', affectation_id=0, phone='',
                email='', first_name='', lastname='',
            )
        self.assertFalse(ok)
        self.assertIsNotNone(errors)
        self.mock_session.add.assert_not_called()
        self.mock_session.close.assert_not_called()


class TestSignIn(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_get_session = patch(
            'app.users.service.get_session',
            return_value=self.mock_session
        ).start()
        self.mock_jwt_encode = patch(
            'app.users.service.jwt.encode', return_value='fake.jwt.token'
        ).start()

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

        session_query = self.mock_session.query.return_value
        session_query.filter_by.return_value.first.return_value = mock_user

        with patch('app.users.service.verify_password', return_value=True):
            ok, username, error = sign_in('test', 'password')

        self.assertTrue(ok)
        self.assertEqual(username, 'test')
        self.assertIsNone(error)

    def test_sign_in_username_does_not_exist(self):
        session_query = self.mock_session.query.return_value
        session_query.filter_by.return_value.first.return_value = None

        ok, username, error = sign_in('unknown', 'password')
        self.assertFalse(ok)
        self.assertIsNone(username)
        self.assertIsNotNone(error)

    def test_sign_in_wrong_password(self):
        mock_user = self._make_user_mock()

        session_query = self.mock_session.query.return_value
        session_query.filter_by.return_value.first.return_value = mock_user

        with patch('app.users.service.verify_password', return_value=False):
            ok, username, error = sign_in('test', 'wrongpass')
        self.assertFalse(ok)
        self.assertIsNone(username)
        self.assertIsNotNone(error)

    def test_sign_in_validation_error(self):
        from marshmallow import ValidationError
        with patch(
            'app.users.service.AuthSchema.load',
            side_effect=ValidationError({'USERNAME': ['Required']})
        ):
            ok, username, error = sign_in('', '')
        self.assertFalse(ok)
        self.assertIsNone(username)
        self.assertIsNotNone(error)

    def test_sign_in_exception_triggers_rollback(self):
        self.mock_session.query.side_effect = Exception('DB error')
        ok, username, error = sign_in('test', 'password')
        self.assertFalse(ok)
        self.assertIsNone(username)
        self.assertIsNotNone(error)
        self.mock_session.rollback.assert_called_once()


class TestLogout(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_get_session = patch(
            'app.users.service.get_session',
            return_value=self.mock_session
        ).start()
        self.mock_toml = patch('app.users.service.toml').start()
        self.mock_iface = MagicMock()

    def tearDown(self):
        patch.stopall()

    def test_logout_clears_cookie_and_closes(self):
        mock_user = MagicMock()
        mock_user.active = True
        self.mock_toml.load.return_value = {
            'Session': {'cookie': 'tok', 'uid': 1}
        }

        session_query = self.mock_session.query.return_value
        session_query.filter.return_value.first.return_value = mock_user

        with patch('builtins.open', MagicMock()):
            logout(self.mock_iface, None)

        self.assertIsNone(mock_user.api_key)
        self.mock_session.commit.assert_called_once()
        self.mock_session.close.assert_called_once()

    def test_logout_no_cookie_skips_clear(self):
        self.mock_toml.load.return_value = {
            'Session': {'cookie': None, 'uid': None}
        }
        with patch('builtins.open', MagicMock()):
            logout(self.mock_iface, None)
        self.mock_session.query.assert_not_called()

    def test_logout_no_cookie_entry_skips_clear(self):
        self.mock_toml.load.return_value = {}
        with patch('builtins.open', MagicMock()):
            logout(self.mock_iface, None)
        self.mock_session.query.assert_not_called()


if __name__ == '__main__':
    unittest.main()
