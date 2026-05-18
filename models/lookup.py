"""Lookup table models for the addressing plans database."""

from sqlalchemy import Column, String
from sqlalchemy.orm import Session

try:
    from .base import Base
except ImportError:
    from models.base import Base


class _BaseLookup(Base):
    """Abstract base for simple lookup tables with a string PK."""
    __abstract__ = True

    def save(self, session: Session) -> None:
        """Persists the lookup record to the database."""
        session.add(self)
        session.commit()


class MountingStatus(_BaseLookup):
    """Lookup table for mounting statuses."""
    __tablename__ = 'situation_Montage'
    pk = Column(String, primary_key=True, nullable=False)


class SubdivisionType(_BaseLookup):
    """Lookup table for subdivision types."""
    __tablename__ = 'type_cite'
    pk = Column(String, primary_key=True)


class PanelDimension(_BaseLookup):
    """Lookup table for panel dimensions."""
    __tablename__ = 'DimPan'
    pk = Column(String, primary_key=True)


class RoadType(_BaseLookup):
    """Lookup table for road types."""
    __tablename__ = 'type_voie'
    pk = Column(String, primary_key=True)


class ZoneType(_BaseLookup):
    """Lookup table for zone types."""
    __tablename__ = 'type_zone'
    pk = Column(String, primary_key=True)


class NumberingState(_BaseLookup):
    """Lookup table for numbering states."""
    __tablename__ = 'Etat_Numerotation'
    pk = Column(String, primary_key=True)


class ActivityType(Base):
    """Lookup table for activity types."""
    __tablename__ = 'activity'
    cat = Column(String, primary_key=True)
    type = Column(String, primary_key=True)
    subcat = Column(String, primary_key=True, default='')

    def save(self, session: Session) -> None:
        """Persists the activity type to the database."""
        session.add(self)
        session.commit()


class OrganizationType(Base):
    """Lookup table for organization types."""
    __tablename__ = 'type_organisme'
    pk = Column(String, primary_key=True)
    cat = Column(String, primary_key=True)
    subcat = Column(String, primary_key=True, default='')

    def save(self, session: Session) -> None:
        """Persists the organization type to the database."""
        session.add(self)
        session.commit()
