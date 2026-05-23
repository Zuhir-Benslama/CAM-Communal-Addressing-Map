#!/usr/bin/env python3
"""
Rename old DB column names to new Python-friendly names.

Run this AFTER backing up your database. All old column names
will be gone — the DB will match the Python attribute names.

Usage:
    python scripts/rename_columns.py [--db data/database.sqlite]
"""
import argparse
import logging
import sqlite3
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("rename_columns")

RENAMES: dict[str, list[tuple[str, str]]] = {
    "localite": [
        ("pk_uid", "id"),
        ("codeWilaya", "wilaya_code"),
        ("communeAr", "commune_ar"),
        ("codeCommun", "commune_code"),
    ],
    "refpoly": [
        ("pkuid", "id"),
        ("idLoc", "locality_id"),
        ("uid", "user_id"),
    ],
    "refpolychild": [
        ("pkuid", "id"),
        ("idLoc", "locality_id"),
        ("uid", "user_id"),
    ],
    "RefLine": [
        ("pkuid", "id"),
        ("num_decision", "decision_number"),
        ("idLoc", "locality_id"),
        ("pkuid_poly", "zone_id"),
        ("uid", "user_id"),
    ],
    "reforg": [
        ("pkuid", "id"),
        ("idLoc", "locality_id"),
        ("Cat", "category"),
        ("uid", "user_id"),
        ("pkuid_poly", "zone_id"),
    ],
    "Numerotation": [
        ("pkuid", "id"),
        ("idLine", "road_id"),
        ("idPoly", "subdivision_id"),
        ("uid", "user_id"),
    ],
    "Pannautage": [
        ("pkuid", "id"),
        ("dim", "dimensions"),
        ("Stituation", "situation"),
        ("idLine", "road_id"),
        ("idPoly", "subdivision_id"),
        ("idOrg", "organization_id"),
        ("uid", "user_id"),
    ],
}


def get_existing_columns(cursor: sqlite3.Cursor, table: str) -> set[str]:
    cursor.execute(f'PRAGMA table_info("{table}")')
    return {row[1] for row in cursor.fetchall()}


def rename_columns(db_path: str, dry_run: bool = False) -> None:
    if not dry_run:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = OFF")
        cursor = conn.cursor()
    else:
        conn = None
        cursor = None

    total = 0
    try:
        for table, renames in RENAMES.items():
            existing = (
                set()
                if dry_run
                else get_existing_columns(cursor, table)
            )
            for old_name, new_name in renames:
                if dry_run:
                    logger.info(
                        "  [DRY-RUN] %s.%s → %s", table, old_name, new_name
                    )
                    total += 1
                    continue

                if old_name not in existing:
                    logger.warning(
                        "  %s.%s not found, skipping", table, old_name
                    )
                    continue
                if new_name in existing:
                    logger.warning(
                        "  %s.%s already exists, skipping", table, new_name
                    )
                    continue

                cursor.execute(
                    f'ALTER TABLE "{table}" RENAME COLUMN "{old_name}" TO "{new_name}"'
                )
                logger.info("  %s.%s → %s", table, old_name, new_name)
                total += 1

        if not dry_run:
            conn.commit()
            logger.info("Renamed %d columns in %s", total, db_path)
    except Exception:
        if not dry_run:
            conn.rollback()
        logger.exception("Column rename failed")
        raise
    finally:
        if not dry_run:
            conn.close()

    if dry_run:
        logger.info("[DRY-RUN] Would rename %d columns", total)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rename old DB column names to new Python-friendly names."
    )
    parser.add_argument(
        "--db",
        default=None,
        help="Path to database.sqlite (default: data/database.sqlite)",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be renamed without making changes",
    )
    args = parser.parse_args()

    if args.db:
        db_path = args.db
    else:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(project_root, "data", "database.sqlite")

    logger.info("Database: %s", db_path)
    if args.dry_run:
        logger.info("*** DRY RUN — No changes will be made ***")

    rename_columns(db_path, dry_run=args.dry_run)

    if args.dry_run:
        logger.info("Dry-run complete. Run without --dry-run to apply.")
    else:
        logger.info("Done. Run migrate_production.py to refresh views.")


if __name__ == "__main__":
    import os
    main()
