import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.orders.repository import (  # noqa: E402
    count_numberings, count_panels,
    query_missing_pan, query_missing_num, query_missing_rep,
    get_zone_distribution,
)


class TestCountQueries(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_get_session = patch(
            'app.orders.repository.get_session', return_value=self.mock_session
        ).start()

    def tearDown(self):
        patch.stopall()

    def test_count_numberings_returns_count(self):
        self.mock_session.execute.return_value.fetchone.return_value = (5,)
        result = count_numberings('test_state')
        self.assertEqual(result, 5)
        call_args = self.mock_session.execute.call_args
        self.assertIn('etat', str(call_args))

    def test_count_numberings_no_result_returns_zero(self):
        self.mock_session.execute.return_value.fetchone.return_value = None
        result = count_numberings('missing')
        self.assertEqual(result, 0)

    def test_count_panels_returns_count(self):
        self.mock_session.execute.return_value.fetchone.return_value = (3,)
        result = count_panels('road', 'mounted')
        self.assertEqual(result, 3)

    def test_count_panels_no_result_returns_zero(self):
        self.mock_session.execute.return_value.fetchone.return_value = None
        result = count_panels('road', 'nonexistent')
        self.assertEqual(result, 0)

    def test_query_missing_pan_returns_list(self):
        self.mock_session.execute.return_value.fetchall.return_value = [
            ('Main St', 'road', 10),
            ('Second St', 'road', 5),
        ]
        result = query_missing_pan('planned')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['label'], 'Main St')
        self.assertEqual(result[0]['total'], 10)

    def test_query_missing_num_returns_list(self):
        self.mock_session.execute.return_value.fetchall.return_value = [
            ('A1', 3),
            ('B2', 7),
        ]
        result = query_missing_num('planned')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1]['valeur'], 'B2')

    def test_query_missing_rep_returns_list(self):
        self.mock_session.execute.return_value.fetchall.return_value = [
            ('R1', 2),
        ]
        result = query_missing_rep('planned')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['valeur'], 'R1')


class TestGetZoneDistribution(unittest.TestCase):
    """Tests for get_zone_distribution() in app/orders/repository."""

    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_get_session = patch(
            'app.orders.repository.get_session', return_value=self.mock_session
        ).start()

    def tearDown(self):
        patch.stopall()

    def test_returns_type_count_pairs(self):
        self.mock_session.execute.return_value.fetchall.return_value = [
            ('industrial', 8), ('residential', 12), ('commercial', 5),
        ]
        result = get_zone_distribution(16)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], ('industrial', 8))
        self.assertEqual(result[1], ('residential', 12))
        self.assertEqual(result[2], ('commercial', 5))

    def test_passes_wilaya_number_to_query(self):
        self.mock_session.execute.return_value.fetchall.return_value = []
        get_zone_distribution(31)
        call_args = self.mock_session.execute.call_args
        self.assertIn('wilaya', str(call_args))
        self.assertIn('31', str(call_args))

    def test_orders_by_total_descending(self):
        self.mock_session.execute.return_value.fetchall.return_value = [
            ('commercial', 20), ('residential', 10),
        ]
        result = get_zone_distribution(16)
        self.assertEqual(result[0][1], 20)
        self.assertEqual(result[1][1], 10)

    def test_empty_result_returns_empty_list(self):
        self.mock_session.execute.return_value.fetchall.return_value = []
        result = get_zone_distribution(99)
        self.assertEqual(result, [])

    def test_closes_session(self):
        self.mock_session.execute.return_value.fetchall.return_value = []
        get_zone_distribution(16)
        self.mock_session.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
