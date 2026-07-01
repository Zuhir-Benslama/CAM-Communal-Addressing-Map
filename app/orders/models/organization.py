"""Organization / facility spatial model."""

from __future__ import annotations

import uuid
from typing import Any, ClassVar

from geoalchemy2 import Geometry
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import Session, relationship

from ...shared.constants import SRID
from .base import _BaseSpatialModel, _get_current_user, _parent_zone_id


class Organization(_BaseSpatialModel):
    """Organization / facility spatial model."""

    __tablename__ = 'organization'
    _list_columns: ClassVar[list[str]] = ['category', 'type', 'name']

    id = Column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    locality_id = Column(String, index=True)
    type = Column(String, nullable=True)
    category = Column(String, nullable=True)
    name = Column(String)
    name_fr = Column(String, nullable=True)
    name_en = Column(String, nullable=True)
    geometry = Column(Geometry('POLYGON', srid=SRID), nullable=True)
    user_id = Column(Text, ForeignKey('user.id'), nullable=True, index=True)
    zone_id = Column(Text, ForeignKey('zone.id'), nullable=True, index=True)
    user = relationship('User', backref='organizations', foreign_keys=[user_id])

    @property
    def cat(self) -> str | None:
        """Return the category value."""
        return self.category

    @classmethod
    def update(
        cls, session: Session, record_id: str, **kwargs: Any
    ) -> Organization | None:
        """Update organization attributes and recalc parent zone."""
        from ...core.base import _allowlist_columns

        instance = session.query(cls).filter_by(id=record_id).first()
        user_data = _get_current_user()
        if not user_data or not instance:
            raise ValueError('Organization not found or no authenticated user')
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.user_id = user_data.get('id')
        instance.locality_id = user_data.get('commune_code')
        instance.zone_id = _parent_zone_id(session, instance.geometry)
        session.commit()
        return instance

    def save(self, session: Session) -> None:
        """Persist organization, linking to user and parent zone."""
        user_data = _get_current_user()
        if not user_data:
            raise ValueError('No user found')
        self.user_id = user_data.get('id')
        self.locality_id = user_data.get('commune_code')
        self.zone_id = _parent_zone_id(session, self.geometry)
        session.add(self)
        session.commit()

    def delete(self, session: Session) -> None:
        """Delete organization and recalc parent zone has_child."""
        from .zone import Zone

        zone_id = self.zone_id
        session.delete(self)
        session.commit()
        if zone_id:
            Zone._recalc_has_child(session, zone_id)
