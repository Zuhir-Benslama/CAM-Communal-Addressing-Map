"""Tests for app.orders.models.road."""

import unittest
from unittest.mock import MagicMock, patch


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


if __name__ == '__main__':
    unittest.main()
