"""ComboBox population functions for reference data."""
import logging

from qgis.PyQt.QtWidgets import QCompleter, QComboBox
from qgis.PyQt.QtCore import QSettings

from ..models import (
    Localite, get_session
)
from ..scripts.lookup_data import (
    road_types, zone_types, subdivision_types, mounting_statuses,
    numbering_states, org_categories, org_types_for_category,
    org_subcategories, activity_categories, activity_types_for_category,
    activity_subcategories, locale_label,
)
from ..db.operations import qgis_config
from ..constants import (
    NO_ACTIVITY, SETTINGS_ORG, SETTINGS_APP, SETTINGS_KEY_LOCALE,
    current_locale,
)
from ..i18n import tr as _i18n_tr

logger = logging.getLogger(__name__)


def _locale() -> str:
    return current_locale()


def fill_wilayas_list(combobox: QComboBox) -> None:
    """Populate a combobox with distinct wilaya names from the database."""
    loc = _locale()
    combobox.clear()
    session = get_session()
    results = (
        session.query(Localite.wilaya, Localite.codeWilaya)
        .distinct().order_by(Localite.codeWilaya).all()
    )
    for result in results:
        combobox.addItem(_i18n_tr(result.wilaya, loc), result.codeWilaya)
    session.close()
    combobox.setCurrentIndex(0)
    combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_paper(combobox: QComboBox) -> None:
    """Populate a combobox with paper size options (A3, A0)."""
    loc = _locale()
    combobox.clear()
    combobox.addItem(_i18n_tr("\u202Bورقة A3 للعمل الميداني\u202C", loc), 'A3')
    combobox.addItem(_i18n_tr("\u202Bورقة A0 للإدارة\u202C", loc), 'A0')


def _fill_from_json(combobox, data, loc):
    """Fill a combobox from a list of {pk, label_fr, label_en} dicts."""
    combobox.clear()
    for entry in data:
        display = locale_label(entry, loc)
        combobox.addItem(display, entry.get('pk', ''))
    combobox.setCurrentIndex(0)
    combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_subdivision_type(combobox: QComboBox) -> None:
    """Populate a combobox with subdivision types from JSON."""
    _fill_from_json(combobox, subdivision_types(), _locale())


def fill_type_zone(combobox: QComboBox) -> None:
    """Populate a combobox with zone types from JSON."""
    _fill_from_json(combobox, zone_types(), _locale())


def fill_commune_of_wilaya(combobox: QComboBox, code_w: int) -> None:
    """Populate a combobox with communes for a given wilaya code."""
    loc = _locale()
    combobox.clear()
    session = get_session()
    results = (
        session.query(Localite)
        .filter(Localite.codeWilaya == code_w).all()
    )
    for result in results:
        if loc == 'ar':
            name = result.communeAr
        else:
            name = getattr(result, f'commune_{loc}', None)
            if not name:
                name = _i18n_tr(result.communeAr, loc)
        combobox.addItem(name, result.pk_uid)
    session.close()
    combobox.setCurrentIndex(0)
    combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_road_reference(combobox) -> None:
    """Populate a combobox with road reference types from config."""
    loc = _locale()
    data_list = qgis_config().get('refs')
    combobox.clear()
    for dl in data_list:
        source = dl.get('label')
        combobox.addItem(_i18n_tr(source, loc), source)
    combobox.setCurrentIndex(0)


def fill_panel_reference(combobox) -> None:
    """Populate a combobox with panel reference types from config."""
    loc = _locale()
    data_list = qgis_config().get('refs2')
    combobox.clear()
    for dl in data_list:
        source = dl.get('label')
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
    combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_activity_category(combobox) -> None:
    """Populate a combobox with distinct activity categories from JSON."""
    loc = _locale()
    combobox.clear()
    combobox.addItem(_i18n_tr(NO_ACTIVITY, loc), NO_ACTIVITY)
    for display, value in activity_categories(loc):
        combobox.addItem(display, value)
    combobox.setCurrentIndex(0)
    combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_org_subcategory(combobox, cat) -> None:
    """Populate a combobox with distinct organization subcategories."""
    combobox.clear()
    for sub in org_subcategories(cat):
        combobox.addItem(sub, sub)
    combobox.setCurrentIndex(0)
    combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_activity_subcategory(combobox, cat) -> None:
    """Populate a combobox with distinct activity subcategories."""
    combobox.clear()
    for sub in activity_subcategories(cat):
        combobox.addItem(sub, sub)
    combobox.setCurrentIndex(0)
    combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_type_act(combobox, cat) -> None:
    """Populate a combobox with activity types for a given category."""
    loc = _locale()
    combobox.clear()
    if cat != NO_ACTIVITY:
        for display, value in activity_types_for_category(cat, loc):
            combobox.addItem(display, value)
    else:
        combobox.addItem(_i18n_tr(NO_ACTIVITY, loc), NO_ACTIVITY)


def fill_type_org(combobox, cat) -> None:
    """Populate a combobox with organization types for a given category."""
    loc = _locale()
    combobox.clear()
    for display, value in org_types_for_category(cat, loc):
        combobox.addItem(display, value)
    combobox.setCurrentIndex(0)
    combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
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
