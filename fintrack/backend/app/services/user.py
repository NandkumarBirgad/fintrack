from app.extensions import db
from app.models.user import User, RoleEnum


def get_all_users():
    """Returns all users in the system."""
    return User.query.order_by(User.created_at.desc()).all()


def get_user_by_id(user_id: int):
    """Fetch a user by primary key."""
    return User.query.get(user_id)


def update_user(user_id: int, data: dict):
    """
    Admin: update a user's name, role, or active status.
    Returns (user, error_message).
    """
    user = User.query.get(user_id)
    if not user:
        return None, "User not found."

    if "name" in data:
        user.name = data["name"].strip()

    if "role" in data:
        if data["role"] not in RoleEnum.ALL:
            return None, f"Invalid role. Choose from: {', '.join(RoleEnum.ALL)}"
        user.role = data["role"]

    if "is_active" in data:
        user.is_active = data["is_active"]

    db.session.commit()
    return user, None


def delete_user(user_id: int, requesting_user_id: int):
    """
    Admin: deletes a user. Cannot delete yourself.
    Returns (True, None) or (False, error_message).
    """
    if user_id == requesting_user_id:
        return False, "You cannot delete your own account."

    user = User.query.get(user_id)
    if not user:
        return False, "User not found."

    db.session.delete(user)
    db.session.commit()
    return True, None
