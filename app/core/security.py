"""Password hashing helpers."""

import logging

import bcrypt

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Return a bcrypt hash of *password*."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Return True if *password* matches *hashed_password*."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
