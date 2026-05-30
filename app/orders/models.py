"""SQLAlchemy models for spatial entities (zones, roads, etc.)."""
# mypy: disable-error-code="assignment,arg-type,return-value"
import uuid
import logging
from typing import Any, ClassVar, List, Optional

from sqlalchemy import (
    Column, String, Text, Boolean, ForeignKey,
)
from sqlalchemy.orm import relationship, Session
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_Within

from ..core.base import Base, TimestampMixin, _allowlist_columns
from ..shared.constants import (
    SRID, LAYER_ROADS, LAYER_FACILITIES, LAYER_SUBDIVISIONS,
)
from ..shared.utils import current_locale, locale_value


def _get_current_user():
    """Return the currently authenticated user dict, or None."""
    from ..users.repository import get_current_user
    return get_current_user()


def _parent_zone_id(session: Session, geometry: Any) -> Optional[str]:
    """Return the ID of the Zone that contains *geometry*, or None."""
    try:
        zone = session.query(Zone).filter(
            ST_Within(geometry, Zone.geometry)
        ).first()
        return zone.id if zone else None
    except Exception:
        logger.warning("parent zone lookup failed", exc_info=True)
        return None


def _has_child_entities(session: Session, zone_geometry: Any) -> bool:
    """Check if any Road, Organization, or Subdivision lies inside the zone."""
    try:
        for cls in (Road, Organization, Subdivision):
            if session.query(cls).filter(
                ST_Within(cls.geometry, zone_geometry)
            ).first():
                return True
    except Exception:
        logger.warning("has_child check failed", exc_info=True)
    return False


logger = logging.getLogger(__name__)


class _BaseSpatialModel(Base, TimestampMixin):
    """Base class for spatial models providing shared CRUD operations.

    Subclasses override :attr:`_list_columns` to control which columns
    appear in :meth:`list_all`.
    """
    __abstract__ = True

    _list_columns: ClassVar[List[str]] = []

    @property
    def username(self) -> Optional[str]:
        """Return the related user's username, or None."""
        if self.user_id:
            return self.user.username
        return None

    @classmethod
    def list_all(cls, session: Session) -> dict:
        """Query all rows, returning only columns listed in _list_columns."""
        columns = [column for column in cls.__table__.columns
                   if column.name in cls._list_columns]
        return {'data': session.query(*columns).all(), "cols": columns}

    def delete(self, session: Session) -> None:
        """Delete this instance via *session* and commit."""
        session.delete(self)
        session.commit()


class Zone(_BaseSpatialModel):
    """Spatial zone (polygon) model."""

    __tablename__ = 'zone'
    _list_columns = ['type', 'name']

    id = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    locality_id = Column(
        String, index=True,
        info={'label': 'Location'},
    )
    type = Column(
        String, nullable=False,
        info={'label': 'Type', 'label_fr': 'Type', 'label_en': 'Type'},
    )
    name = Column(
        String,
        info={'label': 'Name', 'label_fr': 'Nom', 'label_en': 'Name'},
    )
    name_fr = Column(String, nullable=True)
    name_en = Column(String, nullable=True)
    geometry = Column(Geometry('POLYGON', srid=SRID), nullable=False,
                      info={'label': 'Geometry'})
    has_child = Column(Boolean, default=False, nullable=False)
    user_id = Column(Text, ForeignKey('user.id'), nullable=True, index=True,
                     info={'label': 'User'})
    user = relationship("User", backref="user_poly", foreign_keys=[user_id])

    @classmethod
    def update(cls, session: Session, id: str,
               **kwargs: Any) -> Optional['Zone']:
        """Update zone attributes and recalc has_child."""

        instance = session.query(cls).filter_by(id=id).first()
        user_data = _get_current_user()
        if not user_data or not instance:
            raise ValueError("Zone not found or no authenticated user")
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.user_id = user_data.get('id')
        instance.locality_id = user_data.get('commune_code')
        instance.has_child = _has_child_entities(session, instance.geometry)
        session.commit()
        return instance

    @classmethod
    def _recalc_has_child(cls, session: Session,
                          zone_id: str) -> None:
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
            raise ValueError("No user found")
        self.user_id = user_data.get('id')
        self.locality_id = user_data.get('commune_code')
        self.has_child = _has_child_entities(session, self.geometry)
        session.add(self)
        session.commit()


class Subdivision(_BaseSpatialModel):
    """Subdivision spatial model."""

    __tablename__ = 'subdivision'
    _list_columns = ['type', 'name']

    id = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    locality_id = Column(String, index=True)
    type = Column(
        String, nullable=False,
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
        Text, ForeignKey('user.id'), nullable=True, index=True,
        info={'label': 'User'},
    )
    user = relationship(
        "User", backref="user_poly_child", foreign_keys=[user_id],
    )

    @classmethod
    def update(cls, session: Session, id: str,
               **kwargs: Any) -> Optional['Subdivision']:
        """Update subdivision attributes and recalc parent zone."""
        instance = session.query(cls).filter_by(id=id).first()
        user_data = _get_current_user()
        if not user_data or not instance:
            raise ValueError("Subdivision not found or no authenticated user")
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
            raise ValueError("No user found")
        self.user_id = user_data.get('id')
        self.locality_id = user_data.get('commune_code')
        self.parent = _parent_zone_id(session, self.geometry)
        session.add(self)
        session.commit()

    def delete(self, session: Session) -> None:
        """Delete subdivision and recalc parent zone has_child."""
        zone_id = self.parent
        session.delete(self)
        session.commit()
        if zone_id:
            Zone._recalc_has_child(session, zone_id)


class Road(_BaseSpatialModel):
    """Road spatial model."""

    __tablename__ = 'road'
    _list_columns = ['type', 'name', 'decision_number']

    id = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    decision_number = Column(
        Text, nullable=True,
        info={
            'label': 'Decision No.',
            'label_fr': 'N° décision',
            'label_en': 'Decision No.',
        },
    )
    type = Column(
        String, nullable=False,
        info={'label': 'Type', 'label_fr': 'Type', 'label_en': 'Type'},
    )
    name = Column(
        String,
        info={'label': 'Name', 'label_fr': 'Nom', 'label_en': 'Name'},
    )
    name_fr = Column(String, nullable=True)
    name_en = Column(String, nullable=True)
    locality_id = Column(
        String, nullable=False, index=True,
    )
    geometry = Column(Geometry('LINESTRING', srid=SRID), nullable=True)
    zone_id = Column(Text, ForeignKey('zone.id'), nullable=True, index=True)
    user_id = Column(Text, ForeignKey('user.id'), nullable=True, index=True)
    user = relationship("User", backref="user_line", foreign_keys=[user_id])

    @classmethod
    def update(cls, session: Session, id: str,
               **kwargs: Any) -> Optional['Zone']:
        """Update zone attributes and recalc has_child."""
        instance = session.query(cls).filter_by(id=id).first()
        user_data = _get_current_user()
        if not user_data or not instance:
            raise ValueError("Zone not found or no authenticated user")
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.user_id = user_data.get('id')
        instance.locality_id = user_data.get('commune_code')
        instance.has_child = _has_child_entities(session, instance.geometry)
        session.commit()
        return instance

    @classmethod
    def _recalc_has_child(cls, session: Session,
                          zone_id: str) -> None:
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
            raise ValueError("No user found")
        self.user_id = user_data.get('id')
        self.locality_id = user_data.get('commune_code')
        self.zone_id = _parent_zone_id(session, self.geometry)
        session.add(self)
        session.commit()

    def delete(self, session: Session) -> None:
        """Delete road and recalc parent zone has_child."""
        zone_id = self.zone_id
        session.delete(self)
        session.commit()
        if zone_id:
            Zone._recalc_has_child(session, zone_id)


class Organization(_BaseSpatialModel):
    """Organization / facility spatial model."""

    __tablename__ = 'organization'
    _list_columns = ['category', 'type', 'name']

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
    user = relationship("User", backref="user_org", foreign_keys=[user_id])

    @property
    def cat(self) -> Optional[str]:
        """Return the category value."""
        return self.category

    @classmethod
    def update(cls, session: Session, id: str,
               **kwargs: Any) -> Optional['Organization']:
        """Update organization attributes and recalc parent zone."""
        instance = session.query(cls).filter_by(id=id).first()
        user_data = _get_current_user()
        if not user_data or not instance:
            raise ValueError("Organization not found or no authenticated user")
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.user_id = user_data.get('id')
        instance.locality_id = user_data.get('commune_code')
        instance.zone_id = _parent_zone_id(session, instance.geometry)
        session.commit()
        return instance

    def save(self, session: Session) -> None:
        """Persist organization, linking to user and parent zone."""
        user_data = _get_current_user()
        if not user_data:
            raise ValueError("No user found")
        self.user_id = user_data.get('id')
        self.locality_id = user_data.get('commune_code')
        self.zone_id = _parent_zone_id(session, self.geometry)
        session.add(self)
        session.commit()

    def delete(self, session: Session) -> None:
        """Delete organization and recalc parent zone has_child."""
        zone_id = self.zone_id
        session.delete(self)
        session.commit()
        if zone_id:
            Zone._recalc_has_child(session, zone_id)


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
    def update(cls, session: Session, id: str,
               **kwargs: Any) -> Optional['Numbering']:
        """Update numbering attributes."""
        instance = session.query(cls).filter_by(id=id).first()
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


class PanelSign(_BaseSpatialModel):
    """Panel sign model."""

    __tablename__ = 'panel_sign'

    id = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    dimensions = Column(String, nullable=False,
                        info={'label': 'Dimensions'})
    type = Column(Text, nullable=True, info={'label': 'Reference Type'})
    status = Column(
        String, nullable=True,
        info={'label': 'Status'},
    )
    road_id = Column(Text, ForeignKey('road.id'), nullable=True, index=True,
                     info={'label': 'Road'})
    subdivision_id = Column(
        Text, ForeignKey('subdivision.id'), nullable=True, index=True,
        info={'label': 'Subdivision'},
    )
    organization_id = Column(
        Text, ForeignKey('organization.id'), nullable=True, index=True,
        info={'label': 'Facility'},
    )
    geometry = Column(Geometry('POINT', srid=SRID), nullable=True,
                      info={'label': 'Geometry'})
    user_id = Column(Text, ForeignKey('user.id'), nullable=True, index=True,
                     info={'label': 'User'})

    organization = relationship(
        "Organization",
        backref="ref_org_pan",
        foreign_keys=[organization_id],
    )
    road = relationship("Road", backref="ref_line_pan", foreign_keys=[road_id])
    subdivision = relationship(
        "Subdivision",
        backref="ref_polychild_pan",
        foreign_keys=[subdivision_id],
    )
    user = relationship("User", backref="user_pan", foreign_keys=[user_id])

    @property
    def label(self) -> Optional[str]:
        """Return a human-readable label based on the referenced entity."""
        loc = current_locale()
        if self.road_id is not None and self.subdivision_id is None \
                and self.organization_id is None:
            return ('\u200F' + locale_value(self.road, 'type', loc) +
                    ' ' + locale_value(self.road, 'name', loc))
        if self.road_id is None and self.subdivision_id is not None \
                and self.organization_id is None:
            return ('\u200F' + locale_value(self.subdivision, 'type', loc) +
                    ' ' + locale_value(self.subdivision, 'name', loc))
        if self.road_id is None and self.subdivision_id is None \
                and self.organization_id is not None:
            return ('\u200F' + locale_value(self.organization, 'type', loc) +
                    ' ' + locale_value(self.organization, 'name', loc))
        return None

    @classmethod
    def update(cls, session: Session, id: str,
               **kwargs: Any) -> Optional['PanelSign']:
        """Update panel sign attributes."""
        instance = session.query(cls).filter_by(id=id).first()
        user_data = _get_current_user()
        if not user_data or not instance:
            raise ValueError("PanelSign not found or no authenticated user")
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.user_id = user_data.get('id')
        session.commit()
        return instance

    def save(self, session: Session) -> None:
        """Validate referenced entities and persist panel sign."""
        user_data = _get_current_user()
        if user_data:
            self.user_id = user_data.get('id')
            if self.road_id:
                road = (
                    session.query(Road)
                    .filter(Road.id == self.road_id)
                    .first()
                )
                if not road:
                    raise ValueError(
                        f"Road with id {self.road_id} not found"
                    )
                self.type = LAYER_ROADS
            if self.organization_id:
                org = (
                    session.query(Organization)
                    .filter(Organization.id == self.organization_id)
                    .first()
                )
                if not org:
                    raise ValueError(
                        f"Organization {self.organization_id} not found"
                    )
                self.type = LAYER_FACILITIES
            if self.subdivision_id:
                sub = (
                    session.query(Subdivision)
                    .filter(Subdivision.id == self.subdivision_id)
                    .first()
                )
                if not sub:
                    raise ValueError(
                        f"Subdivision {self.subdivision_id} not found"
                    )
                self.type = LAYER_SUBDIVISIONS
            session.add(self)
            session.commit()
        else:
            raise ValueError("No user found")
