from app.extensions import db
from datetime import datetime, timezone


class TransactionType:
    INCOME = "income"
    EXPENSE = "expense"
    ALL = [INCOME, EXPENSE]


class Transaction(db.Model):
    """
    Represents a single financial record (income or expense).
    Belongs to a User (owner).
    """
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    type = db.Column(db.String(10), nullable=False)          # income / expense
    category = db.Column(db.String(100), nullable=False)     # e.g. Salary, Rent, Food
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Transaction {self.type} {self.amount} [{self.category}]>"
