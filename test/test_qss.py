"""Tests for generated QSS theme stylesheets."""

import os
import re
import sys

import pytest

from app.shared.constants import THEME_DARK

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import (
    DARK_QSS,
    DARK_QSS_DIALOG,
    LIGHT_QSS,
    LIGHT_QSS_DIALOG,
    get_dialog_qss,
    get_theme_qss,
    normalize_theme,
)


GENERATED_QSS = {
    'dark': DARK_QSS,
    'dark_dialog': DARK_QSS_DIALOG,
    'light': LIGHT_QSS,
    'light_dialog': LIGHT_QSS_DIALOG,
}

DARK_PALETTE_COLORS = {
    '#1a1b26',
    '#24253a',
    '#2f3048',
    '#3b3d54',
    '#c9d1d9',
    '#8b949e',
    '#58a6ff',
    '#79b8ff',
    '#3fb950',
    '#f85149',
    '#264f78',
}


def _extract_block(selector: str, qss: str) -> str:
    match = re.search(rf'{re.escape(selector)}\s*\{{(?P<body>.*?)\}}', qss, re.S)
    assert match is not None
    return match.group('body')


def test_qss_templates_render_without_placeholders() -> None:
    for name, qss in GENERATED_QSS.items():
        assert qss.strip(), name
        assert '{{' not in qss, name
        assert '}}' not in qss, name
        assert qss.count('{') == qss.count('}'), name


def test_light_qss_does_not_leak_dark_palette_colors() -> None:
    light_colors = set(re.findall(r'#[0-9a-fA-F]{6}', LIGHT_QSS + LIGHT_QSS_DIALOG))
    assert not DARK_PALETTE_COLORS & light_colors


def test_light_header_toolbar_uses_light_border() -> None:
    selector = (
        'QFrame[surfaceRole="header"],\n'
        '    QFrame[surfaceRole="toolbar"],\n'
        '    QGroupBox[surfaceRole="toolbar"]'
    )
    block = _extract_block(selector, LIGHT_QSS)
    assert 'border: 1px solid #d0d7de;' in block


@pytest.mark.parametrize(
    ('theme_name', 'expected'),
    [
        ('light', LIGHT_QSS),
        ('dark', DARK_QSS),
        ('Light', LIGHT_QSS),
        ('Dark', DARK_QSS),
        ('فاتح', LIGHT_QSS),
        ('داكن', DARK_QSS),
    ],
)
def test_theme_lookup_returns_matching_stylesheet(
    theme_name: str,
    expected: str,
) -> None:
    assert get_theme_qss(theme_name) is expected
    assert get_dialog_qss(theme_name) is (
        DARK_QSS_DIALOG if expected is DARK_QSS else LIGHT_QSS_DIALOG
    )


def test_normalize_theme_defaults_unknown_values_to_dark() -> None:
    assert normalize_theme('unknown') is THEME_DARK
    assert normalize_theme(None) is THEME_DARK
