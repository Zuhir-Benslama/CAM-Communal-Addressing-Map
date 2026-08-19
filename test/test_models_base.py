"""Tests for app.orders.models.base."""

import unittest
from unittest.mock import MagicMock, patch


class TestGetCurrentUser(unittest.TestCase):
    @patch('app.users.repository.get_current_user')
    def test_returns_user_dict(self, mock_get):
        mock_get.return_value = {'id': 1}
        from app.orders.models.base import _get_current_user

        result = _get_current_user()
        self.assertEqual(result['id'], 1)

    @patch('app.users.repository.get_current_user')
    def test_returns_none_when_no_user(self, mock_get):
        mock_get.return_value = None
        from app.orders.models.base import _get_current_user

        result = _get_current_user()
        self.assertIsNone(result)


class TestParentZoneId(unittest.TestCase):
    def test_returns_zone_id_when_within(self):
        from app.orders.models.base import _parent_zone_id

        mock_session = MagicMock()
        mock_zone = MagicMock()
        mock_zone.id = 42
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_zone
        )
        result = _parent_zone_id(mock_session, 'POINT(0 0)')
        self.assertEqual(result, 42)

    def test_returns_none_when_outside(self):
        from app.orders.models.base import _parent_zone_id

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        result = _parent_zone_id(mock_session, 'POINT(999 999)')
        self.assertIsNone(result)

    def test_returns_none_on_sql_error(self):
        from app.orders.models.base import _parent_zone_id
        from sqlalchemy.exc import SQLAlchemyError

        mock_session = MagicMock()
        mock_session.query.side_effect = SQLAlchemyError('fail')
        result = _parent_zone_id(mock_session, 'POINT(0 0)')
        self.assertIsNone(result)


class TestHasChildEntities(unittest.TestCase):
    def test_returns_true_when_children_exist(self):
        from app.orders.models.base import _has_child_entities

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = (
            MagicMock()
        )
        result = _has_child_entities(mock_session, 'POLYGON((0 0,1 0,1 1,0 1,0 0))')
        self.assertTrue(result)

    def test_returns_false_when_no_children(self):
        from app.orders.models.base import _has_child_entities

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        result = _has_child_entities(mock_session, 'POLYGON((0 0,1 0,1 1,0 1,0 0))')
        self.assertFalse(result)

    def test_returns_false_on_sql_error(self):
        from app.orders.models.base import _has_child_entities
        from sqlalchemy.exc import SQLAlchemyError

        mock_session = MagicMock()
        mock_session.query.side_effect = SQLAlchemyError('fail')
        result = _has_child_entities(mock_session, 'POLYGON((0 0,1 0,1 1,0 1,0 0))')
        self.assertFalse(result)


class TestBaseSpatialModelRegistry(unittest.TestCase):
    def test_registry_contains_subclasses(self):
        from app.orders.models.base import _BaseSpatialModel

        self.assertTrue(len(_BaseSpatialModel._registry) > 0)

    def test_zone_in_registry(self):
        from app.orders.models.base import _BaseSpatialModel
        from app.orders.models.zone import Zone

        self.assertIn(Zone, _BaseSpatialModel._registry)
