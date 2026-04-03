from app.extensions import db
from app.models.transaction import Transaction
from datetime import date


def create_transaction(user_id: int, data: dict):
    """Creates and persists a new transaction record."""
    txn = Transaction(
        user_id=user_id,
        amount=data["amount"],
        type=data["type"],
        category=data["category"].strip(),
        date=data["date"],
        notes=data.get("notes"),
    )
    db.session.add(txn)
    db.session.commit()
    return txn


def get_transactions(user_id: int, filters: dict):
    """
    Returns a paginated list of transactions for the workspace,
    with optional filters: type, category, date_from, date_to.
    """
    query = Transaction.query

    if filters.get("type"):
        query = query.filter(Transaction.type == filters["type"])

    if filters.get("category"):
        query = query.filter(
            Transaction.category.ilike(f"%{filters['category']}%")
        )

    if filters.get("date_from"):
        query = query.filter(Transaction.date >= filters["date_from"])

    if filters.get("date_to"):
        query = query.filter(Transaction.date <= filters["date_to"])

    query = query.order_by(Transaction.date.desc(), Transaction.id.desc())

    page = filters.get("page", 1)
    per_page = filters.get("per_page", 20)
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return paginated


def get_transaction_by_id(transaction_id: int, user_id: int):
    """Fetches a single transaction by ID for the workspace."""
    return Transaction.query.filter_by(id=transaction_id).first()


def update_transaction(transaction_id: int, user_id: int, data: dict):
    """
    Updates allowed fields on an existing transaction.
    Returns (transaction, error_message).
    """
    txn = get_transaction_by_id(transaction_id, user_id)
    if not txn:
        return None, "Transaction not found."

    updatable_fields = ["amount", "type", "category", "date", "notes"]
    for field in updatable_fields:
        if field in data:
            value = data[field]
            if field == "category" and isinstance(value, str):
                value = value.strip()
            setattr(txn, field, value)

    db.session.commit()
    return txn, None


def delete_transaction(transaction_id: int, user_id: int):
    """
    Deletes a transaction.
    Returns (True, None) on success or (False, error_message) on failure.
    """
    txn = get_transaction_by_id(transaction_id, user_id)
    if not txn:
        return False, "Transaction not found."

    db.session.delete(txn)
    db.session.commit()
    return True, None
