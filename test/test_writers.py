"""Tests for db/writers.py — lookup type insertion functions."""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from db.writers import (
    add_road_type, add_type_zone, add_subdivision_type,
    add_organization_type, add_activity_type,
)


class TestLookupTypeWriters(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_get_session = patch(
            'db.writers.get_session', return_value=self.mock_session
        ).start()
        self.mock_msgbox = patch(
            'db.writers.QMessageBox'
        ).start()

    def tearDown(self):
        patch.stopall()

    def test_add_road_type_saves_and_notifies(self):
        add_road_type('National Road')
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()

    def test_add_road_type_empty_does_not_save(self):
        add_road_type('')
        self.mock_session.add.assert_not_called()

    def test_add_type_zone_saves_and_notifies(self):
        add_type_zone('Urban Zone')
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()

    def test_add_type_zone_empty_shows_error(self):
        add_type_zone('')
        self.mock_session.add.assert_not_called()

    def test_add_subdivision_type_saves(self):
        add_subdivision_type('Residential')
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()

    def test_add_subdivision_type_empty_skips(self):
        add_subdivision_type('')
        self.mock_session.add.assert_not_called()

    def test_add_organization_type_saves_with_both_args(self):
        add_organization_type('School', 'Education')
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()

    def test_add_organization_type_missing_arg_skips(self):
        add_organization_type('School', '')
        self.mock_session.add.assert_not_called()

    def test_add_activity_type_saves(self):
        add_activity_type('Commerce', 'Shop')
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()

    def test_add_activity_type_no_activity_skips(self):
        from db.writers import NO_ACTIVITY
        add_activity_type(NO_ACTIVITY, 'Shop')
        self.mock_session.add.assert_not_called()

    def test_add_activity_type_missing_arg_skips(self):
        add_activity_type('', 'Shop')
        self.mock_session.add.assert_not_called()


if __name__ == '__main__':
    unittest.main()
