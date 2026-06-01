"""Static lookup data loaded from JSON files at runtime."""

import json
import os
from typing import Any

from qgis.PyQt.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QWidget,
)

_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'template_data',
)

_cache: dict[str, list[dict[str, Any]]] = {}


def _load(filename: str) -> list[dict[str, Any]]:
    """Load and cache JSON data from a template data file."""
    if filename not in _cache:
        path = os.path.join(_DATA_DIR, filename)
        with open(path, encoding='utf-8') as f:
            _cache[filename] = json.load(f)
    return _cache[filename]


# ---------------------------------------------------------------------------
# Simple lookups: {pk, label_fr?, label_en?}
# ---------------------------------------------------------------------------

def road_types() -> list[dict[str, Any]]:
    """Return road type lookup data."""
    return _load('type_road.json')


def zone_types() -> list[dict[str, Any]]:
    """Return zone type lookup data."""
    return _load('zone_type.json')


def subdivision_types() -> list[dict[str, Any]]:
    """Return subdivision type lookup data."""
    return _load('type_cite.json')


def mounting_statuses() -> list[dict[str, Any]]:
    """Return mounting status lookup data."""
    return _load('mounting_status.json')


def numbering_states() -> list[dict[str, Any]]:
    """Return numbering state lookup data."""
    return _load('State_Numbering.json')


# ---------------------------------------------------------------------------
# Organization types: {type_ar, type_fr?, category, category_fr?,
#                     category_en?, ...}
#   - type_ar = Arabic PK
#   - type_fr -> pk_fr equivalent
#   - category = category (Arabic)
# ---------------------------------------------------------------------------

def organization_types() -> list[dict[str, Any]]:
    """Return organization type lookup data."""
    return _load('organization_type.json')


def org_categories(locale: str = 'ar') -> list[tuple[str, str]]:
    """Return distinct organization categories -> (display, value)."""
    seen: set[str] = set()
    result: list[tuple[str, str]] = []
    for entry in organization_types():
        category = entry.get('category', '')
        if category and category not in seen:
            seen.add(category)
            if locale != 'ar':
                val = entry.get(f'category_{locale}', '') or category
            else:
                val = category
            result.append((val, category))
    result.sort(key=lambda x: x[1])
    return result


def org_types_for_category(
    category: str, locale: str = 'ar',
) -> list[tuple[str, str]]:
    """Return organization types for a category -> (display, pk)."""
    result: list[tuple[str, str]] = []
    for entry in organization_types():
        if entry.get('category', '') == category:
            pk = entry.get('type_ar', '')
            if locale != 'ar':
                display = entry.get('type_fr', '') or pk
            else:
                display = pk
            if pk:
                result.append((display, pk))
    return result


def org_subcategories(category: str) -> list[str]:
    """Return distinct subcategories for an org category."""
    seen: set[str] = set()
    result: list[str] = []
    for entry in organization_types():
        if entry.get('category', '') == category:
            subcategory = entry.get('subcat', '')
            if subcategory and subcategory not in seen:
                seen.add(subcategory)
                result.append(subcategory)
    return result


# ---------------------------------------------------------------------------
# Activity types: {sector, type, cat_fr?, cat_en?, type_fr?, type_en?}
# ---------------------------------------------------------------------------

def activity_types() -> list[dict[str, Any]]:
    """Return activity type lookup data."""
    return _load('activity.json')


def activity_categories(locale: str = 'ar') -> list[tuple[str, str]]:
    """Return distinct activity categories -> (display, value)."""
    seen: set[str] = set()
    result: list[tuple[str, str]] = []
    for entry in activity_types():
        category = entry.get('sector', '')
        if category and category not in seen:
            seen.add(category)
            if locale != 'ar':
                val = entry.get(f'cat_{locale}', '') or category
            else:
                val = category
            result.append((val, category))
    result.sort(key=lambda x: x[1])
    return result


def activity_types_for_category(
    cat: str, locale: str = 'ar',
) -> list[tuple[str, str]]:
    """Return activity types for a category -> (display, value)."""
    result: list[tuple[str, str]] = []
    for entry in activity_types():
        if entry.get('sector', '') == cat:
            type_val = entry.get('type', '')
            if locale != 'ar':
                display = entry.get(f'type_{locale}', '') or type_val
            else:
                display = type_val
            if type_val:
                result.append((display, type_val))
    return result


def activity_subcategories(cat: str) -> list[str]:
    """Return distinct subcategories for an activity category."""
    seen: set[str] = set()
    result: list[str] = []
    for entry in activity_types():
        if entry.get('sector', '') == cat:
            subcategory = entry.get('subcat', '')
            if subcategory and subcategory not in seen:
                seen.add(subcategory)
                result.append(subcategory)
    return result


# ---------------------------------------------------------------------------
# Administrative geography — communes, dairas, wilayas
# ---------------------------------------------------------------------------

def communes_data() -> dict[str, dict[str, Any]]:
    """Return all communes as a dict keyed by commune_id (str)."""
    return _load('communes.json')


def communes_list() -> list[dict[str, Any]]:
    """Return all communes as a list."""
    return list(communes_data().values())


def wilayas_data() -> dict[str, dict[str, Any]]:
    """Return all wilayas as a dict keyed by wilaya_id (str)."""
    return _load('wilayas.json')


def dairas_data() -> dict[str, dict[str, Any]]:
    """Return all dairas as a dict keyed by daira_id (str)."""
    return _load('daira.json')


def _commune_code_key(c: dict[str, Any]) -> int:
    """Return the commune_code as int (handles both int and str storage)."""
    v = c.get('commune_code', 0)
    return int(v) if v is not None else 0


def _lookup_wilaya_for_commune_code(commune_code: str) -> int | None:
    """Resolve a commune_code (str) to a wilaya_id via the daira."""
    code = int(commune_code) if commune_code else None
    if code is None:
        return None
    for c in communes_list():
        if _commune_code_key(c) == code:
            daira = dairas_data().get(str(c['daira_id']))
            if daira:
                return int(daira['wilaya_id'])
            return None
    return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def locale_label(entry: dict[str, Any], locale: str) -> str:
    """Return locale-appropriate label for a simple lookup entry."""
    if locale == 'ar':
        return entry.get('pk', '') or ''
    return entry.get(f'label_{locale}', None) or entry.get('pk', '') or ''


def clear_cache() -> None:
    """Clear the lookup data cache."""
    _cache.clear()


# ---------------------------------------------------------------------------
# UI widget text (from widgets.json)
# ---------------------------------------------------------------------------

_str_cache: dict[str, dict[str, str]] = {}


def _get_string(source: str, locale: str) -> str:
    """Look up a source string in strings.json for the given locale."""
    if 'strings' not in _str_cache:
        path = os.path.join(_DATA_DIR, 'strings.json')
        with open(path, encoding='utf-8') as f:
            _str_cache['strings'] = json.load(f)
    data = _str_cache['strings'].get(source)
    if isinstance(data, dict):
        return data.get(locale, data.get('ar', source))
    return source


_widgets_data: dict[str, dict[str, str]] | None = None


def _load_widgets() -> dict[str, dict[str, str]]:
    """Load and cache widgets.json data."""
    global _widgets_data  # pylint: disable=global-statement
    if _widgets_data is None:
        path = os.path.join(_DATA_DIR, 'widgets.json')
        with open(path, encoding='utf-8') as f:
            _widgets_data = json.load(f)
    return _widgets_data


def widget_text(object_name: str, locale: str) -> str:
    """Return localized text for a widget by objectName."""
    data = _load_widgets().get(object_name)
    if data:
        return data.get(locale, data.get('ar', ''))
    return ''


def get_string(source: str, locale: str) -> str:
    """Return localized string for a source text from strings.json."""
    return _get_string(source, locale)


def clear_i18n_cache() -> None:
    """Clear the cached strings.json data."""
    _str_cache.pop('strings', None)


def _src_text(w, attr='text'):
    """Get or cache the original Arabic source text on a widget.
    Uses attr-specific cache attribute (_rna_src, _rna_src_tip, _rna_src_win)
    to avoid clashes when a widget appears in multiple findChildren passes."""
    cache_attr = {
        'text': '_rna_src', 'title': '_rna_src',
        'placeholder': '_rna_src', 'tooltip': '_rna_src_tip',
        'windowtitle': '_rna_src_win',
    }.get(attr, '_rna_src')
    cached = getattr(w, cache_attr, None)
    if cached is not None:
        return cached
    getters = {
        'text': getattr(w, 'text', lambda: ''),
        'title': getattr(w, 'title', lambda: ''),
        'placeholder': getattr(w, 'placeholderText', lambda: ''),
        'tooltip': getattr(w, 'toolTip', lambda: ''),
        'windowtitle': getattr(w, 'windowTitle', lambda: ''),
    }
    src = getters.get(attr, lambda: '')()
    if src:
        setattr(w, cache_attr, src)
    return src


def _translate_text(src: str, locale: str) -> str:
    """Translate a source string via _get_string, or return empty."""
    if not src:
        return ''
    translated = _get_string(src, locale)
    return translated if translated != src else ''


def _set_from_lookup(w, locale, widgets_data, *, attr='text', setter='setText',
                     src_attr=None) -> None:
    """Set a widget attribute from widgets_data or _src_text fallback."""
    name = w.objectName()
    if name in widgets_data:
        value = widgets_data[name].get(
            locale, widgets_data[name].get('ar', ''),
        )
        getattr(w, setter)(value)
        return
    src = _src_text(w, src_attr or attr)
    if src:
        translated = _translate_text(src, locale)
        if translated:
            getattr(w, setter)(translated)


def _translate_labels(dialog, locale, widgets_data) -> None:
    """Translate QLabel, QPushButton, QCheckBox text."""
    for w in dialog.findChildren((QLabel, QPushButton, QCheckBox)):
        _set_from_lookup(w, locale, widgets_data)


def _translate_groupbox(dialog, locale, widgets_data) -> None:
    """Translate QGroupBox titles."""
    for w in dialog.findChildren(QGroupBox):
        _set_from_lookup(w, locale, widgets_data,
                         attr='title', setter='setTitle')


def _translate_placeholder(dialog, locale) -> None:
    """Translate QLineEdit placeholder text."""
    for w in dialog.findChildren(QLineEdit):
        src = _src_text(w, 'placeholder')
        if src:
            translated = _translate_text(src, locale)
            if translated:
                w.setPlaceholderText(translated)


def _translate_tabs(dialog, locale) -> None:
    """Translate QTabWidget tab texts using cached source strings."""
    for w in dialog.findChildren(QTabWidget):
        if not hasattr(w, '_rna_tab_src'):
            w._rna_tab_src = [w.tabText(i) for i in range(w.count())]  # pylint: disable=protected-access
        for i in range(w.count()):
            src = w._rna_tab_src[i]  # pylint: disable=protected-access
            if src:
                w.setTabText(i, _get_string(src, locale))


def _translate_window_title(dialog, locale) -> None:
    """Translate dialog window title."""
    if not hasattr(dialog, 'windowTitle'):
        return
    src = _src_text(dialog, 'windowtitle')
    if src:
        translated = _translate_text(src, locale)
        if translated:
            dialog.setWindowTitle(translated)


def _translate_tooltips(dialog, locale, widgets_data) -> None:
    """Translate QWidget tooltips."""
    for w in dialog.findChildren(QWidget):
        name = w.objectName()
        tip = _src_text(w, 'tooltip')
        if not tip:
            continue
        if name in widgets_data:
            w.setToolTip(widgets_data[name].get(
                locale, widgets_data[name].get('ar', ''),
            ))
        else:
            translated = _translate_text(tip, locale)
            if translated:
                w.setToolTip(translated)


def apply_widget_texts(dialog, locale: str) -> None:
    """Set text on all children of dialog using widgets.json data."""
    widgets_data = _load_widgets()
    _translate_labels(dialog, locale, widgets_data)
    _translate_groupbox(dialog, locale, widgets_data)
    _translate_placeholder(dialog, locale)
    _translate_tabs(dialog, locale)
    _translate_window_title(dialog, locale)
    _translate_tooltips(dialog, locale, widgets_data)
