"""Zone spatial model."""

import uuid
from typing import Any, ClassVar, Optional

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.orm import Session, relationship

from ...core.base import _allowlist_columns
from ...shared.constants import SRID
from .base import _BaseSpatialModel, _get_current_user, _has_child_entities


class Zone(_BaseSpatialModel):
    """Spatial zone (polygon) model."""

    __tablename__ = 'zone'
    _list_columns: ClassVar[list[str]] = ['type', 'name']

    id = Column(
        Text,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    locality_id = Column(
        String,
        index=True,
        info={'label': 'Location'},
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
    geometry = Column(
        Geometry('POLYGON', srid=SRID), nullable=False, info={'label': 'Geometry'}
    )
    has_child = Column(Boolean, default=False, nullable=False)
    user_id = Column(
        Text, ForeignKey('user.id'), nullable=True, index=True, info={'label': 'User'}
    )
    user = relationship('User', backref='user_poly', foreign_keys=[user_id])

    @classmethod
    def update(
        cls, session: Session, record_id: str, **kwargs: Any
    ) -> Optional['Zone']:
        """Update zone attributes and recalc has_child."""

        instance = session.query(cls).filter_by(id=record_id).first()
        user_data = _get_current_user()
        if not user_data or not instance:
            raise ValueError('Zone not found or no authenticated user')
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.user_id = user_data.get('id')
        instance.locality_id = user_data.get('commune_code')
        instance.has_child = _has_child_entities(session, instance.geometry)
        session.commit()
        return instance

    @classmethod
    def _recalc_has_child(cls, session: Session, zone_id: str) -> None:
        """Recalculate has_child for a zone based on actual spatial data."""
        zone = session.query(cls).filter_by(id=zone_id).first()
        if not zone:
            return
        zone.has_child = _has_child_entities(session, zone.geometry)
        session.commit()

    def save(self, session: Session) -> None:
        """Persist zone, linking to user and locality."""
        user_data = _get_current_user()
        if not user_data:
            raise ValueError('No user found')
        self.user_id = user_data.get('id')
        self.locality_id = user_data.get('commune_code')
        self.has_child = _has_child_entities(session, self.geometry)
        session.add(self)
        session.commit()
