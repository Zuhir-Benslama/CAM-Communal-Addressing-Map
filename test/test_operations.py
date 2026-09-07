"""Tests for repository operations (counts, missing entities)."""

import unittest
from unittest.mock import MagicMock, patch

from app.orders.repository import (
    count_numberings,
    count_numberings_total,
    count_organizations,
    count_panels,
    count_panels_by_dimension,
    count_panels_total,
    count_roads,
    count_subdivisions,
    count_zones,
    query_missing_num,
    query_missing_pan,
    query_missing_rep,
)


class TestCountQueries(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_session = MagicMock()
        self.mock_get_session = patch(
            'app.orders.repository.get_session', return_value=self.mock_session
        ).start()

    def tearDown(self) -> None:
        patch.stopall()

    def test_count_numberings_returns_count(self) -> None:
        self.mock_session.execute.return_value.fetchone.return_value = (5,)
        result = count_numberings('test_state')
        self.assertEqual(result, 5)
        call_args = self.mock_session.execute.call_args
        self.assertIn('state', str(call_args))

    def test_count_numberings_no_result_returns_zero(self) -> None:
        self.mock_session.execute.return_value.fetchone.return_value = None
        result = count_numberings('missing')
        self.assertEqual(result, 0)

    def test_count_panels_returns_count(self) -> None:
        self.mock_session.execute.return_value.fetchone.return_value = (3,)
        result = count_panels('road', 'mounted')
        self.assertEqual(result, 3)

    def test_count_panels_no_result_returns_zero(self) -> None:
        self.mock_session.execute.return_value.fetchone.return_value = None
        result = count_panels('road', 'nonexistent')
        self.assertEqual(result, 0)

    def test_query_missing_pan_returns_list(self) -> None:
        self.mock_session.execute.return_value.fetchall.return_value = [
            ('Main St', 'road', 10),
            ('Second St', 'road', 5),
        ]
        result = query_missing_pan('planned')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['label'], 'Main St')
        self.assertEqual(result[0]['total'], 10)

    def test_query_missing_num_returns_list(self) -> None:
        self.mock_session.execute.return_value.fetchall.return_value = [
            ('A1', 3),
            ('B2', 7),
        ]
        result = query_missing_num('planned')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1]['value'], 'B2')

    def test_query_missing_rep_returns_list(self) -> None:
        self.mock_session.execute.return_value.fetchall.return_value = [
            ('R1', 2),
        ]
        result = query_missing_rep('planned')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['value'], 'R1')


class TestReportCounts(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_session = MagicMock()
        self.mock_get_session = patch(
            'app.orders.repository.get_session', return_value=self.mock_session
        ).start()

    def tearDown(self) -> None:
        patch.stopall()

    def _rows(self, value):
        self.mock_session.execute.return_value.fetchone.return_value = (value,)

    def test_total_counts_scalar(self) -> None:
        self._rows(11)
        self.assertEqual(count_zones(), 11)
        self._rows(22)
        self.assertEqual(count_roads(), 22)
        self._rows(33)
        self.assertEqual(count_subdivisions(), 33)
        self._rows(44)
        self.assertEqual(count_organizations(), 44)
        self._rows(55)
        self.assertEqual(count_numberings_total(), 55)
        self._rows(66)
        self.assertEqual(count_panels_total(), 66)

    def test_total_counts_use_allowlisted_tables(self) -> None:
        count_zones()
        sql = self.mock_session.execute.call_args.args[0].text
        self.assertIn('from zone', sql)
        count_panels_total()
        sql = self.mock_session.execute.call_args.args[0].text
        self.assertIn('from panel_sign', sql)

    def test_unsafe_table_rejected(self) -> None:
        import app.orders.repository as repo

        with self.assertRaises(ValueError):
            repo._scalar_count('users; DROP TABLE')

    def test_count_panels_by_dimension(self) -> None:
        self._rows(7)
        self.assertEqual(count_panels_by_dimension('30X40'), 7)
        sql = self.mock_session.execute.call_args.args[0].text
        self.assertIn('dimensions', sql)

    def test_count_panels_by_dimension_all(self) -> None:
        self._rows(13)
        self.assertEqual(count_panels_by_dimension(), 13)
        sql = str(self.mock_session.execute.call_args)
        self.assertNotIn('dimensions', sql)


class TestAddEntities(unittest.TestCase):
    """Test the CRUD add_* helpers in app.orders.repository."""

    def setUp(self) -> None:
        self.session = MagicMock()
        self.mock_get_session = patch(
            'app.orders.repository.get_session', return_value=self.session
        ).start()
        self.instance = MagicMock()
        self.add_patch = patch(
            'app.orders.repository._add_entity', return_value=self.instance
        ).start()
        self.mock_wkt = patch('app.orders.repository.WKTElement').start()
        self.models = {}
        for name in (
            'PanelSign',
            'Organization',
            'Road',
            'Numbering',
            'Subdivision',
            'Zone',
        ):
            self.models[name] = patch(f'app.orders.repository.{name}').start()

    def tearDown(self) -> None:
        patch.stopall()

    def _assert_entity(self, result, model_name, record_id) -> None:
        self.assertIs(result, self.instance)
        self.mock_wkt.assert_called_once_with('POINT(1 2)', srid=4326)
        cls = self.models[model_name]
        cls.assert_called_once()
        self.assertEqual(cls.call_args.kwargs.get('id'), record_id)

    def test_add_panel_sign(self) -> None:
        from app.orders.repository import add_panel_sign

        result = add_panel_sign(
            geometry_wkt='POINT(1 2)',
            mount_status='mounted',
            road_id='r1',
            subdivision_id=None,
            organization_id=None,
            record_id='p-1',
            dimensions=None,
        )
        self._assert_entity(result, 'PanelSign', 'p-1')
        panel = self.models['PanelSign'].call_args.kwargs
        self.assertEqual(panel['status'], 'mounted')
        self.assertEqual(panel['road_id'], 'r1')

    def test_add_panel_sign_uses_default_dimensions(self) -> None:
        from app.orders.repository import add_panel_sign

        add_panel_sign(geometry_wkt='POINT(1 2)', mount_status='mounted')
        panel = self.models['PanelSign'].call_args.kwargs
        self.assertEqual(panel['dimensions'], '30X40')

    def test_add_organization(self) -> None:
        from app.orders.repository import add_organization

        result = add_organization(
            geometry_wkt='POINT(1 2)',
            org_name='CHU',
            org_type='hospital',
            org_cat='health',
            record_id='o-1',
        )
        self._assert_entity(result, 'Organization', 'o-1')
        org = self.models['Organization'].call_args.kwargs
        self.assertEqual(org['name'], 'CHU')
        self.assertEqual(org['type'], 'hospital')
        self.assertEqual(org['category'], 'health')

    def test_add_road(self) -> None:
        from app.orders.repository import add_road

        result = add_road(
            geometry_wkt='POINT(1 2)',
            road_name='Main St',
            type_road='avenue',
            road_decision='2024/01',
            record_id='rd-1',
            name_fr='Rue Principale',
            name_en='Main Street',
        )
        self._assert_entity(result, 'Road', 'rd-1')
        road = self.models['Road'].call_args.kwargs
        self.assertEqual(road['type'], 'avenue')
        self.assertEqual(road['decision_number'], '2024/01')
        self.assertEqual(road['name_fr'], 'Rue Principale')

    def test_add_numbering(self) -> None:
        from app.orders.repository import add_numbering

        result = add_numbering(
            geometry_wkt='POINT(1 2)',
            value='42',
            road_id='rd-1',
            subdivision_id=None,
            repetition='bis',
            state='booked',
            activity_cat='residential',
            activity_type='house',
            record_id='n-1',
        )
        self._assert_entity(result, 'Numbering', 'n-1')
        num = self.models['Numbering'].call_args.kwargs
        self.assertEqual(num['value'], '42')
        self.assertEqual(num['repetition'], 'bis')
        self.assertEqual(num['activity_type'], 'house')

    def test_add_subdivision(self) -> None:
        from app.orders.repository import add_subdivision

        result = add_subdivision(
            geometry_wkt='POINT(1 2)',
            subdivision_type='cite',
            name='Cite 500',
            record_id='s-1',
        )
        self._assert_entity(result, 'Subdivision', 's-1')
        sub = self.models['Subdivision'].call_args.kwargs
        self.assertEqual(sub['type'], 'cite')
        self.assertEqual(sub['name'], 'Cite 500')

    def test_add_zone(self) -> None:
        from app.orders.repository import add_zone

        result = add_zone(
            geometry_wkt='POINT(1 2)',
            zone_type='residential',
            name='Zone A',
            record_id='z-1',
            name_fr=None,
            name_en='Zone A EN',
        )
        self._assert_entity(result, 'Zone', 'z-1')
        zone = self.models['Zone'].call_args.kwargs
        self.assertEqual(zone['type'], 'residential')
        self.assertEqual(zone['name_en'], 'Zone A EN')


if __name__ == '__main__':
    unittest.main()
