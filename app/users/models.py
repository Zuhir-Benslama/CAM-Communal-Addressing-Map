"""User model for authentication and session management."""

import uuid

from sqlalchemy import Boolean, Column, Integer, String, Text
from sqlalchemy.orm import Session

from ..core.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User model for authentication and session management."""

    __tablename__ = 'user'
    id = Column(Text, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(255), unique=True, nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    password = Column(String(255), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    wilaya_code = Column(Integer, nullable=True)
    commune_code = Column(String(255), nullable=True)
    api_key = Column(Text, default='', nullable=True)
    session_token = Column(Text, default='', nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=True)

    def save(self, session: Session) -> None:
        """Persist the user to *session* and commit."""
        session.add(self)
        session.commit()
