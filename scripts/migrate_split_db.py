"""
Migration script: copies existing users from database.sqlite to auth.sqlite.

Run this once after upgrading to the split-database version.
Safe to run multiple times — skips already-migrated users.
"""
import logging
import sys
import os

try:
    from models import User, get_session, get_auth_engine, get_auth_session
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from models import User, get_session, get_auth_engine, get_auth_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_users() -> int:
    get_auth_engine()
    spatial_session = get_session()
    auth_session = get_auth_session()
    count = 0

    try:
        existing_ids = {
            row[0] for row in auth_session.query(User.id).all()
        }

        spatial_users = spatial_session.query(User).all()

        for user in spatial_users:
            if user.id in existing_ids:
                continue
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
            count += 1

        auth_session.commit()
        logger.info("Migrated %d users to auth.sqlite", count)
    except Exception:
        auth_session.rollback()
        logger.exception("Migration failed")
        raise
    finally:
        spatial_session.close()
        auth_session.close()

    return count


if __name__ == '__main__':
    count = migrate_users()
    print(f"Migrated {count} user(s) to auth.sqlite")
