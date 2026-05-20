import uuid
import logging
from typing import Any, Optional

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey,
)
from sqlalchemy.orm import relationship, Session
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_Within

from ..core.database import Base, _allowlist_columns
from ..shared.constants import (
    SRID, LAYER_ROADS, LAYER_FACILITIES, LAYER_SUBDIVISIONS,
)
from ..shared.utils import current_locale, locale_value
from ..users.repository import get_current_user

logger = logging.getLogger(__name__)


class Localite(Base):
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


class Zone(Base):
    __tablename__ = 'refpoly'

    pkuid = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'المفتاح'},
    )
    idLoc = Column(String, ForeignKey('localite.pk_uid'),
                   info={'label': 'الموقع'})
    Type = Column(String, nullable=False,
                  info={'label': 'نوع', 'label_fr': 'Type', 'label_en': 'Type'})
    Nom = Column(String, info={'label': 'اسم', 'label_fr': 'Nom', 'label_en': 'Name'})
    Nom_fr = Column(String, nullable=True)
    Nom_en = Column(String, nullable=True)
    geometry = Column(Geometry('POLYGON', srid=SRID), nullable=False,
                      info={'label': 'شكل هندسي'})
    has_child = Column(Boolean)
    uid = Column(Text, ForeignKey('user.id'), nullable=True,
                 info={'label': 'مستخدم'})
    user = relationship("User", backref="user_poly", foreign_keys=[uid])

    @property
    def username(self) -> Optional[str]:
        if self.uid:
            return self.user.username
        return None

    def delete(self, session: Session) -> None:
        session.delete(self)
        session.commit()

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Zone']:
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
    __tablename__ = 'refpolychild'

    pkuid = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'المفتاح'},
    )
    idLoc = Column(String, ForeignKey('localite.pk_uid'))
    Type = Column(String, nullable=False,
                  info={'label': 'نوع', 'label_fr': 'Type', 'label_en': 'Type'})
    Nom = Column(String, info={'label': 'اسم', 'label_fr': 'Nom', 'label_en': 'Name'})
    Nom_fr = Column(String, nullable=True)
    Nom_en = Column(String, nullable=True)
    geometry = Column(Geometry('POLYGON', srid=SRID), nullable=True)
    parent = Column(Text, ForeignKey('refpoly.pkuid'), nullable=True)
    uid = Column(Text, ForeignKey('user.id'), nullable=True,
                 info={'label': 'مستخدم'})
    user = relationship("User", backref="user_poly_child", foreign_keys=[uid])

    @property
    def username(self) -> Optional[str]:
        if self.uid:
            return self.user.username
        return None

    @classmethod
    def list_all(cls, session: Session) -> dict:
        allowed_columns = ['Type', 'Nom']
        columns = [column for column in cls.__table__.columns
                   if column.name in allowed_columns]
        return {'data': session.query(*columns).all(), "cols": columns}

    def delete(self, session: Session) -> None:
        session.delete(self)
        session.commit()

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Subdivision']:
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
    __tablename__ = 'RefLine'
    pkuid = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'المفتاح'},
    )
    num_decision = Column(Text, nullable=True, info={'label': 'رقم القرار', 'label_fr': 'N° décision', 'label_en': 'Decision No.'})
    Type = Column(String, nullable=False,
                  info={'label': 'نوع', 'label_fr': 'Type', 'label_en': 'Type'})
    Nom = Column(String, info={'label': 'اسم', 'label_fr': 'Nom', 'label_en': 'Name'})
    Nom_fr = Column(String, nullable=True)
    Nom_en = Column(String, nullable=True)
    idLoc = Column(String, ForeignKey('localite.pk_uid'), nullable=False)
    geometry = Column(Geometry('LINESTRING', srid=SRID), nullable=True)
    pkuid_poly = Column(Text, ForeignKey('refpoly.pkuid'), nullable=True)
    uid = Column(Text, ForeignKey('user.id'), nullable=True)
    user = relationship("User", backref="user_line", foreign_keys=[uid])

    @property
    def username(self) -> Optional[str]:
        if self.uid:
            return self.user.username
        return None

    @classmethod
    def list_all(cls, session: Session) -> dict:
        allowed_columns = ['Type', 'Nom', 'num_decision']
        columns = [column for column in cls.__table__.columns
                   if column.name in allowed_columns]
        return {'data': session.query(*columns).all(), "cols": columns}

    def delete(self, session: Session) -> None:
        session.delete(self)
        session.commit()

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Road']:
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
    __tablename__ = 'reforg'

    pkuid = Column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    idLoc = Column(String, ForeignKey('localite.pk_uid'))
    Type = Column(String, nullable=True)
    Cat = Column(String, nullable=True)
    Nom = Column(String)
    Nom_fr = Column(String, nullable=True)
    Nom_en = Column(String, nullable=True)
    geometry = Column(Geometry('POLYGON', srid=SRID), nullable=True)
    uid = Column(Text, ForeignKey('user.id'), nullable=True)
    pkuid_poly = Column(Text, ForeignKey('refpoly.pkuid'), nullable=True)
    user = relationship("User", backref="user_org", foreign_keys=[uid])

    @property
    def username(self) -> Optional[str]:
        if self.uid:
            return self.user.username
        return None

    @classmethod
    def list_all(cls, session: Session) -> dict:
        allowed_columns = ['Cat', 'Type', 'Nom']
        columns = [column for column in cls.__table__.columns
                   if column.name in allowed_columns]
        return {'data': session.query(*columns).all(), "cols": columns}

    @property
    def cat(self) -> Optional[str]:
        return self.Cat

    def delete(self, session: Session) -> None:
        session.delete(self)
        session.commit()

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Organization']:
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
    etat = Column(String, nullable=True,
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

    @property
    def username(self) -> Optional[str]:
        if self.uid:
            return self.user.username
        return None

    @classmethod
    def list_all(cls, session: Session) -> dict:
        allowed_columns = ['Type', 'Nom']
        columns = [column for column in cls.__table__.columns
                   if column.name in allowed_columns]
        return {'data': session.query(*columns).all(), "cols": columns}

    def delete(self, session: Session) -> None:
        session.delete(self)
        session.commit()

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['Numbering']:
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
        user_data = get_current_user()
        if user_data:
            self.uid = user_data.get('id')
            session.add(self)
            session.commit()
        else:
            raise ValueError("No user found")


class PanelSign(Base):
    __tablename__ = 'Pannautage'

    pkuid = Column(
        Text, primary_key=True, default=lambda: str(uuid.uuid4()),
        info={'label': 'المفتاح'},
    )
    dim = Column(String, nullable=False,
                 info={'label': 'الأبعاد'})
    Type = Column(Text, nullable=True, info={'label': 'نوع المرجع'})
    Stituation = Column(
        String, nullable=True,
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
        if self.uid:
            return self.user.username
        return None

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

    def delete(self, session: Session) -> None:
        session.delete(self)
        session.commit()

    @classmethod
    def update(cls, session: Session, pkuid: str,
               **kwargs: Any) -> Optional['PanelSign']:
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
