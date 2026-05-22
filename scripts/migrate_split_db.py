"""
Migration script: copies existing users from database.sqlite to auth.sqlite.

Run this once after upgrading to the split-database version.
Safe to run multiple times — skips already-migrated users.
"""
import logging
import sys
import os

# Ensure the project root is on sys.path so 'app' is importable
# as a top-level package.
_PKG_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PKG_ROOT not in sys.path:
    sys.path.insert(0, _PKG_ROOT)

from app.users.models import User  # noqa: E402
from app.core.database import get_session, get_auth_engine, get_auth_session  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_users() -> int:
    get_auth_engine()
    spatial_session = get_session()
    auth_session = get_auth_session()
    migrated = 0

    try:
        existing_ids = {
            row[0] for row in auth_session.query(User.id).all()
        }

        spatial_users = spatial_session.query(User).all()

        for user in spatial_users:
            if user.id in existing_ids:
                continue
            migrated += 1
            auth_session.add(User(
                id=user.id,
                username=user.username,
                password=user.password,
                active=user.active,
                affectation_id=user.affectation_id,
                api_key=user.api_key,
                email=user.email,
                phone=user.phone,
                first_name=user.first_name,
                last_name=user.last_name,
            ))
            migrated += 1

        auth_session.commit()
        logger.info("Migrated %d users to auth.sqlite", migrated)
    except Exception:
        auth_session.rollback()
        logger.exception("Migration failed")
        raise
    finally:
        spatial_session.close()
        auth_session.close()

    return migrated


if __name__ == '__main__':
    count = migrate_users()
    print(f"Migrated {count} user(s) to auth.sqlite")
