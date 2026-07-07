"""
test_auth.py
Integration tests for authentication endpoints.
Tests signup, login, and current user profile.
Uses the client and db fixtures from conftest.py.
"""

import pytest


# ── Signup tests ──────────────────────────────────────────────────────────────

class TestSignup:
    """Tests for POST /api/v1/auth/signup"""

    def test_signup_happy_path(self, client):
        # Arrange
        payload = {
            "username": "chidi",
            "email": "chidi@gmail.com",
            "password": "securepassword123",
        }
        # Act
        response = client.post("/api/v1/auth/signup", json=payload)
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "chidi@gmail.com"
        assert data["username"] == "chidi"
        assert data["role"] == "user"
        assert data["is_active"] is True

    def test_signup_password_never_in_response(self, client):
        payload = {
            "username": "chidi",
            "email": "chidi@gmail.com",
            "password": "securepassword123",
        }
        response = client.post("/api/v1/auth/signup", json=payload)
        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data

    def test_signup_duplicate_email(self, client):
        payload = {
            "username": "chidi",
            "email": "chidi@gmail.com",
            "password": "securepassword123",
        }
        # First signup
        client.post("/api/v1/auth/signup", json=payload)
        # Second signup with same email
        payload["username"] = "chidi2"
        response = client.post("/api/v1/auth/signup", json=payload)
        assert response.status_code == 400

    def test_signup_duplicate_username(self, client):
        payload = {
            "username": "chidi",
            "email": "chidi@gmail.com",
            "password": "securepassword123",
        }
        client.post("/api/v1/auth/signup", json=payload)
        payload["email"] = "different@gmail.com"
        response = client.post("/api/v1/auth/signup", json=payload)
        assert response.status_code == 400

    def test_signup_invalid_email(self, client):
        payload = {
            "username": "chidi",
            "email": "notanemail",
            "password": "securepassword123",
        }
        response = client.post("/api/v1/auth/signup", json=payload)
        assert response.status_code == 422

    def test_signup_missing_password(self, client):
        payload = {
            "username": "chidi",
            "email": "chidi@gmail.com",
        }
        response = client.post("/api/v1/auth/signup", json=payload)
        assert response.status_code == 422

    def test_signup_role_cannot_be_set_by_user(self, client):
        # User tries to sign up as admin
        payload = {
            "username": "hacker",
            "email": "hacker@gmail.com",
            "password": "password123",
            "role": "admin",  # should be ignored
        }
        response = client.post("/api/v1/auth/signup", json=payload)
        assert response.status_code == 201
        assert response.json()["role"] == "user"  # always user, never admin

    def test_signup_sql_injection_handled_safely(self, client):
        payload = {
            "username": "'; DROP TABLE users; --",
            "email": "safe@gmail.com",
            "password": "password123",
        }
        response = client.post("/api/v1/auth/signup", json=payload)
        # Should not crash — either 201 or 422, never 500
        assert response.status_code != 500


# ── Login tests ───────────────────────────────────────────────────────────────

class TestLogin:
    """Tests for POST /api/v1/auth/login"""

    def test_login_happy_path(self, client):
        # Arrange — create user first
        client.post("/api/v1/auth/signup", json={
            "username": "chidi",
            "email": "chidi@gmail.com",
            "password": "securepassword123",
        })
        # Act
        response = client.post("/api/v1/auth/login", data={
            "username": "chidi@gmail.com",
            "password": "securepassword123",
        })
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        client.post("/api/v1/auth/signup", json={
            "username": "chidi",
            "email": "chidi@gmail.com",
            "password": "correctpassword",
        })
        response = client.post("/api/v1/auth/login", data={
            "username": "chidi@gmail.com",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_login_nonexistent_email(self, client):
        response = client.post("/api/v1/auth/login", data={
            "username": "ghost@gmail.com",
            "password": "password123",
        })
        assert response.status_code == 401

    def test_login_wrong_email_and_wrong_password_same_error(self, client):
        """
        Security test — both failures must return identical error messages.
        Prevents user enumeration: attacker can't tell if email exists.
        """
        response_bad_email = client.post("/api/v1/auth/login", data={
            "username": "ghost@gmail.com",
            "password": "password123",
        })
        client.post("/api/v1/auth/signup", json={
            "username": "chidi",
            "email": "chidi@gmail.com",
            "password": "correctpassword",
        })
        response_bad_password = client.post("/api/v1/auth/login", data={
            "username": "chidi@gmail.com",
            "password": "wrongpassword",
        })
        assert response_bad_email.json()["detail"] == \
               response_bad_password.json()["detail"]


# ── /me tests ─────────────────────────────────────────────────────────────────

class TestMe:
    """Tests for GET /api/v1/auth/me"""

    def _get_token(self, client):
        """Helper — signup and login, return token."""
        client.post("/api/v1/auth/signup", json={
            "username": "chidi",
            "email": "chidi@gmail.com",
            "password": "securepassword123",
        })
        response = client.post("/api/v1/auth/login", data={
            "username": "chidi@gmail.com",
            "password": "securepassword123",
        })
        return response.json()["access_token"]

    def test_me_happy_path(self, client):
        token = self._get_token(client)
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["email"] == "chidi@gmail.com"

    def test_me_no_token(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_me_invalid_token(self, client):
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalidtoken"}
        )
        assert response.status_code == 401

    def test_me_password_never_in_response(self, client):
        token = self._get_token(client)
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data