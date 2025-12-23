"""Tests for middleware components."""

from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.testclient import TestClient
from starlette.responses import Response

from gradioapp.api.middleware.auth import AuthMiddleware
from gradioapp.api.middleware.logging import LoggingMiddleware
from gradioapp.api.middleware.session import SessionMiddleware
from gradioapp.domain.auth import create_access_token
from gradioapp.domain.session.backends.memory import InMemorySessionStore
from gradioapp.domain.session.store import initialize_session_store


@pytest.fixture
def app():
    """Create a test FastAPI app."""
    test_app = FastAPI()
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
def test_token():
    """Create a valid test token."""
    return create_access_token(
        {"sub": "test_user", "session_id": "test_session"},
        expires_delta=timedelta(minutes=30),
    )


class TestAuthMiddleware:
    """Tests for AuthMiddleware."""

    def test_auth_middleware_allowed_path(self, app):
        """Test that allowed paths bypass authentication."""
        @app.get("/login")
        async def login():
            return {"message": "ok"}

        app.add_middleware(AuthMiddleware)
        client = TestClient(app)

        response = client.get("/login")

        assert response.status_code == 200
        assert response.json() == {"message": "ok"}

    def test_auth_middleware_missing_token(self, app):
        """Test that missing token returns unauthorized response."""
        @app.get("/protected")
        async def protected():
            return {"message": "ok"}

        app.add_middleware(AuthMiddleware)
        client = TestClient(app)

        response = client.get("/protected")

        assert response.status_code in [302, 401]  # Redirect or JSON error

    def test_auth_middleware_valid_token(self, app, test_token):
        """Test that valid token allows request to proceed."""
        from fastapi import Request

        @app.get("/protected")
        async def protected(request: Request):
            return {
                "message": "ok",
                "user_id": getattr(request.state, "user_id", None),
                "session_id": getattr(request.state, "session_id", None),
            }

        app.add_middleware(AuthMiddleware)
        client = TestClient(app)

        response = client.get("/protected", cookies={"access_token": test_token})

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test_user"
        assert data["session_id"] == "test_session"

    def test_auth_middleware_invalid_token(self, app):
        """Test that invalid token returns unauthorized response."""
        @app.get("/protected")
        async def protected():
            return {"message": "ok"}

        app.add_middleware(AuthMiddleware)
        client = TestClient(app)

        response = client.get("/protected", cookies={"access_token": "invalid_token"})

        assert response.status_code in [302, 401]  # Redirect or JSON error


class TestSessionMiddleware:
    """Tests for SessionMiddleware."""

    def test_session_middleware_allowed_path(self, app):
        """Test that allowed paths bypass session validation."""
        @app.get("/login")
        async def login():
            return {"message": "ok"}

        app.add_middleware(SessionMiddleware)
        client = TestClient(app)

        response = client.get("/login")

        assert response.status_code == 200
        assert response.json() == {"message": "ok"}

    def test_session_middleware_missing_session_id(self, app, session_store):
        """Test that missing session ID returns unauthorized response."""
        @app.get("/protected")
        async def protected():
            return {"message": "ok"}

        # Add AuthMiddleware first to set session_id in request.state
        from gradioapp.api.middleware.auth import AuthMiddleware
        from gradioapp.domain.auth import create_access_token

        token = create_access_token(
            {"sub": "test_user", "session_id": "test_session"},
            expires_delta=timedelta(minutes=30),
        )

        app.add_middleware(SessionMiddleware)
        app.add_middleware(AuthMiddleware)
        client = TestClient(app)

        # Request without token - AuthMiddleware won't set session_id
        response = client.get("/protected")

        assert response.status_code in [302, 401]  # Redirect or JSON error

    def test_session_middleware_valid_session(self, app, session_store):
        """Test that valid session allows request to proceed."""
        from gradioapp.api.middleware.auth import AuthMiddleware
        from gradioapp.domain.auth import create_access_token

        # Create a session
        session_id = "test_session"
        session_store.create_session(
            session_id=session_id, username="test_user", data={}
        )

        token = create_access_token(
            {"sub": "test_user", "session_id": session_id},
            expires_delta=timedelta(minutes=30),
        )

        @app.get("/protected")
        async def protected():
            return {"message": "ok"}

        app.add_middleware(SessionMiddleware)
        app.add_middleware(AuthMiddleware)
        client = TestClient(app)

        response = client.get("/protected", cookies={"access_token": token})

        assert response.status_code == 200
        assert response.json() == {"message": "ok"}

    def test_session_middleware_expired_session(self, app, session_store):
        """Test that expired session returns unauthorized response."""
        from gradioapp.api.middleware.auth import AuthMiddleware
        from gradioapp.domain.auth import create_access_token

        # Create token with non-existent session
        token = create_access_token(
            {"sub": "test_user", "session_id": "nonexistent_session"},
            expires_delta=timedelta(minutes=30),
        )

        @app.get("/protected")
        async def protected():
            return {"message": "ok"}

        app.add_middleware(SessionMiddleware)
        app.add_middleware(AuthMiddleware)
        client = TestClient(app)

        response = client.get("/protected", cookies={"access_token": token})

        assert response.status_code in [302, 401]  # Redirect or JSON error


class TestLoggingMiddleware:
    """Tests for LoggingMiddleware."""

    def test_logging_middleware_success(self, app):
        """Test that logging middleware logs successful requests."""
        @app.get("/test")
        async def test():
            return {"message": "ok"}

        app.add_middleware(LoggingMiddleware)
        client = TestClient(app)

        with patch("gradioapp.api.middleware.logging.logger") as mock_logger:
            response = client.get("/test")

            assert response.status_code == 200
            assert response.json() == {"message": "ok"}
            mock_logger.debug.assert_called()

    def test_logging_middleware_exception(self, app):
        """Test that logging middleware logs exceptions."""
        @app.get("/test")
        async def test():
            raise ValueError("Test error")

        app.add_middleware(LoggingMiddleware)
        client = TestClient(app)

        with patch("gradioapp.api.middleware.logging.logger") as mock_logger:
            with pytest.raises(ValueError):
                client.get("/test")

            mock_logger.exception.assert_called_once()

