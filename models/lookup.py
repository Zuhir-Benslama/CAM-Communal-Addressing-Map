"""Lookup table models for the addressing plans database."""

from sqlalchemy import Column, String
from sqlalchemy.orm import Session

try:
    from .base import Base
except ImportError:
    from models.base import Base


class MountingStatus(Base):
    """Lookup table for mounting statuses."""
    __tablename__ = 'situation_Montage'
    pk = Column(String, primary_key=True, nullable=False)

    def save(self, session: Session) -> None:
        """Persists the mounting status to the database."""
        session.add(self)
        session.commit()


class SubdivisionType(Base):
    """Lookup table for subdivision types."""
    __tablename__ = 'type_cite'
    pk = Column(String, primary_key=True)

    def save(self, session: Session) -> None:
        """Persists the subdivision type to the database."""
        session.add(self)
        session.commit()


class ActivityType(Base):
    """Lookup table for activity types."""
    __tablename__ = 'activity'
    cat = Column(String, primary_key=True)
    type = Column(String, primary_key=True)

    def save(self, session: Session) -> None:
        """Persists the activity type to the database."""
        session.add(self)
        session.commit()


class PanelDimension(Base):
    """Lookup table for panel dimensions."""
    __tablename__ = 'DimPan'
    pk = Column(String, primary_key=True)

    def save(self, session: Session) -> None:
        """Persists the panel dimension to the database."""
        session.add(self)
        session.commit()


class OrganizationType(Base):
    """Lookup table for organization types."""
    __tablename__ = 'type_organisme'
    pk = Column(String, primary_key=True)
    cat = Column(String, primary_key=True)

    def save(self, session: Session) -> None:
        """Persists the organization type to the database."""
        session.add(self)
        session.commit()


class RoadType(Base):
    """Lookup table for road types."""
    __tablename__ = 'type_voie'
    pk = Column(String, primary_key=True)

    def save(self, session: Session) -> None:
        """Persists the road type to the database."""
        session.add(self)
        session.commit()


class ZoneType(Base):
    """Lookup table for zone types."""
    __tablename__ = 'type_zone'
    pk = Column(String, primary_key=True)

    def save(self, session: Session) -> None:
        """Persists the zone type to the database."""
        session.add(self)
        session.commit()


class NumberingState(Base):
    """Lookup table for numbering states."""
    __tablename__ = 'Etat_Numerotation'
    pk = Column(String, primary_key=True)

    def save(self, session: Session) -> None:
        """Persists the numbering state to the database."""
        session.add(self)
        session.commit()
