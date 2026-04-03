"""
tests/test_api.py — Unit tests for FinTrack API.

Run with:
    python -m pytest tests/ -v
"""

import pytest
import json
from app import create_app
from app.extensions import db as _db
from app.models.user import User, RoleEnum
from app.extensions import bcrypt


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def app():
    """Create a test Flask app using SQLite in-memory DB."""
    test_app = create_app()
    test_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_ECHO": False,
        "JWT_SECRET_KEY": "test-secret",
    })
    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def seed_users(app):
    """Insert admin, analyst, viewer users once for the session."""
    with app.app_context():
        admin = User(
            name="Test Admin",
            email="admin@test.com",
            password_hash=bcrypt.generate_password_hash("Admin@123").decode("utf-8"),
            role=RoleEnum.ADMIN,
        )
        analyst = User(
            name="Test Analyst",
            email="analyst@test.com",
            password_hash=bcrypt.generate_password_hash("Analyst@123").decode("utf-8"),
            role=RoleEnum.ANALYST,
        )
        viewer = User(
            name="Test Viewer",
            email="viewer@test.com",
            password_hash=bcrypt.generate_password_hash("Viewer@123").decode("utf-8"),
            role=RoleEnum.VIEWER,
        )
        _db.session.add_all([admin, analyst, viewer])
        _db.session.commit()
    return {"admin": "admin@test.com", "analyst": "analyst@test.com", "viewer": "viewer@test.com"}


def get_token(client, email, password):
    """Helper to log in and return the access token."""
    resp = client.post(
        "/auth/login",
        json={"email": email, "password": password},
        content_type="application/json",
    )
    return resp.get_json()["data"]["access_token"]


# ─── Auth Tests ───────────────────────────────────────────────────────────────

class TestAuth:

    def test_register_success(self, client):
        resp = client.post("/auth/register", json={
            "name": "New User",
            "email": "newuser@test.com",
            "password": "Pass@123",
            "role": "viewer",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["success"] is True
        assert data["data"]["email"] == "newuser@test.com"

    def test_register_duplicate_email(self, client, seed_users):
        resp = client.post("/auth/register", json={
            "name": "Dup",
            "email": "admin@test.com",
            "password": "Admin@123",
        })
        assert resp.status_code == 409

    def test_register_missing_fields(self, client):
        resp = client.post("/auth/register", json={"name": "Missing"})
        assert resp.status_code == 422
        assert "errors" in resp.get_json()

    def test_register_invalid_email(self, client):
        resp = client.post("/auth/register", json={
            "name": "Bad Email",
            "email": "not-an-email",
            "password": "Pass@123",
        })
        assert resp.status_code == 422

    def test_login_success(self, client, seed_users):
        resp = client.post("/auth/login", json={
            "email": "admin@test.com",
            "password": "Admin@123",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]

    def test_login_wrong_password(self, client, seed_users):
        resp = client.post("/auth/login", json={
            "email": "admin@test.com",
            "password": "WrongPass",
        })
        assert resp.status_code == 401

    def test_login_unknown_email(self, client):
        resp = client.post("/auth/login", json={
            "email": "ghost@test.com",
            "password": "Pass@123",
        })
        assert resp.status_code == 401

    def test_me_authenticated(self, client, seed_users):
        token = get_token(client, "admin@test.com", "Admin@123")
        resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.get_json()["data"]["email"] == "admin@test.com"

    def test_me_unauthenticated(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 401


# ─── Transaction Tests ────────────────────────────────────────────────────────

class TestTransactions:

    def test_create_transaction_as_admin(self, client, seed_users):
        token = get_token(client, "admin@test.com", "Admin@123")
        resp = client.post("/transactions", json={
            "amount": 5000.00,
            "type": "income",
            "category": "Salary",
            "date": "2024-10-01",
            "notes": "October salary",
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 201
        data = resp.get_json()["data"]
        assert data["category"] == "Salary"
        assert data["type"] == "income"

    def test_create_transaction_as_viewer_forbidden(self, client, seed_users):
        token = get_token(client, "viewer@test.com", "Viewer@123")
        resp = client.post("/transactions", json={
            "amount": 100,
            "type": "expense",
            "category": "Food",
            "date": "2024-10-05",
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403

    def test_create_transaction_negative_amount(self, client, seed_users):
        token = get_token(client, "admin@test.com", "Admin@123")
        resp = client.post("/transactions", json={
            "amount": -500,
            "type": "expense",
            "category": "Rent",
            "date": "2024-10-01",
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 422

    def test_create_transaction_invalid_type(self, client, seed_users):
        token = get_token(client, "admin@test.com", "Admin@123")
        resp = client.post("/transactions", json={
            "amount": 100,
            "type": "transfer",   # invalid
            "category": "Misc",
            "date": "2024-10-01",
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 422

    def test_list_transactions_as_viewer(self, client, seed_users):
        token = get_token(client, "viewer@test.com", "Viewer@123")
        resp = client.get("/transactions", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_update_transaction_as_admin(self, client, seed_users):
        # First create
        token = get_token(client, "admin@test.com", "Admin@123")
        create_resp = client.post("/transactions", json={
            "amount": 200,
            "type": "expense",
            "category": "Groceries",
            "date": "2024-10-10",
        }, headers={"Authorization": f"Bearer {token}"})
        txn_id = create_resp.get_json()["data"]["id"]

        # Then update
        resp = client.put(f"/transactions/{txn_id}", json={
            "amount": 250,
            "notes": "Updated amount",
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.get_json()["data"]["notes"] == "Updated amount"

    def test_delete_transaction_as_admin(self, client, seed_users):
        token = get_token(client, "admin@test.com", "Admin@123")
        create_resp = client.post("/transactions", json={
            "amount": 99,
            "type": "expense",
            "category": "Misc",
            "date": "2024-10-15",
        }, headers={"Authorization": f"Bearer {token}"})
        txn_id = create_resp.get_json()["data"]["id"]

        del_resp = client.delete(
            f"/transactions/{txn_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert del_resp.status_code == 200

        # Verify gone
        get_resp = client.get(
            f"/transactions/{txn_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert get_resp.status_code == 404

    def test_delete_nonexistent_transaction(self, client, seed_users):
        token = get_token(client, "admin@test.com", "Admin@123")
        resp = client.delete("/transactions/99999", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404


# ─── Analytics Tests ──────────────────────────────────────────────────────────

class TestAnalytics:

    def test_summary_accessible_to_viewer(self, client, seed_users):
        token = get_token(client, "viewer@test.com", "Viewer@123")
        resp = client.get("/analytics/summary", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert "total_income" in data
        assert "total_expenses" in data
        assert "net_balance" in data

    def test_monthly_blocked_for_viewer(self, client, seed_users):
        token = get_token(client, "viewer@test.com", "Viewer@123")
        resp = client.get("/analytics/monthly", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403

    def test_monthly_accessible_to_analyst(self, client, seed_users):
        token = get_token(client, "analyst@test.com", "Analyst@123")
        resp = client.get("/analytics/monthly", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_categories_accessible_to_admin(self, client, seed_users):
        token = get_token(client, "admin@test.com", "Admin@123")
        resp = client.get("/analytics/categories?type=expense", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_recent_returns_list(self, client, seed_users):
        token = get_token(client, "admin@test.com", "Admin@123")
        resp = client.get("/analytics/recent?limit=5", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert isinstance(resp.get_json()["data"], list)


# ─── Health Check ─────────────────────────────────────────────────────────────

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"
