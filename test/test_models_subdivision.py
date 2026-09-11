"""Tests for app.orders.models.subdivision."""

import unittest
from unittest.mock import MagicMock, patch

from app.users.models import User  # noqa: F401  (register User for mapper config)


class TestSubdivisionRefreshDerived(unittest.TestCase):
    @patch('app.orders.models.subdivision._parent_zone_id', return_value='z1')
    def test_sets_parent_from_geometry(self, mock_parent):
        from app.orders.models.subdivision import Subdivision

        subdivision = Subdivision()
        subdivision.geometry = 'POLYGON((0 0,1 0,1 1,0 1,0 0))'
        subdivision._refresh_derived(MagicMock())
        self.assertEqual(subdivision.parent, 'z1')
        mock_parent.assert_called_once()

    @patch('app.orders.models.subdivision._parent_zone_id', return_value=None)
    def test_sets_parent_none_when_outside(self, mock_parent):
        from app.orders.models.subdivision import Subdivision

        subdivision = Subdivision()
        subdivision.geometry = 'POLYGON((0 0,1 0,1 1,0 1,0 0))'
        subdivision._refresh_derived(MagicMock())
        self.assertIsNone(subdivision.parent)


class TestSubdivisionDelete(unittest.TestCase):
    @patch('app.orders.models.zone.Zone._recalc_has_child')
    def test_delete_recalcs_zone(self, mock_recalc):
        from app.orders.models.subdivision import Subdivision

        subdivision = Subdivision()
        subdivision.parent = 'z1'
        session = MagicMock()
        subdivision.delete(session)
        session.delete.assert_called_once_with(subdivision)
        session.commit.assert_called_once()
        mock_recalc.assert_called_once_with(session, 'z1')

    @patch('app.orders.models.zone.Zone._recalc_has_child')
    def test_delete_skips_recalc_when_no_parent(self, mock_recalc):
        from app.orders.models.subdivision import Subdivision

        subdivision = Subdivision()
        subdivision.parent = None
        subdivision.delete(MagicMock())
        mock_recalc.assert_not_called()


if __name__ == '__main__':
    unittest.main()
