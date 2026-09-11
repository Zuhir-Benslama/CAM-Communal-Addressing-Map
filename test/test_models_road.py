"""Tests for app.orders.models.road."""

import unittest
from unittest.mock import MagicMock, patch

from app.users.models import User  # noqa: F401  (register User for mapper config)


class TestRoadRefreshDerived(unittest.TestCase):
    @patch('app.orders.models.road._parent_zone_id', return_value='z1')
    def test_sets_zone_id_from_geometry(self, mock_parent):
        from app.orders.models.road import Road

        road = Road()
        road.geometry = 'LINESTRING(0 0,1 1)'
        road._refresh_derived(MagicMock())
        self.assertEqual(road.zone_id, 'z1')
        mock_parent.assert_called_once()

    @patch('app.orders.models.road._parent_zone_id', return_value=None)
    def test_does_not_set_has_child(self, mock_parent):
        from app.orders.models.road import Road

        road = Road()
        road.geometry = 'LINESTRING(0 0,1 1)'
        road._refresh_derived(MagicMock())
        self.assertFalse(hasattr(road, 'has_child'))


class TestRoadDelete(unittest.TestCase):
    @patch('app.orders.models.zone.Zone._recalc_has_child')
    def test_delete_recalcs_zone(self, mock_recalc):
        from app.orders.models.road import Road

        road = Road()
        road.zone_id = 'z1'
        session = MagicMock()
        road.delete(session)
        session.delete.assert_called_once_with(road)
        session.commit.assert_called_once()
        mock_recalc.assert_called_once_with(session, 'z1')

    @patch('app.orders.models.zone.Zone._recalc_has_child')
    def test_delete_skips_recalc_when_no_zone(self, mock_recalc):
        from app.orders.models.road import Road

        road = Road()
        road.zone_id = None
        road.delete(MagicMock())
        mock_recalc.assert_not_called()


if __name__ == '__main__':
    unittest.main()
