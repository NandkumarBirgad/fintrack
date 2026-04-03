from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields, validate, ValidationError

from app.services.analytics import (
    get_summary,
    get_monthly_breakdown,
    get_category_breakdown,
    get_recent_transactions,
)
from app.utils.responses import success, error
from app.utils.decorators import get_current_user, analyst_or_above
from app.models.transaction import TransactionType

analytics_bp = Blueprint("analytics", __name__)


class MonthlyQuerySchema(Schema):
    year = fields.Int(validate=validate.Range(min=2000, max=2100))


class CategoryQuerySchema(Schema):
    type = fields.Str(validate=validate.OneOf(TransactionType.ALL))


class RecentQuerySchema(Schema):
    limit = fields.Int(load_default=10, validate=validate.Range(min=1, max=50))


@analytics_bp.route("/summary", methods=["GET"])
@jwt_required()
def summary():
    """
    GET /analytics/summary
    Access: viewer, analyst, admin
    """
    user = get_current_user()
    data = get_summary(user.id)
    return success(data=data, message="Financial summary retrieved.")


@analytics_bp.route("/alerts", methods=["GET"])
@jwt_required()
def alerts():
    """
    GET /analytics/alerts
    Returns smart notifications and budget warnings.
    """
    from app.services.analytics import get_alerts
    data = get_alerts()
    return success(data=data, message="Alerts retrieved.")


@analytics_bp.route("/monthly", methods=["GET"])
@jwt_required()
@analyst_or_above
def monthly():
    """
    GET /analytics/monthly?year=2024
    Returns month-wise income and expense breakdown.
    Access: analyst, admin
    """
    try:
        params = MonthlyQuerySchema().load(request.args.to_dict())
    except ValidationError as e:
        return error("Invalid query parameters.", 422, errors=e.messages)

    user = get_current_user()
    data = get_monthly_breakdown(user.id, year=params.get("year"))
    return success(data=data, message="Monthly breakdown retrieved.")


@analytics_bp.route("/categories", methods=["GET"])
@jwt_required()
@analyst_or_above
def categories():
    """
    GET /analytics/categories?type=expense
    Returns category-wise totals, optionally filtered by transaction type.
    Access: analyst, admin
    """
    try:
        params = CategoryQuerySchema().load(request.args.to_dict())
    except ValidationError as e:
        return error("Invalid query parameters.", 422, errors=e.messages)

    user = get_current_user()
    data = get_category_breakdown(user.id, txn_type=params.get("type"))
    return success(data=data, message="Category breakdown retrieved.")


@analytics_bp.route("/recent", methods=["GET"])
@jwt_required()
def recent():
    """
    GET /analytics/recent?limit=10
    Returns the most recent N transactions.
    Access: viewer, analyst, admin
    """
    try:
        params = RecentQuerySchema().load(request.args.to_dict())
    except ValidationError as e:
        return error("Invalid query parameters.", 422, errors=e.messages)

    user = get_current_user()
    if not user:
        return error("Unauthorized.", 401)

    data = get_recent_transactions(user.id, limit=params["limit"])
    return success(data=data, message="Recent transactions retrieved.")
