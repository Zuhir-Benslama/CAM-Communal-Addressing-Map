"""SQLAlchemy models for spatial entities (zones, roads, etc.)."""
# mypy: disable-error-code="assignment,arg-type,return-value"
import uuid
import logging
from typing import Any, ClassVar, List, Optional

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey,
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


class Localite(Base, TimestampMixin):
    """Municipality / locality spatial model."""

    __tablename__ = 'localite'
    id = Column(Integer, primary_key=True, autoincrement=True)
    wilaya = Column(Text, nullable=False)
    wilaya_code = Column(Integer, nullable=False)
    commune_ar = Column(Text, nullable=False)
    commune_fr = Column(Text, nullable=True)
    commune_en = Column(Text, nullable=True)
    commune_code = Column(Text, nullable=False)
    geometry = Column(Geometry(geometry_type='GEOMETRY', srid=SRID))

    def save(self, session: Session) -> None:
        """Persist this locality via *session* and commit."""
        session.add(self)
        session.commit()


class Zone(_BaseSpatialModel):
    """Spatial zone (polygon) model — refpoly in the DB."""

    __tablename__ = 'refpoly'
    _list_columns = ['Type', 'Nom']

    id = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    locality_id = Column(
        String, ForeignKey('localite.id'), index=True,
        info={'label': 'Location'},
    )
    Type = Column(
        String, nullable=False,
        info={'label': 'Type', 'label_fr': 'Type', 'label_en': 'Type'},
    )
    Nom = Column(
        String,
        info={'label': 'Name', 'label_fr': 'Nom', 'label_en': 'Name'},
    )
    Nom_fr = Column(String, nullable=True)
    Nom_en = Column(String, nullable=True)
    geometry = Column(Geometry('POLYGON', srid=SRID), nullable=False,
                      info={'label': 'Geometry'})
    has_child = Column(Boolean, default=False, nullable=False)
    user_id = Column(Text, ForeignKey('user.id'), nullable=True, index=True,
                     info={'label': 'User'})
    user = relationship("User", backref="user_poly", foreign_keys=[user_id])

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Zone']:
        """Update zone attributes and recalc has_child."""

        instance = session.query(cls).filter_by(id=pkuid).first()
        user_data = _get_current_user()
        if not user_data or not instance:
            raise ValueError("Zone not found or no authenticated user")
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.user_id = user_data.get('id')
        instance.locality_id = user_data.get('loc')
        instance.has_child = _has_child_entities(session, instance.geometry)
        session.commit()
        return instance

    @classmethod
    def _recalc_has_child(cls, session: Session,
                          zone_pkuid: str) -> None:
        """Recalculate has_child for a zone based on actual spatial data."""
        zone = session.query(cls).filter_by(id=zone_pkuid).first()
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
        self.locality_id = user_data.get('loc')
        self.has_child = _has_child_entities(session, self.geometry)
        session.add(self)
        session.commit()


class Subdivision(_BaseSpatialModel):
    """Subdivision (referred to as refpolychild in the DB)."""

    __tablename__ = 'refpolychild'
    _list_columns = ['Type', 'Nom']

    id = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    locality_id = Column(String, ForeignKey('localite.id'), index=True)
    Type = Column(
        String, nullable=False,
        info={'label': 'Type', 'label_fr': 'Type', 'label_en': 'Type'},
    )
    Nom = Column(
        String,
        info={'label': 'Name', 'label_fr': 'Nom', 'label_en': 'Name'},
    )
    Nom_fr = Column(String, nullable=True)
    Nom_en = Column(String, nullable=True)
    geometry = Column(Geometry('POLYGON', srid=SRID), nullable=True)
    parent = Column(Text, ForeignKey('refpoly.id'), nullable=True, index=True)
    user_id = Column(
        Text, ForeignKey('user.id'), nullable=True, index=True,
        info={'label': 'User'},
    )
    user = relationship(
        "User", backref="user_poly_child", foreign_keys=[user_id],
    )

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Subdivision']:
        """Update subdivision attributes and recalc parent zone."""
        instance = session.query(cls).filter_by(id=pkuid).first()
        user_data = _get_current_user()
        if not user_data or not instance:
            raise ValueError("Subdivision not found or no authenticated user")
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.user_id = user_data.get('id')
        instance.locality_id = user_data.get('loc')
        instance.parent = _parent_zone_id(session, instance.geometry)
        session.commit()
        return instance

    def save(self, session: Session) -> None:
        """Persist subdivision, linking to user and parent zone."""
        user_data = _get_current_user()
        if not user_data:
            raise ValueError("No user found")
        self.user_id = user_data.get('id')
        self.locality_id = user_data.get('loc')
        self.parent = _parent_zone_id(session, self.geometry)
        session.add(self)
        session.commit()

    def delete(self, session: Session) -> None:
        """Delete subdivision and recalc parent zone has_child."""
        zone_pkuid = self.parent
        session.delete(self)
        session.commit()
        if zone_pkuid:
            Zone._recalc_has_child(session, zone_pkuid)


class Road(_BaseSpatialModel):
    """Road spatial model (RefLine in the DB)."""

    __tablename__ = 'RefLine'
    _list_columns = ['Type', 'Nom', 'decision_number']

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
    Type = Column(
        String, nullable=False,
        info={'label': 'Type', 'label_fr': 'Type', 'label_en': 'Type'},
    )
    Nom = Column(
        String,
        info={'label': 'Name', 'label_fr': 'Nom', 'label_en': 'Name'},
    )
    Nom_fr = Column(String, nullable=True)
    Nom_en = Column(String, nullable=True)
    locality_id = Column(
        String, ForeignKey('localite.id'), nullable=False, index=True,
    )
    geometry = Column(Geometry('LINESTRING', srid=SRID), nullable=True)
    zone_id = Column(Text, ForeignKey('refpoly.id'), nullable=True, index=True)
    user_id = Column(Text, ForeignKey('user.id'), nullable=True, index=True)
    user = relationship("User", backref="user_line", foreign_keys=[user_id])

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Zone']:
        """Update zone attributes and recalc has_child."""
        instance = session.query(cls).filter_by(id=pkuid).first()
        user_data = _get_current_user()
        if not user_data or not instance:
            raise ValueError("Zone not found or no authenticated user")
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.user_id = user_data.get('id')
        instance.locality_id = user_data.get('loc')
        instance.has_child = _has_child_entities(session, instance.geometry)
        session.commit()
        return instance

    @classmethod
    def _recalc_has_child(cls, session: Session,
                          zone_pkuid: str) -> None:
        """Recalculate has_child flag for a road's parent zone."""
        instance = session.query(cls).filter_by(id=zone_pkuid).first()
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
        self.locality_id = user_data.get('loc')
        self.zone_id = _parent_zone_id(session, self.geometry)
        session.add(self)
        session.commit()

    def delete(self, session: Session) -> None:
        """Delete road and recalc parent zone has_child."""
        zone_pkuid = self.zone_id
        session.delete(self)
        session.commit()
        if zone_pkuid:
            Zone._recalc_has_child(session, zone_pkuid)


class Organization(_BaseSpatialModel):
    """Organization / facility spatial model (reforg in the DB)."""

    __tablename__ = 'reforg'
    _list_columns = ['category', 'Type', 'Nom']

    id = Column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    locality_id = Column(String, ForeignKey('localite.id'), index=True)
    Type = Column(String, nullable=True)
    category = Column(String, nullable=True)
    Nom = Column(String)
    Nom_fr = Column(String, nullable=True)
    Nom_en = Column(String, nullable=True)
    geometry = Column(Geometry('POLYGON', srid=SRID), nullable=True)
    user_id = Column(Text, ForeignKey('user.id'), nullable=True, index=True)
    zone_id = Column(Text, ForeignKey('refpoly.id'), nullable=True, index=True)
    user = relationship("User", backref="user_org", foreign_keys=[user_id])

    @property
    def cat(self) -> Optional[str]:
        """Return the category value."""
        return self.category

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Organization']:
        """Update organization attributes and recalc parent zone."""
        instance = session.query(cls).filter_by(id=pkuid).first()
        user_data = _get_current_user()
        if not user_data or not instance:
            raise ValueError("Organization not found or no authenticated user")
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.user_id = user_data.get('id')
        instance.locality_id = user_data.get('loc')
        instance.zone_id = _parent_zone_id(session, instance.geometry)
        session.commit()
        return instance

    def save(self, session: Session) -> None:
        """Persist organization, linking to user and parent zone."""
        user_data = _get_current_user()
        if not user_data:
            raise ValueError("No user found")
        self.user_id = user_data.get('id')
        self.locality_id = user_data.get('loc')
        self.zone_id = _parent_zone_id(session, self.geometry)
        session.add(self)
        session.commit()

    def delete(self, session: Session) -> None:
        """Delete organization and recalc parent zone has_child."""
        zone_pkuid = self.zone_id
        session.delete(self)
        session.commit()
        if zone_pkuid:
            Zone._recalc_has_child(session, zone_pkuid)


class Numbering(_BaseSpatialModel):
    """Numbering attribute model (Numerotation in the DB)."""

    __tablename__ = 'Numerotation'
    _list_columns = ['valeur', 'repetition', 'etat']
    id = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    valeur = Column(Text, nullable=False, info={'label': 'Number'})
    road_id = Column(Text, ForeignKey('RefLine.id'), nullable=True, index=True,
                     info={'label': 'Road'})
    subdivision_id = Column(
        Text, ForeignKey('refpolychild.id'), nullable=True, index=True,
        info={'label': 'Subdivision'},
    )
    repetition = Column(String, info={'label': 'Duplicated'})
    etat = Column(String, nullable=True,
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
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Numbering']:
        """Update numbering attributes."""
        instance = session.query(cls).filter_by(id=pkuid).first()
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
    """Panel sign model (Pannautage in the DB)."""

    __tablename__ = 'Pannautage'

    id = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    dimensions = Column(String, nullable=False,
                        info={'label': 'Dimensions'})
    Type = Column(Text, nullable=True, info={'label': 'Reference Type'})
    situation = Column(
        String, nullable=True,
        info={'label': 'Status'},
    )
    road_id = Column(Text, ForeignKey('RefLine.id'), nullable=True, index=True,
                     info={'label': 'Road'})
    subdivision_id = Column(
        Text, ForeignKey('refpolychild.id'), nullable=True, index=True,
        info={'label': 'Subdivision'},
    )
    organization_id = Column(
        Text, ForeignKey('reforg.id'), nullable=True, index=True,
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
            return ('\u200F' + locale_value(self.road, 'Type', loc) +
                    ' ' + locale_value(self.road, 'Nom', loc))
        if self.road_id is None and self.subdivision_id is not None \
                and self.organization_id is None:
            return ('\u200F' + locale_value(self.subdivision, 'Type', loc) +
                    ' ' + locale_value(self.subdivision, 'Nom', loc))
        if self.road_id is None and self.subdivision_id is None \
                and self.organization_id is not None:
            return ('\u200F' + locale_value(self.organization, 'Type', loc) +
                    ' ' + locale_value(self.organization, 'Nom', loc))
        return None

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['PanelSign']:
        """Update panel sign attributes."""
        instance = session.query(cls).filter_by(id=pkuid).first()
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
                        f"Road with pkuid {self.road_id} not found"
                    )
                self.Type = LAYER_ROADS
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
                self.Type = LAYER_FACILITIES
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
                self.Type = LAYER_SUBDIVISIONS
            session.add(self)
            session.commit()
        else:
            raise ValueError("No user found")
