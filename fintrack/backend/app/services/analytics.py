from sqlalchemy import func, extract
from app.extensions import db
from app.models.transaction import Transaction, TransactionType
from decimal import Decimal


def get_summary(user_id: int) -> dict:
    """
    Returns total income, total expenses, net balance, and savings percentage.
    """
    rows = (
        db.session.query(Transaction.type, func.sum(Transaction.amount))
        .group_by(Transaction.type)
        .all()
    )

    totals = {TransactionType.INCOME: Decimal("0"), TransactionType.EXPENSE: Decimal("0")}
    for txn_type, total in rows:
        totals[txn_type] = total or Decimal("0")

    income = totals[TransactionType.INCOME]
    expenses = totals[TransactionType.EXPENSE]
    balance = income - expenses
    
    savings_pct = "0"
    if income > 0:
        savings_pct = str(round((max(Decimal("0"), balance) / income) * 100, 1))

    return {
        "total_income": str(income),
        "total_expenses": str(expenses),
        "net_balance": str(balance),
        "balance_status": "surplus" if balance >= 0 else "deficit",
        "savings_percentage": savings_pct
    }

def get_alerts() -> list:
    """Smart Alerts & Budget Warnings (Trend Analysis)"""
    from datetime import datetime
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    
    BUDGETS = {"Food": Decimal("5000"), "Travel": Decimal("3000"), "Entertainment": Decimal("2000")}
    
    month_expenses = (
        db.session.query(Transaction.category, func.sum(Transaction.amount))
        .filter(Transaction.type == TransactionType.EXPENSE)
        .filter(extract('month', Transaction.date) == current_month)
        .filter(extract('year', Transaction.date) == current_year)
        .group_by(Transaction.category)
        .all()
    )
    
    alerts = []
    for cat, total in month_expenses:
        if cat in BUDGETS and total > BUDGETS[cat]:
            alerts.append({
                "type": "warning", 
                "message": f"Budget Exceeded: You spent ₹{total} on {cat} this month (Limit: ₹{BUDGETS[cat]})."
            })
            
    large_txns = Transaction.query.filter(Transaction.type == TransactionType.EXPENSE, Transaction.amount > 10000).limit(1).count()
    if large_txns > 0:
        alerts.append({"type": "info", "message": "High Expense Alert: You have recorded an unusually large transaction (>₹10000)."})

    return alerts


def get_monthly_breakdown(user_id: int, year: int = None) -> list:
    """
    Returns month-wise income and expense totals.
    If year is provided, filters to that year only.
    """
    query = (
        db.session.query(
            extract("year", Transaction.date).label("year"),
            extract("month", Transaction.date).label("month"),
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
        )
        .group_by("year", "month", Transaction.type)
        .order_by("year", "month")
    )

    if year:
        query = query.filter(extract("year", Transaction.date) == year)

    rows = query.all()

    # Pivot into {year-month: {income: X, expense: Y}} structure
    pivot = {}
    for row in rows:
        key = f"{int(row.year)}-{int(row.month):02d}"
        if key not in pivot:
            pivot[key] = {
                "year": int(row.year),
                "month": int(row.month),
                "month_label": key,
                "income": "0.00",
                "expenses": "0.00",
                "net": "0.00",
            }
        if row.type == TransactionType.INCOME:
            pivot[key]["income"] = str(row.total)
        else:
            pivot[key]["expenses"] = str(row.total)

    # Compute net per month
    result = []
    for entry in pivot.values():
        income = Decimal(entry["income"])
        expenses = Decimal(entry["expenses"])
        entry["net"] = str(income - expenses)
        result.append(entry)

    return result


def get_category_breakdown(user_id: int, txn_type: str = None) -> list:
    """
    Returns spending/income breakdown by category.
    Optionally filtered by transaction type.
    """
    query = (
        db.session.query(
            Transaction.category,
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count"),
        )
        .group_by(Transaction.category, Transaction.type)
        .order_by(func.sum(Transaction.amount).desc())
    )

    if txn_type:
        query = query.filter(Transaction.type == txn_type)

    rows = query.all()
    return [
        {
            "category": row.category,
            "type": row.type,
            "total": str(row.total),
            "transaction_count": row.count,
        }
        for row in rows
    ]


def get_recent_transactions(user_id: int, limit: int = 10) -> list:
    """Returns the most recent N transactions for the user."""
    limit = max(1, min(limit, 50))  # clamp between 1 and 50
    rows = (
        Transaction.query
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": t.id,
            "amount": str(t.amount),
            "type": t.type,
            "category": t.category,
            "date": str(t.date),
            "notes": t.notes,
        }
        for t in rows
    ]
