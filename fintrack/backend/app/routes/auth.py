from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.schemas.user import RegisterSchema, LoginSchema, UserOutputSchema
from app.services.auth import register_user, login_user, refresh_access_token
from app.utils.responses import success, error

auth_bp = Blueprint("auth", __name__)

register_schema = RegisterSchema()
login_schema = LoginSchema()
user_output_schema = UserOutputSchema()


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    POST /auth/register
    Register a new user account.
    Body: { name, email, password, role (optional) }
    """
    try:
        data = register_schema.load(request.get_json() or {})
    except ValidationError as e:
        return error("Validation failed.", 422, errors=e.messages)

    user, err = register_user(
        name=data["name"],
        email=data["email"],
        password=data["password"],
        role=data.get("role", "viewer"),
    )

    if err:
        return error(err, 409)

    return success(
        data=user_output_schema.dump(user),
        message="Account created successfully.",
        status=201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    POST /auth/login
    Authenticate and receive JWT tokens.
    Body: { email, password }
    """
    try:
        data = login_schema.load(request.get_json() or {})
    except ValidationError as e:
        return error("Validation failed.", 422, errors=e.messages)

    tokens, err = login_user(data["email"], data["password"])
    if err:
        return error(err, 401)

    return success(data=tokens, message="Login successful.")


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    POST /auth/refresh
    Get a new access token using a valid refresh token.
    Header: Authorization: Bearer <refresh_token>
    """
    user_id = get_jwt_identity()
    tokens, err = refresh_access_token(user_id)
    if err:
        return error(err, 401)
    return success(data=tokens, message="Token refreshed.")


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """
    GET /auth/me
    Returns the currently authenticated user's profile.
    """
    user_id = get_jwt_identity()
    from app.models.user import User
    user = User.query.get(user_id)
    if not user:
        return error("User not found.", 404)
    return success(data=user_output_schema.dump(user))
