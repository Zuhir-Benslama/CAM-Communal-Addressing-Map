"""Base class and shared helpers for spatial models."""

import logging
from typing import Any, ClassVar

from geoalchemy2.functions import ST_Within
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ...core.base import Base, TimestampMixin, _allowlist_columns

logger = logging.getLogger(__name__)


def _get_current_user() -> Any:
    """Return the currently authenticated user dict, or None."""
    from ...users.repository import get_current_user

    return get_current_user()


def _parent_zone_id(session: Session, geometry: Any) -> str | None:
    """Return the ID of the Zone that contains *geometry*, or None."""
    from .zone import Zone

    try:
        zone = session.query(Zone).filter(ST_Within(geometry, Zone.geometry)).first()
        return zone.id if zone else None
    except SQLAlchemyError:
        logger.warning('parent zone lookup failed', exc_info=True)
        return None


def _has_child_entities(session: Session, zone_geometry: Any) -> bool:
    """Check if any Road, Organization, or Subdivision lies inside the zone."""
    from .organization import Organization
    from .road import Road
    from .subdivision import Subdivision

    try:
        for cls in (Road, Organization, Subdivision):
            if (
                session.query(cls)
                .filter(ST_Within(cls.geometry, zone_geometry))
                .first()
            ):
                return True
    except SQLAlchemyError:
        logger.warning('has_child check failed', exc_info=True)
    return False


class _BaseSpatialModel(Base, TimestampMixin):
    """Base class for spatial models providing shared CRUD operations.

    Subclasses override :attr:`_list_columns` to control which columns
    appear in :meth:`list_all`.

    Subclasses are automatically registered in :attr:`_registry` via
    ``__init_subclass__``.  The abstract base itself is excluded.
    """

    __abstract__ = True

    _registry: ClassVar[list[type['_BaseSpatialModel']]] = []
    _list_columns: ClassVar[list[str]] = []

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        cls._registry.append(cls)

    @property
    def username(self) -> str | None:
        """Return the related user's username, or None."""
        if self.user_id:
            return self.user.username
        return None

    def delete(self, session: Session) -> None:
        """Delete this instance via *session* and commit."""
        session.delete(self)
        session.commit()

    @classmethod
    def update(
        cls, session: Session, record_id: str, **kwargs: Any
    ) -> '_BaseSpatialModel | None':
        """Update record attributes and refresh derived columns."""
        instance = session.query(cls).filter_by(id=record_id).first()
        user_data = _get_current_user()
        if not user_data or not instance:
            raise ValueError(f'{cls.__name__} not found or no authenticated user')
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.user_id = user_data.get('id')
        if hasattr(instance, 'locality_id'):
            instance.locality_id = user_data.get('commune_code')
        instance._refresh_derived(session)
        session.commit()
        return instance

    def save(self, session: Session) -> None:
        """Persist this instance, linking to the current user."""
        user_data = _get_current_user()
        if not user_data:
            raise ValueError('No user found')
        self.user_id = user_data.get('id')
        if hasattr(self, 'locality_id'):
            self.locality_id = user_data.get('commune_code')
        self._refresh_derived(session)
        session.add(self)
        session.commit()

    def _refresh_derived(self, session: Session) -> None:
        """Hook for subclasses to recompute derived columns before commit."""
