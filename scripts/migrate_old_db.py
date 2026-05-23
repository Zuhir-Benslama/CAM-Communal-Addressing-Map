#!/usr/bin/env python3
"""
Migration script: upgrades an old-format database.sqlite to the current schema
with split auth database.

Usage:
    python migrate_old_db.py --source path/to/database.sqlite [--auth path/to/auth.sqlite]

If --source is omitted, defaults to 'data/database.sqlite' relative to the
project root.  Safe to run multiple times (idempotent).
"""
import argparse
import os
import sys
import sqlite3
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ADD_COLUMNS = {
    "refpoly": [("has_child", "INTEGER")],
    "Numerotation": [("activity_cat", "TEXT"), ("activity_type", "TEXT")],
    "user": [
        ("first_name", "TEXT"),
        ("last_name", "TEXT"),
        ("email", "TEXT"),
        ("phone", "TEXT"),
    ],
}

VIEWS_SQL = """
create view if not exists Num as
    SELECT n.*, u.affectation_id
    FROM Numerotation n
    JOIN "user" u ON n.uid = u.id;

create view if not exists Roads as
    SELECT
        r.*,
        u.affectation_id,
        CASE
            WHEN r.num_decision IS NOT NULL AND r.num_decision != '' THEN 1
            ELSE 0
        END AS has_decision
    FROM "RefLine" r
    JOIN "user" u ON r.uid = u.id;

create view if not exists Pan as
    SELECT
        p.*,
        o.type || ' ' || o.nom AS org,
        c.type || ' ' || c.nom AS city,
        r.type || ' ' || r.nom AS road,
        u.affectation_id
    FROM Pannautage p
    LEFT JOIN "RefLine" r ON p.idline = r.pkuid
    LEFT JOIN refpolychild c ON p.idPoly = c.pkuid
    LEFT JOIN reforg o ON p.idOrg = o.pkuid
    JOIN "user" u ON p.uid = u.id;

create view if not exists Pan2 as
    select *, COALESCE(city, org, road) as label from Pan;
"""

REQUIRED_TABLES = [
    "refpoly", "Numerotation", "user", "RefLine", "Pannautage", "refpolychild", "reforg"
]


def resolve_project_root() -> str:
    """Return the project root directory containing both data/ and scripts/."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resolve_auth_path(source_path: str, auth_arg: str | None) -> str:
    if auth_arg:
        return os.path.abspath(auth_arg)
    source_dir = os.path.dirname(os.path.abspath(source_path))
    candidate = os.path.join(source_dir, "auth.sqlite")
    if os.path.exists(candidate):
        return candidate
    return os.path.join(resolve_project_root(), "data", "auth.sqlite")


def get_column_names(cursor: sqlite3.Cursor, table: str) -> set:
    cursor.execute(f'PRAGMA table_info("{table}")')
    return {row[1] for row in cursor.fetchall()}


def add_missing_columns(cursor: sqlite3.Cursor) -> None:
    for table, columns in ADD_COLUMNS.items():
        existing = get_column_names(cursor, table)
        for col_name, col_type in columns:
            if col_name not in existing:
                logger.info("Adding column %s.%s (%s)", table, col_name, col_type)
                cursor.execute(
                    f'ALTER TABLE "{table}" ADD COLUMN "{col_name}" {col_type}'
                )
            else:
                logger.debug("Column %s.%s already exists, skipping", table, col_name)


def create_views(cursor: sqlite3.Cursor) -> None:
    for statement in VIEWS_SQL.split(";"):
        stmt = statement.strip()
        if stmt:
            cursor.execute(stmt)
    logger.info("Views created/verified")


def validate_tables(cursor: sqlite3.Cursor) -> list[str]:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing = {row[0] for row in cursor.fetchall()}
    missing = [t for t in REQUIRED_TABLES if t not in existing]
    return missing


def migrate_users(source_path: str, auth_path: str) -> int:
    try:
        auth_conn = sqlite3.connect(auth_path)
        auth_cursor = auth_conn.cursor()
        auth_cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS "user" (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                first_name TEXT,
                last_name TEXT,
                password TEXT,
                active INTEGER,
                affectation_id INTEGER,
                api_key TEXT DEFAULT '',
                email TEXT,
                phone TEXT
            )
            '''
        )
        auth_cursor.execute('SELECT COUNT(*) FROM "user"')
        count = auth_cursor.fetchone()[0]
        if count > 0:
            logger.info("Auth DB already has %d users, skipping migration", count)
            auth_conn.close()
            return 0

        source_conn = sqlite3.connect(source_path)
        source_cursor = source_conn.cursor()
        source_cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='user'"
        )
        if not source_cursor.fetchone():
            logger.info("No user table in source DB, nothing to migrate")
            source_conn.close()
            auth_conn.close()
            return 0

        source_cursor.execute('SELECT * FROM "user"')
        columns = [desc[0] for desc in source_cursor.description]
        rows = source_cursor.fetchall()

        migrated = 0
        for row in rows:
            user_data = dict(zip(columns, row))
            auth_cursor.execute(
                '''
                INSERT OR IGNORE INTO "user"
                    (id, username, first_name, last_name, password, active,
                     affectation_id, api_key, email, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    user_data.get("id"),
                    user_data.get("username"),
                    user_data.get("first_name"),
                    user_data.get("last_name"),
                    user_data.get("password"),
                    user_data.get("active"),
                    user_data.get("affectation_id"),
                    user_data.get("api_key", ""),
                    user_data.get("email"),
                    user_data.get("phone"),
                ),
            )
            if auth_cursor.rowcount > 0:
                migrated += 1

        auth_conn.commit()
        source_conn.close()
        auth_conn.close()
        logger.info("Migrated %d user(s) to auth DB", migrated)
        return migrated
    except Exception:
        logger.exception("User migration failed")
        raise


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upgrade old-format database.sqlite to current schema with split auth DB."
    )
    parser.add_argument(
        "--source", "-s",
        default=None,
        help="Path to source database.sqlite (default: data/database.sqlite in project root)",
    )
    parser.add_argument(
        "--auth", "-a",
        default=None,
        help="Path to target auth.sqlite (default: auto-detected next to source or in data/)",
    )
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()

    if args.source:
        db_path = os.path.abspath(args.source)
    else:
        db_path = os.path.join(resolve_project_root(), "data", "database.sqlite")

    if not os.path.exists(db_path):
        logger.error("Database not found: %s", db_path)
        sys.exit(1)

    auth_path = resolve_auth_path(db_path, args.auth)
    logger.info("Upgrading schema in: %s", db_path)
    logger.info("Auth database: %s", auth_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        missing = validate_tables(cursor)
        if missing:
            logger.error(
                "Source DB missing required tables: %s. Aborting.", ", ".join(missing)
            )
            sys.exit(1)

        add_missing_columns(cursor)
        create_views(cursor)
        conn.commit()
        logger.info("Schema upgrade complete")
    except Exception:
        conn.rollback()
        logger.exception("Schema upgrade failed")
        sys.exit(1)
    finally:
        conn.close()

    migrate_users(db_path, auth_path)
    logger.info("Migration complete")


if __name__ == "__main__":
    main()
