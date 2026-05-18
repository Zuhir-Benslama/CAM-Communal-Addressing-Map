"""Functions for writing/inserting data into the database."""
import logging

from geoalchemy2.elements import WKTElement

try:
    from qgis.PyQt.QtWidgets import QMessageBox
except ImportError:
    from unittest.mock import MagicMock
    QMessageBox = MagicMock()

try:
    from ..models import (
        RoadType, ZoneType, SubdivisionType, OrganizationType, ActivityType,
        Road, Organization, Subdivision, Zone, PanelSign,
        Numbering, get_session,
    )
    from ..constants import (
        SRID, DEFAULT_PANEL_DIM, NO_ACTIVITY,
        current_theme, get_theme_qss,
        SETTINGS_ORG, SETTINGS_APP, SETTINGS_KEY_LOCALE,
    )
    from ..i18n import tr as _i18n_tr
except ImportError:
    from models import (
        RoadType, ZoneType, SubdivisionType, OrganizationType, ActivityType,
        Road, Organization, Subdivision, Zone, PanelSign,
        Numbering, get_session,
    )
    from constants import (
        SRID, DEFAULT_PANEL_DIM, NO_ACTIVITY,
        current_theme, get_theme_qss,
    )

logger = logging.getLogger(__name__)


def _msg_locale() -> str:
    try:
        from qgis.PyQt.QtCore import QSettings
        s = QSettings(SETTINGS_ORG, SETTINGS_APP)
        locale = s.value(SETTINGS_KEY_LOCALE, '')
        if not locale:
            locale_val = QSettings().value('locale/userLocale')
            locale = locale_val[0:2] if locale_val else 'en'
        return locale
    except Exception:
        return 'en'


def add_panel_sign(
    geometry_wkt, etat_mont, idLine, idPoly, idOrg, dim=DEFAULT_PANEL_DIM,
    pkuid=None,
):
    """Add a panel sign feature to the database and return the instance."""
    instance = PanelSign(
        pkuid=pkuid,
        Stituation=etat_mont,
        idLine=idLine, idPoly=idPoly, idOrg=idOrg, dim=dim,
        geometry=WKTElement(geometry_wkt, srid=SRID),
    )
    session = get_session()
    try:
        instance.save(session)
        return instance
    finally:
        session.close()


def add_organization(geometry_wkt, nom_org, type_org, cat_org, pkuid=None):
    """Add an organization feature to the database and return the instance."""
    instance = Organization(
        pkuid=pkuid,
        Type=type_org, Cat=cat_org, Nom=nom_org,
        geometry=WKTElement(geometry_wkt, srid=SRID),
    )
    session = get_session()
    try:
        instance.save(session)
        return instance
    finally:
        session.close()


def add_road(geometry_wkt, nom_voie, type_voie, dec_voie, pkuid=None):
    """Add a road feature to the database and return the instance."""
    instance = Road(
        pkuid=pkuid,
        Type=type_voie, Nom=nom_voie, num_decision=dec_voie,
        geometry=WKTElement(geometry_wkt, srid=SRID),
    )
    session = get_session()
    try:
        instance.save(session)
        return instance
    finally:
        session.close()


def add_numbering(
    geometry_wkt, valeur, idLine, idPoly, repetition, etat,
    cat_act=None, type_act=None, pkuid=None,
):
    """Add a numbering feature to the database and return the instance."""
    instance = Numbering(
        pkuid=pkuid,
        valeur=valeur, idLine=idLine, idPoly=idPoly,
        repetition=repetition, etat=etat,
        activity_cat=cat_act, activity_type=type_act,
        geometry=WKTElement(geometry_wkt, srid=SRID),
    )
    session = get_session()
    try:
        instance.save(session)
        return instance
    finally:
        session.close()


def add_subdivision(geometry_wkt, subdivision_type, name, pkuid=None):
    """Add a subdivision feature to the database and return the instance."""
    instance = Subdivision(
        pkuid=pkuid,
        Nom=name, Type=subdivision_type,
        geometry=WKTElement(geometry_wkt, srid=SRID),
    )
    session = get_session()
    try:
        instance.save(session)
        return instance
    finally:
        session.close()


def add_zone(geometry_wkt, zone_type, name, pkuid=None):
    """Add a zone feature to the database and return the instance."""
    instance = Zone(
        pkuid=pkuid,
        Nom=name, Type=zone_type,
        geometry=WKTElement(geometry_wkt, srid=SRID),
    )
    session = get_session()
    try:
        instance.save(session)
        return instance
    finally:
        session.close()


def add_road_type(text) -> None:
    """Add a new road type to the database and notify the user."""
    if text:
        session = get_session()
        try:
            RoadType(pk=text).save(session)
        finally:
            session.close()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setInformativeText(_i18n_tr('تمة إظافة   نوع الطريق', _msg_locale()))
        msg.setStyleSheet(get_theme_qss(current_theme()))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    else:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setInformativeText(_i18n_tr('لم يتم إظافة  نوع الطريق', _msg_locale()))
        msg.setStyleSheet(get_theme_qss(current_theme()))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


def add_type_zone(text) -> None:
    """Add a new zone type to the database and notify the user."""
    if text:
        session = get_session()
        try:
            ZoneType(pk=text).save(session)
        finally:
            session.close()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setInformativeText(_i18n_tr('تمة إظافة   نوع المنطقة', _msg_locale()))
        msg.setStyleSheet(get_theme_qss(current_theme()))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    else:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setInformativeText(_i18n_tr('لم يتم إظافة  نوع المنطقة', _msg_locale()))
        msg.setStyleSheet(get_theme_qss(current_theme()))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


def add_subdivision_type(text) -> None:
    """Add a new subdivision type to the database and notify the user."""
    if text:
        session = get_session()
        try:
            SubdivisionType(pk=text).save(session)
        finally:
            session.close()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setInformativeText(_i18n_tr('تمة إظافة  نوع التجزئة', _msg_locale()))
        msg.setStyleSheet(get_theme_qss(current_theme()))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    else:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setInformativeText(_i18n_tr('لم يتم إظافة  نوع التجزئة', _msg_locale()))
        msg.setStyleSheet(get_theme_qss(current_theme()))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


def add_organization_type(text1, text2, text3='') -> None:
    """Add a new organization type to the database and notify the user."""
    if text1 and text2:
        session = get_session()
        try:
            OrganizationType(pk=text1, cat=text2, subcat=text3).save(session)
        finally:
            session.close()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setInformativeText(_i18n_tr('تمة إظافة  نوع المرفق', _msg_locale()))
        msg.setStyleSheet(get_theme_qss(current_theme()))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    else:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setInformativeText(_i18n_tr('لم يتم إظافة  نوع المرفق', _msg_locale()))
        msg.setStyleSheet(get_theme_qss(current_theme()))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


def add_activity_type(text1, text2, text3='') -> None:
    """Add a new activity type to the database and notify the user."""
    if text1 and text2:
        if NO_ACTIVITY in (text1, text2):
            return
        session = get_session()
        try:
            ActivityType(cat=text1, type=text2, subcat=text3).save(session)
        finally:
            session.close()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setInformativeText(_i18n_tr('تمة إظافة  نوع النشاط', _msg_locale()))
        msg.setStyleSheet(get_theme_qss(current_theme()))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    else:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setInformativeText(_i18n_tr('لم يتم إظافة  نوع النشاط', _msg_locale()))
        msg.setStyleSheet(get_theme_qss(current_theme()))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
