"""Static lookup data loaded from JSON files at runtime."""

import json
import os
from typing import Any

_DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'template_data',
)

_cache: dict[str, Any] = {}


def _load(filename: str) -> Any:
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
    category: str,
    locale: str = 'ar',
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
                val = entry.get(f'cat_{locale}', '')
                if not val or val == category:
                    val = category
            else:
                val = category
            result.append((val, category))
    result.sort(key=lambda x: x[1])
    return result


def activity_types_for_category(
    cat: str,
    locale: str = 'ar',
) -> list[tuple[str, str]]:
    """Return activity types for a category -> (display, value)."""
    result: list[tuple[str, str]] = []
    for entry in activity_types():
        if entry.get('sector', '') == cat:
            type_val = entry.get('type', '')
            if type_val:
                if locale != 'ar':
                    display = entry.get(f'type_{locale}', '')
                    if not display or display == type_val:
                        display = type_val
                else:
                    display = type_val
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
        return entry.get('label_ar') or entry.get('pk', '') or ''
    return entry.get(f'label_{locale}', None) or entry.get('pk', '') or ''


def clear_cache() -> None:
    """Clear the lookup data cache."""
    _cache.clear()
