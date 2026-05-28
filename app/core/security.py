"""Password hashing and JWT secret management."""
import logging
import os
import bcrypt

logger = logging.getLogger(__name__)

_SECRET: str | None = None


def get_jwt_secret() -> str:
    """Return the JWT signing secret from the RNA_JWT_SECRET env var."""
    global _SECRET
    if _SECRET is None:
        secret = os.getenv('RNA_JWT_SECRET')
        if not secret:
            raise RuntimeError(
                "RNA_JWT_SECRET environment variable must be set. "
                "Generate a secret with: "
                "python3 -c \"import secrets; print(secrets.token_hex(32))\""
            )
        _SECRET = secret
    return _SECRET


def hash_password(password: str) -> str:
    """Return a bcrypt hash of *password*."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Return True if *password* matches *hashed_password*."""
    return bcrypt.checkpw(
        password.encode('utf-8'), hashed_password.encode('utf-8')
    )
