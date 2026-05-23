"""SQLAlchemy models for spatial entities (zones, roads, etc.)."""
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
    from ..users.repository import get_current_user
    return get_current_user()


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
        if self.uid:
            return self.user.username
        return None

    @classmethod
    def list_all(cls, session: Session) -> dict:
        columns = [column for column in cls.__table__.columns
                   if column.name in cls._list_columns]
        return {'data': session.query(*columns).all(), "cols": columns}

    def delete(self, session: Session) -> None:
        session.delete(self)
        session.commit()


class Localite(Base, TimestampMixin):
    __tablename__ = 'localite'
    pk_uid = Column(Integer, primary_key=True, autoincrement=True)
    wilaya = Column(Text, nullable=False)
    codeWilaya = Column(Integer, nullable=False)
    communeAr = Column(Text, nullable=False)
    commune_fr = Column(Text, nullable=True)
    commune_en = Column(Text, nullable=True)
    codeCommun = Column(Text, nullable=False)
    geometry = Column(Geometry(geometry_type='GEOMETRY', srid=SRID))

    def save(self, session: Session) -> None:
        session.add(self)
        session.commit()


class Zone(_BaseSpatialModel):
    __tablename__ = 'refpoly'
    _list_columns = ['Type', 'Nom']

    pkuid = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    idLoc = Column(String, ForeignKey('localite.pk_uid'), index=True,
                   info={'label': 'Location'})
    Type = Column(String, nullable=False,
                  info={'label': 'Type', 'label_fr': 'Type', 'label_en': 'Type'})
    Nom = Column(String, info={'label': 'Name', 'label_fr': 'Nom', 'label_en': 'Name'})
    Nom_fr = Column(String, nullable=True)
    Nom_en = Column(String, nullable=True)
    geometry = Column(Geometry('POLYGON', srid=SRID), nullable=False,
                      info={'label': 'Geometry'})
    has_child = Column(Boolean, default=False, nullable=False)
    uid = Column(Text, ForeignKey('user.id'), nullable=True, index=True,
                 info={'label': 'User'})
    user = relationship("User", backref="user_poly", foreign_keys=[uid])

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Zone']:
        instance = session.query(cls).filter_by(pkuid=pkuid).first()
        user_data = _get_current_user()
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
        user_data = _get_current_user()
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


class Subdivision(_BaseSpatialModel):
    __tablename__ = 'refpolychild'
    _list_columns = ['Type', 'Nom']

    pkuid = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    idLoc = Column(String, ForeignKey('localite.pk_uid'), index=True)
    Type = Column(String, nullable=False,
                  info={'label': 'Type', 'label_fr': 'Type', 'label_en': 'Type'})
    Nom = Column(String, info={'label': 'Name', 'label_fr': 'Nom', 'label_en': 'Name'})
    Nom_fr = Column(String, nullable=True)
    Nom_en = Column(String, nullable=True)
    geometry = Column(Geometry('POLYGON', srid=SRID), nullable=True)
    parent = Column(Text, ForeignKey('refpoly.pkuid'), nullable=True, index=True)
    uid = Column(Text, ForeignKey('user.id'), nullable=True, index=True,
                 info={'label': 'User'})
    user = relationship("User", backref="user_poly_child", foreign_keys=[uid])

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Subdivision']:
        instance = session.query(cls).filter_by(pkuid=pkuid).first()
        user_data = _get_current_user()
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
        user_data = _get_current_user()
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


class Road(_BaseSpatialModel):
    __tablename__ = 'RefLine'
    _list_columns = ['Type', 'Nom', 'num_decision']

    pkuid = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    num_decision = Column(Text, nullable=True, info={'label': 'Decision No.', 'label_fr': 'N° décision', 'label_en': 'Decision No.'})
    Type = Column(String, nullable=False,
                  info={'label': 'Type', 'label_fr': 'Type', 'label_en': 'Type'})
    Nom = Column(String, info={'label': 'Name', 'label_fr': 'Nom', 'label_en': 'Name'})
    Nom_fr = Column(String, nullable=True)
    Nom_en = Column(String, nullable=True)
    idLoc = Column(String, ForeignKey('localite.pk_uid'), nullable=False, index=True)
    geometry = Column(Geometry('LINESTRING', srid=SRID), nullable=True)
    pkuid_poly = Column(Text, ForeignKey('refpoly.pkuid'), nullable=True, index=True)
    uid = Column(Text, ForeignKey('user.id'), nullable=True, index=True)
    user = relationship("User", backref="user_line", foreign_keys=[uid])

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Road']:
        instance = session.query(cls).filter_by(pkuid=pkuid).first()
        user_data = _get_current_user()
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
        user_data = _get_current_user()
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


class Organization(_BaseSpatialModel):
    __tablename__ = 'reforg'
    _list_columns = ['Cat', 'Type', 'Nom']

    pkuid = Column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    idLoc = Column(String, ForeignKey('localite.pk_uid'), index=True)
    Type = Column(String, nullable=True)
    Cat = Column(String, nullable=True)
    Nom = Column(String)
    Nom_fr = Column(String, nullable=True)
    Nom_en = Column(String, nullable=True)
    geometry = Column(Geometry('POLYGON', srid=SRID), nullable=True)
    uid = Column(Text, ForeignKey('user.id'), nullable=True, index=True)
    pkuid_poly = Column(Text, ForeignKey('refpoly.pkuid'), nullable=True, index=True)
    user = relationship("User", backref="user_org", foreign_keys=[uid])

    @property
    def cat(self) -> Optional[str]:
        return self.Cat

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Organization']:
        instance = session.query(cls).filter_by(pkuid=pkuid).first()
        user_data = _get_current_user()
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
        user_data = _get_current_user()
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


class Numbering(_BaseSpatialModel):
    __tablename__ = 'Numerotation'
    _list_columns = ['valeur', 'repetition', 'etat']
    pkuid = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    valeur = Column(Text, nullable=False, info={'label': 'Number'})
    idLine = Column(Text, ForeignKey('RefLine.pkuid'), nullable=True, index=True,
                    info={'label': 'Road'})
    idPoly = Column(
        Text, ForeignKey('refpolychild.pkuid'), nullable=True, index=True,
        info={'label': 'Subdivision'},
    )
    repetition = Column(String, info={'label': 'Duplicated'})
    etat = Column(String, nullable=True,
                  info={'label': 'State'})
    geometry = Column(Geometry('POINT', srid=SRID), nullable=True,
                      info={'label': 'Geometry'})
    uid = Column(Text, ForeignKey('user.id'), nullable=True, index=True,
                 info={'label': 'User'})

    road = relationship("Road", backref="ref_line_num", foreign_keys=[idLine])
    subdivision = relationship("Subdivision",
                               backref="ref_polychild_num",
                               foreign_keys=[idPoly])
    user = relationship("User", backref="user_num", foreign_keys=[uid])

    activity_cat = Column(String, nullable=True)
    activity_type = Column(String, nullable=True)

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Numbering']:
        instance = session.query(cls).filter_by(pkuid=pkuid).first()
        user_data = _get_current_user()
        if not user_data or not instance:
            raise ValueError("Numbering not found or no authenticated user")
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.uid = user_data.get('id')
        session.commit()
        return instance

    def save(self, session: Session) -> None:
        user_data = _get_current_user()
        if user_data:
            self.uid = user_data.get('id')
            session.add(self)
            session.commit()
        else:
            raise ValueError("No user found")


class PanelSign(_BaseSpatialModel):
    __tablename__ = 'Pannautage'

    pkuid = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'Key'},
    )
    dim = Column(String, nullable=False,
                 info={'label': 'Dimensions'})
    Type = Column(Text, nullable=True, info={'label': 'Reference Type'})
    situation = Column(
        "Stituation", String, nullable=True,
        info={'label': 'Status'},
    )
    idLine = Column(Text, ForeignKey('RefLine.pkuid'), nullable=True, index=True,
                    info={'label': 'Road'})
    idPoly = Column(
        Text, ForeignKey('refpolychild.pkuid'), nullable=True, index=True,
        info={'label': 'Subdivision'},
    )
    idOrg = Column(Text, ForeignKey('reforg.pkuid'), nullable=True, index=True,
                   info={'label': 'Facility'})
    geometry = Column(Geometry('POINT', srid=SRID), nullable=True,
                      info={'label': 'Geometry'})
    uid = Column(Text, ForeignKey('user.id'), nullable=True, index=True,
                 info={'label': 'User'})

    organization = relationship("Organization",
                                 backref="ref_org_pan",
                                 foreign_keys=[idOrg])
    road = relationship("Road", backref="ref_line_pan", foreign_keys=[idLine])
    subdivision = relationship("Subdivision",
                               backref="ref_polychild_pan",
                               foreign_keys=[idPoly])
    user = relationship("User", backref="user_pan", foreign_keys=[uid])

    @property
    def label(self) -> Optional[str]:
        loc = current_locale()
        if self.idLine is not None and self.idPoly is None \
                and self.idOrg is None:
            return ('\u200F' + locale_value(self.road, 'Type', loc)
                    + ' ' + locale_value(self.road, 'Nom', loc))
        if self.idLine is None and self.idPoly is not None \
                and self.idOrg is None:
            return ('\u200F' + locale_value(self.subdivision, 'Type', loc)
                    + ' ' + locale_value(self.subdivision, 'Nom', loc))
        if self.idLine is None and self.idPoly is None \
                and self.idOrg is not None:
            return ('\u200F' + locale_value(self.organization, 'Type', loc)
                    + ' ' + locale_value(self.organization, 'Nom', loc))
        return None

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['PanelSign']:
        instance = session.query(cls).filter_by(pkuid=pkuid).first()
        user_data = _get_current_user()
        if not user_data or not instance:
            raise ValueError("PanelSign not found or no authenticated user")
        for key, value in _allowlist_columns(cls, **kwargs).items():
            setattr(instance, key, value)
        instance.uid = user_data.get('id')
        session.commit()
        return instance

    def save(self, session: Session) -> None:
        user_data = _get_current_user()
        if user_data:
            self.uid = user_data.get('id')
            if self.idLine:
                road = (
                    session.query(Road)
                    .filter(Road.pkuid == self.idLine)
                    .first()
                )
                if not road:
                    raise ValueError(
                        f"Road with pkuid {self.idLine} not found"
                    )
                self.Type = LAYER_ROADS
            if self.idOrg:
                org = (
                    session.query(Organization)
                    .filter(Organization.pkuid == self.idOrg)
                    .first()
                )
                if not org:
                    raise ValueError(
                        f"Organization with pkuid {self.idOrg} not found"
                    )
                self.Type = LAYER_FACILITIES
            if self.idPoly:
                sub = (
                    session.query(Subdivision)
                    .filter(Subdivision.pkuid == self.idPoly)
                    .first()
                )
                if not sub:
                    raise ValueError(
                        f"Subdivision with pkuid {self.idPoly} not found"
                    )
                self.Type = LAYER_SUBDIVISIONS
            session.add(self)
            session.commit()
        else:
            raise ValueError("No user found")
