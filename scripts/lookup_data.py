"""Static lookup data loaded from JSON files at runtime."""

import json
import os
from typing import Any, Optional

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'template_data')

_cache: dict[str, list[dict[str, Any]]] = {}


def _load(filename: str) -> list[dict[str, Any]]:
    if filename not in _cache:
        path = os.path.join(_DATA_DIR, filename)
        with open(path, 'r', encoding='utf-8') as f:
            _cache[filename] = json.load(f)
    return _cache[filename]


# ---------------------------------------------------------------------------
# Simple lookups: {pk, label_fr?, label_en?}
# ---------------------------------------------------------------------------

def road_types() -> list[dict[str, Any]]:
    return _load('type_voie.json')

def zone_types() -> list[dict[str, Any]]:
    return _load('type_zone.json')

def subdivision_types() -> list[dict[str, Any]]:
    return _load('type_cite.json')

def mounting_statuses() -> list[dict[str, Any]]:
    return _load('situation_Montage.json')

def numbering_states() -> list[dict[str, Any]]:
    return _load('Etat_Numerotation.json')


# ---------------------------------------------------------------------------
# Organization types: {TypeAr, TypeFr?, categorie, categorie_fr?, categorie_en?, ...}
#   - TypeAr = Arabic PK
#   - TypeFr -> pk_fr equivalent
#   - categorie = category (Arabic)
# ---------------------------------------------------------------------------

def organization_types() -> list[dict[str, Any]]:
    return _load('type_organisme.json')

def org_categories(locale: str = 'ar') -> list[tuple[str, str]]:
    """Return distinct organization categories -> (display, value)."""
    seen: set[str] = set()
    result: list[tuple[str, str]] = []
    for entry in organization_types():
        cat = entry.get('categorie', '')
        if cat and cat not in seen:
            seen.add(cat)
            if locale != 'ar':
                val = entry.get(f'categorie_{locale}', '') or cat
            else:
                val = cat
            result.append((val, cat))
    result.sort(key=lambda x: x[1])
    return result

def org_types_for_category(cat: str, locale: str = 'ar') -> list[tuple[str, str]]:
    """Return organization types for a category -> (display, pk)."""
    result: list[tuple[str, str]] = []
    for entry in organization_types():
        if entry.get('categorie', '') == cat:
            pk = entry.get('TypeAr', '')
            if locale != 'ar':
                display = entry.get('TypeFr', '') or pk
            else:
                display = pk
            if pk:
                result.append((display, pk))
    return result

def org_subcategories(cat: str) -> list[str]:
    """Return distinct subcategories for an org category."""
    seen: set[str] = set()
    result: list[str] = []
    for entry in organization_types():
        if entry.get('categorie', '') == cat:
            sub = entry.get('subcat', '')
            if sub and sub not in seen:
                seen.add(sub)
                result.append(sub)
    return result


# ---------------------------------------------------------------------------
# Activity types: {القطاع, النوع, cat_fr?, cat_en?, type_fr?, type_en?}
# ---------------------------------------------------------------------------

def activity_types() -> list[dict[str, Any]]:
    return _load('activity.json')

def activity_categories(locale: str = 'ar') -> list[tuple[str, str]]:
    """Return distinct activity categories -> (display, value)."""
    seen: set[str] = set()
    result: list[tuple[str, str]] = []
    for entry in activity_types():
        cat = entry.get('القطاع', '')
        if cat and cat not in seen:
            seen.add(cat)
            if locale != 'ar':
                val = entry.get(f'cat_{locale}', '') or cat
            else:
                val = cat
            result.append((val, cat))
    result.sort(key=lambda x: x[1])
    return result

def activity_types_for_category(cat: str, locale: str = 'ar') -> list[tuple[str, str]]:
    """Return activity types for a category -> (display, value)."""
    result: list[tuple[str, str]] = []
    for entry in activity_types():
        if entry.get('القطاع', '') == cat:
            typ = entry.get('النوع', '')
            if locale != 'ar':
                display = entry.get(f'type_{locale}', '') or typ
            else:
                display = typ
            if typ:
                result.append((display, typ))
    return result

def activity_subcategories(cat: str) -> list[str]:
    """Return distinct subcategories for an activity category."""
    seen: set[str] = set()
    result: list[str] = []
    for entry in activity_types():
        if entry.get('القطاع', '') == cat:
            sub = entry.get('subcat', '')
            if sub and sub not in seen:
                seen.add(sub)
                result.append(sub)
    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def locale_label(entry: dict[str, Any], locale: str) -> str:
    """Return locale-appropriate label for a simple lookup entry."""
    if locale == 'ar':
        return entry.get('pk', '') or ''
    return entry.get(f'label_{locale}', None) or entry.get('pk', '') or ''


def clear_cache() -> None:
    _cache.clear()


# ---------------------------------------------------------------------------
# UI widget text (from widgets.json)
# ---------------------------------------------------------------------------

_str_cache: dict[str, dict[str, str]] = {}

def _get_string(source: str, locale: str) -> str:
    """Look up a source string in strings.json for the given locale."""
    if 'strings' not in _str_cache:
        path = os.path.join(_DATA_DIR, 'strings.json')
        with open(path, 'r', encoding='utf-8') as f:
            _str_cache['strings'] = json.load(f)
    data = _str_cache['strings'].get(source)
    if data:
        return data.get(locale, data.get('ar', source))
    return source


_widgets_data: dict[str, dict[str, str]] | None = None

def _load_widgets() -> dict[str, dict[str, str]]:
    global _widgets_data
    if _widgets_data is None:
        path = os.path.join(_DATA_DIR, 'widgets.json')
        with open(path, 'r', encoding='utf-8') as f:
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


def apply_widget_texts(dialog, locale: str) -> None:
    """Set text on all children of dialog using widgets.json data."""
    from qgis.PyQt.QtWidgets import QLabel, QPushButton, QCheckBox, QGroupBox, QTabWidget
    from qgis.PyQt.QtWidgets import QWidget
    widgets_data = _load_widgets()
    for w in dialog.findChildren((QLabel, QPushButton, QCheckBox)):
        name = w.objectName()
        if name in widgets_data:
            w.setText(widgets_data[name].get(locale, widgets_data[name].get('ar', '')))
    for w in dialog.findChildren(QGroupBox):
        name = w.objectName()
        if name in widgets_data:
            w.setTitle(widgets_data[name].get(locale, widgets_data[name].get('ar', '')))
    for w in dialog.findChildren(QTabWidget):
        if not hasattr(w, '_rna_tab_src'):
            w._rna_tab_src = [w.tabText(i) for i in range(w.count())]
        for i in range(w.count()):
            src = w._rna_tab_src[i]
            if src:
                w.setTabText(i, _get_string(src, locale))
    for w in dialog.findChildren(QWidget):
        name = w.objectName()
        tip = w.toolTip()
        if not tip:
            continue
        if name in widgets_data:
            w.setToolTip(widgets_data[name].get(locale, widgets_data[name].get('ar', '')))
        else:
            translated = _get_string(tip, locale)
            if translated != tip:
                w.setToolTip(translated)
