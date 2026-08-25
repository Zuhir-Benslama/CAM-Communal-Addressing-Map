"""Road spatial model."""

from __future__ import annotations

import uuid
from typing import ClassVar

from geoalchemy2 import Geometry
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import Session, relationship

from ...shared.constants import SRID
from .base import _BaseSpatialModel, _has_child_entities, _parent_zone_id


class Road(_BaseSpatialModel):
    """Road spatial model."""

    __tablename__ = 'road'
    _list_columns: ClassVar[list[str]] = ['type', 'name', 'decision_number']

    id = Column(
        Text,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    decision_number = Column(
        Text,
        nullable=True,
        info={
            'label': 'Decision No.',
            'label_fr': 'N° décision',
            'label_en': 'Decision No.',
        },
    )
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
    locality_id = Column(
        String,
        nullable=False,
        index=True,
    )
    geometry = Column(Geometry('LINESTRING', srid=SRID), nullable=True)
    zone_id = Column(Text, ForeignKey('zone.id'), nullable=True, index=True)
    user_id = Column(Text, ForeignKey('user.id'), nullable=True, index=True)
    user = relationship('User', backref='roads', foreign_keys=[user_id])

    def _refresh_derived(self, session: Session) -> None:
        """Recompute parent zone and has_child flag from the current geometry."""
        self.zone_id = _parent_zone_id(session, self.geometry)
        self.has_child = _has_child_entities(session, self.geometry)

    def delete(self, session: Session) -> None:
        """Delete road and recalc parent zone has_child."""
        from .zone import Zone

        zone_id = self.zone_id
        session.delete(self)
        session.commit()
        if zone_id:
            Zone._recalc_has_child(session, zone_id)  # pylint: disable=protected-access
