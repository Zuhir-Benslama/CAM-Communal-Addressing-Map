"""Tests for app.orders.models.organization."""

import unittest
from unittest.mock import MagicMock, patch

from app.users.models import User  # noqa: F401  (register User for mapper config)


class TestOrganizationCat(unittest.TestCase):
    def test_cat_returns_category(self):
        from app.orders.models.organization import Organization

        org = Organization()
        org.category = 'school'
        self.assertEqual(org.cat, 'school')

    def test_cat_returns_none_when_unset(self):
        from app.orders.models.organization import Organization

        org = Organization()
        org.category = None
        self.assertIsNone(org.cat)


class TestOrganizationRefreshDerived(unittest.TestCase):
    @patch('app.orders.models.organization._parent_zone_id', return_value='z1')
    def test_sets_zone_id_from_geometry(self, mock_parent):
        from app.orders.models.organization import Organization

        org = Organization()
        org.geometry = 'POLYGON((0 0,1 0,1 1,0 1,0 0))'
        org._refresh_derived(MagicMock())
        self.assertEqual(org.zone_id, 'z1')
        mock_parent.assert_called_once()

    @patch('app.orders.models.organization._parent_zone_id', return_value=None)
    def test_sets_zone_id_none_when_outside(self, mock_parent):
        from app.orders.models.organization import Organization

        org = Organization()
        org.geometry = 'POLYGON((0 0,1 0,1 1,0 1,0 0))'
        org._refresh_derived(MagicMock())
        self.assertIsNone(org.zone_id)


class TestOrganizationDelete(unittest.TestCase):
    @patch('app.orders.models.zone.Zone._recalc_has_child')
    def test_delete_recalcs_zone(self, mock_recalc):
        from app.orders.models.organization import Organization

        org = Organization()
        org.zone_id = 'z1'
        session = MagicMock()
        org.delete(session)
        session.delete.assert_called_once_with(org)
        session.commit.assert_called_once()
        mock_recalc.assert_called_once_with(session, 'z1')

    @patch('app.orders.models.zone.Zone._recalc_has_child')
    def test_delete_skips_recalc_when_no_zone(self, mock_recalc):
        from app.orders.models.organization import Organization

        org = Organization()
        org.zone_id = None
        org.delete(MagicMock())
        mock_recalc.assert_not_called()


if __name__ == '__main__':
    unittest.main()
