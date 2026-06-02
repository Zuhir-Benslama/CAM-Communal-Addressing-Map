"""Panel sign model."""

import uuid
from typing import Any, Optional

from geoalchemy2 import Geometry
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import Session, relationship

from ...shared.constants import LAYER_FACILITIES, LAYER_ROADS, LAYER_SUBDIVISIONS, SRID
from ...shared.utils import current_locale, locale_value
from .base import _BaseSpatialModel, _get_current_user


class PanelSign(_BaseSpatialModel):
    """Panel sign model."""

    __tablename__ = 'panel_sign'

    id = Column(
        Text,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    dimensions = Column(String, nullable=False, info={'label': 'Dimensions'})
    type = Column(Text, nullable=True, info={'label': 'Reference Type'})
    status = Column(
        String,
        nullable=True,
        info={'label': 'Status'},
    )
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
    organization_id = Column(
        Text,
        ForeignKey('organization.id'),
        nullable=True,
        index=True,
        info={'label': 'Facility'},
    )
    geometry = Column(
        Geometry('POINT', srid=SRID), nullable=True, info={'label': 'Geometry'}
    )
    user_id = Column(
        Text, ForeignKey('user.id'), nullable=True, index=True, info={'label': 'User'}
    )

    organization = relationship(
        'Organization',
        backref='ref_org_pan',
        foreign_keys=[organization_id],
    )
    road = relationship('Road', backref='ref_line_pan', foreign_keys=[road_id])
    subdivision = relationship(
        'Subdivision',
        backref='ref_polychild_pan',
        foreign_keys=[subdivision_id],
    )
    user = relationship('User', backref='user_pan', foreign_keys=[user_id])

    @property
    def label(self) -> str | None:
        """Return a human-readable label based on the referenced entity."""
        loc = current_locale()
        if (
            self.road_id is not None
            and self.subdivision_id is None
            and self.organization_id is None
        ):
            return (
                '\u200f'
                + locale_value(self.road, 'type', loc)
                + ' '
                + locale_value(self.road, 'name', loc)
            )
        if (
            self.road_id is None
            and self.subdivision_id is not None
            and self.organization_id is None
        ):
            return (
                '\u200f'
                + locale_value(self.subdivision, 'type', loc)
                + ' '
                + locale_value(self.subdivision, 'name', loc)
            )
        if (
            self.road_id is None
            and self.subdivision_id is None
            and self.organization_id is not None
        ):
            return (
                '\u200f'
                + locale_value(self.organization, 'type', loc)
                + ' '
                + locale_value(self.organization, 'name', loc)
            )
        return None

    @classmethod
    def update(
        cls, session: Session, record_id: str, **kwargs: Any
    ) -> Optional['PanelSign']:
        """Update panel sign attributes."""
        from ...core.base import _allowlist_columns

        instance = session.query(cls).filter_by(id=record_id).first()
        user_data = _get_current_user()
        if not user_data or not instance:
            raise ValueError('PanelSign not found or no authenticated user')
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.user_id = user_data.get('id')
        session.commit()
        return instance

    def save(self, session: Session) -> None:
        """Validate referenced entities and persist panel sign."""
        from .organization import Organization
        from .road import Road
        from .subdivision import Subdivision

        user_data = _get_current_user()
        if user_data:
            self.user_id = user_data.get('id')
            if self.road_id:
                road = session.query(Road).filter(Road.id == self.road_id).first()
                if not road:
                    raise ValueError(f'Road with id {self.road_id} not found')
                self.type = LAYER_ROADS
            if self.organization_id:
                org = (
                    session.query(Organization)
                    .filter(Organization.id == self.organization_id)
                    .first()
                )
                if not org:
                    raise ValueError(f'Organization {self.organization_id} not found')
                self.type = LAYER_FACILITIES
            if self.subdivision_id:
                sub = (
                    session.query(Subdivision)
                    .filter(Subdivision.id == self.subdivision_id)
                    .first()
                )
                if not sub:
                    raise ValueError(f'Subdivision {self.subdivision_id} not found')
                self.type = LAYER_SUBDIVISIONS
            session.add(self)
            session.commit()
        else:
            raise ValueError('No user found')
