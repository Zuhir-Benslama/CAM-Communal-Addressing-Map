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


if __name__ == '__main__':
    unittest.main()
