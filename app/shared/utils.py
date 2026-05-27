"""Utility functions: locale, validation, theme, and subprocess helpers."""
import logging
import os
import shutil
import subprocess
from types import MappingProxyType
from typing import List, Mapping, Optional, Tuple, TypeVar

from qgis.PyQt.QtCore import QSettings
from sqlalchemy import inspect

from ..shared.constants import (
    SETTINGS_ORG, SETTINGS_APP, SETTINGS_KEY_LOCALE,
    SETTINGS_KEY_THEME, THEME_DARK, THEME_LIGHT,
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


def ensure(value: Optional[T], message: str = "") -> T:
    """Assert value is not None, returning it or raising ValueError."""
    if value is None:
        raise ValueError(message or "Expected non-None value")
    return value


def validate_text(value: str, max_length: int = 255) -> str:
    value = value.strip()
    if len(value) > max_length:
        value = value[:max_length]
    return value


def current_locale() -> str:
    settings = QSettings(SETTINGS_ORG, SETTINGS_APP)
    locale = settings.value(SETTINGS_KEY_LOCALE, '')
    if not locale:
        locale_val = QSettings().value('locale/userLocale')
        locale = locale_val[0:2] if locale_val else 'en'
    return locale


def locale_value(instance, field_base: str, locale: str = '') -> str:
    if not locale:
        locale = current_locale()
    if locale == 'ar':
        return getattr(instance, field_base, '') or ''
    locale_field = f'{field_base}_{locale}'
    value = getattr(instance, locale_field, None)
    return value if value else (getattr(instance, field_base, '') or '')


def current_theme() -> str:
    settings = QSettings(SETTINGS_ORG, SETTINGS_APP)
    value = settings.value(SETTINGS_KEY_THEME, THEME_DARK)
    # Backward compat: old Arabic values were changed to English
    theme_map = {'فاتح': THEME_LIGHT, 'داكن': THEME_DARK}
    migrated = theme_map.get(value)
    if migrated is not None:
        settings.setValue(SETTINGS_KEY_THEME, migrated)
        return migrated
    return value


def get_qgis_python() -> Optional[str]:
    python = os.getenv('PYTHON_QGIS_BAT')
    if python:
        if not os.path.isfile(python) or not os.access(python, os.X_OK):
            logger.warning(
                "PYTHON_QGIS_BAT path is not executable: %s, falling back",
                python,
            )
        else:
            return python
    if os.name == 'nt':
        return 'python.exe'
    if shutil.which('python3'):
        return 'python3'
    return 'python3'


def get_all_fields_and_labels(
    model_class, property_labels=None, locale=''
) -> Tuple[List[str], List[str]]:
    if not locale:
        locale = current_locale()
    fields = []
    labels = []

    mapper = inspect(model_class)
    for attr in mapper.attrs:
        if hasattr(attr, 'columns'):
            column = attr.columns[0]
            if column.name not in [
                'geometry', 'user_id', 'locality_id',
                'has_child', 'parent', 'zone_id',
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


_SUBPROCESS_FLAGS: Mapping[str, int]
if os.name == 'nt':
    _SUBPROCESS_FLAGS = MappingProxyType(
        {'creationflags': subprocess.CREATE_NO_WINDOW},  # type: ignore[attr-defined]
    )
else:
    _SUBPROCESS_FLAGS = MappingProxyType({})
