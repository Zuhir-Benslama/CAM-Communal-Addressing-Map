"""Database query and utility operations."""
import os
from typing import Any
import toml
import json
import geopandas as gpd
import bcrypt
from sqlalchemy import func, text
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
try:
    from .. import models as _models
    from ..models import Localite, get_session, get_current_user
    from ..constants import COOKIE_FILE, QGIS_CONFIG_FILE
except ImportError:
    import models as _models  # type: ignore
    from models import Localite, get_session, get_current_user  # type: ignore
    from constants import COOKIE_FILE, QGIS_CONFIG_FILE  # type: ignore
import logging
logger = logging.getLogger(__name__)

def create_cookie(cookie: str, uid: str) -> None:
    """Save session cookie to a TOML file."""
    data = {'Session': {'cookie': cookie, 'uid': uid}}
    filename = COOKIE_FILE
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            toml.dump(data, f)
        os.chmod(filename, 0o600)
    except (OSError, PermissionError) as e:
        logger.error("Failed to write cookie file %s: %s", filename, e)
        raise


_qgis_config_cache = None

def qgis_config() -> dict:
    """Load QGIS configuration from JSON file (cached)."""
    global _qgis_config_cache
    if _qgis_config_cache is not None:
        return _qgis_config_cache
    filename = QGIS_CONFIG_FILE
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            _qgis_config_cache = json.load(file)
            return _qgis_config_cache
    except FileNotFoundError:
        logger.error("QGIS config file not found: %s", filename)
        raise
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in config file %s: %s", filename, e)
        raise


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(
        password.encode('utf-8'), hashed_password.encode('utf-8'))


def _get_authenticated_user() -> Any:
    """Retrieve authenticated user's localite from cookie."""
    user_data = get_current_user()
    if not user_data:
        return None
    session = get_session()
    try:
        return session.query(Localite).filter(
            Localite.pk_uid == user_data['loc']
        ).first()
    finally:
        session.close()


def get_user_location() -> Any:
    """Get WKT geometry of authenticated user's location."""
    result = _get_authenticated_user()
    if result:
        session = get_session()
        try:
            wkt = str(session.query(func.ST_AsText(result.geometry)).first()[0])
            return wkt
        finally:
            session.close()
    return None


def export_model(model_name: str) -> None:
    """Export a model to a shapefile."""
    session = get_session()
    try:
        model_class = getattr(_models, model_name, None)
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


def count_numberings(etat: str) -> int:
    """Count Num records by status."""
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
    """Count Pan records by type and status."""
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
    """Query missing panels grouped by label and type."""
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
    """Query missing numbers without repetition."""
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
    """Query missing numbers with repetition."""
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
