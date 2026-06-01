"""Numbering attribute model."""
import uuid
from typing import Any, Optional

from geoalchemy2 import Geometry
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import Session, relationship

from ...shared.constants import SRID
from .base import _BaseSpatialModel, _get_current_user


class Numbering(_BaseSpatialModel):
    """Numbering attribute model."""

    __tablename__ = 'numbering'
    _list_columns = ['value', 'repetition', 'state']
    id = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    value = Column(Text, nullable=False, info={'label': 'Number'})
    road_id = Column(Text, ForeignKey('road.id'), nullable=True, index=True,
                     info={'label': 'Road'})
    subdivision_id = Column(
        Text, ForeignKey('subdivision.id'), nullable=True, index=True,
        info={'label': 'Subdivision'},
    )
    repetition = Column(String, info={'label': 'Duplicated'})
    state = Column(String, nullable=True,
                   info={'label': 'State'})
    geometry = Column(Geometry('POINT', srid=SRID), nullable=True,
                      info={'label': 'Geometry'})
    user_id = Column(Text, ForeignKey('user.id'), nullable=True, index=True,
                     info={'label': 'User'})

    road = relationship("Road", backref="ref_line_num", foreign_keys=[road_id])
    subdivision = relationship("Subdivision",
                               backref="ref_polychild_num",
                               foreign_keys=[subdivision_id])
    user = relationship("User", backref="user_num", foreign_keys=[user_id])

    activity_cat = Column(String, nullable=True)
    activity_type = Column(String, nullable=True)

    @classmethod
    def update(cls, session: Session, record_id: str,
               **kwargs: Any) -> Optional['Numbering']:
        """Update numbering attributes."""
        from ...core.base import _allowlist_columns
        instance = session.query(cls).filter_by(id=record_id).first()
        user_data = _get_current_user()
        if not user_data or not instance:
            raise ValueError("Numbering not found or no authenticated user")
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.user_id = user_data.get('id')
        session.commit()
        return instance

    def save(self, session: Session) -> None:
        """Persist numbering, linking to the current user."""
        user_data = _get_current_user()
        if user_data:
            self.user_id = user_data.get('id')
            session.add(self)
            session.commit()
        else:
            raise ValueError("No user found")
