"""Core migration logic for converting old-format databases to the
current schema.  Used by both the CLI tool (``scripts/migrate_db.py``)
and the plugin's Import Database feature.
"""

import logging
import os
import sqlite3
from pathlib import Path

from ..shared.utils import validate_safe_name

logger = logging.getLogger(__name__)


COLUMN_MAP = {
    'user': {
        'id': 'id',
        'username': 'username',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'password': 'password',
        'active': 'active',
        'wilaya_code': 'wilaya_code',
        'commune_code': 'commune_code',
        'api_key': 'api_key',
        'email': 'email',
        'phone': 'phone',
    },
    'refpoly': {
        'pkuid': 'id',
        'idLoc': 'locality_id',
        'Type': 'type',
        'Nom': 'name',
        'geometry': 'geometry',
        'has_child': 'has_child',
        'uid': 'user_id',
    },
    'refpolychild': {
        'pkuid': 'id',
        'idLoc': 'locality_id',
        'Type': 'type',
        'Nom': 'name',
        'geometry': 'geometry',
        'parent': 'parent',
        'uid': 'user_id',
    },
    'RefLine': {
        'pkuid': 'id',
        'num_decision': 'decision_number',
        'Type': 'type',
        'Nom': 'name',
        'idLoc': 'locality_id',
        'geometry': 'geometry',
        'pkuid_poly': 'zone_id',
        'uid': 'user_id',
    },
    'reforg': {
        'pkuid': 'id',
        'idLoc': 'locality_id',
        'Type': 'type',
        'Cat': 'category',
        'Nom': 'name',
        'geometry': 'geometry',
        'uid': 'user_id',
        'pkuid_poly': 'zone_id',
    },
    'Numerotation': {
        'pkuid': 'id',
        'valeur': 'value',
        'idLine': 'road_id',
        'idPoly': 'subdivision_id',
        'repetition': 'repetition',
        'etat': 'state',
        'geometry': 'geometry',
        'uid': 'user_id',
        'activity_cat': 'activity_cat',
        'activity_type': 'activity_type',
    },
    'Pannautage': {
        'pkuid': 'id',
        'dim': 'dimensions',
        'Type': 'type',
        'Stituation': 'status',
        'idLine': 'road_id',
        'idPoly': 'subdivision_id',
        'idOrg': 'organization_id',
        'geometry': 'geometry',
        'uid': 'user_id',
    },
}

LOOKUP_TABLE_DDL: dict[str, str] = {}

NEW_TABLES = {
    'user': """
        CREATE TABLE user (
            id TEXT NOT NULL,
            username VARCHAR(255) NOT NULL,
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            password VARCHAR(255),
            active BOOLEAN,
            wilaya_code INTEGER,
            commune_code VARCHAR(255),
            api_key TEXT,
            session_token TEXT,
            email VARCHAR(255),
            phone VARCHAR(255),
            created_at DATETIME,
            updated_at DATETIME,
            PRIMARY KEY (id),
            UNIQUE (username)
        )
    """,
    'zone': """
        CREATE TABLE zone (
            id TEXT NOT NULL,
            locality_id VARCHAR,
            type VARCHAR NOT NULL,
            name VARCHAR,
            name_fr TEXT,
            name_en TEXT,
            has_child BOOLEAN NOT NULL DEFAULT 0,
            user_id TEXT,
            created_at DATETIME,
            updated_at DATETIME,
            PRIMARY KEY (id),
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
    """,
    'subdivision': """
        CREATE TABLE subdivision (
            id TEXT NOT NULL,
            locality_id VARCHAR,
            type VARCHAR NOT NULL,
            name VARCHAR,
            name_fr TEXT,
            name_en TEXT,
            parent TEXT,
            user_id TEXT,
            created_at DATETIME,
            updated_at DATETIME,
            PRIMARY KEY (id),
            FOREIGN KEY (parent) REFERENCES zone(id),
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
    """,
    'road': """
        CREATE TABLE road (
            id TEXT NOT NULL,
            decision_number TEXT,
            type VARCHAR NOT NULL,
            name VARCHAR,
            name_fr TEXT,
            name_en TEXT,
            locality_id VARCHAR NOT NULL,
            zone_id TEXT,
            user_id TEXT,
            created_at DATETIME,
            updated_at DATETIME,
            PRIMARY KEY (id),
            FOREIGN KEY (zone_id) REFERENCES zone(id),
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
    """,
    'organization': """
        CREATE TABLE organization (
            id TEXT NOT NULL,
            locality_id VARCHAR,
            type VARCHAR,
            category VARCHAR,
            name VARCHAR,
            name_fr TEXT,
            name_en TEXT,
            user_id TEXT,
            zone_id TEXT,
            created_at DATETIME,
            updated_at DATETIME,
            PRIMARY KEY (id),
            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (zone_id) REFERENCES zone(id)
        )
    """,
    'numbering': """
        CREATE TABLE numbering (
            id TEXT NOT NULL,
            value TEXT NOT NULL,
            road_id TEXT,
            subdivision_id TEXT,
            repetition VARCHAR,
            state VARCHAR,
            user_id TEXT,
            activity_cat VARCHAR,
            activity_type VARCHAR,
            created_at DATETIME,
            updated_at DATETIME,
            PRIMARY KEY (id),
            FOREIGN KEY (road_id) REFERENCES road(id),
            FOREIGN KEY (subdivision_id) REFERENCES subdivision(id),
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
    """,
    'panel_sign': """
        CREATE TABLE panel_sign (
            id TEXT NOT NULL,
            dimensions VARCHAR NOT NULL,
            type TEXT,
            status VARCHAR,
            road_id TEXT,
            subdivision_id TEXT,
            organization_id TEXT,
            user_id TEXT,
            created_at DATETIME,
            updated_at DATETIME,
            PRIMARY KEY (id),
            FOREIGN KEY (road_id) REFERENCES road(id),
            FOREIGN KEY (subdivision_id) REFERENCES subdivision(id),
            FOREIGN KEY (organization_id) REFERENCES organization(id),
            FOREIGN KEY (user_id) REFERENCES user(id)
        )
    """,
}

SPATIALITE_LIB = os.environ.get(
    'SPATIALITE_LIB',
    '/usr/libspatialite50/lib/mod_spatialite.so',
)

GEOMETRY_TYPES = {
    'zone': ('POLYGON', 4326, 2, 3),
    'subdivision': ('POLYGON', 4326, 2, 3),
    'road': ('LINESTRING', 4326, 2, 2),
    'organization': ('POLYGON', 4326, 2, 3),
    'numbering': ('POINT', 4326, 2, 1),
    'panel_sign': ('POINT', 4326, 2, 1),
}


def init_spatialite(conn: sqlite3.Connection) -> None:
    """Initialize SpatiaLite metadata in the new database."""
    conn.enable_load_extension(True)
    conn.load_extension(SPATIALITE_LIB)
    conn.execute('SELECT InitSpatialMetadata(1)')


def register_geometry(
    conn: sqlite3.Connection,
    table: str,
    col: str,
    geom_config: tuple,
) -> None:
    """Register a geometry column using AddGeometryColumn."""
    validate_safe_name(table)
    validate_safe_name(col)
    geom_type, srid, dims = geom_config[:3]
    conn.execute(
        'SELECT AddGeometryColumn(?, ?, ?, ?, ?)',
        (table, col, srid, geom_type, dims),
    )


def create_spatial_index(conn: sqlite3.Connection, table: str, col: str) -> None:
    """Create a spatial R-tree index."""
    validate_safe_name(table)
    validate_safe_name(col)
    conn.execute('SELECT CreateSpatialIndex(?, ?)', (table, col))


def _migrate_lookup_tables(old: sqlite3.Connection, new: sqlite3.Connection) -> None:
    """Copy lookup table data from old to new database."""
    for name, ddl in LOOKUP_TABLE_DDL.items():
        validate_safe_name(name)
        new.execute(ddl)
        old_cur = old.execute(f'SELECT * FROM "{name}"')  # nosec S608 - name validated by validate_safe_name()
        old_rows = old_cur.fetchall()
        if old_rows:
            cols = [desc[0] for desc in old_cur.description]
            placeholders = ','.join('?' for _ in cols)
            col_list = ','.join(f'"{c}"' for c in cols)
            for row in old_rows:
                new.execute(
                    f'INSERT INTO "{name}" ({col_list}) VALUES ({placeholders})',  # nosec S608 - name validated by validate_safe_name()
                    tuple(row[c] for c in cols),
                )
            logger.info('  %s: %d rows', name, len(old_rows))
        else:
            logger.info('  %s: 0 rows (skipped)', name)


def _register_geometry_columns(new: sqlite3.Connection) -> None:
    """Register geometry columns for all spatial tables."""
    for table, geom_config in GEOMETRY_TYPES.items():
        try:
            register_geometry(new, table, 'geometry', geom_config)
        except sqlite3.OperationalError:
            logger.exception('  %s.geometry registration failed', table)


def _migrate_data(old: sqlite3.Connection, new: sqlite3.Connection) -> None:
    """Copy table data from old to new database."""
    for table, col_map in COLUMN_MAP.items():
        old_cols = list(col_map.keys())
        new_cols = list(col_map.values())

        validate_safe_name(table)
        old_rows = old.execute(f'SELECT * FROM "{table}"').fetchall()  # nosec S608 - table validated by validate_safe_name()
        if not old_rows:
            logger.info('  %s: 0 rows (skipped)', table)
            continue

        placeholders = ','.join('?' for _ in new_cols)
        new_col_list = ','.join(f'"{c}"' for c in new_cols)

        migrated = 0
        for row in old_rows:
            try:
                values = [row[old_c] for old_c in old_cols]
                new.execute(
                    f'INSERT INTO "{table}" ({new_col_list}) VALUES ({placeholders})',  # nosec S608 - table validated by validate_safe_name()
                    values,
                )
                migrated += 1
            except (sqlite3.OperationalError, ValueError, IndexError) as e:
                logger.warning(
                    '  %s row %s: %s',
                    table,
                    row.get('pkuid', row.get('id', '?')),
                    e,
                )
        logger.info('  %s: %d / %d rows migrated', table, migrated, len(old_rows))


def _create_spatial_indexes(new: sqlite3.Connection) -> None:
    """Create spatial indexes for all geometry columns."""
    for table in GEOMETRY_TYPES:
        try:
            create_spatial_index(new, table, 'geometry')
            logger.info('  %s.geometry: index created', table)
        except sqlite3.OperationalError:
            logger.exception('  %s.geometry index creation failed', table)


def _merge_auth_users(new_path: str, auth_path: str | None) -> None:
    """Merge users from a standalone auth database into the new DB.

    Used when the old setup had a separate ``auth.sqlite`` file.  Users
    whose ``id`` already exists in the target are skipped.
    """
    if not auth_path or not Path(auth_path).exists():
        logger.info('  auth file not found: %s (skipped)', auth_path)
        return

    auth = sqlite3.connect(auth_path)
    auth.row_factory = sqlite3.Row
    try:
        cur = auth.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='user'"
        )
        if not cur.fetchone():
            logger.info('  auth DB has no user table (skipped)')
            return

        users = auth.execute('SELECT * FROM user').fetchall()
        if not users:
            logger.info('  auth DB: 0 users (skipped)')
            return

        target = sqlite3.connect(new_path)
        try:
            cols = users[0].keys()
            placeholders = ','.join('?' for _ in cols)
            col_list = ','.join(f'"{c}"' for c in cols)
            merged = 0
            for row in users:
                try:
                    target.execute(
                        f'INSERT OR IGNORE INTO user ({col_list}) '  # nosec S608 - user is a fixed table name
                        f'VALUES ({placeholders})',
                        tuple(row[c] for c in cols),
                    )
                    if target.total_changes > 0:
                        merged += 1
                except (sqlite3.OperationalError, ValueError) as e:
                    logger.warning('  user %s: %s', row['id'], e)
            target.commit()
            logger.info('  Merged %d user(s) from %s', merged, auth_path)
        finally:
            target.close()
    finally:
        auth.close()


def migrate_database(
    old_path: str,
    new_path: str,
    auth_path: str | None = None,
) -> None:
    """Migrate *old_path* (old-format database) to *new_path* (current
    schema).

    If *auth_path* points to a standalone ``auth.sqlite`` file its users
    are merged into the migrated database.

    Raises ``FileExistsError`` if *new_path* already exists.
    """
    if Path(new_path).exists():
        msg = f'Output already exists: {new_path}'
        raise FileExistsError(msg)

    old = sqlite3.connect(old_path)
    old.row_factory = sqlite3.Row
    new = sqlite3.connect(new_path)
    try:
        new.execute('PRAGMA foreign_keys = OFF')
        new.execute('PRAGMA journal_mode = WAL')

        logger.info('Initializing SpatiaLite metadata...')
        init_spatialite(new)

        logger.info('Creating lookup tables...')
        _migrate_lookup_tables(old, new)

        logger.info('Creating spatial tables...')
        for table, ddl in NEW_TABLES.items():
            new.execute(ddl)
            logger.info('  Created %s', table)

        logger.info('Registering geometry columns...')
        _register_geometry_columns(new)

        logger.info('Copying data...')
        _migrate_data(old, new)

        new.commit()

        logger.info('Creating spatial indexes...')
        _create_spatial_indexes(new)

        _merge_auth_users(new_path, auth_path)

        new.execute('PRAGMA foreign_keys = ON')
        new.commit()
        logger.info('Migration complete: %s', new_path)
    finally:
        new.close()
        old.close()
