"""User model for authentication and session management."""
import uuid
from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import Session

from ..core.database import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    active = Column(Boolean, nullable=True)
    affectation_id = Column(
        String, ForeignKey('localite.pk_uid'), nullable=True
    )
    api_key = Column(Text, default="", nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)

    def to_dict(self) -> dict:
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def save(self, session: Session) -> None:
        session.add(self)
        session.commit()
