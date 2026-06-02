#!/usr/bin/env python3
"""Migrate an old RNA database to the current schema.

Usage:
    python scripts/migrate_db.py /path/to/old.sqlite /path/to/output.sqlite
    python scripts/migrate_db.py /path/to/old.sqlite /path/to/output.sqlite --auth /path/to/auth.sqlite
"""

import argparse
import logging
import sys

# pylint: disable=wrong-import-position,import-error
sys.path.insert(0, '.')

from app.core.migration import migrate_database  # noqa: E402

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Migrate an old RNA database to the current schema.',
    )
    parser.add_argument('old_path', help='Path to the old SQLite database')
    parser.add_argument('new_path', help='Path for the migrated output database')
    parser.add_argument(
        '--auth',
        metavar='AUTH_DB',
        help='Optional standalone auth.sqlite to merge users from',
    )
    args = parser.parse_args()
    try:
        migrate_database(args.old_path, args.new_path, args.auth)
    except FileExistsError:
        logger = logging.getLogger('migrate_db')
        logger.error('Output file already exists: %s', args.new_path)
        sys.exit(1)
