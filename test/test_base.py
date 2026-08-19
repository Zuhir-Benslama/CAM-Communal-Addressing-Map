"""Tests for app.core.base."""

import unittest
from unittest.mock import MagicMock

from app.core.base import _ALLOWLIST_CACHE, TimestampMixin, _allowlist_columns


class _FakeModel:
    """Standalone class that supports __table__ and __mapper__ attributes."""

    def __init__(self, columns=None, mapper_attrs=None):
        self.__table__ = MagicMock()
        self.__table__.columns = columns or []
        self.__mapper__ = MagicMock()
        self.__mapper__.attrs = mapper_attrs or []


class TestTimestampMixin(unittest.TestCase):
    def test_created_at_has_default(self):
        self.assertIsNotNone(TimestampMixin.created_at)

    def test_updated_at_has_default_and_onupdate(self):
        self.assertIsNotNone(TimestampMixin.updated_at)


class TestAllowlistCache(unittest.TestCase):
    def test_cache_is_dict(self):
        self.assertIsInstance(_ALLOWLIST_CACHE, dict)


class TestAllowlistColumns(unittest.TestCase):
    def setUp(self):
        _ALLOWLIST_CACHE.clear()

    def test_filters_invalid_columns(self):
        col = MagicMock()
        col.name = 'name'
        model = _FakeModel(columns=[col])
        result = _allowlist_columns(model, name='test', bad_col='x')
        self.assertIn('name', result)
        self.assertNotIn('bad_col', result)

    def test_returns_empty_for_no_match(self):
        col = MagicMock()
        col.name = 'id'
        model = _FakeModel(columns=[col])
        result = _allowlist_columns(model, nonexistent='x')
        self.assertEqual(result, {})

    def test_uses_cache(self):
        col = MagicMock()
        col.name = 'username'
        model = _FakeModel(columns=[col])
        _allowlist_columns(model, username='alice')
        self.assertIn(model, _ALLOWLIST_CACHE)
        result = _allowlist_columns(model, username='bob')
        self.assertEqual(result, {'username': 'bob'})

    def test_mapper_attrs_key(self):
        col = MagicMock()
        col.name = 'email'
        attr = MagicMock()
        attr.key = 'email'
        attr.columns = [col]
        model = _FakeModel(columns=[col], mapper_attrs=[attr])
        result = _allowlist_columns(model, email='test@test.com')
        self.assertIn('email', result)

    def test_mapper_non_column_attrs(self):
        col = MagicMock()
        col.name = 'id'
        prop_attr = MagicMock(spec=[])
        prop_attr.key = 'hybrid_prop'
        model = _FakeModel(columns=[col], mapper_attrs=[prop_attr])
        result = _allowlist_columns(model, hybrid_prop='val')
        self.assertIn('hybrid_prop', result)

    def test_attribute_error_on_mapper_handled(self):
        col = MagicMock()
        col.name = 'id'

        class _BadMapperModel:
            __table__ = MagicMock(columns=[col])
            __mapper__ = property(lambda self: (_ for _ in ()).throw(AttributeError))

        result = _allowlist_columns(_BadMapperModel(), id='123')
        self.assertIn('id', result)
