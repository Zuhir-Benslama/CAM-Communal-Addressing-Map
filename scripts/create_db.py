"""Database creation and reference data loading."""
import logging
import os
import sys

import geopandas as gpd
from geoalchemy2.elements import WKTElement

# Ensure both the project root and its parent are on sys.path so that
# 'app' and 'plans_adressage' are both importable as top-level packages.
_PKG_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

from app.orders.models import Localite  # noqa: E402
from app.core.database import get_session, get_auth_engine  # noqa: E402
from app.shared.constants import SRID, TEMPLATE_DATA_DIR, VIEWS_SQL  # noqa: E402

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
            wilaya_code = row['codeWilaya']
            commune_ar = row['communeAr']
            commune_code = row['codeCommun']
            geometry = WKTElement(f"SRID={SRID};{row['geometry']}", srid=SRID)

            Localite(
                id=pk_uid, wilaya=wilaya, wilaya_code=wilaya_code,
                commune_code=commune_code, commune_ar=commune_ar, geometry=geometry
            ).save(session)
    finally:
        session.close()


def load_all() -> None:
    """Load all reference data."""
    load_localities()


def create_views() -> None:
    """Create database views from SQL file."""
    sql_path = VIEWS_SQL
    with open(sql_path, 'r', encoding='utf-8') as file:
        sql_query = file.read()

    engine = get_engine()
    try:
        with engine.raw_connection() as conn:
            conn.executescript(sql_query)
        logger.info("SQL file executed successfully.")
    except Exception as e:
        logger.error("Error executing SQL: %s", e)
        raise


def create_all() -> None:
    """Run full database creation and data loading."""
    create_db()
    load_all()
    create_views()
create_all()
