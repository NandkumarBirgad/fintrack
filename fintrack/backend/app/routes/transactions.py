from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.schemas.transaction import (
    TransactionCreateSchema,
    TransactionUpdateSchema,
    TransactionOutputSchema,
    TransactionFilterSchema,
)
from app.services.transaction import (
    create_transaction,
    get_transactions,
    get_transaction_by_id,
    update_transaction,
    delete_transaction,
)
from app.utils.responses import success, error
from app.utils.decorators import get_current_user, admin_only, analyst_or_above
from app.models.user import RoleEnum

transactions_bp = Blueprint("transactions", __name__)

create_schema = TransactionCreateSchema()
update_schema = TransactionUpdateSchema()
output_schema = TransactionOutputSchema()
output_many_schema = TransactionOutputSchema(many=True)
filter_schema = TransactionFilterSchema()


@transactions_bp.route("", methods=["GET"])
@jwt_required()
def list_transactions():
    """
    GET /transactions
    List transactions with optional filters and pagination.

    Query params:
      - type         : income | expense
      - category     : partial match (case-insensitive)
      - date_from    : YYYY-MM-DD
      - date_to      : YYYY-MM-DD
      - page         : default 1
      - per_page     : default 20, max 100

    Access: viewer, analyst, admin
    """
    user = get_current_user()
    if not user:
        return error("Unauthorized.", 401)

    # Analysts and admins can filter; viewers get plain list only
    raw_args = request.args.to_dict()

    # Strip filter params for viewers
    if user.role == RoleEnum.VIEWER:
        raw_args = {k: v for k, v in raw_args.items() if k in ("page", "per_page")}

    try:
        filters = filter_schema.load(raw_args)
    except ValidationError as e:
        return error("Invalid query parameters.", 422, errors=e.messages)

    paginated = get_transactions(user.id, filters)

    meta = {
        "page": paginated.page,
        "per_page": paginated.per_page,
        "total": paginated.total,
        "pages": paginated.pages,
        "has_next": paginated.has_next,
        "has_prev": paginated.has_prev,
    }

    return success(
        data=output_many_schema.dump(paginated.items),
        message="Transactions retrieved.",
        meta=meta,
    )


@transactions_bp.route("/<int:transaction_id>", methods=["GET"])
@jwt_required()
def get_transaction(transaction_id):
    """
    GET /transactions/<id>
    Retrieve a single transaction by ID.
    Access: viewer, analyst, admin
    """
    user = get_current_user()
    if not user:
        return error("Unauthorized.", 401)

    txn = get_transaction_by_id(transaction_id, user.id)
    if not txn:
        return error("Transaction not found.", 404)

    return success(data=output_schema.dump(txn))


@transactions_bp.route("", methods=["POST"])
@jwt_required()
@admin_only
def create():
    """
    POST /transactions
    Create a new financial record.
    Body: { amount, type, category, date, notes? }
    Access: admin only
    """
    try:
        data = create_schema.load(request.get_json() or {})
    except ValidationError as e:
        return error("Validation failed.", 422, errors=e.messages)

    user = get_current_user()
    txn = create_transaction(user.id, data)
    return success(
        data=output_schema.dump(txn),
        message="Transaction created.",
        status=201,
    )


@transactions_bp.route("/<int:transaction_id>", methods=["PUT"])
@jwt_required()
@admin_only
def update(transaction_id):
    """
    PUT /transactions/<id>
    Update an existing transaction.
    Body: any subset of { amount, type, category, date, notes }
    Access: admin only
    """
    try:
        data = update_schema.load(request.get_json() or {})
    except ValidationError as e:
        return error("Validation failed.", 422, errors=e.messages)

    if not data:
        return error("No valid fields provided for update.", 400)

    user = get_current_user()
    txn, err = update_transaction(transaction_id, user.id, data)
    if err:
        return error(err, 404)

    return success(data=output_schema.dump(txn), message="Transaction updated.")


@transactions_bp.route("/<int:transaction_id>", methods=["DELETE"])
@jwt_required()
@admin_only
def delete(transaction_id):
    """
    DELETE /transactions/<id>
    Delete a transaction record.
    Access: admin only
    """
    user = get_current_user()
    ok, err = delete_transaction(transaction_id, user.id)
    if not ok:
        return error(err, 404)

    return success(message="Transaction deleted.")
