"""db/schema.py re-exports."""
# pylint: disable=unused-import
try:
    from RNA.app.users.schemas import AuthSchema, SignupSchema
except ImportError:
    from plans_adressage.app.users.schemas import AuthSchema, SignupSchema
