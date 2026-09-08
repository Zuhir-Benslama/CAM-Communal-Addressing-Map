"""Tests for authentication (JWT, sign-up, sign-in, logout)."""

import sys
import unittest
from unittest.mock import MagicMock, patch

from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

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

from app.users.service import logout, sign_in, sign_up


class TestSignUp(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_session: MagicMock = MagicMock()
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = None
        self.mock_get_session = patch(
            'app.users.service.get_session', return_value=self.mock_session
        ).start()
        patch('app.users.schemas.get_session', return_value=self.mock_session).start()

    def tearDown(self) -> None:
        patch.stopall()

    def test_sign_up_creates_user(self) -> None:
        with (
            patch('app.users.service.hash_password', return_value='hashed_pw'),
            patch('app.shared.geo.COMMUNES_JSON', '/dev/null'),
            patch(
                'app.shared.geo.json.load',
                return_value={'1': {'commune_code': 4112, 'daira_id': 1}},
            ),
            patch('app.users.service.DAIRA_JSON', '/dev/null'),
            patch('app.users.service.open'),
            patch(
                'app.users.service.json.load',
                return_value={'1': {'wilaya_id': 41}},
            ),
        ):
            ok, errors = sign_up(
                username='newuser',
                password='secret123',
                commune_code='4112',
                phone='0555000000',
                email='new@test.com',
                first_name='New',
                lastname='User',
            )
        self.assertTrue(ok)
        self.assertIsNone(errors)
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.mock_session.close.assert_called()

    def test_sign_up_validation_error_returns_false(self) -> None:
        with patch(
            'app.users.service.SignupSchema.load',
            side_effect=ValidationError({'username': ['Required']}),
        ):
            ok, errors = sign_up(
                username='',
                password='',
                commune_code='',
                phone='',
                email='',
                first_name='',
                lastname='',
            )
        self.assertFalse(ok)
        self.assertIsNotNone(errors)
        self.mock_session.add.assert_not_called()
        self.mock_session.close.assert_not_called()

    def test_sign_up_duplicate_username_is_rejected(self) -> None:
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = MagicMock()
        with (
            patch('app.users.service.hash_password', return_value='hashed_pw'),
            patch('app.users.service.DAIRA_JSON', '/dev/null'),
            patch('app.users.service.open'),
            patch('app.users.service.json.load', return_value={}),
        ):
            ok, errors = sign_up(
                username='dupe',
                password='secret123',
                commune_code='4112',
                phone='0555000000',
                email='new@test.com',
                first_name='New',
                lastname='User',
            )
        self.assertFalse(ok)
        self.assertIsNotNone(errors)
        self.mock_session.add.assert_not_called()

    def test_sign_up_empty_username_is_rejected(self) -> None:
        with (
            patch('app.users.service.hash_password', return_value='hashed_pw'),
            patch('app.users.service.DAIRA_JSON', '/dev/null'),
            patch('app.users.service.open'),
            patch('app.users.service.json.load', return_value={}),
        ):
            ok, errors = sign_up(
                username='',
                password='secret123',
                commune_code='4112',
                phone='0555000000',
                email='new@test.com',
                first_name='New',
                lastname='User',
            )
        self.assertFalse(ok)
        self.assertIsNotNone(errors)
        self.mock_session.add.assert_not_called()


class TestSignIn(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_session: MagicMock = MagicMock()
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = None
        self.mock_get_session = patch(
            'app.users.service.get_session', return_value=self.mock_session
        ).start()
        patch('app.users.schemas.get_session', return_value=self.mock_session).start()
        self.mock_token = patch(
            'app.users.service.secrets.token_urlsafe', return_value='fake-session-token'
        ).start()

    def tearDown(self) -> None:
        patch.stopall()

    def _make_user_mock(self, **kwargs: object) -> MagicMock:
        user = MagicMock()
        user.password = kwargs.get('password', 'hashed_pw')
        user.username = kwargs.get('username', 'test')
        user.id = kwargs.get('id', 1)
        return user

    def test_sign_in_success_returns_true(self) -> None:
        mock_user = self._make_user_mock()

        session_query = self.mock_session.query.return_value
        session_query.filter_by.return_value.first.return_value = mock_user

        with patch('app.users.service.verify_password', return_value=True):
            ok, username, error = sign_in('test', 'password')

        self.assertTrue(ok)
        self.assertEqual(username, 'test')
        self.assertIsNone(error)

    def test_sign_in_username_does_not_exist(self) -> None:
        session_query = self.mock_session.query.return_value
        session_query.filter_by.return_value.first.return_value = None

        ok, username, error = sign_in('unknown', 'password')
        self.assertFalse(ok)
        self.assertIsNone(username)
        self.assertIsNotNone(error)

    def test_sign_in_wrong_password(self) -> None:
        mock_user = self._make_user_mock()

        session_query = self.mock_session.query.return_value
        session_query.filter_by.return_value.first.return_value = mock_user

        with patch('app.users.service.verify_password', return_value=False):
            ok, username, error = sign_in('test', 'wrongpass')
        self.assertFalse(ok)
        self.assertIsNone(username)
        self.assertIsNotNone(error)

    def test_sign_in_validation_error(self) -> None:
        with patch(
            'app.users.service.AuthSchema.load',
            side_effect=ValidationError({'USERNAME': ['Required']}),
        ):
            ok, username, error = sign_in('', '')
        self.assertFalse(ok)
        self.assertIsNone(username)
        self.assertIsNotNone(error)

    def test_sign_in_exception_triggers_rollback(self) -> None:
        self.mock_session.query.side_effect = SQLAlchemyError('DB error')
        ok, username, error = sign_in('test', 'password')
        self.assertFalse(ok)
        self.assertIsNone(username)
        self.assertIsNotNone(error)
        self.mock_session.rollback.assert_called_once()


class TestLogout(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_session: MagicMock = MagicMock()
        self.mock_get_session = patch(
            'app.users.service.get_session', return_value=self.mock_session
        ).start()
        self.mock_toml = patch('app.users.repository.toml').start()
        self.mock_iface: MagicMock = MagicMock()

    def tearDown(self) -> None:
        patch.stopall()

    def test_logout_clears_cookie_and_closes(self) -> None:
        mock_user = MagicMock()
        mock_user.active = True
        self.mock_toml.load.return_value = {'Session': {'cookie': 'tok', 'uid': 1}}

        session_query = self.mock_session.query.return_value
        session_query.filter.return_value.first.return_value = mock_user

        with patch('builtins.open', MagicMock()):
            logout(self.mock_iface, None)

        self.assertIsNone(mock_user.session_token)
        self.mock_session.commit.assert_called_once()
        self.mock_session.close.assert_called_once()

    def test_logout_no_cookie_skips_clear(self) -> None:
        self.mock_toml.load.return_value = {'Session': {'cookie': None, 'uid': None}}
        with patch('builtins.open', MagicMock()):
            logout(self.mock_iface, None)
        self.mock_session.query.assert_not_called()

    def test_logout_no_cookie_entry_skips_clear(self) -> None:
        self.mock_toml.load.return_value = {}
        with patch('builtins.open', MagicMock()):
            logout(self.mock_iface, None)
        self.mock_session.query.assert_not_called()


class TestLookupWilayaCode(unittest.TestCase):
    def test_returns_none_when_daira_file_missing(self) -> None:
        from app.users.service import _lookup_wilaya_code

        with (
            patch('app.users.service.DAIRA_JSON', '/nonexistent/daira.json'),
        ):
            result = _lookup_wilaya_code('1601')
        self.assertIsNone(result)

    def test_returns_none_when_commune_not_found(self) -> None:
        from app.users.service import _lookup_wilaya_code

        with (
            patch('app.users.service.DAIRA_JSON', '/dev/null'),
            patch('app.users.service.open'),
            patch(
                'app.users.service.json.load',
                return_value={'1': {'wilaya_id': 16}},
            ),
            patch('app.users.service.find_commune_by_code', return_value=None),
            patch('app.users.service.load_communes', return_value=[]),
        ):
            result = _lookup_wilaya_code('9999')
        self.assertIsNone(result)

    def test_returns_wilaya_code(self) -> None:
        from app.users.service import _lookup_wilaya_code

        commune = {'daira_id': 1}
        with (
            patch('app.users.service.DAIRA_JSON', '/dev/null'),
            patch('app.users.service.open'),
            patch(
                'app.users.service.json.load',
                return_value={'1': {'wilaya_id': 41}},
            ),
            patch('app.users.service.find_commune_by_code', return_value=commune),
            patch('app.users.service.load_communes', return_value=[]),
        ):
            result = _lookup_wilaya_code('1601')
        self.assertEqual(result, 41)

    def test_returns_none_when_daira_not_found(self) -> None:
        from app.users.service import _lookup_wilaya_code

        commune = {'daira_id': 99}
        with (
            patch('app.users.service.DAIRA_JSON', '/dev/null'),
            patch('app.users.service.open'),
            patch(
                'app.users.service.json.load',
                return_value={'1': {'wilaya_id': 41}},
            ),
            patch('app.users.service.find_commune_by_code', return_value=commune),
            patch('app.users.service.load_communes', return_value=[]),
        ):
            result = _lookup_wilaya_code('1601')
        self.assertIsNone(result)

    def test_returns_none_when_wilaya_id_non_numeric(self) -> None:
        from app.users.service import _lookup_wilaya_code

        commune = {'daira_id': 1}
        with (
            patch('app.users.service.DAIRA_JSON', '/dev/null'),
            patch('app.users.service.open'),
            patch(
                'app.users.service.json.load',
                return_value={'1': {'wilaya_id': 'unknown'}},
            ),
            patch('app.users.service.find_commune_by_code', return_value=commune),
            patch('app.users.service.load_communes', return_value=[]),
        ):
            result = _lookup_wilaya_code('1601')
        self.assertIsNone(result)


class TestSignUpDbError(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_session: MagicMock = MagicMock()
        self.mock_session.query.return_value.filter_by.return_value.first.return_value = None
        self.mock_get_session = patch(
            'app.users.service.get_session', return_value=self.mock_session
        ).start()
        patch('app.users.schemas.get_session', return_value=self.mock_session).start()

    def tearDown(self) -> None:
        patch.stopall()

    def test_sign_up_db_error_returns_false(self) -> None:
        self.mock_session.add.side_effect = SQLAlchemyError('DB constraint')
        with (
            patch('app.users.service.hash_password', return_value='hashed_pw'),
            patch('app.shared.geo.COMMUNES_JSON', '/dev/null'),
            patch(
                'app.shared.geo.json.load',
                return_value={'1': {'commune_code': 4112, 'daira_id': 1}},
            ),
            patch('app.users.service.DAIRA_JSON', '/dev/null'),
            patch('app.users.service.open'),
            patch(
                'app.users.service.json.load',
                return_value={'1': {'wilaya_id': 41}},
            ),
        ):
            ok, errors = sign_up(
                username='dupe',
                password='secret',
                commune_code='4112',
                phone='0555',
                email='d@test.com',
                first_name='Dupe',
                lastname='User',
            )
        self.assertFalse(ok)
        self.assertIsNotNone(errors)
        self.mock_session.rollback.assert_called_once()
        self.mock_session.close.assert_called()


class TestLogoutExtended(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_session: MagicMock = MagicMock()
        self.mock_get_session = patch(
            'app.users.service.get_session', return_value=self.mock_session
        ).start()
        self.mock_toml = patch('app.users.repository.toml').start()
        self.mock_iface: MagicMock = MagicMock()

    def tearDown(self) -> None:
        patch.stopall()

    def test_logout_with_valid_user_clears_token(self) -> None:
        mock_user = MagicMock()
        mock_user.active = True
        self.mock_toml.load.return_value = {'Session': {'cookie': 'tok', 'uid': 1}}
        session_query = self.mock_session.query.return_value
        session_query.filter.return_value.first.return_value = mock_user

        with patch('builtins.open', MagicMock()):
            logout(self.mock_iface, None)

        self.assertIsNone(mock_user.session_token)
        self.mock_session.commit.assert_called_once()

    def test_logout_cookie_write_failure_raises(self) -> None:
        self.mock_toml.load.return_value = {'Session': {'cookie': 'tok', 'uid': 1}}
        mock_user = MagicMock()
        session_query = self.mock_session.query.return_value
        session_query.filter.return_value.first.return_value = mock_user

        with (
            patch('builtins.open', MagicMock()),
            patch(
                'app.users.service.tempfile.mkstemp',
                return_value=(1, '/tmp/fail.tmp'),
            ),
            patch('app.users.service.os.fdopen', side_effect=OSError('write fail')),
            self.assertRaises(OSError),
        ):
            logout(self.mock_iface, None)

    def test_logout_removes_layers_and_closes_dlg(self) -> None:
        self.mock_toml.load.return_value = None
        mock_dlg = MagicMock()
        logout(self.mock_iface, mock_dlg)
        self.mock_iface.mapCanvas().refresh.assert_called()
        mock_dlg.close.assert_called_once()

    def test_logout_no_cookie_removes_layers(self) -> None:
        self.mock_toml.load.return_value = {}
        logout(self.mock_iface, None)
        self.mock_iface.mapCanvas().refresh.assert_called()


class TestLogoutPartialCookie(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_session: MagicMock = MagicMock()
        self.mock_get_session = patch(
            'app.users.service.get_session', return_value=self.mock_session
        ).start()
        self.mock_toml = patch('app.users.repository.toml').start()
        self.mock_iface: MagicMock = MagicMock()

    def tearDown(self):
        patch.stopall()

    def test_logout_missing_session_entry_skips_token_clear(self) -> None:
        self.mock_toml.load.return_value = {'other': 'data'}
        mock_dlg = MagicMock()
        logout(self.mock_iface, mock_dlg)
        self.mock_session.commit.assert_not_called()
        self.mock_iface.mapCanvas().refresh.assert_called()
        mock_dlg.close.assert_called_once()

    def test_logout_no_user_commits_without_token_clear(self) -> None:
        self.mock_toml.load.return_value = {'Session': {'cookie': 'tok', 'uid': 1}}
        session_query = self.mock_session.query.return_value
        session_query.filter.return_value.first.return_value = None
        with patch('builtins.open', MagicMock()):
            logout(self.mock_iface, MagicMock())
        self.mock_session.commit.assert_called_once()


class TestSignupSchemaValidators(unittest.TestCase):
    def test_validate_username_empty_value_raises(self) -> None:
        from app.users.schemas import SignupSchema

        schema = SignupSchema()
        with self.assertRaises(ValidationError):
            schema.validate_username('')

    def test_validate_username_none_value_passes(self) -> None:
        from app.users.schemas import SignupSchema

        schema = SignupSchema()
        schema.validate_username(None)


class TestRemoveAllLayers(unittest.TestCase):
    def test_removes_all_layers(self) -> None:
        from app.users.service import remove_all_layers

        iface = MagicMock()
        mock_project = MagicMock()
        layer1 = MagicMock()
        layer2 = MagicMock()
        mock_project.mapLayers.return_value.values.return_value = [
            layer1,
            layer2,
        ]

        with patch('app.users.service.QgsProject') as MockQgsProject:
            MockQgsProject.instance.return_value = mock_project
            remove_all_layers(iface)

        self.assertEqual(mock_project.removeMapLayer.call_count, 2)
        iface.mapCanvas().refresh.assert_called_once()


if __name__ == '__main__':
    unittest.main()
