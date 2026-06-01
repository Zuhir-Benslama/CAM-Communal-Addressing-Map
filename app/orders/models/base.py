"""Base class and shared helpers for spatial models."""
import logging
from typing import Any, ClassVar

from geoalchemy2.functions import ST_Within
from sqlalchemy.orm import Session

from ...core.base import Base, TimestampMixin

logger = logging.getLogger(__name__)


def _get_current_user():
    """Return the currently authenticated user dict, or None."""
    from ...users.repository import get_current_user
    return get_current_user()


def _parent_zone_id(session: Session, geometry: Any) -> str | None:
    """Return the ID of the Zone that contains *geometry*, or None."""
    from .zone import Zone
    try:
        zone = session.query(Zone).filter(
            ST_Within(geometry, Zone.geometry)
        ).first()
        return zone.id if zone else None
    except Exception:  # pylint: disable=W0718
        logger.warning("parent zone lookup failed", exc_info=True)
        return None


def _has_child_entities(session: Session, zone_geometry: Any) -> bool:
    """Check if any Road, Organization, or Subdivision lies inside the zone."""
    from .organization import Organization
    from .road import Road
    from .subdivision import Subdivision
    try:
        for cls in (Road, Organization, Subdivision):
            if session.query(cls).filter(
                ST_Within(cls.geometry, zone_geometry)
            ).first():
                return True
    except Exception:  # pylint: disable=W0718
        logger.warning("has_child check failed", exc_info=True)
    return False


class _BaseSpatialModel(Base, TimestampMixin):
    """Base class for spatial models providing shared CRUD operations.

    Subclasses override :attr:`_list_columns` to control which columns
    appear in :meth:`list_all`.
    """
    __abstract__ = True

    _list_columns: ClassVar[list[str]] = []

    @property
    def username(self) -> str | None:
        """Return the related user's username, or None."""
        if self.user_id:
            return self.user.username
        return None

    @classmethod
    def list_all(cls, session: Session) -> dict:
        """Query all rows, returning only columns listed in _list_columns."""
        columns = [column for column in cls.__table__.columns
                   if column.name in cls._list_columns]
        return {'data': session.query(*columns).all(), "cols": columns}

    def delete(self, session: Session) -> None:
        """Delete this instance via *session* and commit."""
        session.delete(self)
        session.commit()
