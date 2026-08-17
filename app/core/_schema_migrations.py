"""Schema migration helpers — column renames, timestamp columns,
spatial indexes, view creation, and auth-DB user merge.

All functions are private (``_``-prefixed) and called from
``app.core.database.ConnectionPool.get_engine()`` at startup.
"""

import logging
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from ..shared.constants import AUTH_DATABASE_FILE, VIEWS_SQL
from ..shared.utils import validate_safe_name

logger = logging.getLogger(__name__)


_SPATIAL_INDEXES = (
    ('zone', 'geometry'),
    ('subdivision', 'geometry'),
    ('road', 'geometry'),
    ('organization', 'geometry'),
    ('numbering', 'geometry'),
    ('panel_sign', 'geometry'),
)

_MISSING_COLUMNS: tuple[tuple[str, str, str], ...] = (
    ('user', 'session_token', 'TEXT'),
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


def _add_column_if_not_exists(
    conn: Any, table: str, column: str, col_type: str
) -> None:
    """Add a column to a SQLite table if it does not already exist."""
    validate_safe_name(table)
    validate_safe_name(column)
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
        conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN {column} {col_type}'))
        logger.info('Added column %s.%s (%s)', table, column, col_type)


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


def _migrate_missing_columns(engine: Any) -> None:
    """Add columns introduced during attribute renames."""
    with engine.connect() as conn:
        for table, column, col_type in _MISSING_COLUMNS:
            _add_column_if_not_exists(conn, table, column, col_type)


def _create_spatial_indexes(engine: Any) -> None:
    """Create SpatiaLite spatial indexes for all geometry columns."""
    with engine.connect() as conn:
        for table, column in _SPATIAL_INDEXES:
            validate_safe_name(table)
            validate_safe_name(column)
            if _spatial_index_exists(conn, table, column):
                logger.debug(
                    'Spatial index already exists on %s.%s',
                    table,
                    column,
                )
                continue
            try:
                conn.execute(
                    text('SELECT CreateSpatialIndex(:table, :col)'),
                    {'table': table, 'col': column},
                )
                conn.commit()
                logger.info('Created spatial index on %s.%s', table, column)
            except (OperationalError, SQLAlchemyError):
                logger.warning(
                    'Could not create spatial index on %s.%s',
                    table,
                    column,
                    exc_info=True,
                )


def _rename_column_if_needed(
    conn: Any, table: str, old_name: str, new_name: str, existing_cols: set[str]
) -> None:
    if old_name not in existing_cols or new_name in existing_cols:
        return
    try:
        conn.execute(
            text(f'ALTER TABLE {table} RENAME COLUMN {old_name} TO {new_name}')
        )
        conn.commit()
        logger.info('Renamed %s.%s \u2192 %s', table, old_name, new_name)
    except SQLAlchemyError:
        logger.warning(
            'Could not rename %s.%s \u2192 %s',
            table,
            old_name,
            new_name,
            exc_info=True,
        )


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
            existing_cols = {r[1] for r in info}
            for old_name, new_name in renames.items():
                _rename_column_if_needed(conn, table, old_name, new_name, existing_cols)


def _create_views(engine: Any) -> None:
    """Create database views (Num, Roads, Pan, Pan2) from Views.sql."""
    if not Path(VIEWS_SQL).exists():
        logger.warning('Views.sql not found at %s', VIEWS_SQL)
        return
    with engine.connect() as conn:
        try:
            with Path(VIEWS_SQL).open(encoding='utf-8') as f:
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


def _attach_and_merge_users(engine: Any, auth_path: str) -> None:
    """Attach auth.sqlite, merge missing users, then detach."""
    with engine.connect() as conn:
        conn.execute(text(f"ATTACH DATABASE '{auth_path}' AS auth_db"))
        try:
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
                        'api_key, session_token, email, phone, first_name, last_name, '
                        'created_at, updated_at) '
                        'SELECT id, username, password, active, '
                        'wilaya_code, commune_code, api_key, session_token, '
                        'email, phone, '
                        'first_name, last_name, created_at, updated_at '
                        'FROM auth_db.user'
                    )
                )
                conn.commit()
                logger.info(
                    'Merged %d user(s) from auth.sqlite into main DB',
                    missing,
                )
        finally:
            conn.execute(text('DETACH DATABASE auth_db'))


def _rename_migrated_auth(auth_path: str) -> None:
    """Rename auth.sqlite to auth.sqlite.migrated after successful merge."""
    try:
        Path(auth_path).rename(Path(auth_path + '.migrated'))
        logger.info('Renamed auth.sqlite \u2192 auth.sqlite.migrated')
    except OSError:
        logger.warning('Could not rename auth.sqlite after merge')


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
    if not Path(auth_path).exists():
        return

    try:
        _attach_and_merge_users(engine, str(auth_path))
    except (SQLAlchemyError, OSError):
        logger.warning(
            'Failed to merge users from auth.sqlite',
            exc_info=True,
        )
        return

    _rename_migrated_auth(str(auth_path))
