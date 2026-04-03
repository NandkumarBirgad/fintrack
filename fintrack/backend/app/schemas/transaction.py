from marshmallow import Schema, fields, validate, validates, ValidationError
from app.models.transaction import TransactionType
import decimal


class TransactionCreateSchema(Schema):
    amount = fields.Decimal(required=True, places=2, as_string=False)
    type = fields.Str(required=True, validate=validate.OneOf(TransactionType.ALL))
    category = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    date = fields.Date(required=True)           # expects YYYY-MM-DD
    notes = fields.Str(load_default=None, validate=validate.Length(max=500))

    @validates("amount")
    def validate_amount(self, value):
        if value <= 0:
            raise ValidationError("Amount must be greater than zero.")
        if value > decimal.Decimal("9999999999.99"):
            raise ValidationError("Amount exceeds maximum allowed value.")


class TransactionUpdateSchema(Schema):
    """All fields optional for PATCH-style updates."""
    amount = fields.Decimal(places=2, as_string=False)
    type = fields.Str(validate=validate.OneOf(TransactionType.ALL))
    category = fields.Str(validate=validate.Length(min=1, max=100))
    date = fields.Date()
    notes = fields.Str(validate=validate.Length(max=500))

    @validates("amount")
    def validate_amount(self, value):
        if value is not None and value <= 0:
            raise ValidationError("Amount must be greater than zero.")


class TransactionOutputSchema(Schema):
    id = fields.Int(dump_only=True)
    amount = fields.Decimal(as_string=True)
    type = fields.Str()
    category = fields.Str()
    date = fields.Date()
    notes = fields.Str()
    user_id = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class TransactionFilterSchema(Schema):
    """Query params for filtering transactions."""
    type = fields.Str(validate=validate.OneOf(TransactionType.ALL))
    category = fields.Str()
    date_from = fields.Date()
    date_to = fields.Date()
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=20, validate=validate.Range(min=1, max=100))
