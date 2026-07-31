"""Subdivision spatial model."""

from __future__ import annotations

import uuid
from typing import ClassVar

from geoalchemy2 import Geometry
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import Session, relationship

from ...shared.constants import SRID
from .base import _BaseSpatialModel, _parent_zone_id


class Subdivision(_BaseSpatialModel):
    """Subdivision spatial model."""

    __tablename__ = 'subdivision'
    _list_columns: ClassVar[list[str]] = ['type', 'name']

    id = Column(
        Text,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    locality_id = Column(String, index=True)
    type = Column(
        String,
        nullable=False,
        info={'label': 'Type', 'label_fr': 'Type', 'label_en': 'Type'},
    )
    name = Column(
        String,
        info={'label': 'Name', 'label_fr': 'Nom', 'label_en': 'Name'},
    )
    name_fr = Column(String, nullable=True)
    name_en = Column(String, nullable=True)
    geometry = Column(Geometry('POLYGON', srid=SRID), nullable=True)
    parent = Column(Text, ForeignKey('zone.id'), nullable=True, index=True)
    user_id = Column(
        Text,
        ForeignKey('user.id'),
        nullable=True,
        index=True,
        info={'label': 'User'},
    )
    user = relationship(
        'User',
        backref='subdivisions',
        foreign_keys=[user_id],
    )

    def _refresh_derived(self, session: Session) -> None:
        """Recompute the parent zone from the current geometry."""
        self.parent = _parent_zone_id(session, self.geometry)

    def delete(self, session: Session) -> None:
        """Delete subdivision and recalc parent zone has_child."""
        from .zone import Zone

        zone_id = self.parent
        session.delete(self)
        session.commit()
        if zone_id:
            Zone._recalc_has_child(session, zone_id)
