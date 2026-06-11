"""Subdivision spatial model."""

import uuid
from typing import Any, ClassVar, Optional

from geoalchemy2 import Geometry
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import Session, relationship

from ...shared.constants import SRID
from .base import _BaseSpatialModel, _get_current_user, _parent_zone_id


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
        backref='user_poly_child',
        foreign_keys=[user_id],
    )

    @classmethod
    def update(
        cls, session: Session, record_id: str, **kwargs: Any
    ) -> Optional['Subdivision']:
        """Update subdivision attributes and recalc parent zone."""
        from ...core.base import _allowlist_columns

        instance = session.query(cls).filter_by(id=record_id).first()
        user_data = _get_current_user()
        if not user_data or not instance:
            raise ValueError('Subdivision not found or no authenticated user')
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.user_id = user_data.get('id')
        instance.locality_id = user_data.get('commune_code')
        instance.parent = _parent_zone_id(session, instance.geometry)
        session.commit()
        return instance

    def save(self, session: Session) -> None:
        """Persist subdivision, linking to user and parent zone."""
        user_data = _get_current_user()
        if not user_data:
            raise ValueError('No user found')
        self.user_id = user_data.get('id')
        self.locality_id = user_data.get('commune_code')
        self.parent = _parent_zone_id(session, self.geometry)
        session.add(self)
        session.commit()

    def delete(self, session: Session) -> None:
        """Delete subdivision and recalc parent zone has_child."""
        from .zone import Zone

        zone_id = self.parent
        session.delete(self)
        session.commit()
        if zone_id:
            Zone._recalc_has_child(session, zone_id)
