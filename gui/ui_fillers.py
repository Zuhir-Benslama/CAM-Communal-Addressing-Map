"""ComboBox population functions for reference data."""
# mypy: disable-error-code="assignment,union-attr"
import logging

from qgis.PyQt.QtWidgets import QCompleter, QComboBox

from ..app.orders.models import Localite
from ..app.core.database import get_session
from ..scripts.lookup_data import (
    road_types, zone_types, subdivision_types, mounting_statuses,
    numbering_states, org_categories, org_types_for_category,
    org_subcategories, activity_categories, activity_types,
    activity_types_for_category, activity_subcategories, locale_label,
)
from ..app.users.repository import qgis_config
from ..constants import (
    NO_ACTIVITY,
    current_locale,
)
from ..i18n import tr as _i18n_tr
from ..app.shared.constants import LAYER_ZONES, LAYER_ROADS, LAYER_SUBDIVISIONS

logger = logging.getLogger(__name__)


def _locale() -> str:
    """Return the current UI locale code."""
    return current_locale()


def fill_wilayas_list(combobox: QComboBox) -> None:
    """Populate a combobox with distinct wilaya names from the database."""
    loc = _locale()
    combobox.clear()
    session = get_session()
    results = (
        session.query(Localite.wilaya, Localite.wilaya_code)
        .distinct().order_by(Localite.wilaya_code).all()
    )
    for result in results:
        combobox.addItem(_i18n_tr(result.wilaya, loc), result.wilaya_code)
    session.close()
    combobox.setCurrentIndex(0)
    completer = combobox.completer()
    if completer is not None:
        completer.setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_paper(combobox: QComboBox) -> None:
    """Populate a combobox with paper size options (A3, A0)."""
    loc = _locale()
    combobox.clear()
    combobox.addItem(_i18n_tr("A3 Sheet for Field Work", loc), 'A3')
    combobox.addItem(_i18n_tr("A0 Sheet for Administration", loc), 'A0')


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
    session = get_session()
    results = (
        session.query(Localite)
        .filter(Localite.wilaya_code == code_w).all()
    )
    for result in results:
        if loc == 'ar':
            name = result.commune_ar
        else:
            name = getattr(result, f'commune_{loc}', None)
            if not name:
                name = _i18n_tr(str(result.commune_ar), loc)
        combobox.addItem(name, result.id)
    session.close()
    combobox.setCurrentIndex(0)
    completer = combobox.completer()
    if completer is not None:
        completer.setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_road_reference(combobox) -> None:
    """Populate a combobox with road reference types from config."""
    loc = _locale()
    data_list = qgis_config().get('refs')
    combobox.clear()
    for layer_cfg in data_list:
        source = layer_cfg.get('label')
        combobox.addItem(_i18n_tr(source, loc), source)
    combobox.setCurrentIndex(0)


def fill_panel_reference(combobox) -> None:
    """Populate a combobox with panel reference types from config."""
    loc = _locale()
    data_list = qgis_config().get('refs2')
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


_ACTIVITY_KEY = "Activities"

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
    import json
    import os

    type_name = type_name.strip()
    if not type_name or not main_type:
        return False

    _DATA_DIR = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'template_data',
    )

    if main_type == _ACTIVITY_KEY:
        if not category:
            return False
        filepath = os.path.join(_DATA_DIR, 'activity.json')
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data.append({"القطاع": category, "النوع": type_name})
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            from ..scripts.lookup_data import clear_cache
            clear_cache()
            return True
        except (OSError, json.JSONDecodeError):
            logger.exception("Failed to save new activity type to %s", filepath)
            return False

    _JSON_FILES = {
        LAYER_ZONES: 'zone_type.json',
        LAYER_ROADS: 'type_road.json',
        LAYER_SUBDIVISIONS: 'type_cite.json',
    }

    filename = _JSON_FILES.get(main_type)
    if not filename:
        return False

    filepath = os.path.join(_DATA_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data.append({"pk": type_name})
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        from ..scripts.lookup_data import clear_cache
        clear_cache()
        return True
    except (OSError, json.JSONDecodeError):
        logger.exception("Failed to save new type to %s", filepath)
        return False
