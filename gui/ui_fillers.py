"""ComboBox population functions for reference data."""
import logging

from qgis.PyQt.QtWidgets import QCompleter, QComboBox

from ..models import (
    Localite, SubdivisionType, ZoneType, RoadType, OrganizationType,
    ActivityType, MountingStatus, NumberingState, get_session
)
from ..db.operations import qgis_config
from ..constants import NO_ACTIVITY

logger = logging.getLogger(__name__)


def fill_wilayas_list(combobox: QComboBox) -> None:
    """Populate a combobox with distinct wilaya names from the database."""
    combobox.clear()
    session = get_session()
    results = (
        session.query(Localite.wilaya, Localite.codeWilaya)
        .distinct().order_by(Localite.codeWilaya).all()
    )
    for result in results:
        combobox.addItem(result.wilaya, result.codeWilaya)
    session.close()
    combobox.setCurrentIndex(0)
    combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_paper(combobox: QComboBox) -> None:
    """Populate a combobox with paper size options (A3, A0)."""
    combobox.clear()
    combobox.addItem("\u202Bورقة A3 للعمل الميداني\u202C", 'A3')
    combobox.addItem("\u202Bورقة A0 للإدارة\u202C", 'A0')


def fill_subdivision_type(combobox: QComboBox) -> None:
    """Populate a combobox with subdivision types from the database."""
    combobox.clear()
    session = get_session()
    results = session.query(SubdivisionType).all()
    for result in results:
        combobox.addItem(result.pk, result.pk)
    session.close()
    combobox.setCurrentIndex(0)
    combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_type_zone(combobox: QComboBox) -> None:
    """Populate a combobox with zone types from the database."""
    combobox.clear()
    session = get_session()
    results = session.query(ZoneType).all()
    for result in results:
        combobox.addItem(result.pk, result.pk)
    session.close()
    combobox.setCurrentIndex(0)
    combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_commune_of_wilaya(combobox: QComboBox, code_w: int) -> None:
    """Populate a combobox with communes for a given wilaya code."""
    combobox.clear()
    session = get_session()
    results = (
        session.query(Localite)
        .filter(Localite.codeWilaya == code_w).all()
    )
    for result in results:
        combobox.addItem(result.communeAr, result.pk_uid)
    session.close()
    combobox.setCurrentIndex(0)
    combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_road_reference(combobox) -> None:
    """Populate a combobox with road reference types from config."""
    data_list = qgis_config().get('refs')
    for dl in data_list:
        combobox.addItem(dl.get('label'))
    combobox.setCurrentIndex(0)


def fill_panel_reference(combobox) -> None:
    """Populate a combobox with panel reference types from config."""
    data_list = qgis_config().get('refs2')
    for dl in data_list:
        combobox.addItem(dl.get('label'))
    combobox.setCurrentIndex(0)


def fill_org_category(combobox, cat=None) -> None:
    """Populate a combobox with distinct organization categories."""
    cat = cat or []
    combobox.clear()
    session = get_session()
    results = (
        session.query(OrganizationType.cat)
        .distinct().order_by(OrganizationType.cat).all()
    )
    for result in results:
        combobox.addItem(result.cat, result.cat)
        cat.append(result.cat)
    session.close()

    combobox.setCurrentIndex(0)
    combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_activity_category(combobox) -> None:
    """Populate a combobox with distinct activity categories."""
    combobox.clear()
    session = get_session()
    combobox.addItem(NO_ACTIVITY, NO_ACTIVITY)
    results = (
        session.query(ActivityType.cat)
        .distinct().order_by(ActivityType.cat).all()
    )

    for result in results:
        combobox.addItem(result.cat, result.cat)

    session.close()

    combobox.setCurrentIndex(0)
    combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_type_act(combobox, cat) -> None:
    """Populate a combobox with activity types for a given category."""
    combobox.clear()
    if cat != NO_ACTIVITY:
        session = get_session()
        results = (
            session.query(ActivityType)
            .filter(ActivityType.cat == cat).all()
        )
        for result in results:
            combobox.addItem(result.type, result.type)
        session.close()
    else:
        combobox.addItem(NO_ACTIVITY, NO_ACTIVITY)


def fill_type_org(combobox, cat) -> None:
    """Populate a combobox with organization types for a given category."""
    combobox.clear()
    session = get_session()
    results = (
        session.query(OrganizationType)
        .filter(OrganizationType.cat == cat).all()
    )

    for result in results:
        combobox.addItem(result.pk, result.pk)

    session.close()

    combobox.setCurrentIndex(0)
    combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_road_type(combobox) -> None:
    """Populate a combobox with road types from the database."""
    combobox.clear()
    session = get_session()
    results = session.query(RoadType).all()

    for result in results:
        combobox.addItem(result.pk, result.pk)

    session.close()
    combobox.setCurrentIndex(0)

    combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_mounting_status(combobox) -> None:
    """Populate a combobox with mounting statuses from the database."""
    combobox.clear()
    session = get_session()
    results = session.query(MountingStatus).all()

    for result in results:
        combobox.addItem(result.pk, result.pk)

    session.close()
    combobox.setCurrentIndex(0)

    combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)


def fill_numbering_state(combobox) -> None:
    """Populate a combobox with numbering states from the database."""
    combobox.clear()
    session = get_session()
    results = session.query(NumberingState).all()

    for result in results:
        combobox.addItem(result.pk, result.pk)

    session.close()
    combobox.setCurrentIndex(0)

    combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
    combobox.setInsertPolicy(QComboBox.NoInsert)
