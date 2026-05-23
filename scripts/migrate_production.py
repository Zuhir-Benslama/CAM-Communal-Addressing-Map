#!/usr/bin/env python3
"""
Production-ready migration script: upgrades an old monolithic database.sqlite
to the split-database architecture (auth.sqlite + database.sqlite).

Usage:
    # Default: migrates data/database.sqlite in place, creates data/auth.sqlite
    python scripts/migrate_production.py

    # Specify paths explicitly
    python scripts/migrate_production.py \\
        --source /path/to/old/database.sqlite \\
        --auth /path/to/new/auth.sqlite \\
        --db /path/to/new/database.sqlite

    # Dry-run: check what would be done without making changes
    python scripts/migrate_production.py --dry-run

    # Custom backup directory
    python scripts/migrate_production.py --backup-dir /tmp/migration-backups

Safe to run multiple times — all operations are idempotent.
"""
import argparse
import logging
import os
import sqlite3
import shutil
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("migrate_production")

REQUIRED_TABLES = [
    "refpoly", "Numerotation", "user", "RefLine",
    "Pannautage", "refpolychild", "reforg",
]

ADD_COLUMNS = {
    "localite": [
        ("commune_fr", "TEXT"),
        ("commune_en", "TEXT"),
    ],
    "refpoly": [
        ("has_child", "INTEGER DEFAULT 0"),
        ("Nom_fr", "TEXT"),
        ("Nom_en", "TEXT"),
    ],
    "refpolychild": [
        ("Nom_fr", "TEXT"),
        ("Nom_en", "TEXT"),
    ],
    "RefLine": [
        ("Nom_fr", "TEXT"),
        ("Nom_en", "TEXT"),
    ],
    "reforg": [
        ("Nom_fr", "TEXT"),
        ("Nom_en", "TEXT"),
    ],
    "Numerotation": [("activity_cat", "TEXT"), ("activity_type", "TEXT")],
    "user": [
        ("first_name", "TEXT"),
        ("last_name", "TEXT"),
        ("email", "TEXT"),
        ("phone", "TEXT"),
    ],
}

_VIEW_NAMES = ['Num', 'Roads', 'Pan', 'Pan2']

AUTH_USER_SCHEMA = """
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
"""


def resolve_project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_backup(source_path: str, backup_dir: str | None = None) -> str:
    if backup_dir is None:
        backup_dir = os.path.join(
            resolve_project_root(), "data", "backups"
        )
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    basename = os.path.basename(source_path)
    backup_path = os.path.join(
        backup_dir, f"{basename}.{timestamp}.bak"
    )
    shutil.copy2(source_path, backup_path)
    size_mb = os.path.getsize(backup_path) / (1024 * 1024)
    logger.info("Backup created: %s (%.1f MB)", backup_path, size_mb)
    return backup_path


def get_column_names(cursor: sqlite3.Cursor, table: str) -> set:
    cursor.execute(f'PRAGMA table_info("{table}")')
    return {row[1] for row in cursor.fetchall()}


def validate_source(source_path: str) -> None:
    if not os.path.exists(source_path):
        logger.error("Source database not found: %s", source_path)
        sys.exit(1)

    size_mb = os.path.getsize(source_path) / (1024 * 1024)
    logger.info("Source database: %s (%.1f MB)", source_path, size_mb)

    conn = sqlite3.connect(source_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing = {row[0] for row in cursor.fetchall()}
        missing = [t for t in REQUIRED_TABLES if t not in existing]
        if missing:
            logger.warning(
                "Source DB missing tables (may not be a valid RNA database): %s",
                ", ".join(missing),
            )
        else:
            logger.info("All required tables present (%d tables found)", len(existing))

        for table in (t for t in REQUIRED_TABLES if t in existing):
            cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
            count = cursor.fetchone()[0]
            logger.info("  %-20s %d rows", table, count)
    finally:
        conn.close()


def upgrade_schema(source_path: str, dry_run: bool = False) -> None:
    logger.info(
        "%s schema upgrade on: %s",
        "Would perform" if dry_run else "Performing",
        source_path,
    )
    if dry_run:
        conn = sqlite3.connect(source_path)
        cursor = conn.cursor()
        try:
            for table, columns in ADD_COLUMNS.items():
                existing = get_column_names(cursor, table)
                for col_name, col_type in columns:
                    if col_name not in existing:
                        logger.info("  [DRY-RUN] Would add: %s.%s (%s)", table, col_name, col_type)
                    else:
                        logger.debug("  Column %s.%s exists, skipping", table, col_name)
        finally:
            conn.close()
        return

    conn = sqlite3.connect(source_path)
    cursor = conn.cursor()
    try:
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

        conn.commit()
        logger.info("Schema upgrade complete")
    except Exception:
        conn.rollback()
        logger.exception("Schema upgrade failed")
        raise
    finally:
        conn.close()


def create_views(source_path: str, dry_run: bool = False) -> None:
    project_root = resolve_project_root()
    views_path = os.path.join(project_root, "data", "Views.sql")
    logger.info(
        "%s views on: %s",
        "Would create" if dry_run else "Creating",
        source_path,
    )
    if dry_run:
        for name in _VIEW_NAMES:
            logger.info("  [DRY-RUN] Would create view: %s", name)
        return

    conn = sqlite3.connect(source_path)
    try:
        with open(views_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        logger.info("Views created/verified")
    except Exception:
        conn.rollback()
        logger.exception("View creation failed")
        raise
    finally:
        conn.close()


def migrate_users(
    source_path: str,
    auth_path: str,
    dry_run: bool = False,
) -> int:
    logger.info(
        "%s users from %s → %s",
        "Would migrate" if dry_run else "Migrating",
        source_path,
        auth_path,
    )
    if dry_run:
        conn = sqlite3.connect(source_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
            if cursor.fetchone():
                cursor.execute('SELECT COUNT(*) FROM "user"')
                count = cursor.fetchone()[0]
                logger.info("  [DRY-RUN] Source has %d user(s) to migrate", count)
            else:
                logger.info("  [DRY-RUN] No user table in source, nothing to migrate")
        finally:
            conn.close()
        return 0

    try:
        auth_conn = sqlite3.connect(auth_path)
        auth_cursor = auth_conn.cursor()
        auth_cursor.execute(AUTH_USER_SCHEMA)

        auth_cursor.execute('SELECT COUNT(*) FROM "user"')
        existing_count = auth_cursor.fetchone()[0]
        if existing_count > 0:
            logger.info(
                "Auth DB already has %d user(s), verifying completeness",
                existing_count,
            )

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
                """
                INSERT OR IGNORE INTO "user"
                    (id, username, first_name, last_name, password, active,
                     affectation_id, api_key, email, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
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
        logger.info("Migrated %d new user(s) to auth DB", migrated)
        return migrated
    except Exception:
        logger.exception("User migration failed")
        raise


def verify_migration(source_path: str, auth_path: str) -> None:
    logger.info("=== Migration Verification ===")

    source_conn = sqlite3.connect(source_path)
    source_cursor = source_conn.cursor()
    try:
        source_cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        views = [row[0] for row in source_cursor.fetchall()]
        expected_views = {"Num", "Roads", "Pan", "Pan2"}
        missing_views = expected_views - set(views)
        if missing_views:
            logger.warning("Missing views: %s", ", ".join(missing_views))
        else:
            logger.info("All 4 views present: %s", ", ".join(views))

        for table in REQUIRED_TABLES:
            source_cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
            count = source_cursor.fetchone()[0]
            logger.info("  Table %-20s %d rows", table, count)
    finally:
        source_conn.close()

    auth_conn = sqlite3.connect(auth_path)
    auth_cursor = auth_conn.cursor()
    try:
        auth_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if auth_cursor.fetchone():
            auth_cursor.execute('SELECT COUNT(*) FROM "user"')
            count = auth_cursor.fetchone()[0]
            logger.info("Auth DB has %d user(s)", count)
        else:
            logger.warning("Auth DB has no user table!")
    finally:
        auth_conn.close()

    logger.info("=== Verification Complete ===")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migrate old monolithic database.sqlite to split-database architecture.",
    )
    parser.add_argument(
        "--source", "-s",
        default=None,
        help="Path to old-format database.sqlite (default: data/database.sqlite)",
    )
    parser.add_argument(
        "--auth", "-a",
        default=None,
        help="Path to target auth.sqlite (default: data/auth.sqlite next to source)",
    )
    parser.add_argument(
        "--backup-dir",
        default=None,
        help="Directory for backups (default: data/backups/)",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--skip-backup",
        action="store_true",
        help="Skip creating a backup of the source database",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip post-migration verification",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    project_root = resolve_project_root()

    if args.source:
        source_path = os.path.abspath(args.source)
    else:
        source_path = os.path.join(project_root, "data", "database.sqlite")

    if args.auth:
        auth_path = os.path.abspath(args.auth)
    else:
        source_dir = os.path.dirname(os.path.abspath(source_path))
        candidate = os.path.join(source_dir, "auth.sqlite")
        if not os.path.exists(candidate):
            candidate = os.path.join(project_root, "data", "auth.sqlite")
        auth_path = candidate

    logger.info("=" * 50)
    logger.info("RNA Database Migration")
    logger.info("=" * 50)
    logger.info("Source DB:  %s", source_path)
    logger.info("Target Auth: %s", auth_path)
    if args.dry_run:
        logger.info("*** DRY RUN — No changes will be made ***")
    logger.info("")

    if not os.path.exists(source_path):
        logger.error("Source database not found: %s", source_path)
        logger.error(
            "Specify a different path with --source or copy your "
            "old database.sqlite to data/"
        )
        sys.exit(1)

    validate_source(source_path)

    if not args.skip_backup and not args.dry_run:
        create_backup(source_path, args.backup_dir)

    upgrade_schema(source_path, dry_run=args.dry_run)
    create_views(source_path, dry_run=args.dry_run)
    migrate_users(source_path, auth_path, dry_run=args.dry_run)

    if not args.skip_verify and not args.dry_run:
        logger.info("")
        verify_migration(source_path, auth_path)

    logger.info("")
    if args.dry_run:
        logger.info("Dry-run complete. Run without --dry-run to apply changes.")
    else:
        logger.info("Migration complete.")
        logger.info("Your old database.sqlite has been upgraded in-place.")
        logger.info("Users have been copied to: %s", auth_path)
        logger.info(
            "A backup was created in: %s",
            args.backup_dir or os.path.join(project_root, "data", "backups"),
        )


if __name__ == "__main__":
    main()
