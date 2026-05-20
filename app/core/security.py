import os
import bcrypt
import logging

logger = logging.getLogger(__name__)

JWT_SECRET = os.getenv('RNA_JWT_SECRET')
if not JWT_SECRET:
    raise RuntimeError(
        "RNA_JWT_SECRET environment variable must be set. "
        "Generate a secret with: "
        "python3 -c \"import secrets; print(secrets.token_hex(32))\""
    )


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password.encode('utf-8'), hashed_password.encode('utf-8')
    )
