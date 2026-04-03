from marshmallow import Schema, fields, validate, validates, ValidationError
from app.models.user import RoleEnum


class RegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6),
        load_only=True,
    )
    role = fields.Str(
        load_default=RoleEnum.VIEWER,
        validate=validate.OneOf(RoleEnum.ALL),
    )

    @validates("name")
    def validate_name(self, value):
        if not value.strip():
            raise ValidationError("Name cannot be blank.")


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class UserOutputSchema(Schema):
    """Safe output schema — never exposes password_hash."""
    id = fields.Int(dump_only=True)
    name = fields.Str()
    email = fields.Email()
    role = fields.Str()
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)


class UpdateUserSchema(Schema):
    name = fields.Str(validate=validate.Length(min=2, max=100))
    role = fields.Str(validate=validate.OneOf(RoleEnum.ALL))
    is_active = fields.Bool()
