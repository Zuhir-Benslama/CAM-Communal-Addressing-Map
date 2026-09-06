"""Tests for app.core.database."""

import unittest
from unittest.mock import MagicMock, patch

from app.core.database import ConnectionPool, reset_connection_pool


class TestConnectionPool(unittest.TestCase):
    def setUp(self):
        self.pool = ConnectionPool()

    def test_initial_state(self):
        self.assertIsNone(self.pool._engine)
        self.assertIsNone(self.pool._Session)

    def test_reset_clears_state(self):
        self.pool._engine = MagicMock()
        self.pool._Session = MagicMock()
        self.pool.reset()
        self.assertIsNone(self.pool._engine)
        self.assertIsNone(self.pool._Session)

    @patch('app.core.database._create_spatial_indexes')
    @patch('app.core.database._create_views')
    @patch('app.core.database._migrate_missing_columns')
    @patch('app.core.database._migrate_old_columns')
    @patch('app.core.database._migrate_timestamp_columns')
    @patch('app.core.database._migrate_users_from_auth')
    @patch('app.core.database.Base')
    @patch('app.core.database.event')
    @patch('app.core.database.create_engine')
    def test_get_engine_creates_engine_once(
        self,
        mock_create_engine,
        mock_event,
        mock_base,
        mock_migrate_users,
        mock_migrate_ts,
        mock_migrate_old,
        mock_migrate_missing,
        mock_create_views,
        mock_create_spatial,
    ):
        self.pool.get_engine()
        mock_create_engine.assert_called_once()
        self.pool.get_engine()
        self.assertEqual(mock_create_engine.call_count, 1)

    @patch('app.core.database._create_spatial_indexes')
    @patch('app.core.database._create_views')
    @patch('app.core.database._migrate_missing_columns')
    @patch('app.core.database._migrate_old_columns')
    @patch('app.core.database._migrate_timestamp_columns')
    @patch('app.core.database._migrate_users_from_auth')
    @patch('app.core.database.Base')
    @patch('app.core.database.event')
    @patch('app.core.database.sessionmaker')
    @patch('app.core.database.create_engine')
    def test_get_session_returns_session(
        self,
        mock_create_engine,
        mock_sessionmaker,
        mock_event,
        mock_base,
        mock_migrate_users,
        mock_migrate_ts,
        mock_migrate_old,
        mock_migrate_missing,
        mock_create_views,
        mock_create_spatial,
    ):
        self.pool.get_session()
        mock_sessionmaker.assert_called_once()

    def test_reset_connection_pool_resets_global(self):
        import app.core.database as db_mod

        db_mod._pool._engine = MagicMock()
        db_mod._pool._Session = MagicMock()
        reset_connection_pool()
        self.assertIsNone(db_mod._pool._engine)
        self.assertIsNone(db_mod._pool._Session)


class TestConnectSpatialite(unittest.TestCase):
    """Test the engine 'connect' event listener body.

    The listener is registered via ``event.listens_for(engine, 'connect')``;
    patching ``listens_for`` to an identity decorator lets us capture and
    invoke the listener body directly with a fake DBAPI connection.
    """

    def _invoke_listener(self, conn, dll='/x/mod.so', exists=True):
        """Build the engine and invoke the captured 'connect' listener."""
        captured = {}

        def fake_listens_for(target, identifier):
            def deco(fn):
                captured['fn'] = fn
                return fn

            return deco

        with (
            patch('app.core.database.create_engine', return_value=MagicMock()),
            patch('app.core.database.event.listens_for', fake_listens_for),
            patch('app.core.database.Base'),
            patch('app.core.database.find_mod_spatialite_dll', return_value=dll),
            patch(
                'app.core.database.Path',
                MagicMock(**{'return_value.exists.return_value': exists}),
            ),
            patch('app.core.database._migrate_users_from_auth'),
            patch('app.core.database._migrate_timestamp_columns'),
            patch('app.core.database._migrate_old_columns'),
            patch('app.core.database._migrate_missing_columns'),
            patch('app.core.database._create_views'),
            patch('app.core.database._create_spatial_indexes'),
        ):
            ConnectionPool().get_engine()
            return captured['fn'](conn, 'rec')

    def _make_conn(self):
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = (1,)
        conn.execute.return_value = cursor
        return conn

    def test_successful_load(self):
        conn = self._make_conn()
        self.assertIsNone(self._invoke_listener(conn))
        conn.load_extension.assert_called_once_with('/x/mod.so')

    def test_load_fail_dll_exists_sql_fallback(self):
        import sqlite3

        conn = self._make_conn()
        conn.load_extension.side_effect = sqlite3.OperationalError('bad module')
        self.assertIsNone(self._invoke_listener(conn))
        conn.execute.assert_any_call('SELECT load_extension(?)', ('/x/mod.so',))

    def test_load_fail_dll_missing_raises(self):
        import sqlite3

        conn = self._make_conn()
        conn.load_extension.side_effect = sqlite3.OperationalError('bad module')
        with self.assertRaises(RuntimeError):
            self._invoke_listener(conn, dll='/missing/mod.so', exists=False)

    def test_init_spatial_metadata_when_absent(self):
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = (0,)
        conn.execute.return_value = cursor
        self._invoke_listener(conn)
        conn.execute.assert_any_call('SELECT InitSpatialMetadata(0)')
        conn.execute.assert_any_call(
            'INSERT OR IGNORE INTO spatial_ref_sys '
            '(srid, auth_name, auth_srid, ref_sys_name, proj4text) '
            "VALUES (4326, 'EPSG', 4326, 'WGS 84', "
            "'+proj=longlat +datum=WGS84 +no_defs')"
        )

    def test_init_spatial_metadata_when_already_present(self):
        conn = MagicMock()
        cursor = MagicMock()
        cursor.fetchone.return_value = (1,)
        conn.execute.return_value = cursor
        self._invoke_listener(conn)
        init_calls = [
            c for c in conn.execute.call_args_list if 'InitSpatialMetadata' in str(c)
        ]
        self.assertEqual(len(init_calls), 0)

    def test_metadata_error_logs_warning(self):
        from sqlalchemy.exc import OperationalError

        conn = self._make_conn()
        conn.execute.side_effect = OperationalError('stmt', {}, Exception('fail'))
        self.assertIsNone(self._invoke_listener(conn))


class TestConnectSpatialiteExtended(unittest.TestCase):
    """Cover the load-from-module-level and session delegation paths."""

    @patch('app.core.database._pool')
    def test_get_engine_delegates(self, mock_pool):
        from app.core.database import get_engine

        get_engine()
        mock_pool.get_engine.assert_called_once()

    @patch('app.core.database._pool')
    def test_get_session_delegates(self, mock_pool):
        from app.core.database import get_session

        get_session()
        mock_pool.get_session.assert_called_once()


if __name__ == '__main__':
    unittest.main()
