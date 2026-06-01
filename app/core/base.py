"""SQLAlchemy declarative base and shared ORM utilities."""
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TimestampMixin:  # pylint: disable=too-few-public-methods
    """Mixin that adds ``created_at`` / ``updated_at`` datetime columns."""
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
    )


def _allowlist_columns(model_class: type, **kwargs: Any) -> dict:
    """Filter kwargs to only include valid column names for the model.

    Accepts both DB column names and Python attribute names. Returns a
    dict keyed by Python attribute names,
    safe for use with ``setattr``.
    """
    col_map: dict[str, str] = {}
    for col in model_class.__table__.columns:  # type: ignore[attr-defined]
        col_map[col.name] = col.name

    try:
        mapper = model_class.__mapper__  # type: ignore[attr-defined]
        for attr in mapper.attrs:
            if hasattr(attr, "columns"):
                for col in attr.columns:
                    col_map[col.name] = attr.key
                    col_map[attr.key] = attr.key
            else:
                col_map[attr.key] = attr.key
    except AttributeError:
        pass

    return {
        python_name: v
        for k, v in kwargs.items()
        if (python_name := col_map.get(k)) is not None
    }
