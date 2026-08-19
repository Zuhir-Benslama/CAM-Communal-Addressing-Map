"""Extended tests for app.core.config — covers find_mod_spatialite_dll, _find_via_ldconfig, etc."""

import os
import subprocess
import types
import unittest
from unittest.mock import MagicMock, patch

from app.core.config import (
    _find_in_candidate_paths,
    _find_via_ldconfig,
    find_mod_spatialite_dll,
    get_dialog_qss,
    get_theme_qss,
    normalize_theme,
    THEMES,
)
from app.shared.constants import THEME_DARK, THEME_LIGHT, Theme


class TestFindViaLdconfig(unittest.TestCase):
    @patch('app.core.config.shutil.which', return_value=None)
    def test_no_ldconfig_binary(self, _mock_which):
        self.assertIsNone(_find_via_ldconfig())

    @patch('app.core.config.Path')
    @patch('app.core.config.subprocess.run')
    @patch('app.core.config.shutil.which', return_value='/usr/sbin/ldconfig')
    def test_found_valid_path(self, mock_which, mock_run, mock_path_cls):
        mock_result = MagicMock()
        mock_result.stdout = '  mod_spatialite.so => /usr/lib/mod_spatialite.so\n'
        mock_run.return_value = mock_result
        mock_path_cls.return_value.exists.return_value = True
        result = _find_via_ldconfig()
        self.assertEqual(result, '/usr/lib/mod_spatialite.so')

    @patch('app.core.config.Path')
    @patch('app.core.config.subprocess.run')
    @patch('app.core.config.shutil.which', return_value='/usr/sbin/ldconfig')
    def test_found_path_not_exists(self, mock_which, mock_run, mock_path_cls):
        mock_result = MagicMock()
        mock_result.stdout = '  mod_spatialite.so => /fake/path.so\n'
        mock_run.return_value = mock_result
        mock_path_cls.return_value.exists.return_value = False
        result = _find_via_ldconfig()
        self.assertIsNone(result)

    @patch(
        'app.core.config.subprocess.run',
        side_effect=subprocess.CalledProcessError(1, 'ld'),
    )
    @patch('app.core.config.shutil.which', return_value='/usr/sbin/ldconfig')
    def test_called_process_error(self, _mock_which, _mock_run):
        self.assertIsNone(_find_via_ldconfig())

    @patch('app.core.config.subprocess.run', side_effect=FileNotFoundError)
    @patch('app.core.config.shutil.which', return_value='/usr/sbin/ldconfig')
    def test_file_not_found_error(self, _mock_which, _mock_run):
        self.assertIsNone(_find_via_ldconfig())

    @patch('app.core.config.subprocess.run', side_effect=PermissionError)
    @patch('app.core.config.shutil.which', return_value='/usr/sbin/ldconfig')
    def test_permission_error(self, _mock_which, _mock_run):
        self.assertIsNone(_find_via_ldconfig())

    @patch('app.core.config.subprocess.run', side_effect=OSError)
    @patch('app.core.config.shutil.which', return_value='/usr/sbin/ldconfig')
    def test_os_error(self, _mock_which, _mock_run):
        self.assertIsNone(_find_via_ldconfig())

    @patch('app.core.config.Path')
    @patch('app.core.config.subprocess.run')
    @patch('app.core.config.shutil.which', return_value='/usr/sbin/ldconfig')
    def test_no_spatialite_in_output(self, mock_which, mock_run, mock_path_cls):
        mock_result = MagicMock()
        mock_result.stdout = '  libfoo.so => /usr/lib/libfoo.so\n'
        mock_run.return_value = mock_result
        self.assertIsNone(_find_via_ldconfig())

    @patch('app.core.config.Path')
    @patch('app.core.config.subprocess.run')
    @patch('app.core.config.shutil.which', return_value='/usr/sbin/ldconfig')
    def test_malformed_line_no_arrow(self, mock_which, mock_run, mock_path_cls):
        mock_result = MagicMock()
        mock_result.stdout = '  mod_spatialite.so (no arrow here)\n'
        mock_run.return_value = mock_result
        self.assertIsNone(_find_via_ldconfig())


class TestFindModSpatialiteDll(unittest.TestCase):
    @patch.dict(os.environ, {'MOD_SPATIALITE_DLL': '/env/path/mod_spatialite.so'})
    def test_env_var(self):
        self.assertEqual(find_mod_spatialite_dll(), '/env/path/mod_spatialite.so')

    @patch('app.core.config.os.name', 'nt')
    def test_windows(self):
        self.assertEqual(find_mod_spatialite_dll(), 'mod_spatialite.dll')

    @patch('app.core.config.os.uname')
    @patch('app.core.config.os.name', 'posix')
    def test_macos(self, mock_uname):
        mock_uname.return_value = types.SimpleNamespace(sysname='Darwin')
        self.assertEqual(find_mod_spatialite_dll(), 'mod_spatialite.dylib')

    @patch('app.core.config._find_via_ldconfig', return_value='/ldconfig/path.so')
    @patch('app.core.config._find_in_candidate_paths', return_value=None)
    @patch('app.core.config.os.uname')
    @patch('app.core.config.os.name', 'posix')
    def test_ldconfig_fallback(self, mock_uname, mock_cands, mock_ldconfig):
        mock_uname.return_value = types.SimpleNamespace(sysname='Linux')
        self.assertEqual(find_mod_spatialite_dll(), '/ldconfig/path.so')

    @patch('app.core.config._find_via_ldconfig', return_value=None)
    @patch('app.core.config._find_in_candidate_paths', return_value=None)
    @patch('app.core.config.os.uname')
    @patch('app.core.config.os.name', 'posix')
    def test_fallback_default(self, mock_uname, mock_cands, mock_ldconfig):
        mock_uname.return_value = types.SimpleNamespace(sysname='Linux')
        self.assertEqual(find_mod_spatialite_dll(), 'mod_spatialite.so')


class TestNormalizeThemeExtended(unittest.TestCase):
    def test_theme_dark_enum(self):
        self.assertEqual(normalize_theme(Theme.DARK), THEME_DARK)

    def test_theme_light_enum(self):
        self.assertEqual(normalize_theme(Theme.LIGHT), THEME_LIGHT)

    def test_whitespace_string(self):
        self.assertEqual(normalize_theme('   '), THEME_DARK)

    def test_unknown_string(self):
        self.assertEqual(normalize_theme('neon'), THEME_DARK)


class TestGetThemeQssExtended(unittest.TestCase):
    def test_dark_returns_str(self):
        result = get_theme_qss(THEME_DARK)
        self.assertIsInstance(result, str)

    def test_light_returns_str(self):
        result = get_theme_qss(THEME_LIGHT)
        self.assertIsInstance(result, str)

    def test_none_returns_default(self):
        result = get_theme_qss(None)
        self.assertIsInstance(result, str)

    def test_unknown_falls_back_to_dark(self):
        result = get_theme_qss('unknown')
        self.assertIsInstance(result, str)


class TestGetDialogQssExtended(unittest.TestCase):
    def test_dark(self):
        self.assertIsInstance(get_dialog_qss('dark'), str)

    def test_light(self):
        self.assertIsInstance(get_dialog_qss('light'), str)

    def test_none_returns_default_dialog(self):
        self.assertIsInstance(get_dialog_qss(None), str)


class TestFindInCandidatePaths(unittest.TestCase):
    def test_first_existing(self):
        result = _find_in_candidate_paths(['/nonexistent', '/etc/hostname'])
        self.assertEqual(result, '/etc/hostname')

    def test_empty_list(self):
        self.assertIsNone(_find_in_candidate_paths([]))

    def test_none_exist(self):
        self.assertIsNone(_find_in_candidate_paths(['/totally/fake/path']))


class TestThemesDict(unittest.TestCase):
    def test_has_both_themes(self):
        self.assertIn(THEME_DARK, THEMES)
        self.assertIn(THEME_LIGHT, THEMES)

    def test_tuples_have_two_elements(self):
        for theme_tuple in THEMES.values():
            self.assertEqual(len(theme_tuple), 2)


if __name__ == '__main__':
    unittest.main()
