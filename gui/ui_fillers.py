"""ComboBox population functions for reference data."""

import json
import logging

from qgis.PyQt.QtWidgets import QComboBox, QCompleter

from ..app.shared.constants import (
    LAYER_ROADS,
    LAYER_SUBDIVISIONS,
    LAYER_ZONES,
    TEMPLATE_DATA_DIR,
)
from ..app.users.repository import qgis_config
from ..constants import (
    LOCALE_AR,
    NO_ACTIVITY,
    current_locale,
)
from ..i18n import tr as _i18n_tr
from ..scripts.lookup_data import (
    activity_categories,
    activity_types,
    activity_types_for_category,
    clear_cache,
    communes_list,
    dairas_data,
    locale_label,
    mounting_statuses,
    numbering_states,
    org_categories,
    org_types_for_category,
    road_types,
    subdivision_types,
    wilayas_data,
    zone_types,
)

logger = logging.getLogger(__name__)


def _setup_combo(combobox: QComboBox) -> None:
    """Configure a combobox with popup completion and no-insert policy."""
    completer = combobox.completer()
    if completer is not None:
        completer.setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def _locale() -> str:
    """Return the current UI locale code."""
    return current_locale()


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
    _setup_combo(combobox)


def fill_paper(combobox: QComboBox) -> None:
    """Populate a combobox with paper size options (A3, A0)."""
    loc = _locale()
    combobox.clear()
    combobox.addItem(_i18n_tr('A3 Sheet for Field Work', loc), 'A3')
    combobox.addItem(_i18n_tr('A0 Sheet for Administration', loc), 'A0')


def _fill_from_json(combobox: QComboBox, data: list[dict], loc: str) -> None:
    """Fill a combobox from a list of {pk, label_fr, label_en} dicts."""
    combobox.clear()
    if not isinstance(data, list):
        logger.warning('Expected a list for combo data, got %s', type(data).__name__)
        return
    for entry in data:
        display = locale_label(entry, loc)
        combobox.addItem(display, entry.get('pk', ''))
    combobox.setCurrentIndex(0)
    _setup_combo(combobox)


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
            if loc == LOCALE_AR:
                name = entry.get('commune_ar', '')
            else:
                name = entry.get(f'commune_{loc}', '')
                if not name:
                    name = entry.get('commune_fr', '')
                if not name:
                    name = _i18n_tr(str(entry.get('commune_ar', '')), loc)
            combobox.addItem(name, str(entry.get('commune_code', '') or ''))
    combobox.setCurrentIndex(0)
    _setup_combo(combobox)


def _fill_reference(combobox: QComboBox, config_key: str) -> None:
    """Populate a combobox with reference types from *config_key* in qgis_config."""
    loc = _locale()
    data_list = qgis_config().get(config_key) or []
    combobox.clear()
    for layer_cfg in data_list:
        source = layer_cfg.get('label')
        combobox.addItem(_i18n_tr(source, loc), source)
    combobox.setCurrentIndex(0)


def fill_road_reference(combobox: QComboBox) -> None:
    """Populate a combobox with road reference types from config."""
    _fill_reference(combobox, 'refs')


def fill_panel_reference(combobox: QComboBox) -> None:
    """Populate a combobox with panel reference types from config."""
    _fill_reference(combobox, 'refs2')


def fill_org_category(combobox: QComboBox) -> None:
    """Populate a combobox with distinct organization categories from JSON."""
    loc = _locale()
    combobox.clear()
    for display, value in org_categories(loc):
        combobox.addItem(display, value)
    combobox.setCurrentIndex(0)
    _setup_combo(combobox)


def fill_activity_category(combobox: QComboBox) -> None:
    """Populate a combobox with distinct activity categories from JSON."""
    loc = _locale()
    combobox.clear()
    combobox.addItem(_i18n_tr(NO_ACTIVITY, loc), NO_ACTIVITY)
    for display, value in activity_categories(loc):
        combobox.addItem(display, value)
    combobox.setCurrentIndex(0)
    _setup_combo(combobox)


def fill_activity_type(combobox: QComboBox, cat: str) -> None:
    """Populate a combobox with activity types for a given category."""
    loc = _locale()
    combobox.clear()
    if cat != NO_ACTIVITY:
        for display, value in activity_types_for_category(cat, loc):
            combobox.addItem(display, value)
    else:
        combobox.addItem(_i18n_tr(NO_ACTIVITY, loc), NO_ACTIVITY)


def fill_org_type(combobox: QComboBox, cat: str) -> None:
    """Populate a combobox with organization types for a given category."""
    loc = _locale()
    combobox.clear()
    for display, value in org_types_for_category(cat, loc):
        combobox.addItem(display, value)
    combobox.setCurrentIndex(0)
    _setup_combo(combobox)


def fill_road_type(combobox: QComboBox) -> None:
    """Populate a combobox with road types from JSON."""
    _fill_from_json(combobox, road_types(), _locale())


def fill_mounting_status(combobox: QComboBox) -> None:
    """Populate a combobox with mounting statuses from JSON."""
    _fill_from_json(combobox, mounting_statuses(), _locale())


def fill_numbering_state(combobox: QComboBox) -> None:
    """Populate a combobox with numbering states from JSON."""
    _fill_from_json(combobox, numbering_states(), _locale())


ACTIVITY_KEY = 'Activities'

_MAIN_TYPE_MAP = {
    LAYER_ZONES: zone_types,
    LAYER_ROADS: road_types,
    LAYER_SUBDIVISIONS: subdivision_types,
    ACTIVITY_KEY: activity_types,
}


def fill_feature_combo(combobox: QComboBox) -> None:
    """Populate the main type combo with layer names."""
    loc = _locale()
    combobox.clear()
    for key in _MAIN_TYPE_MAP:
        combobox.addItem(_i18n_tr(key, loc), key)
    combobox.setCurrentIndex(0)


def fill_subtype_combo(combobox: QComboBox, main_type: str) -> None:
    """Populate subtype combo with existing types from JSON for *main_type*."""
    if main_type == ACTIVITY_KEY:
        loc = _locale()
        combobox.clear()
        for display, value in activity_categories(loc):
            combobox.addItem(display, value)
        combobox.setCurrentIndex(0)
        _setup_combo(combobox)
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

    if main_type == ACTIVITY_KEY and not category:
        return False

    if main_type == ACTIVITY_KEY:
        filepath = TEMPLATE_DATA_DIR / 'activity.json'
        entry = {'sector': category, 'type': type_name}
    else:
        _json_files = {
            LAYER_ZONES: 'zone_type.json',
            LAYER_ROADS: 'type_road.json',
            LAYER_SUBDIVISIONS: 'type_cite.json',
        }
        filename = _json_files.get(main_type)
        if not filename:
            return False
        filepath = TEMPLATE_DATA_DIR / filename
        entry = {'pk': type_name}

    try:
        with filepath.open(encoding='utf-8') as f:
            data = json.load(f)
        data.append(entry)
        with filepath.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except (OSError, json.JSONDecodeError):
        logger.exception('Failed to save new type to %s', filepath)
        return False
    else:
        clear_cache()
        return True
