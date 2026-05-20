from marshmallow import Schema, fields, pre_load, validates, ValidationError

from ..core.database import get_auth_session
from ..users.models import User


class AuthSchema(Schema):
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

    @pre_load
    def convert_empty_strings(self, data, **kwargs) -> dict:
        return {
            key: (None if value == "" else value)
            for key, value in data.items()
        }


class SignupSchema(Schema):
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
    affectation_id = fields.Int(
        required=True,
        error_messages={"required": "Affectation is required"},
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

    @pre_load
    def convert_empty_strings(self, data, **kwargs) -> dict:
        return {
            key: (None if value == "" else value)
            for key, value in data.items()
        }

    @validates('username')
    def validate_username(self, value, **kwargs) -> None:
        if value is not None:
            if value:
                session = get_auth_session()
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
