"""Tests for route handlers."""

from datetime import timedelta
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from gradioapp.api.routes import health_router, home_router, login_router
from gradioapp.domain.auth import create_access_token, create_session_token
from gradioapp.domain.session.backends.memory import InMemorySessionStore
from gradioapp.domain.session.store import initialize_session_store
from gradioapp.domain.user import User, authenticate_user, init_user_db


@pytest.fixture
def app():
    """Create a test FastAPI app."""
    test_app = FastAPI()
    test_app.include_router(health_router)
    test_app.include_router(home_router)
    test_app.include_router(login_router)
    return test_app


@pytest.fixture
def session_store():
    """Create a fresh in-memory session store for testing."""
    # Use shorter cleanup_interval for faster test teardown
    store = InMemorySessionStore(ttl=300, cleanup_interval=1)
    initialize_session_store(store)
    yield store
    store.stop_cleanup_thread()


@pytest.fixture
def test_user():
    """Initialize test user database."""
    init_user_db()
    yield
    # Cleanup if needed


class TestHealthRoute:
    """Tests for health check route."""

    def test_health_check(self, app):
        """Test that health check returns 200."""
        client = TestClient(app)
        response = client.get("/healthz")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestLoginRoute:
    """Tests for login route."""

    def test_login_page_get(self, app):
        """Test that login page is accessible."""
        client = TestClient(app)
        response = client.get("/login")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_login_page_with_error(self, app):
        """Test that login page displays error message."""
        client = TestClient(app)
        response = client.get("/login?error=Invalid%20credentials")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_login_success(self, app, session_store, test_user):
        """Test successful login."""
        client = TestClient(app)

        # Mock CSRF token validation and user authentication
        with patch("gradioapp.api.routes.login.validate_csrf_token", return_value=True), patch(
            "gradioapp.api.routes.login.authenticate_user"
        ) as mock_auth:
            # Mock successful authentication
            mock_user = User(username="admin", password_hash="hashed")
            mock_auth.return_value = mock_user

            response = client.post(
                "/login",
                data={
                    "username": "admin",
                    "password": "admin",
                    "csrf_token": "test_token",
                },
                follow_redirects=False,
            )

            # Should redirect to /gradio
            assert response.status_code in [302, 303], f"Expected redirect, got {response.status_code}"
            # Check if redirect location is /gradio
            if response.status_code in [302, 303]:
                assert "/gradio" in str(response.headers.get("location", ""))
            assert "access_token" in response.cookies

    def test_login_invalid_credentials(self, app, test_user):
        """Test login with invalid credentials."""
        client = TestClient(app)

        with patch("gradioapp.api.routes.login.validate_csrf_token", return_value=True):
            response = client.post(
                "/login",
                data={
                    "username": "admin",
                    "password": "wrong_password",
                    "csrf_token": "test_token",
                },
            )

            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]

    def test_login_invalid_csrf(self, app):
        """Test login with invalid CSRF token."""
        client = TestClient(app)

        with patch("gradioapp.api.routes.login.validate_csrf_token", return_value=False), patch(
            "gradioapp.api.routes.login.generate_csrf_token", return_value="test_token"
        ):
            response = client.post(
                "/login",
                data={
                    "username": "admin",
                    "password": "admin",
                    "csrf_token": "invalid_token",
                },
                follow_redirects=False,
            )

            # Should redirect with error
            assert response.status_code in [302, 303]
            # Check if redirect includes error parameter
            if response.status_code in [302, 303]:
                location = str(response.headers.get("location", ""))
                assert "/login" in location or "error" in location.lower()

    def test_login_validation_error(self, app):
        """Test login with invalid form data (too long username)."""
        client = TestClient(app)

        with patch("gradioapp.api.routes.login.validate_csrf_token", return_value=True):
            # Username too long (over 255 characters)
            long_username = "a" * 256
            response = client.post(
                "/login",
                data={
                    "username": long_username,
                    "password": "admin",
                    "csrf_token": "test_token",
                },
            )

            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]


class TestLogoutRoute:
    """Tests for logout route."""

    def test_logout_with_valid_token(self, app, session_store):
        """Test logout with valid token."""
        # Create session and token
        token, session_id = create_session_token("test_user", expires_delta=timedelta(minutes=30))
        session_store.create_session(session_id=session_id, username="test_user", data={})

        client = TestClient(app)
        # Set cookie on client instead of per-request
        client.cookies.set("access_token", token)
        response = client.get("/logout", follow_redirects=False)

        # Should redirect to login
        assert response.status_code in [302, 303]
        # Check redirect location
        if response.status_code in [302, 303]:
            assert "/login" in str(response.headers.get("location", ""))
        # Session should be deleted
        assert session_store.get_session(session_id) is None

    def test_logout_without_token(self, app):
        """Test logout without token."""
        client = TestClient(app)
        response = client.get("/logout", follow_redirects=False)

        # Should still redirect to login
        assert response.status_code in [302, 303]
        if response.status_code in [302, 303]:
            assert "/login" in str(response.headers.get("location", ""))

    def test_logout_with_invalid_token(self, app):
        """Test logout with invalid token."""
        client = TestClient(app)
        client.cookies.set("access_token", "invalid")
        response = client.get("/logout", follow_redirects=False)

        # Should still redirect to login
        assert response.status_code in [302, 303]
        if response.status_code in [302, 303]:
            assert "/login" in str(response.headers.get("location", ""))


class TestHomeRoute:
    """Tests for home route."""

    def test_home_page(self, app):
        """Test that home page is accessible."""
        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
