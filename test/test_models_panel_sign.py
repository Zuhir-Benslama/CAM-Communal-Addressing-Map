"""Tests for app.orders.models.panel_sign."""

import unittest
from unittest.mock import MagicMock, patch

from app.users.models import User  # noqa: F401  (register User for mapper config)


class TestPanelSignLabel(unittest.TestCase):
    @patch('app.orders.models.panel_sign.locale_value', return_value='Avenue Test')
    @patch('app.orders.models.panel_sign.current_locale', return_value='fr')
    def test_label_returns_road_label(self, mock_loc, mock_lv):
        ps = MagicMock()
        ps.road_id = 'r1'
        ps.subdivision_id = None
        ps.organization_id = None
        ps.road = MagicMock()
        ps.subdivision = None
        ps.organization = None
        from app.orders.models.panel_sign import PanelSign

        result = PanelSign.label.fget(ps)
        self.assertIsNotNone(result)

    @patch('app.orders.models.panel_sign.locale_value', return_value='Cite 500')
    @patch('app.orders.models.panel_sign.current_locale', return_value='fr')
    def test_label_returns_subdivision_label(self, mock_loc, mock_lv):
        ps = MagicMock()
        ps.road_id = None
        ps.subdivision_id = 's1'
        ps.organization_id = None
        ps.road = None
        ps.subdivision = MagicMock()
        ps.organization = None
        from app.orders.models.panel_sign import PanelSign

        result = PanelSign.label.fget(ps)
        self.assertIsNotNone(result)

    @patch('app.orders.models.panel_sign.locale_value', return_value='School')
    @patch('app.orders.models.panel_sign.current_locale', return_value='fr')
    def test_label_returns_org_label(self, mock_loc, mock_lv):
        ps = MagicMock()
        ps.road_id = None
        ps.subdivision_id = None
        ps.organization_id = 'o1'
        ps.road = None
        ps.subdivision = None
        ps.organization = MagicMock()
        from app.orders.models.panel_sign import PanelSign

        result = PanelSign.label.fget(ps)
        self.assertIsNotNone(result)

    @patch('app.orders.models.panel_sign.current_locale', return_value='fr')
    def test_label_returns_none_when_no_refs(self, mock_loc):
        ps = MagicMock()
        ps.road_id = None
        ps.subdivision_id = None
        ps.organization_id = None
        from app.orders.models.panel_sign import PanelSign

        self.assertIsNone(PanelSign.label.fget(ps))

    @patch('app.orders.models.panel_sign.current_locale', return_value='fr')
    def test_label_returns_none_when_multiple_refs(self, mock_loc):
        ps = MagicMock()
        ps.road_id = 'r1'
        ps.subdivision_id = 's1'
        ps.organization_id = None
        from app.orders.models.panel_sign import PanelSign

        self.assertIsNone(PanelSign.label.fget(ps))


class TestValidateReference(unittest.TestCase):
    def test_returns_none_when_no_ref(self):
        from app.orders.models.panel_sign import PanelSign

        result = PanelSign._validate_reference(MagicMock(), MagicMock(), None, 'Road')
        self.assertIsNone(result)

    def test_success(self):
        from app.orders.models.panel_sign import PanelSign

        mock_session = MagicMock()
        mock_cls = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = (
            MagicMock()
        )
        result = PanelSign._validate_reference(mock_session, mock_cls, 1, 'Road')
        self.assertEqual(result, 'Road')

    def test_not_found(self):
        from app.orders.models.panel_sign import PanelSign

        mock_session = MagicMock()
        mock_cls = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        with self.assertRaises(ValueError):
            PanelSign._validate_reference(mock_session, mock_cls, 999, 'Road')


class TestPanelSignSave(unittest.TestCase):
    def _make_panel(self, road_id=None, subdivision_id=None, organization_id=None):
        from app.orders.models.panel_sign import PanelSign

        ps = PanelSign()
        ps.road_id = road_id
        ps.subdivision_id = subdivision_id
        ps.organization_id = organization_id
        ps.type = None
        return ps

    @patch('app.orders.models.base._BaseSpatialModel.save')
    def test_save_sets_type_from_road_ref(self, mock_super_save):
        ps = self._make_panel(road_id='r1')
        session = MagicMock()
        session.query.return_value.filter.return_value.first.return_value = MagicMock()
        ps.save(session)
        self.assertEqual(ps.type, 'Roads')
        mock_super_save.assert_called_once_with(session)

    @patch('app.orders.models.base._BaseSpatialModel.save')
    def test_save_sets_type_from_org_ref(self, mock_super_save):
        ps = self._make_panel(organization_id='o1')
        session = MagicMock()
        session.query.return_value.filter.return_value.first.return_value = MagicMock()
        ps.save(session)
        self.assertEqual(ps.type, 'Facilities')

    @patch('app.orders.models.base._BaseSpatialModel.save')
    def test_save_sets_type_from_subdivision_ref(self, mock_super_save):
        ps = self._make_panel(subdivision_id='s1')
        session = MagicMock()
        session.query.return_value.filter.return_value.first.return_value = MagicMock()
        ps.save(session)
        self.assertEqual(ps.type, 'Subdivisions')

    @patch('app.orders.models.base._BaseSpatialModel.save')
    def test_save_leaves_type_none_without_refs(self, mock_super_save):
        ps = self._make_panel()
        ps.save(MagicMock())
        self.assertIsNone(ps.type)

    def test_save_raises_when_reference_missing(self):
        ps = self._make_panel(road_id='missing')
        session = MagicMock()
        session.query.return_value.filter.return_value.first.return_value = None
        with self.assertRaises(ValueError):
            ps.save(session)
