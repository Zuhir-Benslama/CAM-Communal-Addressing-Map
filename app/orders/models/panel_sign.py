"""Panel sign model."""

from __future__ import annotations

import uuid
from typing import Any

from geoalchemy2 import Geometry
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import Session, relationship

from ...shared.constants import LAYER_FACILITIES, LAYER_ROADS, LAYER_SUBDIVISIONS, SRID
from ...shared.utils import current_locale, locale_value
from .base import _BaseSpatialModel


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
        candidates = [
            (self.road_id, self.road, 'road'),
            (self.subdivision_id, self.subdivision, 'subdivision'),
            (self.organization_id, self.organization, 'organization'),
        ]
        active = [(fid, ent) for fid, ent, _ in candidates if fid is not None]
        if len(active) == 1:
            _, entity = active[0]
            return (
                '\u200f'
                + locale_value(entity, 'type', loc)
                + ' '
                + locale_value(entity, 'name', loc)
            )
        return None

    @staticmethod
    def _validate_reference(
        session: Session, model_class: Any, ref_id: str | None, type_label: str
    ) -> str | None:
        """Validate a referenced entity exists and return its type label."""
        if not ref_id:
            return None
        entity = session.query(model_class).filter(model_class.id == ref_id).first()
        if not entity:
            msg = f'{type_label} with id {ref_id} not found'
            raise ValueError(msg)
        return type_label

    def save(self, session: Session) -> None:
        """Validate referenced entities, then persist panel sign."""
        from .organization import Organization
        from .road import Road
        from .subdivision import Subdivision

        refs = [
            (self.road_id, Road, LAYER_ROADS),
            (self.organization_id, Organization, LAYER_FACILITIES),
            (self.subdivision_id, Subdivision, LAYER_SUBDIVISIONS),
        ]
        for ref_id, model_class, type_label in refs:
            found = self._validate_reference(session, model_class, ref_id, type_label)
            if found:
                self.type = found
        super().save(session)
