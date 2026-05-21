"""Database engine and session management for SQLite/SpatiaLite."""
import logging
from contextlib import contextmanager
from typing import Any, Iterator

from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from ..shared.constants import DATABASE_FILE, AUTH_DATABASE_FILE
from ..core.config import find_mod_spatialite_dll

logger = logging.getLogger(__name__)

Base = declarative_base()


def _allowlist_columns(model_class: type, **kwargs: Any) -> dict:
    valid_columns = {col.name for col in model_class.__table__.columns}
    return {k: v for k, v in kwargs.items() if k in valid_columns}


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
                dbapi_conn.execute(f"SELECT load_extension('{dll}')")
            try:
                cursor = dbapi_conn.execute(
                    "SELECT count(*) FROM sqlite_master "
                    "WHERE type='table' AND name='spatial_ref_sys'"
                )
                if cursor.fetchone()[0] == 0:
                    dbapi_conn.execute("SELECT InitSpatialMetadata(1)")
            except Exception:
                pass

        Base.metadata.create_all(_engine)
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
        _migrate_users_to_auth()
    return _auth_engine


def _migrate_users_to_auth() -> None:
    from ..users.models import User
    try:
        auth_session = sessionmaker(bind=_auth_engine)()
        count = auth_session.query(User).count()
        if count > 0:
            auth_session.close()
            return
        spatial_engine = get_engine()
        spatial_session = sessionmaker(bind=spatial_engine)()
        try:
            if not inspect(spatial_engine).has_table('user'):
                return
            users = spatial_session.query(User).all()
            for user in users:
                auth_session.add(User(
                    id=user.id, username=user.username,
                    password=user.password, active=user.active,
                    affectation_id=user.affectation_id,
                    api_key=user.api_key, email=user.email,
                    phone=user.phone, first_name=user.first_name,
                    last_name=user.last_name,
                ))
            auth_session.commit()
            logger.info("Migrated %d user(s) to auth.sqlite", len(users))
        finally:
            spatial_session.close()
            auth_session.close()
    except Exception:
        logger.warning(
            "Auto-migration of users to auth.sqlite failed "
            "(spatial DB may not exist yet)"
        )


def get_auth_session() -> Session:
    global _AuthSession
    if _AuthSession is None:
        _AuthSession = sessionmaker(bind=get_auth_engine())
    return _AuthSession()
