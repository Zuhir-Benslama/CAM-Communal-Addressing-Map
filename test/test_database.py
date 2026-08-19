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


class TestModuleFunctions(unittest.TestCase):
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
