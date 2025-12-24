"""Tests for session store management."""

import pytest

from gradioapp.domain.session.backends.memory import InMemorySessionStore
from gradioapp.domain.session.store import get_session_store, initialize_session_store


class TestSessionStore:
    """Tests for session store initialization and access."""

    def test_get_session_store_not_initialized(self):
        """Test that get_session_store raises RuntimeError when not initialized."""
        # Clear any existing initialization
        initialize_session_store(None)

        with pytest.raises(RuntimeError, match="Session store has not been initialized"):
            get_session_store()

    def test_get_session_store_initialized(self):
        """Test that get_session_store returns store when initialized."""
        store = InMemorySessionStore(ttl=300, cleanup_interval=1)
        initialize_session_store(store)

        try:
            retrieved_store = get_session_store()
            assert retrieved_store is store
        finally:
            store.stop_cleanup_thread()
            initialize_session_store(None)

    def test_initialize_session_store(self):
        """Test that initialize_session_store sets the global store."""
        store = InMemorySessionStore(ttl=300, cleanup_interval=1)
        initialize_session_store(store)

        try:
            retrieved_store = get_session_store()
            assert retrieved_store is store
        finally:
            store.stop_cleanup_thread()
            initialize_session_store(None)
