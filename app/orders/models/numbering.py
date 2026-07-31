"""Numbering attribute model."""

from __future__ import annotations

import uuid
from typing import ClassVar

from geoalchemy2 import Geometry
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from ...shared.constants import SRID
from .base import _BaseSpatialModel


class Numbering(_BaseSpatialModel):
    """Numbering attribute model."""

    __tablename__ = 'numbering'
    _list_columns: ClassVar[list[str]] = ['value', 'repetition', 'state']
    id = Column(
        Text,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    value = Column(Text, nullable=False, info={'label': 'Number'})
    road_id = Column(
        Text, ForeignKey('road.id'), nullable=True, index=True, info={'label': 'Road'}
    )
    subdivision_id = Column(
        Text,
        ForeignKey('subdivision.id'),
        nullable=True,
        index=True,
        info={'label': 'Subdivision'},
    )
    repetition = Column(String, info={'label': 'Duplicated'})
    state = Column(String, nullable=True, info={'label': 'State'})
    geometry = Column(
        Geometry('POINT', srid=SRID), nullable=True, info={'label': 'Geometry'}
    )
    user_id = Column(
        Text, ForeignKey('user.id'), nullable=True, index=True, info={'label': 'User'}
    )

    road = relationship('Road', backref='numberings', foreign_keys=[road_id])
    subdivision = relationship(
        'Subdivision', backref='numberings', foreign_keys=[subdivision_id]
    )
    user = relationship('User', backref='numberings', foreign_keys=[user_id])

    activity_cat = Column(String, nullable=True)
    activity_type = Column(String, nullable=True)
