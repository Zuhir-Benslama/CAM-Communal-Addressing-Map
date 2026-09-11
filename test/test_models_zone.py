"""Tests for app.orders.models.zone."""

import unittest
from unittest.mock import MagicMock, patch

from app.users.models import User  # noqa: F401  (register User for mapper config)


class TestZoneRecalcHasChild(unittest.TestCase):
    @patch('app.orders.models.zone._has_child_entities', return_value=True)
    def test_sets_true_when_children_exist(self, mock_has_child):
        from app.orders.models.zone import Zone

        zone = Zone()
        zone.geometry = 'POLYGON((0 0,1 0,1 1,0 1,0 0))'
        session = MagicMock()
        session.query.return_value.filter_by.return_value.first.return_value = zone
        Zone._recalc_has_child(session, 'z1')
        self.assertTrue(zone.has_child)
        mock_has_child.assert_called_once_with(session, zone.geometry)
        session.commit.assert_called_once()

    @patch('app.orders.models.zone._has_child_entities', return_value=False)
    def test_sets_false_when_no_children(self, mock_has_child):
        from app.orders.models.zone import Zone

        zone = Zone()
        zone.geometry = 'POLYGON((0 0,1 0,1 1,0 1,0 0))'
        session = MagicMock()
        session.query.return_value.filter_by.return_value.first.return_value = zone
        Zone._recalc_has_child(session, 'z1')
        self.assertFalse(zone.has_child)

    def test_returns_when_zone_missing(self):
        from app.orders.models.zone import Zone

        session = MagicMock()
        session.query.return_value.filter_by.return_value.first.return_value = None
        Zone._recalc_has_child(session, 'missing')
        session.commit.assert_not_called()


class TestZoneRefreshDerived(unittest.TestCase):
    @patch('app.orders.models.zone._has_child_entities', return_value=True)
    def test_sets_has_child_from_geometry(self, mock_has_child):
        from app.orders.models.zone import Zone

        zone = Zone()
        zone.geometry = 'POLYGON((0 0,1 0,1 1,0 1,0 0))'
        zone._refresh_derived(MagicMock())
        self.assertTrue(zone.has_child)
        mock_has_child.assert_called_once()


if __name__ == '__main__':
    unittest.main()
