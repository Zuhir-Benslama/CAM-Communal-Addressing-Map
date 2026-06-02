"""ComboBox population functions for reference data."""

import json
import logging
import os

from qgis.PyQt.QtWidgets import QComboBox, QCompleter

from ..app.shared.constants import LAYER_ROADS, LAYER_SUBDIVISIONS, LAYER_ZONES
from ..app.users.repository import qgis_config
from ..constants import (
    NO_ACTIVITY,
    current_locale,
)
from ..i18n import tr as _i18n_tr
from ..scripts.lookup_data import (
    activity_categories,
    activity_subcategories,
    activity_types,
    activity_types_for_category,
    clear_cache,
    communes_list,
    dairas_data,
    locale_label,
    mounting_statuses,
    numbering_states,
    org_categories,
    org_subcategories,
    org_types_for_category,
    road_types,
    subdivision_types,
    wilayas_data,
    zone_types,
)

logger = logging.getLogger(__name__)


def _locale() -> str:
    """Return the current UI locale code."""
    return current_locale()


def _load_localites() -> list[dict]:
    """Load commune metadata from JSON file."""
    return communes_list()


def fill_wilayas_list(combobox: QComboBox) -> None:
    """Populate a combobox with distinct wilaya names from JSON."""
    loc = _locale()
    combobox.clear()
    wilayas: list[tuple[str, int]] = []
    for entry in wilayas_data().values():
        code = entry.get('wilaya_id')
        name = entry.get('wilaya_ar', '')
        if code is not None:
            wilayas.append((name, code))
    wilayas.sort(key=lambda x: x[1])
    for name, code in wilayas:
        combobox.addItem(_i18n_tr(name, loc), code)
    combobox.setCurrentIndex(0)
    completer = combobox.completer()
    if completer is not None:
        completer.setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_paper(combobox: QComboBox) -> None:
    """Populate a combobox with paper size options (A3, A0)."""
    loc = _locale()
    combobox.clear()
    combobox.addItem(_i18n_tr('A3 Sheet for Field Work', loc), 'A3')
    combobox.addItem(_i18n_tr('A0 Sheet for Administration', loc), 'A0')


def _fill_from_json(combobox, data, loc):
    """Fill a combobox from a list of {pk, label_fr, label_en} dicts."""
    combobox.clear()
    for entry in data:
        display = locale_label(entry, loc)
        combobox.addItem(display, entry.get('pk', ''))
    combobox.setCurrentIndex(0)
    completer = combobox.completer()
    if completer is not None:
        completer.setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_subdivision_type(combobox: QComboBox) -> None:
    """Populate a combobox with subdivision types from JSON."""
    _fill_from_json(combobox, subdivision_types(), _locale())


def fill_zone_type(combobox: QComboBox) -> None:
    """Populate a combobox with zone types from JSON."""
    _fill_from_json(combobox, zone_types(), _locale())


def fill_commune_of_wilaya(combobox: QComboBox, code_w: int) -> None:
    """Populate a combobox with communes for a given wilaya code."""
    loc = _locale()
    combobox.clear()
    dairas = dairas_data()
    daira_ids = {int(did) for did, d in dairas.items() if int(d['wilaya_id']) == code_w}
    for entry in communes_list():
        if entry.get('daira_id') in daira_ids:
            if loc == 'ar':
                name = entry.get('commune_ar', '')
            else:
                name = entry.get(f'commune_{loc}', '')
                if not name:
                    name = _i18n_tr(str(entry.get('commune_ar', '')), loc)
            combobox.addItem(name, entry.get('commune_code', ''))
    combobox.setCurrentIndex(0)
    completer = combobox.completer()
    if completer is not None:
        completer.setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_road_reference(combobox) -> None:
    """Populate a combobox with road reference types from config."""
    loc = _locale()
    data_list = qgis_config().get('refs') or []
    combobox.clear()
    for layer_cfg in data_list:
        source = layer_cfg.get('label')
        combobox.addItem(_i18n_tr(source, loc), source)
    combobox.setCurrentIndex(0)


def fill_panel_reference(combobox) -> None:
    """Populate a combobox with panel reference types from config."""
    loc = _locale()
    data_list = qgis_config().get('refs2') or []
    combobox.clear()
    for layer_cfg in data_list:
        source = layer_cfg.get('label')
        combobox.addItem(_i18n_tr(source, loc), source)
    combobox.setCurrentIndex(0)


def fill_org_category(combobox, cat=None) -> None:
    """Populate a combobox with distinct organization categories from JSON."""
    loc = _locale()
    cat = cat or []
    combobox.clear()
    for display, value in org_categories(loc):
        combobox.addItem(display, value)
        cat.append(value)
    combobox.setCurrentIndex(0)
    completer = combobox.completer()
    if completer is not None:
        completer.setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_activity_category(combobox) -> None:
    """Populate a combobox with distinct activity categories from JSON."""
    loc = _locale()
    combobox.clear()
    combobox.addItem(_i18n_tr(NO_ACTIVITY, loc), NO_ACTIVITY)
    for display, value in activity_categories(loc):
        combobox.addItem(display, value)
    combobox.setCurrentIndex(0)
    completer = combobox.completer()
    if completer is not None:
        completer.setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_org_subcategory(combobox, cat) -> None:
    """Populate a combobox with distinct organization subcategories."""
    combobox.clear()
    for sub in org_subcategories(cat):
        combobox.addItem(sub, sub)
    combobox.setCurrentIndex(0)
    completer = combobox.completer()
    if completer is not None:
        completer.setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_activity_subcategory(combobox, cat) -> None:
    """Populate a combobox with distinct activity subcategories."""
    combobox.clear()
    for sub in activity_subcategories(cat):
        combobox.addItem(sub, sub)
    combobox.setCurrentIndex(0)
    completer = combobox.completer()
    if completer is not None:
        completer.setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_activity_type(combobox, cat) -> None:
    """Populate a combobox with activity types for a given category."""
    loc = _locale()
    combobox.clear()
    if cat != NO_ACTIVITY:
        for display, value in activity_types_for_category(cat, loc):
            combobox.addItem(display, value)
    else:
        combobox.addItem(_i18n_tr(NO_ACTIVITY, loc), NO_ACTIVITY)


def fill_org_type(combobox, cat) -> None:
    """Populate a combobox with organization types for a given category."""
    loc = _locale()
    combobox.clear()
    for display, value in org_types_for_category(cat, loc):
        combobox.addItem(display, value)
    combobox.setCurrentIndex(0)
    completer = combobox.completer()
    if completer is not None:
        completer.setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_road_type(combobox) -> None:
    """Populate a combobox with road types from JSON."""
    _fill_from_json(combobox, road_types(), _locale())


def fill_mounting_status(combobox) -> None:
    """Populate a combobox with mounting statuses from JSON."""
    _fill_from_json(combobox, mounting_statuses(), _locale())


def fill_numbering_state(combobox) -> None:
    """Populate a combobox with numbering states from JSON."""
    _fill_from_json(combobox, numbering_states(), _locale())


_ACTIVITY_KEY = 'Activities'

_MAIN_TYPE_MAP = {
    LAYER_ZONES: zone_types,
    LAYER_ROADS: road_types,
    LAYER_SUBDIVISIONS: subdivision_types,
    _ACTIVITY_KEY: activity_types,
}


def fill_feature_combo(combobox: QComboBox) -> None:
    """Populate the main type combo with layer names."""
    combobox.clear()
    for key in _MAIN_TYPE_MAP:
        combobox.addItem(key, key)
    combobox.setCurrentIndex(0)


def fill_subtype_combo(combobox: QComboBox, main_type: str) -> None:
    """Populate subtype combo with existing types from JSON for *main_type*."""
    if main_type == _ACTIVITY_KEY:
        loc = _locale()
        combobox.clear()
        for display, value in activity_categories(loc):
            combobox.addItem(display, value)
        combobox.setCurrentIndex(0)
        completer = combobox.completer()
        if completer is not None:
            completer.setCompletionMode(QCompleter.PopupCompletion)
        combobox.setInsertPolicy(QComboBox.NoInsert)
        return
    loader = _MAIN_TYPE_MAP.get(main_type)
    if loader:
        _fill_from_json(combobox, loader(), _locale())
    else:
        combobox.clear()


def save_new_type(main_type: str, type_name: str, category: str = '') -> bool:
    """Append a new type entry to the appropriate JSON file.

    Returns True on success, False on failure.
    """
    type_name = type_name.strip()
    if not type_name or not main_type:
        return False

    _DATA_DIR = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'template_data',
    )

    if main_type == _ACTIVITY_KEY and not category:
        return False

    if main_type == _ACTIVITY_KEY:
        filepath = os.path.join(_DATA_DIR, 'activity.json')
        entry = {'sector': category, 'type': type_name}
    else:
        _JSON_FILES = {
            LAYER_ZONES: 'zone_type.json',
            LAYER_ROADS: 'type_road.json',
            LAYER_SUBDIVISIONS: 'type_cite.json',
        }
        filename = _JSON_FILES.get(main_type)
        if not filename:
            return False
        filepath = os.path.join(_DATA_DIR, filename)
        entry = {'pk': type_name}

    try:
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)
        data.append(entry)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        clear_cache()
        return True
    except (OSError, json.JSONDecodeError):
        logger.exception('Failed to save new type to %s', filepath)
        return False


# ---------------------------------------------------------------------------
# QML option getters (return [{text, value}, ...] lists)
# ---------------------------------------------------------------------------


def _json_to_options(data: list, loc: str) -> list[dict]:
    """Convert a list of JSON entries to QML-friendly option list."""
    return [
        {'text': locale_label(entry, loc), 'value': entry.get('pk', '')}
        for entry in data
    ]


def get_zone_type_options(loc: str) -> list[dict]:
    return _json_to_options(zone_types(), loc)


def get_road_type_options(loc: str) -> list[dict]:
    return _json_to_options(road_types(), loc)


def get_subdivision_type_options(loc: str) -> list[dict]:
    return _json_to_options(subdivision_types(), loc)


def get_numbering_state_options(loc: str) -> list[dict]:
    return _json_to_options(numbering_states(), loc)


def get_mounting_status_options(loc: str) -> list[dict]:
    return _json_to_options(mounting_statuses(), loc)


def get_org_category_options(loc: str) -> list[dict]:
    return [{'text': display, 'value': value} for display, value in org_categories(loc)]


def get_org_type_options(loc: str, cat_value: str = '') -> list[dict]:
    if not cat_value:
        return []
    return [
        {'text': display, 'value': value}
        for display, value in org_types_for_category(cat_value, loc)
    ]


def get_activity_category_options(loc: str) -> list[dict]:
    options = [{'text': _i18n_tr(NO_ACTIVITY, loc), 'value': NO_ACTIVITY}]
    options += [
        {'text': display, 'value': value} for display, value in activity_categories(loc)
    ]
    return options


def get_activity_type_options(loc: str, cat_value: str = '') -> list[dict]:
    if not cat_value or cat_value == NO_ACTIVITY:
        return [{'text': _i18n_tr(NO_ACTIVITY, loc), 'value': NO_ACTIVITY}]
    return [
        {'text': display, 'value': value}
        for display, value in activity_types_for_category(cat_value, loc)
    ]


def get_road_reference_options(loc: str) -> list[dict]:
    data_list = qgis_config().get('refs') or []
    return [
        {'text': _i18n_tr(cfg.get('label', ''), loc), 'value': cfg.get('label', '')}
        for cfg in data_list
    ]


def get_panel_reference_options(loc: str) -> list[dict]:
    data_list = qgis_config().get('refs2') or []
    return [
        {'text': _i18n_tr(cfg.get('label', ''), loc), 'value': cfg.get('label', '')}
        for cfg in data_list
    ]
