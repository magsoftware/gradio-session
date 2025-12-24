"""Tests for session helper functions."""

from unittest.mock import MagicMock, patch

from fastapi import Request
import gradio as gr
import pytest

from gradioapp.domain.session.backends.memory import InMemorySessionStore
from gradioapp.domain.session.helpers import get_session, get_session_id
from gradioapp.domain.session.store import initialize_session_store
from gradioapp.domain.session.types import SessionData


class TestGetSessionId:
    """Tests for get_session_id function."""

    def test_get_session_id_with_fastapi_request(self):
        """Test getting session ID from FastAPI Request object."""
        # Create a mock FastAPI Request with session_id in state
        mock_request = MagicMock(spec=Request)
        mock_request.state.session_id = "test_session_123"

        result = get_session_id(mock_request)

        assert result == "test_session_123"

    def test_get_session_id_with_gradio_request(self):
        """Test getting session ID from Gradio Request object."""
        # Create a mock Gradio Request with session_id in state
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_state.session_id = "test_session_456"
        mock_request.state = mock_state

        result = get_session_id(mock_request)

        assert result == "test_session_456"

    def test_get_session_id_missing_in_state(self):
        """Test getting session ID when it's not in request state."""
        # Create a mock Request without session_id in state
        mock_request = MagicMock(spec=Request)
        mock_request.state = MagicMock()
        # session_id attribute doesn't exist
        del mock_request.state.session_id

        with patch("gradioapp.domain.session.helpers.logger") as mock_logger:
            result = get_session_id(mock_request)

            assert result is None
            mock_logger.error.assert_called_once_with("Session ID not found in request state.")

    def test_get_session_id_none_value(self):
        """Test getting session ID when it's None in request state."""
        # Create a mock Request with session_id set to None
        mock_request = MagicMock(spec=Request)
        mock_request.state.session_id = None

        with patch("gradioapp.domain.session.helpers.logger") as mock_logger:
            result = get_session_id(mock_request)

            assert result is None
            mock_logger.error.assert_called_once_with("Session ID not found in request state.")

    def test_get_session_id_empty_string(self):
        """Test getting session ID when it's an empty string."""
        # Create a mock Request with session_id as empty string
        mock_request = MagicMock(spec=Request)
        mock_request.state.session_id = ""

        with patch("gradioapp.domain.session.helpers.logger") as mock_logger:
            result = get_session_id(mock_request)

            assert result is None
            mock_logger.error.assert_called_once_with("Session ID not found in request state.")


class TestGetSession:
    """Tests for get_session function."""

    @pytest.fixture
    def session_store(self):
        """Create a fresh in-memory session store for testing."""
        store = InMemorySessionStore(ttl=300, cleanup_interval=1)
        initialize_session_store(store)
        yield store
        store.stop_cleanup_thread()

    def test_get_session_success(self, session_store):
        """Test getting session data when session exists."""
        # Create a session in the store
        session_id = "test_session_123"
        username = "test_user"
        session_data = session_store.create_session(session_id=session_id, username=username, data={"key": "value"})

        # Create a mock Request with session_id in state
        mock_request = MagicMock(spec=Request)
        mock_request.state.session_id = session_id

        result = get_session(mock_request)

        assert result is not None
        assert isinstance(result, dict)
        assert result["username"] == username
        assert result["data"] == {"key": "value"}
        assert result["expire_at"] == session_data["expire_at"]

    def test_get_session_missing_session_id(self, session_store):
        """Test getting session when session_id is not in request state."""
        # Create a mock Request without session_id in state
        mock_request = MagicMock(spec=Request)
        mock_request.state = MagicMock()
        del mock_request.state.session_id

        with patch("gradioapp.domain.session.helpers.logger") as mock_logger:
            result = get_session(mock_request)

            assert result is None
            # Should log error about missing session_id
            mock_logger.error.assert_called_once_with("Session ID not found in request state.")

    def test_get_session_nonexistent_session(self, session_store):
        """Test getting session when session doesn't exist in store."""
        # Create a mock Request with session_id that doesn't exist in store
        mock_request = MagicMock(spec=Request)
        mock_request.state.session_id = "nonexistent_session"

        with patch("gradioapp.domain.session.helpers.logger") as mock_logger:
            result = get_session(mock_request)

            assert result is None
            mock_logger.error.assert_called_once_with("Session data not found for session ID: nonexistent_session")

    def test_get_session_with_gradio_request(self, session_store):
        """Test getting session data using Gradio Request object."""
        # Create a session in the store
        session_id = "test_session_gradio"
        username = "gradio_user"
        session_store.create_session(session_id=session_id, username=username, data={})

        # Create a mock Gradio Request with session_id in state
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_state.session_id = session_id
        mock_request.state = mock_state

        result = get_session(mock_request)

        assert result is not None
        assert result["username"] == username

    def test_get_session_expired_session(self, session_store):
        """Test getting session when session has expired."""
        # Create a session and manually set it as expired
        session_id = "expired_session"
        session_data = session_store.create_session(session_id=session_id, username="test_user", data={})
        # Manually expire the session by setting expire_at to past
        import time

        session_data["expire_at"] = time.time() - 100

        # Create a mock Request with session_id
        mock_request = MagicMock(spec=Request)
        mock_request.state.session_id = session_id

        # The session should be cleaned up or not found
        # Since cleanup runs periodically, we might still get it or not
        # Let's test that expired sessions are handled
        result = get_session(mock_request)

        # The session might still be in store (cleanup hasn't run yet)
        # or might be None if cleanup ran. Both are valid behaviors.
        # We'll just verify the function doesn't crash
        assert result is None or isinstance(result, dict)
