"""Database creation and reference data loading."""
import os
try:
    from .models import (
        ActivityType, PanelDimension, NumberingState, Localite, MountingStatus,
        SubdivisionType, OrganizationType, RoadType, ZoneType, get_session,
        get_auth_engine,
    )
    from .constants import SRID, TEMPLATE_DATA_DIR, VIEWS_SQL
except ImportError:
    from models import (
        ActivityType, PanelDimension, NumberingState, Localite, MountingStatus,
        SubdivisionType, OrganizationType, RoadType, ZoneType, get_session,
        get_auth_engine,
    )
    from constants import SRID, TEMPLATE_DATA_DIR, VIEWS_SQL
import geopandas as gpd
import pandas as pd
from geoalchemy2.elements import WKTElement
from concurrent.futures import ThreadPoolExecutor
import json
from sqlalchemy import text
import logging
logger = logging.getLogger(__name__)

def create_db() -> None:
    """Create both spatial and auth databases."""
    get_session()
    get_auth_engine()


def load_localities() -> None:
    """Load localities from shapefile into the database."""
    session = get_session()
    try:
        shp_file=os.path.join(TEMPLATE_DATA_DIR, 'localite', 'localite.shp')
        gdf = gpd.read_file(shp_file)
        for _, row in gdf.iterrows():
            pk_uid = row['pk_uid']
            wilaya = row['wilaya']
            codeWilaya = row['codeWilaya']
            communeAr = row['communeAr']
            codeCommun = row['codeCommun']
            geometry = WKTElement(f"SRID={SRID};{row['geometry']}", srid=SRID)

            Localite(
                pk_uid=pk_uid, wilaya=wilaya, codeWilaya=codeWilaya,
                codeCommun=codeCommun, communeAr=communeAr, geometry=geometry
            ).save(session)
    finally:
        session.close()


def load_road_types() -> None:
    """Load road types from JSON into the database."""
    session = get_session()
    try:
        file_path = os.path.join(TEMPLATE_DATA_DIR, 'type_voie.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if data:
                for element in data:
                    pk = element.get('pk')
                    if pk:
                        RoadType(pk=pk).save(session)
    finally:
        session.close()


def load_zone_types() -> None:
    """Load zone types from JSON into the database."""
    session = get_session()
    try:
        file_path = os.path.join(TEMPLATE_DATA_DIR, 'type_zone.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if data:
                for element in data:
                    pk = element.get('pk')
                    if pk:
                        ZoneType(pk=pk).save(session)
    finally:
        session.close()


def load_subdivision_types() -> None:
    """Load subdivision types from JSON into the database."""
    session = get_session()
    try:
        file_path = os.path.join(TEMPLATE_DATA_DIR, 'type_cite.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if data:
                for element in data:
                    pk = element.get('pk')
                    if pk:
                        SubdivisionType(pk=pk).save(session)
    finally:
        session.close()


def load_organization_types() -> None:
    """Load organization types from JSON into the database."""
    session = get_session()
    try:
        file_path = os.path.join(TEMPLATE_DATA_DIR, 'type_organisme.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if data:
                for element in data:
                    pk = element.get('TypeAr')
                    cat = element.get('categorie')
                    if pk:
                        OrganizationType(pk=pk, cat=cat, subcat='').save(session)
    finally:
        session.close()


def load_activity_types() -> None:
    """Load numbering statuses from JSON into the database."""
    session = get_session()
    try:
        file_path = os.path.join(TEMPLATE_DATA_DIR, 'Etat_Numerotation.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if data:
                for element in data:
                    pk = element.get('pk')
                    if pk:
                        NumberingState(pk=pk).save(session)
    finally:
        session.close()


def load_mounting_statuses() -> None:
    """Load mounting situations from JSON into the database."""
    session = get_session()
    try:
        file_path = os.path.join(TEMPLATE_DATA_DIR, 'situation_Montage.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if data:
                for element in data:
                    pk = element.get('pk')
                    if pk:
                        MountingStatus(pk=pk).save(session)
    finally:
        session.close()


def load_panel_dimensions() -> None:
    """Load panel dimensions from JSON into the database."""
    session = get_session()
    try:
        file_path = os.path.join(TEMPLATE_DATA_DIR, 'DimPan.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if data:
                for element in data:
                    pk = element.get('pk')
                    if pk:
                        PanelDimension(pk=pk).save(session)
    finally:
        session.close()


def load_all() -> None:
    """Load all reference data using thread pool."""
    with ThreadPoolExecutor(max_workers=9) as executor:
        executor.map(
            lambda func: func(),
            [
                load_localities,
                load_organization_types,
                load_subdivision_types,
                load_activity_types,
                load_zone_types,
                load_road_types,
                load_panel_dimensions,
                load_mounting_statuses,
                load_point_types,
            ]
        )


def create_views() -> None:
    """Create database views from SQL file."""
    session = get_session()
    sql_path = VIEWS_SQL
    with open(sql_path, 'r', encoding='utf-8') as file:
        sql_query = file.read()

    sql_statements = sql_query.split(';')
    try:
        for statement in sql_statements:
            statement = statement.strip()
            if statement:
                session.execute(text(statement))

        session.commit()
        logger.info("SQL file executed successfully.")
    except Exception as e:
        session.rollback()
        logger.error("Error executing SQL: %s", e)
    finally:
        session.close()


def load_point_types() -> None:
    """Load activity types from Excel into the database."""
    xlsx_file = os.path.join(TEMPLATE_DATA_DIR, 'activity.xls')
    df = pd.read_excel(xlsx_file)
    session = get_session()
    try:
        for index, row in df.iterrows():
            cat = row['القطاع']
            type = row['النوع']
            if(type and cat):
                ActivityType(cat=cat, type=type, subcat='').save(session)
    finally:
        session.close()


def create_all() -> None:
    """Run full database creation and data loading."""
    create_db()
    load_all()
    create_views()
create_all()
