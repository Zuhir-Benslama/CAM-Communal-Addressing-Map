"""Database engine and session management for SQLite/SpatiaLite."""

import logging
import os
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from ..core.config import find_mod_spatialite_dll
from ..shared.constants import AUTH_DATABASE_FILE, DATABASE_FILE, VIEWS_SQL
from .base import Base

logger = logging.getLogger(__name__)


class ConnectionPool:
    """Lazily-initialised singleton pool for the spatial DB engine and
    session factory."""

    def __init__(self) -> None:
        self._engine: Any = None
        self._Session: Any = None

    def reset(self) -> None:
        """Clear the cached engine and session factory."""
        self._engine = None
        self._Session = None

    def get_engine(self) -> Any:
        """Return (and lazily initialise) the spatial DB engine."""
        if self._engine is None:
            filename = DATABASE_FILE
            self._engine = create_engine(
                f'sqlite:///{filename}', echo=False, pool_pre_ping=True
            )

            @event.listens_for(self._engine, 'connect')
            def connect_spatialite(dbapi_conn, _connection_record) -> None:
                dll = find_mod_spatialite_dll()
                dbapi_conn.enable_load_extension(True)
                try:
                    dbapi_conn.load_extension(dll)
                except Exception as exc:  # pylint: disable=W0718
                    logger.debug(
                        'SpatiaLite load_extension failed, trying SQL fallback',
                        exc_info=True,
                    )
                    if not os.path.exists(dll):
                        raise RuntimeError(f'SpatiaLite DLL not found: {dll}') from exc
                    safe_dll = dll.replace("'", "''")
                    dbapi_conn.execute(f"SELECT load_extension('{safe_dll}')")
                try:
                    cursor = dbapi_conn.execute(
                        'SELECT count(*) FROM sqlite_master '
                        "WHERE type='table' AND name='spatial_ref_sys'"
                    )
                    if cursor.fetchone()[0] == 0:
                        dbapi_conn.execute('SELECT InitSpatialMetadata(0)')
                        dbapi_conn.execute(
                            'INSERT OR IGNORE INTO spatial_ref_sys '
                            '(srid, auth_name, auth_srid, ref_sys_name, proj4text) '
                            "VALUES (4326, 'EPSG', 4326, 'WGS 84', "
                            "'+proj=longlat +datum=WGS84 +no_defs')"
                        )
                except (OperationalError, SQLAlchemyError):
                    logger.warning(
                        'InitSpatialMetadata(1) failed — spatial queries '
                        'may not work correctly',
                        exc_info=True,
                    )

            Base.metadata.create_all(self._engine)
            _migrate_users_from_auth(self._engine)
            _migrate_timestamp_columns(self._engine)
            _migrate_old_columns(self._engine)
            _migrate_missing_columns(self._engine)
            _create_views(self._engine)
            _create_spatial_indexes(self._engine)
        return self._engine

    def get_session(self) -> Session:
        """Return a new session bound to the spatial DB engine."""
        if self._Session is None:
            self._Session = sessionmaker(bind=self.get_engine())
        return self._Session()


_pool = ConnectionPool()


@contextmanager
def session_scope() -> Iterator[Session]:
    """Context manager yielding a spatial DB session, auto-closed on exit."""
    session = _pool.get_session()
    try:
        yield session
    finally:
        session.close()


def reset_connection_pool() -> None:
    """Clear all cached engines and session factories."""
    _pool.reset()


def _add_column_if_not_exists(
    conn: Any, table: str, column: str, col_type: str
) -> None:
    """Add a column to a SQLite table if it does not already exist."""
    result = conn.execute(
        text(
            "SELECT count(*) FROM sqlite_master WHERE type='table' AND name=:name",
        ),
        {'name': table},
    )
    if result.fetchone()[0] == 0:
        return
    result = conn.execute(text(f"PRAGMA table_info('{table}')"))
    existing = {row[1] for row in result.fetchall()}
    if column not in existing:
        conn.execute(text(f"ALTER TABLE '{table}' ADD COLUMN {column} {col_type}"))
        logger.info('Added column %s.%s (%s)', table, column, col_type)


_SPATIAL_INDEXES = (
    ('zone', 'geometry'),
    ('subdivision', 'geometry'),
    ('road', 'geometry'),
    ('organization', 'geometry'),
    ('numbering', 'geometry'),
    ('panel_sign', 'geometry'),
)


def _spatial_index_exists(conn: Any, table: str, column: str) -> bool:
    """Check whether a SpatiaLite spatial index already exists."""
    result = conn.execute(
        text(
            'SELECT spatial_index_enabled FROM geometry_columns '
            'WHERE LOWER(f_table_name) = LOWER(:table) '
            'AND LOWER(f_geometry_column) = LOWER(:col)'
        ),
        {'table': table, 'col': column},
    )
    row = result.fetchone()
    return row is not None and row[0] == 1


_MISSING_COLUMNS: tuple[tuple[str, str, str], ...] = ()


def _migrate_missing_columns(engine: Any) -> None:
    """Add columns introduced during attribute renames."""
    with engine.connect() as conn:
        for table, column, col_type in _MISSING_COLUMNS:
            _add_column_if_not_exists(conn, table, column, col_type)


def _create_spatial_indexes(engine: Any) -> None:
    """Create SpatiaLite spatial indexes for all geometry columns."""
    with engine.connect() as conn:
        for table, column in _SPATIAL_INDEXES:
            if _spatial_index_exists(conn, table, column):
                logger.debug(
                    'Spatial index already exists on %s.%s',
                    table,
                    column,
                )
                continue
            try:
                conn.execute(text(f"SELECT CreateSpatialIndex('{table}', '{column}')"))
                conn.commit()
                logger.info('Created spatial index on %s.%s', table, column)
            except (OperationalError, SQLAlchemyError):
                logger.warning(
                    'Could not create spatial index on %s.%s',
                    table,
                    column,
                    exc_info=True,
                )


_TIMESTAMP_TABLES = (
    'user',
    'zone',
    'subdivision',
    'road',
    'organization',
    'numbering',
    'panel_sign',
)

_OLD_COLUMN_RENAMES: dict[str, dict[str, str]] = {
    'zone': {
        'pkuid': 'id',
        'idLoc': 'locality_id',
        'uid': 'user_id',
        'Type': 'type',
        'Nom': 'name',
        'Nom_fr': 'name_fr',
        'Nom_en': 'name_en',
    },
    'subdivision': {
        'pkuid': 'id',
        'idLoc': 'locality_id',
        'uid': 'user_id',
        'Type': 'type',
        'Nom': 'name',
        'Nom_fr': 'name_fr',
        'Nom_en': 'name_en',
    },
    'road': {
        'pkuid': 'id',
        'num_decision': 'decision_number',
        'idLoc': 'locality_id',
        'pkuid_poly': 'zone_id',
        'uid': 'user_id',
        'Type': 'type',
        'Nom': 'name',
        'Nom_fr': 'name_fr',
        'Nom_en': 'name_en',
    },
    'organization': {
        'pkuid': 'id',
        'idLoc': 'locality_id',
        'Cat': 'category',
        'uid': 'user_id',
        'pkuid_poly': 'zone_id',
        'Type': 'type',
        'Nom': 'name',
        'Nom_fr': 'name_fr',
        'Nom_en': 'name_en',
    },
    'numbering': {
        'pkuid': 'id',
        'idLine': 'road_id',
        'idPoly': 'subdivision_id',
        'uid': 'user_id',
        'valeur': 'value',
        'etat': 'state',
    },
    'panel_sign': {
        'pkuid': 'id',
        'dim': 'dimensions',
        'Stituation': 'status',
        'situation': 'status',
        'idLine': 'road_id',
        'idPoly': 'subdivision_id',
        'idOrg': 'organization_id',
        'uid': 'user_id',
        'Type': 'type',
    },
}


def _migrate_old_columns(engine: Any) -> None:
    """Rename old-format column names to current model names.

    Very early versions of the plugin used different column names
    (e.g. ``pk_uid`` / ``pkuid`` for the primary key, ``codeWilaya``
    instead of ``wilaya_code``, etc.).  This migration renames those
    columns to match the current SQLAlchemy models so that ORM queries
    do not fail with ``no such column`` errors.
    """
    with engine.connect() as conn:
        for table, renames in _OLD_COLUMN_RENAMES.items():
            info = conn.execute(text(f"PRAGMA table_info('{table}')")).fetchall()
            cols = {r[1] for r in info}
            for old_name, new_name in renames.items():
                if old_name in cols and new_name not in cols:
                    try:
                        conn.execute(
                            text(
                                f'ALTER TABLE {table} '
                                f'RENAME COLUMN {old_name} TO {new_name}'
                            )
                        )
                        conn.commit()
                        logger.info(
                            'Renamed %s.%s → %s',
                            table,
                            old_name,
                            new_name,
                        )
                    except SQLAlchemyError:
                        logger.warning(
                            'Could not rename %s.%s → %s',
                            table,
                            old_name,
                            new_name,
                            exc_info=True,
                        )


def _create_views(engine: Any) -> None:
    """Create database views (Num, Roads, Pan, Pan2) from Views.sql."""
    if not os.path.exists(VIEWS_SQL):
        logger.warning('Views.sql not found at %s', VIEWS_SQL)
        return
    with engine.connect() as conn:
        try:
            with open(VIEWS_SQL, encoding='utf-8') as f:
                sql = f.read()
            for statement in sql.split(';'):
                stmt = statement.strip()
                if stmt:
                    conn.execute(text(stmt))
            conn.commit()
            logger.info('Created database views from Views.sql')
        except SQLAlchemyError:
            logger.warning(
                'Could not create database views',
                exc_info=True,
            )


def _migrate_timestamp_columns(engine: Any) -> None:
    """Add ``created_at`` / ``updated_at`` columns to all known tables."""
    with engine.connect() as conn:
        for table in _TIMESTAMP_TABLES:
            try:
                _add_column_if_not_exists(
                    conn,
                    table,
                    'created_at',
                    'DATETIME',
                )
                _add_column_if_not_exists(
                    conn,
                    table,
                    'updated_at',
                    'DATETIME',
                )
            except SQLAlchemyError:
                logger.warning(
                    'Could not add timestamp columns to %s',
                    table,
                    exc_info=True,
                )


def get_engine() -> Any:
    """Return the lazily-initialised spatial DB engine."""
    return _pool.get_engine()


def get_session() -> Session:
    """Return a new session bound to the spatial DB engine."""
    return _pool.get_session()


def _migrate_users_from_auth(engine: Any) -> None:
    """One-shot merge of ``auth.sqlite`` users into the main DB.

    Prior to the DB merge the project used two files:
    ``database.sqlite`` (spatial) and ``auth.sqlite`` (credentials).
    If ``auth.sqlite`` still exists on disk, this function attaches it
    and copies any users not yet present in the main DB, then renames
    the old file to ``auth.sqlite.migrated`` so the migration runs at
    most once.
    """
    auth_path = AUTH_DATABASE_FILE
    if not os.path.exists(auth_path):
        return

    try:
        with engine.connect() as conn:
            conn.execute(text(f"ATTACH DATABASE '{auth_path}' AS auth_db"))
            result = conn.execute(
                text(
                    'SELECT count(*) FROM auth_db.user '
                    'WHERE id NOT IN (SELECT id FROM user)'
                )
            )
            missing = result.fetchone()[0]
            if missing:
                conn.execute(
                    text(
                        'INSERT OR IGNORE INTO user '
                        '(id, username, password, active, wilaya_code, commune_code, '
                        'api_key, email, phone, first_name, last_name, '
                        'created_at, updated_at) '
                        'SELECT id, username, password, active, '
                        'wilaya_code, commune_code, api_key, email, phone, '
                        'first_name, last_name, created_at, updated_at '
                        'FROM auth_db.user'
                    )
                )
                conn.commit()
                logger.info(
                    'Merged %d user(s) from auth.sqlite into main DB',
                    missing,
                )
            conn.execute(text('DETACH DATABASE auth_db'))
    except (SQLAlchemyError, OSError):
        logger.warning(
            'Failed to merge users from auth.sqlite',
            exc_info=True,
        )
        return

    try:
        os.rename(auth_path, auth_path + '.migrated')
        logger.info('Renamed auth.sqlite → auth.sqlite.migrated')
    except OSError:
        logger.warning('Could not rename auth.sqlite after merge')
