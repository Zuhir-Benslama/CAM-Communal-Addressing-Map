"""Database engine and session management for SQLite/SpatiaLite."""

import logging
import re
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from ..core.config import find_mod_spatialite_dll
from ..shared.constants import DATABASE_FILE
from ._schema_migrations import (
    _create_spatial_indexes,
    _create_views,
    _migrate_missing_columns,
    _migrate_old_columns,
    _migrate_timestamp_columns,
    _migrate_users_from_auth,
)
from .base import Base

logger = logging.getLogger(__name__)

_IDENTIFIER_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


def _validate_safe_name(name: str) -> str:
    """Validate that *name* is a safe SQL identifier (no SQL injection risk)."""
    if not _IDENTIFIER_RE.match(name):
        msg = f'Unsafe SQL identifier: {name!r}'
        raise ValueError(msg)
    return name


class ConnectionPool:
    """Lazily-initialised singleton pool for the spatial DB engine and
    session factory."""

    def __init__(self) -> None:
        self._engine: Any = None
        self._Session: Any = None

    def reset(self) -> None:
        self._engine = None
        self._Session = None

    def get_engine(self) -> Any:
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
                except sqlite3.OperationalError as exc:
                    logger.debug(
                        'SpatiaLite load_extension failed, trying SQL fallback',
                        exc_info=True,
                    )
                    if not Path(dll).exists():
                        msg = f'SpatiaLite DLL not found: {dll}'
                        raise RuntimeError(msg) from exc
                    dbapi_conn.execute('SELECT load_extension(?)', (dll,))
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
                        'InitSpatialMetadata(1) failed \u2014 spatial queries '
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
        if self._Session is None:
            self._Session = sessionmaker(bind=self.get_engine())
        return self._Session()


_pool = ConnectionPool()


@contextmanager
def session_scope() -> Iterator[Session]:
    session = _pool.get_session()
    try:
        yield session
    finally:
        session.close()


def reset_connection_pool() -> None:
    _pool.reset()


def get_engine() -> Any:
    return _pool.get_engine()


def get_session() -> Session:
    return _pool.get_session()
