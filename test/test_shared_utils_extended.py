"""Extended tests for app.shared.utils — covers current_locale, current_theme, get_all_fields_and_labels."""

import os
import unittest
from collections.abc import Mapping
from unittest.mock import MagicMock, patch

from pathlib import Path

from app.shared.utils import (
    _SUBPROCESS_FLAGS,
    current_locale,
    current_theme,
    get_all_fields_and_labels,
    get_qgis_python,
    locale_value,
    validate_safe_name,
    validate_text,
)
from app.shared.constants import THEME_DARK, THEME_LIGHT


class TestCurrentLocale(unittest.TestCase):
    @patch('app.shared.utils.QSettings')
    def test_returns_stored_locale(self, mock_qs_cls):
        mock_settings = MagicMock()
        mock_settings.value.return_value = 'fr'
        mock_qs_cls.return_value = mock_settings
        result = current_locale()
        self.assertEqual(result, 'fr')

    @patch('app.shared.utils.QSettings')
    def test_empty_stored_uses_global(self, mock_qs_cls):
        mock_app_settings = MagicMock()
        mock_app_settings.value.return_value = ''
        mock_global_settings = MagicMock()
        mock_global_settings.value.return_value = 'en_US'
        mock_qs_cls.side_effect = [mock_app_settings, mock_global_settings]
        result = current_locale()
        self.assertEqual(result, 'en')

    @patch('app.shared.utils.QSettings')
    def test_empty_stored_no_global(self, mock_qs_cls):
        mock_app_settings = MagicMock()
        mock_app_settings.value.return_value = ''
        mock_global_settings = MagicMock()
        mock_global_settings.value.return_value = None
        mock_qs_cls.side_effect = [mock_app_settings, mock_global_settings]
        result = current_locale()
        self.assertEqual(result, 'en')


class TestLocaleValue(unittest.TestCase):
    def test_arabic_returns_field_base(self):
        obj = MagicMock()
        obj.name = 'test_name'
        self.assertEqual(locale_value(obj, 'name', 'ar'), 'test_name')

    def test_non_arabic_returns_locale_field(self):
        obj = MagicMock()
        obj.name_fr = 'test_fr'
        obj.name = 'test_name'
        self.assertEqual(locale_value(obj, 'name', 'fr'), 'test_fr')

    def test_non_arabic_falls_back_to_base(self):
        obj = MagicMock()
        obj.name_fr = None
        obj.name = 'fallback'
        self.assertEqual(locale_value(obj, 'name', 'fr'), 'fallback')

    def test_empty_locale_uses_current_locale(self):
        obj = MagicMock()
        obj.name_en = 'english_val'
        obj.name = 'base_val'
        with patch('app.shared.utils.current_locale', return_value='en'):
            result = locale_value(obj, 'name')
        self.assertEqual(result, 'english_val')

    def test_field_does_not_exist(self):
        obj = MagicMock(spec=[])
        result = locale_value(obj, 'missing', 'fr')
        self.assertEqual(result, '')


class TestCurrentTheme(unittest.TestCase):
    @patch('app.shared.utils.QSettings')
    def test_returns_theme_from_settings(self, mock_qs_cls):
        mock_settings = MagicMock()
        mock_settings.value.return_value = 'dark'
        mock_qs_cls.return_value = mock_settings
        result = current_theme()
        self.assertEqual(result, THEME_DARK)

    @patch('app.shared.utils.QSettings')
    def test_persists_corrected_theme(self, mock_qs_cls):
        mock_settings = MagicMock()
        mock_settings.value.return_value = 'invalid_value'
        mock_qs_cls.return_value = mock_settings
        result = current_theme()
        # invalid_value normalizes to THEME_DARK, which gets saved back
        mock_settings.setValue.assert_called_once()
        self.assertEqual(result, THEME_DARK)

    @patch('app.shared.utils.QSettings')
    def test_light_theme(self, mock_qs_cls):
        mock_settings = MagicMock()
        mock_settings.value.return_value = 'light'
        mock_qs_cls.return_value = mock_settings
        result = current_theme()
        self.assertEqual(result, THEME_LIGHT)


class TestGetQgisPython(unittest.TestCase):
    @patch.dict(os.environ, {}, clear=True)
    @patch('app.shared.utils.os.name', 'posix')
    def test_posix_default(self):
        result = get_qgis_python()
        self.assertIn(result, ('python3', None))

    @patch.dict(os.environ, {'PYTHON_QGIS_BAT': '/usr/bin/python3'}, clear=False)
    @patch('app.shared.utils.os.access', return_value=True)
    @patch.object(Path, 'is_file', return_value=True)
    def test_env_var_valid(self, mock_is_file, mock_access):
        result = get_qgis_python()
        self.assertEqual(result, '/usr/bin/python3')

    @patch.dict(os.environ, {'PYTHON_QGIS_BAT': '/bad/path'}, clear=False)
    @patch('app.shared.utils.os.access', return_value=False)
    @patch.object(Path, 'is_file', return_value=True)
    def test_env_var_not_executable(self, mock_is_file, mock_access):
        result = get_qgis_python()
        self.assertIn(result, ('python3', 'python.exe'))

    @patch.dict(os.environ, {'PYTHON_QGIS_BAT': ''}, clear=False)
    @patch('app.shared.utils.os.name', 'nt')
    def test_nt_default(self):
        # empty string is falsy, so falls through to OS default
        os.environ.pop('PYTHON_QGIS_BAT', None)
        result = get_qgis_python()
        self.assertIn(result, ('python3', 'python.exe'))


class TestGetAllFieldsAndLabels(unittest.TestCase):
    @patch('app.shared.utils.inspect')
    def test_filters_excluded_columns(self, mock_inspect):
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

    @patch('app.shared.utils.inspect')
    def test_arabic_locale_uses_label(self, mock_inspect):
        col = MagicMock()
        col.name = 'name'
        col.info = {'label': 'Arabic Label'}
        attr = MagicMock()
        attr.columns = [col]
        mock_mapper = MagicMock()
        mock_mapper.attrs = [attr]
        mock_inspect.return_value = mock_mapper

        _fields, labels = get_all_fields_and_labels(MagicMock(), locale='ar')
        self.assertEqual(labels[0], 'Arabic Label')

    @patch('app.shared.utils.inspect')
    def test_arabic_locale_no_label_falls_back(self, mock_inspect):
        col = MagicMock()
        col.name = 'name'
        col.info = {}
        attr = MagicMock()
        attr.columns = [col]
        mock_mapper = MagicMock()
        mock_mapper.attrs = [attr]
        mock_inspect.return_value = mock_mapper

        _fields, labels = get_all_fields_and_labels(MagicMock(), locale='ar')
        self.assertEqual(labels[0], 'name')

    @patch('app.shared.utils.inspect')
    def test_property_labels_added(self, mock_inspect):
        col = MagicMock()
        col.name = 'name'
        col.info = {'label': 'Name'}
        attr = MagicMock()
        attr.columns = [col]
        mock_mapper = MagicMock()
        mock_mapper.attrs = [attr]
        mock_inspect.return_value = mock_mapper

        fields, labels = get_all_fields_and_labels(
            MagicMock(), locale='en', property_labels={'extra': 'Extra'}
        )
        self.assertIn('extra', fields)
        self.assertIn('Extra', labels)

    @patch('app.shared.utils.inspect')
    def test_empty_locale_uses_current_locale(self, mock_inspect):
        col = MagicMock()
        col.name = 'name'
        col.info = {'label_en': 'English Label'}
        attr = MagicMock()
        attr.columns = [col]
        mock_mapper = MagicMock()
        mock_mapper.attrs = [attr]
        mock_inspect.return_value = mock_mapper

        with patch('app.shared.utils.current_locale', return_value='en'):
            _fields, labels = get_all_fields_and_labels(MagicMock())
        self.assertEqual(labels[0], 'English Label')

    @patch('app.shared.utils.inspect')
    def test_excludes_all_special_columns(self, mock_inspect):
        excluded = [
            'geometry',
            'user_id',
            'locality_id',
            'has_child',
            'parent',
            'zone_id',
        ]
        attrs = []
        for name in excluded:
            col = MagicMock()
            col.name = name
            col.info = {}
            attr = MagicMock()
            attr.columns = [col]
            attrs.append(attr)
        mock_mapper = MagicMock()
        mock_mapper.attrs = attrs
        mock_inspect.return_value = mock_mapper

        fields, _ = get_all_fields_and_labels(MagicMock(), locale='en')
        self.assertEqual(fields, [])


class TestValidateSafeName(unittest.TestCase):
    def test_valid_names(self):
        for name in ('users', '_private', 'Table123', 'a'):
            self.assertEqual(validate_safe_name(name), name)

    def test_invalid_names(self):
        for name in ('123abc', 'has space', 'has-dash', 'table;DROP', '', 'a.b'):
            with self.assertRaises(ValueError):
                validate_safe_name(name)


class TestValidateText(unittest.TestCase):
    def test_strips_whitespace(self):
        self.assertEqual(validate_text('  hello  '), 'hello')

    def test_truncates(self):
        self.assertEqual(validate_text('a' * 300, max_length=10), 'a' * 10)

    def test_empty_string(self):
        self.assertEqual(validate_text(''), '')


class TestSubprocessFlags(unittest.TestCase):
    def test_is_mapping(self):
        self.assertIsInstance(_SUBPROCESS_FLAGS, Mapping)

    def test_nt_has_creationflags(self):
        if os.name == 'nt':
            self.assertIn('creationflags', _SUBPROCESS_FLAGS)
        else:
            self.assertEqual(len(_SUBPROCESS_FLAGS), 0)


if __name__ == '__main__':
    unittest.main()
