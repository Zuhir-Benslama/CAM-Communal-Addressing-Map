"""SQLAlchemy declarative base and shared ORM utilities."""
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TimestampMixin:
    """Mixin that adds ``created_at`` / ``updated_at`` datetime columns."""
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def _allowlist_columns(model_class: type, **kwargs: Any) -> dict:
    """Filter kwargs to only include valid column names for the model."""
    valid_columns = {col.name for col in model_class.__table__.columns}
    return {k: v for k, v in kwargs.items() if k in valid_columns}
