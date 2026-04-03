from flask_jwt_extended import create_access_token, create_refresh_token
from app.extensions import db, bcrypt
from app.models.user import User, RoleEnum


def register_user(name: str, email: str, password: str, role: str = RoleEnum.VIEWER):
    """
    Creates a new user.
    Returns (user, error_message).
    """
    if User.query.filter_by(email=email.lower()).first():
        return None, "Email is already registered."

    if role not in RoleEnum.ALL:
        return None, f"Invalid role. Choose from: {', '.join(RoleEnum.ALL)}"

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(
        name=name.strip(),
        email=email.lower().strip(),
        password_hash=hashed,
        role=role,
    )
    db.session.add(user)
    db.session.commit()
    return user, None


def login_user(email: str, password: str):
    """
    Validates credentials and returns JWT tokens.
    Returns (tokens_dict, error_message).
    """
    user = User.query.filter_by(email=email.lower()).first()

    if not user:
        return None, "Invalid email or password."

    if not user.is_active:
        return None, "Account is deactivated. Contact an admin."

    if not bcrypt.check_password_hash(user.password_hash, password):
        return None, "Invalid email or password."

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
    }, None


def refresh_access_token(user_id: int):
    """Issues a new access token from a valid refresh token."""
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return None, "User not found or inactive."
    access_token = create_access_token(identity=str(user.id))
    return {"access_token": access_token}, None
