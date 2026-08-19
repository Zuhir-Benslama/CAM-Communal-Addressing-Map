"""Tests for app.core.config."""

import unittest
from app.core.config import (
    normalize_theme,
    get_theme_qss,
    get_dialog_qss,
    _find_in_candidate_paths,
    THEMES,
)


class TestNormalizeTheme(unittest.TestCase):
    def test_none_returns_dark(self):
        from app.shared.constants import THEME_DARK

        self.assertEqual(normalize_theme(None), THEME_DARK)

    def test_dark_string(self):
        from app.shared.constants import THEME_DARK

        self.assertEqual(normalize_theme('dark'), THEME_DARK)

    def test_light_string(self):
        from app.shared.constants import THEME_LIGHT

        self.assertEqual(normalize_theme('light'), THEME_LIGHT)

    def test_arabic_light(self):
        from app.shared.constants import THEME_LIGHT

        self.assertEqual(normalize_theme('فاتح'), THEME_LIGHT)

    def test_arabic_dark(self):
        from app.shared.constants import THEME_DARK

        self.assertEqual(normalize_theme('داكن'), THEME_DARK)

    def test_empty_string_returns_dark(self):
        from app.shared.constants import THEME_DARK

        self.assertEqual(normalize_theme(''), THEME_DARK)

    def test_whitespace_returns_dark(self):
        from app.shared.constants import THEME_DARK

        self.assertEqual(normalize_theme('   '), THEME_DARK)

    def test_unknown_returns_dark(self):
        from app.shared.constants import THEME_DARK

        self.assertEqual(normalize_theme('unknown'), THEME_DARK)

    def test_theme_enum_passthrough(self):
        from app.shared.constants import THEME_LIGHT

        self.assertEqual(normalize_theme(THEME_LIGHT), THEME_LIGHT)


class TestGetThemeQss(unittest.TestCase):
    def test_dark_returns_string(self):
        result = get_theme_qss('dark')
        self.assertIsInstance(result, str)

    def test_light_returns_string(self):
        result = get_theme_qss('light')
        self.assertIsInstance(result, str)

    def test_none_returns_default(self):
        result = get_theme_qss(None)
        self.assertIsInstance(result, str)


class TestGetDialogQss(unittest.TestCase):
    def test_returns_string(self):
        result = get_dialog_qss('dark')
        self.assertIsInstance(result, str)


class TestFindInCandidatePaths(unittest.TestCase):
    def test_returns_first_existing(self):

        result = _find_in_candidate_paths(['/nonexistent', '/etc/hostname'])
        self.assertEqual(result, '/etc/hostname')

    def test_returns_none_if_empty(self):

        self.assertIsNone(_find_in_candidate_paths([]))

    def test_returns_none_if_none_exist(self):

        self.assertIsNone(_find_in_candidate_paths(['/totally/fake/path']))


class TestThemesDict(unittest.TestCase):
    def test_themes_has_both(self):
        from app.shared.constants import THEME_DARK, THEME_LIGHT

        self.assertIn(THEME_DARK, THEMES)
        self.assertIn(THEME_LIGHT, THEMES)

    def test_theme_tuples_have_two_elements(self):
        for theme_tuple in THEMES.values():
            self.assertEqual(len(theme_tuple), 2)
