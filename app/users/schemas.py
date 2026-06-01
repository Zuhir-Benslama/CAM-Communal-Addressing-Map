"""Marshmallow schemas for user authentication and signup validation."""
from marshmallow import Schema, ValidationError, fields, pre_load, validates

from ..core.database import get_session
from ..users.models import User


class _EmptyStringMixin:
    """Convert empty strings to None during deserialization."""

    @pre_load
    def convert_empty_strings(self, data, **_kwargs) -> dict:
        """Replace empty-string values with None during deserialization."""
        return {
            key: (None if value == "" else value)
            for key, value in data.items()
        }


class AuthSchema(_EmptyStringMixin, Schema):
    """Validate login credentials (USERNAME + PASSWORD)."""
    USERNAME = fields.Str(
        required=True,
        error_messages={"required": "Username is required"},
        allow_none=False
    )
    PASSWORD = fields.Str(
        required=True,
        error_messages={"required": "Password is required"},
        allow_none=False
    )


class SignupSchema(_EmptyStringMixin, Schema):
    """Validate sign-up fields (username, name, password, affectation, contact)."""
    username = fields.Str(
        required=True,
        error_messages={"required": "Username is required"},
        allow_none=False
    )
    first_name = fields.Str(
        required=True,
        error_messages={"required": "Firstname is required"},
        allow_none=False
    )
    last_name = fields.Str(
        required=True,
        error_messages={"required": "Lastname is required"},
        allow_none=False
    )
    password = fields.Str(
        required=True,
        error_messages={"required": "Password is required"},
        allow_none=False
    )
    commune_code = fields.Str(
        required=True,
        error_messages={"required": "Commune is required"},
        allow_none=False
    )
    email = fields.Str(
        required=True,
        error_messages={"required": "Email is required"},
        allow_none=False
    )
    phone = fields.Str(
        required=True,
        error_messages={"required": "Phone number is required"},
        allow_none=False
    )

    @validates('username')
    def validate_username(self, value, **_kwargs) -> None:
        """Ensure the username is unique and non-empty."""
        if value is not None:
            if value:
                session = get_session()
                try:
                    existing_user = (
                        session.query(User).filter_by(username=value).first()
                    )
                    if existing_user:
                        msg = f"This User ( {value} ) already exists"
                        raise ValidationError(msg)
                finally:
                    session.close()
            else:
                raise ValidationError("Username is required")
