"""Database creation and reference data loading."""
import logging
import os

import geopandas as gpd
from geoalchemy2.elements import WKTElement
from sqlalchemy import text

try:
    from .models import Localite, get_session, get_auth_engine
    from .constants import SRID, TEMPLATE_DATA_DIR, VIEWS_SQL
except ImportError:
    from models import Localite, get_session, get_auth_engine
    from constants import SRID, TEMPLATE_DATA_DIR, VIEWS_SQL

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


def load_all() -> None:
    """Load all reference data."""
    load_localities()


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


def create_all() -> None:
    """Run full database creation and data loading."""
    create_db()
    load_all()
    create_views()
create_all()
