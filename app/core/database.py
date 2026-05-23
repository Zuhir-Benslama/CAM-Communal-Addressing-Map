"""Database engine and session management for SQLite/SpatiaLite."""
import logging
import os
from contextlib import contextmanager
from typing import Any, Iterator

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import sessionmaker, Session

from ..shared.constants import DATABASE_FILE, AUTH_DATABASE_FILE
from ..core.config import find_mod_spatialite_dll
from .base import Base

logger = logging.getLogger(__name__)


_engine = None
_Session = None
_auth_engine = None
_AuthSession = None


@contextmanager
def session_scope() -> Iterator[Session]:
    session = get_session()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def auth_session_scope() -> Iterator[Session]:
    session = get_auth_session()
    try:
        yield session
    finally:
        session.close()


def reset_connection_pool() -> None:
    global _engine, _Session, _auth_engine, _AuthSession
    _engine = None
    _Session = None
    _auth_engine = None
    _AuthSession = None


def _add_column_if_not_exists(
    conn: Any, table: str, column: str, col_type: str
) -> None:
    """Add a column to a SQLite table if it does not already exist."""
    result = conn.execute(
        text("SELECT count(*) FROM sqlite_master WHERE type='table' AND name=:name"),
        {"name": table},
    )
    if result.fetchone()[0] == 0:
        return
    result = conn.execute(text(f"PRAGMA table_info('{table}')"))
    existing = {row[1] for row in result.fetchall()}
    if column not in existing:
        conn.execute(text(f"ALTER TABLE '{table}' ADD COLUMN {column} {col_type}"))
        logger.info("Added column %s.%s (%s)", table, column, col_type)


_SPATIAL_INDEXES = (
    ('localite', 'geometry'),
    ('refpoly', 'geometry'),
    ('refpolychild', 'geometry'),
    ('RefLine', 'geometry'),
    ('reforg', 'geometry'),
    ('Numerotation', 'geometry'),
    ('Pannautage', 'geometry'),
)


def _spatial_index_exists(conn: Any, table: str, column: str) -> bool:
    """Check whether a SpatiaLite spatial index already exists."""
    result = conn.execute(
        text(
            "SELECT spatial_index_enabled FROM geometry_columns "
            "WHERE LOWER(f_table_name) = LOWER(:table) "
            "AND LOWER(f_geometry_column) = LOWER(:col)"
        ),
        {"table": table, "col": column},
    )
    row = result.fetchone()
    return row is not None and row[0] == 1


_MISSING_COLUMNS = (
    ("localite", "commune_fr", "TEXT"),
    ("localite", "commune_en", "TEXT"),
    ("refpoly", "Nom_fr", "TEXT"),
    ("refpoly", "Nom_en", "TEXT"),
    ("refpolychild", "Nom_fr", "TEXT"),
    ("refpolychild", "Nom_en", "TEXT"),
    ("RefLine", "Nom_fr", "TEXT"),
    ("RefLine", "Nom_en", "TEXT"),
    ("reforg", "Nom_fr", "TEXT"),
    ("reforg", "Nom_en", "TEXT"),
)


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
                logger.debug("Spatial index already exists on %s.%s", table, column)
                continue
            try:
                conn.execute(
                    text(f"SELECT CreateSpatialIndex('{table}', '{column}')")
                )
                conn.commit()
                logger.info("Created spatial index on %s.%s", table, column)
            except Exception:
                logger.warning(
                    "Could not create spatial index on %s.%s",
                    table, column, exc_info=True,
                )


_TIMESTAMP_TABLES = (
    'user', 'localite', 'refpoly', 'refpolychild',
    'RefLine', 'reforg', 'Numerotation', 'Pannautage',
)


def _migrate_timestamp_columns(engine: Any) -> None:
    """Add ``created_at`` / ``updated_at`` columns to all known tables."""
    with engine.connect() as conn:
        for table in _TIMESTAMP_TABLES:
            try:
                _add_column_if_not_exists(conn, table, 'created_at', 'DATETIME')
                _add_column_if_not_exists(conn, table, 'updated_at', 'DATETIME')
            except Exception:
                logger.warning(
                    "Could not add timestamp columns to %s", table, exc_info=True
                )


def get_engine() -> Any:
    global _engine
    if _engine is None:
        filename = DATABASE_FILE
        _engine = create_engine(
            f'sqlite:///{filename}', echo=False, pool_pre_ping=True
        )

        @event.listens_for(_engine, "connect")
        def connect_spatialite(dbapi_conn, _connection_record) -> None:
            dll = find_mod_spatialite_dll()
            dbapi_conn.enable_load_extension(True)
            try:
                dbapi_conn.load_extension(dll)
            except Exception:
                logger.debug(
                    "SpatiaLite load_extension API failed, trying SQL fallback",
                    exc_info=True,
                )
                if not os.path.exists(dll):
                    raise RuntimeError(
                        f"SpatiaLite DLL not found: {dll}"
                    )
                safe_dll = dll.replace("'", "''")
                dbapi_conn.execute(
                    f"SELECT load_extension('{safe_dll}')"
                )
            try:
                cursor = dbapi_conn.execute(
                    "SELECT count(*) FROM sqlite_master "
                    "WHERE type='table' AND name='spatial_ref_sys'"
                )
                if cursor.fetchone()[0] == 0:
                    dbapi_conn.execute("SELECT InitSpatialMetadata(1)")
            except Exception:
                logger.warning(
                    "InitSpatialMetadata(1) failed — spatial queries "
                    "may not work correctly",
                    exc_info=True,
                )

        Base.metadata.create_all(_engine)
        _migrate_timestamp_columns(_engine)
        _migrate_missing_columns(_engine)
        _create_spatial_indexes(_engine)
    return _engine


def get_session() -> Session:
    global _Session
    if _Session is None:
        _Session = sessionmaker(bind=get_engine())
    return _Session()


def get_auth_engine() -> Any:
    global _auth_engine
    if _auth_engine is None:
        from ..users.models import User
        filename = AUTH_DATABASE_FILE
        _auth_engine = create_engine(
            f'sqlite:///{filename}', echo=False, pool_pre_ping=True
        )
        Base.metadata.create_all(_auth_engine, tables=[User.__table__])
        _migrate_timestamp_columns(_auth_engine)
        _migrate_users_to_auth()
    return _auth_engine


def _migrate_users_to_auth() -> None:
    """One-shot migration from legacy spatial DB user table to auth DB.

    The spatial DB retains a ``user`` table purely to satisfy ``FOREIGN KEY``
    constraints from spatial entity models (Zone, Road, etc. have a ``uid``
    column referencing ``user.id``).  Auth-sensitive columns (``password``,
    ``api_key``, ``email``, etc.) exist in both tables but **auth operations
    always read from ``auth.sqlite``** — the spatial ``user`` table is only
    ever written to keep FK constraints satisfied.

    This migration copies rows from the pre-existing spatial ``user`` table
    into the new auth DB exactly once (when the auth DB is first created).
    After that, ``sign_up`` / ``sign_in`` / ``logout`` keep both tables in
    sync via dual-write.
    """
    from ..users.models import User
    try:
        auth_session = sessionmaker(bind=_auth_engine)()
    except Exception:
        logger.exception(
            "Cannot create auth session for user migration"
        )
        return
    try:
        count = auth_session.query(User).count()
        if count > 0:
            return
        spatial_engine = get_engine()
        spatial_session = sessionmaker(bind=spatial_engine)()
        try:
            if not inspect(spatial_engine).has_table('user'):
                return
            users = spatial_session.query(User).all()
            migrated = 0
            for user in users:
                try:
                    auth_session.add(User(
                        id=user.id, username=user.username,
                        password=user.password, active=user.active,
                        affectation_id=user.affectation_id,
                        api_key=user.api_key, email=user.email,
                        phone=user.phone, first_name=user.first_name,
                        last_name=user.last_name,
                    ))
                    migrated += 1
                except Exception:
                    logger.warning(
                        "Failed to migrate user %s", user.id,
                        exc_info=True,
                    )
            auth_session.commit()
            if migrated:
                logger.info(
                    "Migrated %d user(s) to auth.sqlite", migrated
                )
        finally:
            spatial_session.close()
            auth_session.close()
    except Exception:
        logger.warning(
            "Auto-migration of users to auth.sqlite failed "
            "(spatial DB may not exist yet)",
            exc_info=True,
        )
    finally:
        auth_session.close()


def get_auth_session() -> Session:
    global _AuthSession
    if _AuthSession is None:
        _AuthSession = sessionmaker(bind=get_auth_engine())
    return _AuthSession()
