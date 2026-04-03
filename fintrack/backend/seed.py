"""
seed.py — Populates the database with realistic mock data for testing.

Usage:
    python seed.py

Creates:
  - 3 users (admin, analyst, viewer)
  - ~40 transactions spread across 3 months
"""

from app import create_app
from app.extensions import db, bcrypt
from app.models.user import User, RoleEnum
from app.models.transaction import Transaction, TransactionType
from datetime import date, timedelta
import random

app = create_app()

INCOME_CATEGORIES = ["Salary", "Freelance", "Investment", "Bonus", "Rental Income"]
EXPENSE_CATEGORIES = ["Rent", "Groceries", "Utilities", "Transport", "Dining", "Healthcare", "Entertainment", "Insurance"]

SAMPLE_NOTES = [
    "Monthly payment",
    "Q3 bonus received",
    "Recurring expense",
    "One-time purchase",
    "Split with partner",
    None,
    None,
]


def random_date_in_range(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def seed():
    with app.app_context():
        print("🌱 Seeding database...")

        # Drop and recreate all tables (dev only)
        db.drop_all()
        db.create_all()

        # ── Users ──────────────────────────────────────────────────
        admin = User(
            name="Alice Admin",
            email="admin@fintrack.com",
            password_hash=bcrypt.generate_password_hash("Admin@123").decode("utf-8"),
            role=RoleEnum.ADMIN,
        )
        analyst = User(
            name="Bob Analyst",
            email="analyst@fintrack.com",
            password_hash=bcrypt.generate_password_hash("Analyst@123").decode("utf-8"),
            role=RoleEnum.ANALYST,
        )
        viewer = User(
            name="Carol Viewer",
            email="viewer@fintrack.com",
            password_hash=bcrypt.generate_password_hash("Viewer@123").decode("utf-8"),
            role=RoleEnum.VIEWER,
        )
        db.session.add_all([admin, analyst, viewer])
        db.session.flush()  # get IDs before commit

        # ── Transactions for admin user ────────────────────────────
        start = date(2024, 10, 1)
        end = date(2025, 1, 15)

        transactions = []

        # Fixed income entries
        fixed_incomes = [
            (5000.00, "Salary", date(2024, 10, 1), "October salary"),
            (5000.00, "Salary", date(2024, 11, 1), "November salary"),
            (5000.00, "Salary", date(2024, 12, 1), "December salary"),
            (1500.00, "Freelance", date(2024, 10, 15), "Website project"),
            (2000.00, "Bonus", date(2024, 12, 20), "Year-end performance bonus"),
            (800.00,  "Investment", date(2024, 11, 10), "Dividend income"),
        ]

        for amount, category, txn_date, notes in fixed_incomes:
            transactions.append(Transaction(
                user_id=admin.id,
                amount=amount,
                type=TransactionType.INCOME,
                category=category,
                date=txn_date,
                notes=notes,
            ))

        # Fixed expense entries
        fixed_expenses = [
            (1200.00, "Rent",          date(2024, 10, 3),  "October rent"),
            (1200.00, "Rent",          date(2024, 11, 3),  "November rent"),
            (1200.00, "Rent",          date(2024, 12, 3),  "December rent"),
            (250.00,  "Groceries",     date(2024, 10, 8),  None),
            (230.00,  "Groceries",     date(2024, 11, 9),  None),
            (280.00,  "Groceries",     date(2024, 12, 7),  "Holiday shopping"),
            (80.00,   "Utilities",     date(2024, 10, 12), "Electricity bill"),
            (90.00,   "Utilities",     date(2024, 11, 12), "Water + electricity"),
            (75.00,   "Utilities",     date(2024, 12, 12), "Electricity"),
            (120.00,  "Transport",     date(2024, 10, 20), "Monthly pass"),
            (120.00,  "Transport",     date(2024, 11, 20), "Monthly pass"),
            (120.00,  "Transport",     date(2024, 12, 20), "Monthly pass"),
            (200.00,  "Dining",        date(2024, 10, 25), "Team dinner"),
            (150.00,  "Dining",        date(2024, 11, 18), None),
            (320.00,  "Entertainment", date(2024, 12, 26), "New Year plans"),
            (400.00,  "Healthcare",    date(2024, 11, 5),  "Annual checkup"),
            (180.00,  "Insurance",     date(2024, 10, 1),  "Health insurance premium"),
            (180.00,  "Insurance",     date(2024, 11, 1),  "Health insurance premium"),
            (180.00,  "Insurance",     date(2024, 12, 1),  "Health insurance premium"),
        ]

        for amount, category, txn_date, notes in fixed_expenses:
            transactions.append(Transaction(
                user_id=admin.id,
                amount=amount,
                type=TransactionType.EXPENSE,
                category=category,
                date=txn_date,
                notes=notes,
            ))

        # A few random transactions for analyst user
        for _ in range(10):
            txn_type = random.choice(TransactionType.ALL)
            category = random.choice(
                INCOME_CATEGORIES if txn_type == TransactionType.INCOME else EXPENSE_CATEGORIES
            )
            amount = round(random.uniform(50, 3000), 2)
            transactions.append(Transaction(
                user_id=analyst.id,
                amount=amount,
                type=txn_type,
                category=category,
                date=random_date_in_range(start, end),
                notes=random.choice(SAMPLE_NOTES),
            ))

        db.session.add_all(transactions)
        db.session.commit()

        print("✅ Seeding complete!\n")
        print("  Users created:")
        print(f"    Admin   → admin@fintrack.com    / Admin@123")
        print(f"    Analyst → analyst@fintrack.com  / Analyst@123")
        print(f"    Viewer  → viewer@fintrack.com   / Viewer@123")
        print(f"\n  Transactions: {len(transactions)} records inserted.")


if __name__ == "__main__":
    seed()
