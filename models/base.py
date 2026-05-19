"""Database engine, session management, and shared utilities
for SQLAlchemy models."""

import os
import logging
from contextlib import contextmanager
from typing import Any, Iterator, Optional, List, Tuple

from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import declarative_base, sessionmaker, Session

try:
    from ..constants import (
        COOKIE_FILE, DATABASE_FILE, AUTH_DATABASE_FILE,
        current_locale,
    )
except ImportError:
    # Fallback for standalone/test mode when not loaded as a package
    from constants import (
        COOKIE_FILE, DATABASE_FILE, AUTH_DATABASE_FILE,
        current_locale,
    )

logger = logging.getLogger(__name__)

Base = declarative_base()


def _allowlist_columns(model_class: type, **kwargs: Any) -> dict:
    """Filter kwargs to only include keys that are actual DB columns."""
    valid_columns = {col.name for col in model_class.__table__.columns}
    return {k: v for k, v in kwargs.items() if k in valid_columns}


def find_mod_spatialite_dll() -> str:
    """Finds path to mod_spatialite shared library."""
    env_path = os.getenv('MOD_SPATIALITE_DLL')
    if env_path:
        return env_path
    if os.name == 'nt':
        return 'mod_spatialite.dll'
    if os.uname().sysname == 'Darwin':
        return 'mod_spatialite.dylib'

    candidates = [
        '/usr/lib/spatialite50/lib/mod_spatialite.so',
        '/usr/libspatialite50/lib/mod_spatialite.so',
        '/usr/lib/spatialite/mod_spatialite.so',
        '/usr/lib/mod_spatialite.so',
        '/usr/lib64/mod_spatialite.so',
        '/usr/lib/x86_64-linux-gnu/mod_spatialite.so',
    ]
    for p in candidates:
        if os.path.exists(p):
            return p

    try:
        import subprocess
        result = subprocess.run(
            ['ldconfig', '-p'], capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines():
            if 'mod_spatialite' in line:
                parts = line.split('=>')
                if len(parts) == 2:
                    path = parts[1].strip()
                    if os.path.exists(path):
                        return path
    except Exception:
        logger.debug(
            "mod_spatialite not found at candidate path", exc_info=True
        )

    return 'mod_spatialite.so'


def get_current_user() -> Optional[dict]:
    """Returns current authenticated user info or None."""
    import toml
    from .user import User
    from .spatial import Localite

    filename = COOKIE_FILE
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = toml.load(f)
    except (FileNotFoundError, toml.TomlDecodeError):
        return None
    cookie = data.get('Session', {}).get('cookie', None)
    uid = data.get('Session', {}).get('uid', None)
    if not cookie or not uid:
        return None

    session = get_session()
    try:
        user = session.query(User).filter(
            User.id == uid, User.api_key == cookie, User.active == True
        ).first()
        if not user:
            return None
        localite = (
            session.query(Localite)
            .filter(Localite.pk_uid == user.affectation_id)
            .first()
        )
        if not localite:
            return None
        return {
            'id': user.id,
            'loc': user.affectation_id,
            'wilaya': localite.wilaya,
            'commune': localite.communeAr
        }
    finally:
        session.close()


_engine = None
_Session = None
_auth_engine = None
_AuthSession = None


@contextmanager
def session_scope() -> Iterator[Session]:
    """Context manager providing a session that auto-closes on exit.

    Usage:
        with session_scope() as session:
            session.query(User).all()
    """
    session = get_session()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def auth_session_scope() -> Iterator[Session]:
    """Context manager providing an auth session that auto-closes on exit.

    Usage:
        with auth_session_scope() as session:
            session.query(User).all()
    """
    session = get_auth_session()
    try:
        yield session
    finally:
        session.close()


def reset_connection_pool() -> None:
    """Reset all cached engine/session globals (useful for testing)."""
    global _engine, _Session, _auth_engine, _AuthSession
    _engine = None
    _Session = None
    _auth_engine = None
    _AuthSession = None


def get_engine() -> Any:
    """Creates and returns SQLAlchemy engine for spatial database."""
    global _engine
    if _engine is None:
        filename = DATABASE_FILE
        _engine = create_engine(
            f'sqlite:///{filename}', echo=False, pool_pre_ping=True
        )

        @event.listens_for(_engine, "connect")
        def connect_spatialite(dbapi_conn, connection_record) -> None:
            """Loads SpatiaLite extension on database connect."""
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
    """Creates and returns a new spatial database session."""
    global _Session
    if _Session is None:
        _Session = sessionmaker(bind=get_engine())
    return _Session()


def get_auth_engine() -> Any:
    """Creates and returns SQLAlchemy engine for auth database
    (no SpatiaLite)."""
    global _auth_engine
    if _auth_engine is None:
        from .user import User
        filename = AUTH_DATABASE_FILE
        _auth_engine = create_engine(
            f'sqlite:///{filename}', echo=False, pool_pre_ping=True
        )
        Base.metadata.create_all(_auth_engine, tables=[User.__table__])
        _migrate_users_to_auth()
    return _auth_engine


def _migrate_users_to_auth() -> None:
    """Copy users from spatial DB to auth DB if auth DB is empty."""
    from .user import User
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
    """Creates and returns a new auth database session."""
    global _AuthSession
    if _AuthSession is None:
        _AuthSession = sessionmaker(bind=get_auth_engine())
    return _AuthSession()


def get_all_fields_and_labels(
    model_class, property_labels=None, locale=''
) -> Tuple[List[str], List[str]]:
    """Return (fields, labels) including both SQLAlchemy columns
    and @property fields.

    Labels are locale-aware: uses 'label_fr'/'label_en' from column.info
    if available, falling back to 'label' (Arabic).
    """
    if not locale:
        locale = current_locale()
    fields = []
    labels = []

    mapper = inspect(model_class)
    for attr in mapper.attrs:
        if hasattr(attr, 'columns'):
            column = attr.columns[0]
            if(column.name not in [
                'geometry', 'uid', 'idLoc', 'has_child', 'parent', 'pkuid_poly'
            ]):
                fields.append(column.name)
                if locale != 'ar':
                    label_key = f'label_{locale}'
                    label = column.info.get(label_key)
                else:
                    label = None
                if not label:
                    label = column.info.get('label', column.name)
                labels.append(label)

    if property_labels:
        for prop_name, prop_label in property_labels.items():
            fields.append(prop_name)
            labels.append(prop_label)

    return fields, labels
