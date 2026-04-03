from app.extensions import db
from datetime import datetime, timezone


class RoleEnum:
    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"

    ALL = [VIEWER, ANALYST, ADMIN]


class User(db.Model):
    """
    Represents a system user.

    Roles:
      - viewer   : read-only access to transactions & summaries
      - analyst  : viewer + filters + detailed analytics
      - admin    : full CRUD + user management
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=RoleEnum.VIEWER)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship: one user -> many transactions
    transactions = db.relationship(
        "Transaction", backref="owner", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.email} [{self.role}]>"
