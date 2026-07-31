"""Organization / facility spatial model."""

from __future__ import annotations

import uuid
from typing import ClassVar

from geoalchemy2 import Geometry
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import Session, relationship

from ...shared.constants import SRID
from .base import _BaseSpatialModel, _parent_zone_id


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

    def _refresh_derived(self, session: Session) -> None:
        """Recompute the parent zone from the current geometry."""
        self.zone_id = _parent_zone_id(session, self.geometry)

    def delete(self, session: Session) -> None:
        """Delete organization and recalc parent zone has_child."""
        from .zone import Zone

        zone_id = self.zone_id
        session.delete(self)
        session.commit()
        if zone_id:
            Zone._recalc_has_child(session, zone_id)
