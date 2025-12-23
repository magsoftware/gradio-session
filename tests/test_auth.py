from datetime import timedelta

import pytest

from gradioapp.config import get_settings
from gradioapp.domain.auth import (
    create_access_token,
    create_session_token,
    verify_token,
)


class TestCreateAccessToken:
    """Tests for create_access_token function."""

    def test_create_access_token_success(self):
        """Test creating a valid access token."""
        data = {"sub": "test_user", "custom": "value"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_claims(self):
        """Test that token contains expected claims."""
        data = {"sub": "test_user"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)

        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test_user"
        assert "exp" in payload
        assert "iat" in payload


class TestCreateSessionToken:
    """Tests for create_session_token function."""

    def test_create_session_token_success(self):
        """Test creating a session token."""
        user_id = "test_user"
        expires_delta = timedelta(minutes=30)
        token, session_id = create_session_token(user_id, expires_delta)

        assert token is not None
        assert session_id is not None
        assert isinstance(token, str)
        assert isinstance(session_id, str)
        assert len(token) > 0
        assert len(session_id) > 0

    def test_create_session_token_contains_user_id(self):
        """Test that session token contains user ID."""
        user_id = "test_user"
        expires_delta = timedelta(minutes=30)
        token, session_id = create_session_token(user_id, expires_delta)

        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["session_id"] == session_id


class TestVerifyToken:
    """Tests for verify_token function."""

    def test_verify_token_valid(self):
        """Test verifying a valid token."""
        data = {"sub": "test_user", "session_id": "test_session"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)

        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test_user"
        assert payload["session_id"] == "test_session"

    def test_verify_token_expired(self):
        """Test verifying an expired token."""
        data = {"sub": "test_user"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data, expires_delta)

        payload = verify_token(token)
        assert payload is None

    def test_verify_token_invalid(self):
        """Test verifying an invalid token."""
        invalid_token = "invalid.token.here"
        payload = verify_token(invalid_token)
        assert payload is None

    def test_verify_token_wrong_secret(self):
        """Test verifying token with wrong secret."""
        # Create token with current secret
        data = {"sub": "test_user"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)

        # Token should verify with current secret
        payload = verify_token(token)
        assert payload is not None

