"""Spatial SQLAlchemy models for the addressing plans database."""

import uuid
import logging
from typing import Any, Optional

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey,
    ForeignKeyConstraint,
)
from sqlalchemy.orm import relationship, Session
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_Within

try:
    from .base import Base, _allowlist_columns, get_current_user
except ImportError:
    from models.base import Base, _allowlist_columns, get_current_user

try:
    from ..constants import (
        SRID, LAYER_ROADS, LAYER_FACILITIES, LAYER_SUBDIVISIONS,
    )
except ImportError:
    from constants import (
        SRID, LAYER_ROADS, LAYER_FACILITIES, LAYER_SUBDIVISIONS,
    )

logger = logging.getLogger(__name__)


class Localite(Base):
    """Model for municipalities (localite table)."""
    __tablename__ = 'localite'
    pk_uid = Column(Integer, primary_key=True, autoincrement=True)
    wilaya = Column(Text, nullable=False)
    codeWilaya = Column(Integer, nullable=False)
    communeAr = Column(Text, nullable=False)
    codeCommun = Column(Text, nullable=False)
    geometry = Column(Geometry(geometry_type='GEOMETRY', srid=SRID))

    def save(self, session: Session) -> None:
        """Persists the localite instance to the database."""
        session.add(self)
        session.commit()


class Zone(Base):
    """Spatial model for zones (refpoly table)."""
    __tablename__ = 'refpoly'

    pkuid = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'المفتاح'},
    )
    idLoc = Column(String, ForeignKey('localite.pk_uid'),
                   info={'label': 'الموقع'})
    Type = Column(String, ForeignKey('type_zone.pk'), nullable=False,
                  info={'label': 'نوع'})
    Nom = Column(String, info={'label': 'اسم'})
    geometry = Column(Geometry('POLYGON', srid=SRID), nullable=False,
                      info={'label': 'شكل هندسي'})
    has_child = Column(Boolean)
    uid = Column(Text, ForeignKey('user.id'), nullable=True,
                 info={'label': 'مستخدم'})
    user = relationship("User", backref="user_poly", foreign_keys=[uid])

    @property
    def username(self) -> Optional[str]:
        """Returns the username of the user who created the zone."""
        if self.uid:
            return self.user.username
        return None

    def delete(self, session: Session) -> None:
        """Deletes the zone instance from the database."""
        session.delete(self)
        session.commit()

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Zone']:
        """Updates a zone with the given kwargs and sets spatial context."""
        instance = session.query(cls).filter_by(pkuid=pkuid).first()
        user_data = get_current_user()
        if not user_data or not instance:
            raise ValueError("Zone not found or no authenticated user")
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.uid = user_data.get('id')
        instance.idLoc = user_data.get('loc')
        instance.has_child = False
        try:
            query = session.query(Road).filter(
                ST_Within(Road.geometry, instance.geometry)
            ).first()
            if query:
                instance.has_child = True
            query = session.query(Organization).filter(
                ST_Within(Organization.geometry, instance.geometry)
            ).first()
            if query:
                instance.has_child = True
            query = session.query(Subdivision).filter(
                ST_Within(Subdivision.geometry, instance.geometry)
            ).first()
            if query:
                instance.has_child = True
        except Exception:
            logger.warning("Failed to set has_child on %s",
                           instance, exc_info=True)
            instance.has_child = False
        session.commit()
        return instance

    def save(self, session: Session) -> None:
        """Persists a new zone with spatial context from the current user."""
        user_data = get_current_user()
        if user_data:
            self.uid = user_data.get('id')
            self.idLoc = user_data.get('loc')
            self.has_child = False
            query = session.query(Road).filter(
                ST_Within(Road.geometry, self.geometry)
            ).first()
            if query:
                self.has_child = True
            query = session.query(Organization).filter(
                ST_Within(Organization.geometry, self.geometry)
            ).first()
            if query:
                self.has_child = True
            query = session.query(Subdivision).filter(
                ST_Within(Subdivision.geometry, self.geometry)
            ).first()
            if query:
                self.has_child = True
            session.add(self)
            session.commit()
        else:
            raise ValueError("No user found")


class Subdivision(Base):
    """Spatial model for subdivisions (refpolychild table)."""
    __tablename__ = 'refpolychild'

    pkuid = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'المفتاح'},
    )
    idLoc = Column(String, ForeignKey('localite.pk_uid'))
    Type = Column(String, ForeignKey('type_cite.pk'), nullable=False,
                  info={'label': 'نوع'})
    Nom = Column(String, info={'label': 'اسم'})
    geometry = Column(Geometry('POLYGON', srid=SRID), nullable=True)
    parent = Column(Text, ForeignKey('refpoly.pkuid'), nullable=True)
    uid = Column(Text, ForeignKey('user.id'), nullable=True,
                 info={'label': 'مستخدم'})
    user = relationship("User", backref="user_poly_child", foreign_keys=[uid])

    @property
    def username(self) -> Optional[str]:
        """Returns the username of the user who created the subdivision."""
        if self.uid:
            return self.user.username
        return None

    @classmethod
    def list_all(cls, session: Session) -> dict:
        """Lists all subdivisions with allowed columns."""
        allowed_columns = ['Type', 'Nom']
        columns = [column for column in cls.__table__.columns
                   if column.name in allowed_columns]
        return {'data': session.query(*columns).all(), "cols": columns}

    def delete(self, session: Session) -> None:
        """Deletes the subdivision instance from the database."""
        session.delete(self)
        session.commit()

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Subdivision']:
        """Updates a subdivision with the given kwargs
        and sets spatial context."""
        instance = session.query(cls).filter_by(pkuid=pkuid).first()
        user_data = get_current_user()
        if not user_data or not instance:
            raise ValueError("Subdivision not found or no authenticated user")
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.uid = user_data.get('id')
        instance.idLoc = user_data.get('loc')
        instance.parent = None
        try:
            query = session.query(Zone).filter(
                ST_Within(instance.geometry, Zone.geometry)
            ).first()
            if query:
                instance.parent = query.pkuid
        except Exception:
            logger.warning("Failed to set parent on %s",
                           instance, exc_info=True)
            instance.parent = None
        session.commit()
        return instance

    def save(self, session: Session) -> None:
        """Persists a new subdivision with spatial context
        from the current user."""
        user_data = get_current_user()
        if user_data:
            self.uid = user_data.get('id')
            self.idLoc = user_data.get('loc')
            query = session.query(Zone).filter(
                ST_Within(self.geometry, Zone.geometry)
            ).first()
            if query:
                self.parent = query.pkuid
            session.add(self)
            session.commit()
        else:
            raise ValueError("No user found")


class Road(Base):
    """Spatial model for roads (RefLine table)."""
    __tablename__ = 'RefLine'
    pkuid = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'المفتاح'},
    )
    num_decision = Column(Text, nullable=True, info={'label': 'رقم القرار'})
    Type = Column(String, ForeignKey('type_voie.pk'), nullable=False,
                  info={'label': 'نوع'})
    Nom = Column(String, info={'label': 'اسم'})
    idLoc = Column(String, ForeignKey('localite.pk_uid'), nullable=False)
    geometry = Column(Geometry('LINESTRING', srid=SRID), nullable=True)
    pkuid_poly = Column(Text, ForeignKey('refpoly.pkuid'), nullable=True)
    uid = Column(Text, ForeignKey('user.id'), nullable=True)
    user = relationship("User", backref="user_line", foreign_keys=[uid])

    @property
    def username(self) -> Optional[str]:
        """Returns the username of the user who created the road."""
        if self.uid:
            return self.user.username
        return None

    @classmethod
    def list_all(cls, session: Session) -> dict:
        """Lists all roads with allowed columns."""
        allowed_columns = ['Type', 'Nom', 'num_decision']
        columns = [column for column in cls.__table__.columns
                   if column.name in allowed_columns]
        return {'data': session.query(*columns).all(), "cols": columns}

    def delete(self, session: Session) -> None:
        """Deletes the road instance from the database."""
        session.delete(self)
        session.commit()

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Road']:
        """Updates a road with the given kwargs and sets spatial context."""
        instance = session.query(cls).filter_by(pkuid=pkuid).first()
        user_data = get_current_user()
        if not user_data or not instance:
            raise ValueError("Road not found or no authenticated user")
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.uid = user_data.get('id')
        instance.idLoc = user_data.get('loc')
        instance.pkuid_poly = None
        try:
            query = session.query(Zone).filter(
                ST_Within(instance.geometry, Zone.geometry)
            ).first()
            if query:
                instance.pkuid_poly = query.pkuid
        except Exception:
            logger.warning("Failed to set pkuid_poly on %s",
                           instance, exc_info=True)
            instance.pkuid_poly = None
        session.commit()
        return instance

    def save(self, session: Session) -> None:
        """Persists a new road with spatial context from the current user."""
        user_data = get_current_user()
        if user_data:
            self.uid = user_data.get('id')
            self.idLoc = user_data.get('loc')
            query = session.query(Zone).filter(
                ST_Within(self.geometry, Zone.geometry)
            ).first()
            if query:
                self.pkuid_poly = query.pkuid
            session.add(self)
            session.commit()
        else:
            raise ValueError("No user found")


class Organization(Base):
    """Spatial model for organizations/facilities (reforg table)."""
    __tablename__ = 'reforg'

    pkuid = Column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    idLoc = Column(String, ForeignKey('localite.pk_uid'))
    Type = Column(String, ForeignKey('type_organisme.pk'), nullable=True)
    Cat = Column(String, ForeignKey('type_organisme.cat'), nullable=True)
    Nom = Column(String)
    geometry = Column(Geometry('POLYGON', srid=SRID), nullable=True)
    uid = Column(Text, ForeignKey('user.id'), nullable=True)
    pkuid_poly = Column(Text, ForeignKey('refpoly.pkuid'), nullable=True)
    user = relationship("User", backref="user_org", foreign_keys=[uid])

    @property
    def username(self) -> Optional[str]:
        """Returns the username of the user who created the organization."""
        if self.uid:
            return self.user.username
        return None

    @classmethod
    def list_all(cls, session: Session) -> dict:
        """Lists all organizations with allowed columns."""
        allowed_columns = ['Cat', 'Type', 'Nom']
        columns = [column for column in cls.__table__.columns
                   if column.name in allowed_columns]
        return {'data': session.query(*columns).all(), "cols": columns}

    @property
    def cat(self) -> Optional[str]:
        """Returns the category of the organization."""
        return self.Cat

    def delete(self, session: Session) -> None:
        """Deletes the organization instance from the database."""
        session.delete(self)
        session.commit()

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Organization']:
        """Updates an organization with the given kwargs
        and sets spatial context."""
        instance = session.query(cls).filter_by(pkuid=pkuid).first()
        user_data = get_current_user()
        if not user_data or not instance:
            raise ValueError("Organization not found or no authenticated user")
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.uid = user_data.get('id')
        instance.idLoc = user_data.get('loc')
        instance.pkuid_poly = None
        try:
            query = session.query(Zone).filter(
                ST_Within(instance.geometry, Zone.geometry)
            ).first()
            if query:
                instance.pkuid_poly = query.pkuid
        except Exception:
            logger.warning("Failed to set pkuid_poly on %s",
                           instance, exc_info=True)
            instance.pkuid_poly = None
        session.commit()
        return instance

    def save(self, session: Session) -> None:
        """Persists a new organization with spatial context
        from the current user."""
        user_data = get_current_user()
        if user_data:
            self.uid = user_data.get('id')
            self.idLoc = user_data.get('loc')
            query = session.query(Zone).filter(
                ST_Within(self.geometry, Zone.geometry)
            ).first()
            if query:
                self.pkuid_poly = query.pkuid
            session.add(self)
            session.commit()
        else:
            raise ValueError("No user found")


class Numbering(Base):
    """Spatial model for numbering points (Numerotation table)."""
    __tablename__ = 'Numerotation'
    pkuid = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'المفتاح'},
    )
    valeur = Column(Text, nullable=False, info={'label': 'رقم'})
    idLine = Column(Text, ForeignKey('RefLine.pkuid'), nullable=True,
                    info={'label': 'الطريق'})
    idPoly = Column(
        Text, ForeignKey('refpolychild.pkuid'), nullable=True,
        info={'label': 'التجزئة'},
    )
    repetition = Column(String, info={'label': 'تكرار'})
    etat = Column(String, ForeignKey('Etat_Numerotation.pk'), nullable=True,
                  info={'label': 'حالة'})
    geometry = Column(Geometry('POINT', srid=SRID), nullable=True,
                      info={'label': 'شكل هندسي'})
    uid = Column(Text, ForeignKey('user.id'), nullable=True,
                 info={'label': 'مستخدم'})

    road = relationship("Road", backref="ref_line_num", foreign_keys=[idLine])
    subdivision = relationship("Subdivision",
                               backref="ref_polychild_num",
                               foreign_keys=[idPoly])
    user = relationship("User", backref="user_num", foreign_keys=[uid])

    activity_cat = Column(String, nullable=True)
    activity_type = Column(String, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ['activity_cat', 'activity_type'],
            ['activity.cat', 'activity.type']
        ),
    )

    @property
    def username(self) -> Optional[str]:
        """Returns the username of the user who created the numbering."""
        if self.uid:
            return self.user.username
        return None

    @classmethod
    def list_all(cls, session: Session) -> dict:
        """Lists all numbering entries with allowed columns."""
        allowed_columns = ['Type', 'Nom']
        columns = [column for column in cls.__table__.columns
                   if column.name in allowed_columns]
        return {'data': session.query(*columns).all(), "cols": columns}

    def delete(self, session: Session) -> None:
        """Deletes the numbering instance from the database."""
        session.delete(self)
        session.commit()

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Numbering']:
        """Updates a numbering entry with the given kwargs."""
        instance = session.query(cls).filter_by(pkuid=pkuid).first()
        user_data = get_current_user()
        if not user_data or not instance:
            raise ValueError("Numbering not found or no authenticated user")
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.uid = user_data.get('id')
        session.commit()
        return instance

    def save(self, session: Session) -> None:
        """Persists a new numbering entry from the current user."""
        user_data = get_current_user()
        if user_data:
            self.uid = user_data.get('id')
            session.add(self)
            session.commit()
        else:
            raise ValueError("No user found")


class PanelSign(Base):
    """Spatial model for panel/sign posts (Pannautage table)."""
    __tablename__ = 'Pannautage'

    pkuid = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'المفتاح'},
    )
    dim = Column(String, ForeignKey('DimPan.pk'), nullable=False,
                 info={'label': 'الأبعاد'})
    Type = Column(Text, nullable=True, info={'label': 'نوع المرجع'})
    Stituation = Column(
        String, ForeignKey('situation_Montage.pk'), nullable=True,
        info={'label': 'الحالة'},
    )
    idLine = Column(Text, ForeignKey('RefLine.pkuid'), nullable=True,
                    info={'label': 'الطريق'})
    idPoly = Column(
        Text, ForeignKey('refpolychild.pkuid'), nullable=True,
        info={'label': 'التجزئة'},
    )
    idOrg = Column(Text, ForeignKey('reforg.pkuid'), nullable=True,
                   info={'label': 'المرفق'})
    geometry = Column(Geometry('POINT', srid=SRID), nullable=True,
                      info={'label': 'شكل هندسي'})
    uid = Column(Text, ForeignKey('user.id'), nullable=True,
                 info={'label': 'مستخدم'})

    organization = relationship("Organization",
                                 backref="ref_org_pan",
                                 foreign_keys=[idOrg])
    road = relationship("Road", backref="ref_line_pan", foreign_keys=[idLine])
    subdivision = relationship("Subdivision",
                                backref="ref_polychild_pan",
                                foreign_keys=[idPoly])
    user = relationship("User", backref="user_pan", foreign_keys=[uid])

    @property
    def username(self) -> Optional[str]:
        """Returns the username of the user who created the panel."""
        if self.uid:
            return self.user.username
        return None

    @property
    def label(self) -> Optional[str]:
        """Returns a human-readable label based on the referenced feature."""
        if self.idLine is not None and self.idPoly is None \
                and self.idOrg is None:
            return '\u200F' + self.road.Type + ' ' + self.road.Nom
        if self.idLine is None and self.idPoly is not None \
                and self.idOrg is None:
            return '\u200F' + self.subdivision.Type + ' ' + self.subdivision.Nom
        if self.idLine is None and self.idPoly is None \
                and self.idOrg is not None:
            return '\u200F' + self.organization.Type \
                + ' ' + self.organization.Nom
        return None

    def delete(self, session: Session) -> None:
        """Deletes the panel instance from the database."""
        session.delete(self)
        session.commit()

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['PanelSign']:
        """Updates a panel with the given kwargs."""
        instance = session.query(cls).filter_by(pkuid=pkuid).first()
        user_data = get_current_user()
        if not user_data or not instance:
            raise ValueError("PanelSign not found or no authenticated user")
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.uid = user_data.get('id')
        session.commit()
        return instance

    def save(self, session: Session) -> None:
        """Persists a new panel with spatial context from the current user."""
        user_data = get_current_user()
        if user_data:
            self.uid = user_data.get('id')
            if self.idLine:
                session.query(Road).filter(Road.pkuid == self.idLine).first()
                self.Type = LAYER_ROADS
            if self.idOrg:
                session.query(Organization).filter(
                    Organization.pkuid == self.idOrg
                ).first()
                self.Type = LAYER_FACILITIES
            if self.idPoly:
                session.query(Subdivision).filter(
                    Subdivision.pkuid == self.idPoly
                ).first()
                self.Type = LAYER_SUBDIVISIONS
            session.add(self)
            session.commit()
        else:
            raise ValueError("No user found")
