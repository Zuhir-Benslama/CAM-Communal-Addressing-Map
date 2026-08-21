"""Utility functions: locale, validation, theme, and subprocess helpers."""

import logging
import os
import re
import subprocess
from pathlib import Path
from typing import TypedDict

from qgis.PyQt.QtCore import QSettings
from sqlalchemy import inspect

from ..core.config import normalize_theme
from ..shared.constants import (
    SETTINGS_APP,
    SETTINGS_KEY_LOCALE,
    SETTINGS_KEY_THEME,
    SETTINGS_ORG,
    THEME_DARK,
    Theme,
)

logger = logging.getLogger(__name__)

_IDENTIFIER_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


def validate_safe_name(name: str) -> str:
    """Validate that *name* is a safe SQL identifier (no SQL injection risk)."""
    if not _IDENTIFIER_RE.match(name):
        msg = f'Unsafe SQL identifier: {name!r}'
        raise ValueError(msg)
    return name


def validate_text(value: str, max_length: int = 255) -> str:
    """Strip whitespace and truncate *value* to *max_length* chars."""
    value = value.strip()
    if len(value) > max_length:
        value = value[:max_length]
    return value


def current_locale() -> str:
    """Return the current locale code ('ar', 'fr', 'en', etc.)."""
    settings = QSettings(SETTINGS_ORG, SETTINGS_APP)
    locale = settings.value(SETTINGS_KEY_LOCALE, '')
    if not locale:
        locale_val = QSettings().value('locale/userLocale')
        locale = locale_val[0:2] if locale_val else 'en'
    return locale


def locale_value(instance, field_base: str, locale: str = '') -> str:
    """Return a locale-aware field value from a model instance."""
    if not locale:
        locale = current_locale()
    if locale == 'ar':
        return getattr(instance, field_base, '') or ''
    locale_field = f'{field_base}_{locale}'
    value = getattr(instance, locale_field, None)
    return value if value else (getattr(instance, field_base, '') or '')


def current_theme() -> Theme:
    """Return the current theme (:data:`THEME_DARK` or :data:`THEME_LIGHT`)."""
    settings = QSettings(SETTINGS_ORG, SETTINGS_APP)
    value = settings.value(SETTINGS_KEY_THEME, THEME_DARK)
    theme = normalize_theme(value)
    if value != theme:
        settings.setValue(SETTINGS_KEY_THEME, theme)
    return theme


def get_qgis_python() -> str:
    """Return the path to a suitable QGIS Python interpreter."""
    python = os.getenv('PYTHON_QGIS_BAT')
    if python:
        if not Path(python).is_file() or not os.access(python, os.X_OK):
            logger.warning(
                'PYTHON_QGIS_BAT path is not executable: %s, falling back',
                python,
            )
        else:
            return python
    if os.name == 'nt':
        return 'python.exe'
    return 'python3'


def get_all_fields_and_labels(
    model_class, property_labels=None, locale=''
) -> tuple[list[str], list[str]]:
    """Return column names and their locale-aware labels for a model class."""
    if not locale:
        locale = current_locale()
    fields = []
    labels = []

    mapper = inspect(model_class)
    for attr in mapper.attrs:
        if hasattr(attr, 'columns'):
            column = attr.columns[0]
            if column.name not in [
                'geometry',
                'user_id',
                'locality_id',
                'has_child',
                'parent',
                'zone_id',
            ]:
                fields.append(column.name)
                if locale != 'ar':
                    label_key = f'label_{locale}'
                    label = column.info.get(label_key)
                else:
                    label = None
                if not label:
                    label = column.info.get('label', column.name)
                labels.append(label)

    if property_labels:
        for prop_name, prop_label in property_labels.items():
            fields.append(prop_name)
            labels.append(prop_label)

    return fields, labels


class _SubprocessFlags(TypedDict, total=False):
    """Platform-specific keyword flags for :func:`subprocess.run`."""

    creationflags: int


_SUBPROCESS_FLAGS: _SubprocessFlags = (
    {'creationflags': subprocess.CREATE_NO_WINDOW}  # type: ignore[attr-defined]
    if os.name == 'nt'
    else {}
)
