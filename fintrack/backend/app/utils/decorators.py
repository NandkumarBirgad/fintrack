from functools import wraps
from flask_jwt_extended import get_jwt_identity
from app.models.user import User, RoleEnum
from app.utils.responses import error

# Role hierarchy — higher index = more permissions
ROLE_HIERARCHY = {
    RoleEnum.VIEWER: 0,
    RoleEnum.ANALYST: 1,
    RoleEnum.ADMIN: 2,
}


def role_required(*allowed_roles):
    """
    Decorator that restricts a route to users with one of the allowed roles.

    Usage:
        @role_required(RoleEnum.ADMIN)
        @role_required(RoleEnum.ANALYST, RoleEnum.ADMIN)
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user or not user.is_active:
                return error("User not found or inactive.", 401)

            if user.role not in allowed_roles:
                return error(
                    f"Access denied. Required role(s): {', '.join(allowed_roles)}.",
                    403,
                )
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def analyst_or_above(fn):
    """Shorthand: allows analyst and admin."""
    return role_required(RoleEnum.ANALYST, RoleEnum.ADMIN)(fn)


def admin_only(fn):
    """Shorthand: allows admin only."""
    return role_required(RoleEnum.ADMIN)(fn)


def get_current_user():
    """Returns the current logged-in User object."""
    user_id = get_jwt_identity()
    return User.query.get(user_id)
