from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.schemas.user import UserOutputSchema, UpdateUserSchema
from app.services.user import get_all_users, get_user_by_id, update_user, delete_user
from app.utils.responses import success, error
from app.utils.decorators import get_current_user, admin_only

users_bp = Blueprint("users", __name__)

user_output_schema = UserOutputSchema()
users_output_schema = UserOutputSchema(many=True)
update_schema = UpdateUserSchema()


@users_bp.route("", methods=["GET"])
@jwt_required()
@admin_only
def list_users():
    """
    GET /users
    List all registered users.
    Access: admin only
    """
    users = get_all_users()
    return success(
        data=users_output_schema.dump(users),
        message=f"{len(users)} user(s) found.",
    )


@users_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
@admin_only
def get_user(user_id):
    """
    GET /users/<id>
    Retrieve a single user's details.
    Access: admin only
    """
    user = get_user_by_id(user_id)
    if not user:
        return error("User not found.", 404)
    return success(data=user_output_schema.dump(user))


@users_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
@admin_only
def update(user_id):
    """
    PUT /users/<id>
    Update a user's name, role, or active status.
    Body: { name?, role?, is_active? }
    Access: admin only
    """
    try:
        data = update_schema.load(request.get_json() or {})
    except ValidationError as e:
        return error("Validation failed.", 422, errors=e.messages)

    if not data:
        return error("No valid fields provided.", 400)

    user, err = update_user(user_id, data)
    if err:
        return error(err, 404)

    return success(data=user_output_schema.dump(user), message="User updated.")


@users_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
@admin_only
def delete(user_id):
    """
    DELETE /users/<id>
    Delete a user and all their transactions.
    Access: admin only (cannot delete self)
    """
    requesting_user = get_current_user()
    ok, err = delete_user(user_id, requesting_user.id)
    if not ok:
        return error(err, 400)

    return success(message="User deleted successfully.")
