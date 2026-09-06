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

    def test_abstract_base_not_in_registry(self):
        from app.orders.models.base import _BaseSpatialModel

        self.assertNotIn(_BaseSpatialModel, _BaseSpatialModel._registry)


class TestUsernameProperty(unittest.TestCase):
    def test_returns_user_username(self):
        from app.orders.models.base import _BaseSpatialModel

        model = _BaseSpatialModel.__new__(_BaseSpatialModel)
        model.user_id = 1
        model.user = MagicMock()
        model.user.username = 'admin'
        self.assertEqual(model.username, 'admin')

    def test_returns_none_when_no_user(self):
        from app.orders.models.base import _BaseSpatialModel

        model = _BaseSpatialModel.__new__(_BaseSpatialModel)
        model.user_id = None
        self.assertIsNone(model.username)


class TestDelete(unittest.TestCase):
    def test_delete_persists_single_delete(self):
        from app.orders.models.base import _BaseSpatialModel

        model = _BaseSpatialModel.__new__(_BaseSpatialModel)
        session = MagicMock()
        model.delete(session)
        session.delete.assert_called_once_with(model)
        session.commit.assert_called_once()


class TestSave(unittest.TestCase):
    @patch('app.orders.models.base._get_current_user')
    def test_save_sets_user_and_locality(self, mock_user):
        from app.orders.models.base import _BaseSpatialModel

        mock_user.return_value = {'id': 7, 'commune_code': '16'}
        model = _BaseSpatialModel.__new__(_BaseSpatialModel)
        model.user_id = None
        model.locality_id = None
        model._refresh_derived = MagicMock()
        session = MagicMock()
        model.save(session)
        self.assertEqual(model.user_id, 7)
        self.assertEqual(model.locality_id, '16')
        model._refresh_derived.assert_called_once_with(session)
        session.add.assert_called_once_with(model)
        session.commit.assert_called_once()

    @patch('app.orders.models.base._get_current_user')
    def test_save_skips_locality_when_absent(self, mock_user):
        from app.orders.models.base import _BaseSpatialModel

        mock_user.return_value = {'id': 2}
        model = _BaseSpatialModel.__new__(_BaseSpatialModel)
        model.user_id = None
        model._refresh_derived = MagicMock()
        session = MagicMock()
        model.save(session)
        self.assertEqual(model.user_id, 2)
        self.assertFalse(hasattr(model, 'locality_id'))

    @patch('app.orders.models.base._get_current_user')
    def test_save_raises_when_no_user(self, mock_user):
        from app.orders.models.base import _BaseSpatialModel

        mock_user.return_value = None
        model = _BaseSpatialModel.__new__(_BaseSpatialModel)
        with self.assertRaises(ValueError):
            model.save(MagicMock())


class TestUpdate(unittest.TestCase):
    @patch('app.orders.models.base._get_current_user')
    def test_update_applies_kwargs_and_refreshes(self, mock_user):
        from app.orders.models.base import _BaseSpatialModel

        mock_user.return_value = {'id': 3, 'commune_code': '31'}
        instance = _BaseSpatialModel.__new__(_BaseSpatialModel)
        instance.user_id = None
        instance.locality_id = None
        instance._refresh_derived = MagicMock()
        session = MagicMock()
        session.query.return_value.filter_by.return_value.first.return_value = instance

        with patch(
            'app.orders.models.base._allowlist_columns',
            side_effect=lambda cls, **kw: kw,
        ):
            result = _BaseSpatialModel.update(session, 'rec-1', name='Main')
        self.assertEqual(result, instance)
        self.assertEqual(instance.name, 'Main')
        self.assertEqual(instance.user_id, 3)
        self.assertEqual(instance.locality_id, '31')
        instance._refresh_derived.assert_called_once_with(session)
        session.commit.assert_called_once()

    @patch('app.orders.models.base._get_current_user')
    def test_update_not_found_raises(self, mock_user):
        from app.orders.models.base import _BaseSpatialModel

        mock_user.return_value = {'id': 3}
        session = MagicMock()
        session.query.return_value.filter_by.return_value.first.return_value = None
        with self.assertRaises(ValueError):
            _BaseSpatialModel.update(session, 'missing')

    @patch('app.orders.models.base._get_current_user')
    def test_update_no_user_raises(self, mock_user):
        from app.orders.models.base import _BaseSpatialModel

        mock_user.return_value = None
        instance = _BaseSpatialModel.__new__(_BaseSpatialModel)
        session = MagicMock()
        session.query.return_value.filter_by.return_value.first.return_value = instance
        with self.assertRaises(ValueError):
            _BaseSpatialModel.update(session, 'rec-1')

    @patch('app.orders.models.base._get_current_user')
    def test_update_without_locality_skips_locality(self, mock_user):
        from app.orders.models.base import _BaseSpatialModel

        mock_user.return_value = {'id': 5, 'commune_code': '09'}
        instance = _BaseSpatialModel.__new__(_BaseSpatialModel)
        instance._refresh_derived = MagicMock()
        session = MagicMock()
        session.query.return_value.filter_by.return_value.first.return_value = instance

        with patch(
            'app.orders.models.base._allowlist_columns',
            side_effect=lambda cls, **kw: kw,
        ):
            result = _BaseSpatialModel.update(session, 'rec-1', type='node')
        self.assertEqual(result, instance)
        self.assertEqual(instance.user_id, 5)


class TestRefreshDerivedHook(unittest.TestCase):
    def test_refresh_derived_is_noop_by_default(self):
        from app.orders.models.base import _BaseSpatialModel

        model = _BaseSpatialModel.__new__(_BaseSpatialModel)
        self.assertIsNone(model._refresh_derived(MagicMock()))
