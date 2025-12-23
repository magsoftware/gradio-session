from datetime import timedelta
import os

import pytest

# Set environment variables before importing modules that use settings
os.environ.setdefault("JWT_SECRET", "a" * 32)  # Minimum 32 characters
os.environ.setdefault("VERSION", "test")
os.environ.setdefault("PROJECTNAME", "test")

from gradioapp.config import load_settings
from gradioapp.domain.auth import create_access_token, verify_token
from gradioapp.domain.session.backends.memory import InMemorySessionStore
from gradioapp.domain.session.store import initialize_session_store


@pytest.fixture
def test_jwt_secret():
    """Provide a test JWT secret for testing."""
    return "a" * 32  # Minimum 32 characters


@pytest.fixture
def test_settings():
    """Create test settings with test JWT secret."""
    return load_settings()


@pytest.fixture
def session_store():
    """Create a fresh in-memory session store for testing."""
    store = InMemorySessionStore(ttl=300, cleanup_interval=60)
    yield store
    store.stop_cleanup_thread()


@pytest.fixture
def test_token(test_settings):
    """Create a valid test token."""
    return create_access_token(
        {"sub": "test_user", "session_id": "test_session"},
        expires_delta=timedelta(minutes=30),
    )

