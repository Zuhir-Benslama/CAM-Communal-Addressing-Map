import logging

import geopandas as gpd
from sqlalchemy import text
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape

from ..core.database import get_session
from ..orders.models import (
    Road, Organization, Subdivision, Zone, PanelSign, Numbering,
)
from ..shared.constants import SRID, DEFAULT_PANEL_DIM

logger = logging.getLogger(__name__)

_WRITER_MODELS = {
    'Road': Road,
    'Organization': Organization,
    'Subdivision': Subdivision,
    'Zone': Zone,
    'PanelSign': PanelSign,
    'Numbering': Numbering,
}


def export_model(model_name: str) -> None:
    session = get_session()
    try:
        model_class = _WRITER_MODELS.get(model_name)
        if model_class is None:
            raise ValueError(f"Unknown model: {model_name}")
        query = session.query(model_class).all()

        records = []
        for record in query:
            rec = {}
            for column_name, column_obj in \
                    model_class.__table__.columns.items():
                if isinstance(column_obj.type, Geometry):
                    wkb = getattr(record, column_name)
                    if wkb is not None:
                        rec[column_name] = to_shape(wkb)
                else:
                    rec[column_name] = getattr(record, column_name)
            records.append(rec)

        gdf = gpd.GeoDataFrame(records, geometry='geometry')
        gdf.set_crs('EPSG:4326', inplace=True)
        gdf.to_file(f'{model_name}.shp')
        logger.info("Shapefile export completed successfully.")
    finally:
        session.close()


def add_panel_sign(
    geometry_wkt, etat_mont, idLine, idPoly, idOrg, dim=DEFAULT_PANEL_DIM,
    pkuid=None,
):
    from geoalchemy2.elements import WKTElement
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
    from geoalchemy2.elements import WKTElement
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
    from geoalchemy2.elements import WKTElement
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
    from geoalchemy2.elements import WKTElement
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
    from geoalchemy2.elements import WKTElement
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
    from geoalchemy2.elements import WKTElement
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


def count_numberings(etat: str) -> int:
    session = get_session()
    try:
        result = session.execute(
            text("select count(*) as cpt from Num where etat = :etat"),
            {"etat": etat}
        )
        row = result.fetchone()
        return row[0] if row else 0
    finally:
        session.close()


def count_panels(type: str, etat: str) -> int:
    session = get_session()
    try:
        result = session.execute(
            text(
                "select count(*) as cpt from Pan "
                "where Type = :type and Stituation = :etat"
            ),
            {"type": type, "etat": etat}
        )
        row = result.fetchone()
        return row[0] if row else 0
    finally:
        session.close()


def query_missing_pan(etat: str) -> list:
    session = get_session()
    try:
        result = session.execute(
            text(
                "SELECT label, type, COUNT(*) AS total "
                "FROM Pan2 WHERE Stituation = :etat GROUP BY label, type"
            ),
            {"etat": etat}
        )
        rows = result.fetchall()
        return [
            {'label': row[0], 'type': row[1], 'total': row[2]}
            for row in rows
        ]
    finally:
        session.close()


def query_missing_num(etat: str) -> list:
    session = get_session()
    try:
        result = session.execute(
            text(
                "SELECT valeur, COUNT(*) AS total FROM Num "
                "WHERE etat = :etat "
                "AND (repetition = '' OR repetition IS NULL) GROUP BY valeur"
            ),
            {"etat": etat}
        )
        rows = result.fetchall()
        return [{'valeur': row[0], 'total': row[1]} for row in rows]
    finally:
        session.close()


def query_missing_rep(etat: str) -> list:
    session = get_session()
    try:
        result = session.execute(
            text(
                "SELECT repetition, COUNT(*) AS total FROM Num "
                "WHERE etat = :etat "
                "AND (repetition != '' OR repetition IS NOT NULL) "
                "GROUP BY repetition"
            ),
            {"etat": etat}
        )
        rows = result.fetchall()
        return [{'valeur': row[0], 'total': row[1]} for row in rows]
    finally:
        session.close()
