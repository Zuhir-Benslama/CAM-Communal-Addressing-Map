"""Functions for writing/inserting data into the database."""
import logging

from geoalchemy2.elements import WKTElement

try:
    from ..models import (
        Road, Organization, Subdivision, Zone, PanelSign,
        Numbering, get_session,
    )
    from ..constants import (
        SRID, DEFAULT_PANEL_DIM,
    )
except ImportError:
    from models import (
        Road, Organization, Subdivision, Zone, PanelSign,
        Numbering, get_session,
    )
    from constants import (
        SRID, DEFAULT_PANEL_DIM,
    )

logger = logging.getLogger(__name__)


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


def add_organization(geometry_wkt, nom_org, type_org, cat_org, pkuid=None,
                     nom_org_fr=None, nom_org_en=None):
    """Add an organization feature to the database and return the instance."""
    instance = Organization(
        pkuid=pkuid,
        Type=type_org, Cat=cat_org, Nom=nom_org,
        Nom_fr=nom_org_fr, Nom_en=nom_org_en,
        geometry=WKTElement(geometry_wkt, srid=SRID),
    )
    session = get_session()
    try:
        instance.save(session)
        return instance
    finally:
        session.close()


def add_road(geometry_wkt, nom_voie, type_voie, dec_voie, pkuid=None,
             nom_voie_fr=None, nom_voie_en=None):
    """Add a road feature to the database and return the instance."""
    instance = Road(
        pkuid=pkuid,
        Type=type_voie, Nom=nom_voie, num_decision=dec_voie,
        Nom_fr=nom_voie_fr, Nom_en=nom_voie_en,
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


def add_subdivision(geometry_wkt, subdivision_type, name, pkuid=None,
                    name_fr=None, name_en=None):
    """Add a subdivision feature to the database and return the instance."""
    instance = Subdivision(
        pkuid=pkuid,
        Nom=name, Type=subdivision_type,
        Nom_fr=name_fr, Nom_en=name_en,
        geometry=WKTElement(geometry_wkt, srid=SRID),
    )
    session = get_session()
    try:
        instance.save(session)
        return instance
    finally:
        session.close()


def add_zone(geometry_wkt, zone_type, name, pkuid=None,
             name_fr=None, name_en=None):
    """Add a zone feature to the database and return the instance."""
    instance = Zone(
        pkuid=pkuid,
        Nom=name, Type=zone_type,
        Nom_fr=name_fr, Nom_en=name_en,
        geometry=WKTElement(geometry_wkt, srid=SRID),
    )
    session = get_session()
    try:
        instance.save(session)
        return instance
    finally:
        session.close()



