"""SQLAlchemy declarative base and shared ORM utilities."""
from typing import Any

from sqlalchemy.orm import declarative_base

Base = declarative_base()


def _allowlist_columns(model_class: type, **kwargs: Any) -> dict:
    """Filter kwargs to only include valid column names for the model."""
    valid_columns = {col.name for col in model_class.__table__.columns}
    return {k: v for k, v in kwargs.items() if k in valid_columns}
