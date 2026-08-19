"""Tests for app.shared.utils."""

import os
import unittest
from unittest.mock import MagicMock, patch


class TestValidateSafeName(unittest.TestCase):
    def test_valid_names(self):
        from app.shared.utils import validate_safe_name

        for name in ('users', '_private', 'Table123', 'a'):
            self.assertEqual(validate_safe_name(name), name)

    def test_invalid_names(self):
        from app.shared.utils import validate_safe_name

        for name in ('123abc', 'has space', 'has-dash', 'table;DROP', '', 'a.b'):
            with self.assertRaises(ValueError):
                validate_safe_name(name)


class TestValidateText(unittest.TestCase):
    def test_strips_whitespace(self):
        from app.shared.utils import validate_text

        self.assertEqual(validate_text('  hello  '), 'hello')

    def test_truncates(self):
        from app.shared.utils import validate_text

        self.assertEqual(validate_text('a' * 300, max_length=10), 'a' * 10)

    def test_empty_string(self):
        from app.shared.utils import validate_text

        self.assertEqual(validate_text(''), '')

    def test_custom_max_length(self):
        from app.shared.utils import validate_text

        self.assertEqual(validate_text('abcdef', max_length=3), 'abc')


class TestGetQgisPython(unittest.TestCase):
    @patch.dict(os.environ, {'PYTHON_QGIS_BAT': ''}, clear=False)
    @patch('os.name', 'posix')
    def test_posix_default(self):
        from app.shared.utils import get_qgis_python

        # No env var set, posix => 'python3'
        result = get_qgis_python()
        self.assertIn(result, ('python3', None))

    @patch.dict(os.environ, {'PYTHON_QGIS_BAT': '/usr/bin/python3'}, clear=False)
    @patch('os.access', return_value=True)
    @patch('pathlib.Path.is_file', return_value=True)
    def test_env_var_valid(self, mock_is_file, mock_access):
        from app.shared.utils import get_qgis_python

        result = get_qgis_python()
        self.assertEqual(result, '/usr/bin/python3')

    @patch.dict(os.environ, {'PYTHON_QGIS_BAT': '/bad/path'}, clear=False)
    @patch('os.access', return_value=False)
    @patch('pathlib.Path.is_file', return_value=True)
    def test_env_var_not_executable(self, mock_is_file, mock_access):
        from app.shared.utils import get_qgis_python

        result = get_qgis_python()
        self.assertIn(result, ('python3', 'python.exe'))


class TestSubprocessFlags(unittest.TestCase):
    def test_is_mapping(self):
        from app.shared.utils import _SUBPROCESS_FLAGS
        from collections.abc import Mapping

        self.assertIsInstance(_SUBPROCESS_FLAGS, Mapping)

    def test_nt_has_creationflags(self):
        from app.shared.utils import _SUBPROCESS_FLAGS

        if os.name == 'nt':
            self.assertIn('creationflags', _SUBPROCESS_FLAGS)
        else:
            self.assertEqual(len(_SUBPROCESS_FLAGS), 0)


class TestLocaleValue(unittest.TestCase):
    def test_arabic_returns_field_base(self):
        from app.shared.utils import locale_value

        obj = MagicMock()
        obj.name = 'test_name'
        self.assertEqual(locale_value(obj, 'name', 'ar'), 'test_name')

    def test_non_arabic_returns_locale_field(self):
        from app.shared.utils import locale_value

        obj = MagicMock()
        obj.name_fr = 'test_fr'
        obj.name = 'test_name'
        self.assertEqual(locale_value(obj, 'name', 'fr'), 'test_fr')

    def test_non_arabic_falls_back_to_base(self):
        from app.shared.utils import locale_value

        obj = MagicMock()
        obj.name_fr = None
        obj.name = 'fallback'
        self.assertEqual(locale_value(obj, 'name', 'fr'), 'fallback')


class TestGetAllFieldsAndLabels(unittest.TestCase):
    @patch('app.shared.utils.inspect')
    def test_filters_excluded_columns(self, mock_inspect):
        from app.shared.utils import get_all_fields_and_labels

        col1 = MagicMock()
        col1.name = 'id'
        col1.info = {}
        col2 = MagicMock()
        col2.name = 'name'
        col2.info = {'label': 'Name'}
        col3 = MagicMock()
        col3.name = 'geometry'
        col3.info = {}

        attr1 = MagicMock()
        attr1.columns = [col1]
        attr2 = MagicMock()
        attr2.columns = [col2]
        attr3 = MagicMock()
        attr3.columns = [col3]

        mock_mapper = MagicMock()
        mock_mapper.attrs = [attr1, attr2, attr3]
        mock_inspect.return_value = mock_mapper

        fields, _labels = get_all_fields_and_labels(MagicMock(), locale='en')
        self.assertIn('id', fields)
        self.assertIn('name', fields)
        self.assertNotIn('geometry', fields)
