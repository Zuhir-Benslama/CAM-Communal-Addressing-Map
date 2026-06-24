"""Road spatial model."""

import uuid
from typing import Any, ClassVar, Optional

from geoalchemy2 import Geometry
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import Session, relationship

from ...shared.constants import SRID
from .base import (
    _BaseSpatialModel,
    _get_current_user,
    _has_child_entities,
    _parent_zone_id,
)


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

    @classmethod
    def update(
        cls, session: Session, record_id: str, **kwargs: Any
    ) -> Optional['Road']:
        """Update zone attributes and recalc has_child."""
        from ...core.base import _allowlist_columns

        instance = session.query(cls).filter_by(id=record_id).first()
        user_data = _get_current_user()
        if not user_data or not instance:
            raise ValueError('Road not found or no authenticated user')
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.user_id = user_data.get('id')
        instance.locality_id = user_data.get('commune_code')
        instance.has_child = _has_child_entities(session, instance.geometry)
        session.commit()
        return instance

    @classmethod
    def _recalc_has_child(cls, session: Session, zone_id: str) -> None:
        """Recalculate has_child flag for a road's parent zone."""
        instance = session.query(cls).filter_by(id=zone_id).first()
        if not instance:
            return
        instance.has_child = _has_child_entities(session, instance.geometry)
        session.commit()

    def save(self, session: Session) -> None:
        """Persist road, linking to user and parent zone."""
        user_data = _get_current_user()
        if not user_data:
            raise ValueError('No user found')
        self.user_id = user_data.get('id')
        self.locality_id = user_data.get('commune_code')
        self.zone_id = _parent_zone_id(session, self.geometry)
        session.add(self)
        session.commit()

    def delete(self, session: Session) -> None:
        """Delete road and recalc parent zone has_child."""
        from .zone import Zone

        zone_id = self.zone_id
        session.delete(self)
        session.commit()
        if zone_id:
            Zone._recalc_has_child(session, zone_id)  # pylint: disable=protected-access
