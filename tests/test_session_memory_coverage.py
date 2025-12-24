"""Additional tests for InMemorySessionStore to improve coverage."""

import time

import pytest

from gradioapp.domain.session.backends.memory import InMemorySessionStore


class TestInMemorySessionStoreCoverage:
    """Tests for InMemorySessionStore to cover missing lines."""

    @pytest.fixture
    def session_store(self):
        """Create a fresh in-memory session store for testing."""
        store = InMemorySessionStore(ttl=300, cleanup_interval=1)
        yield store
        store.stop_cleanup_thread()

    def test_dump_session_nonexistent(self, session_store):
        """Test dumping a nonexistent session returns empty string."""
        dumped = session_store.dump_session("nonexistent_session")
        assert dumped == ""

    def test_dump_session_existing(self, session_store):
        """Test dumping an existing session."""
        session_id = "test_session_dump"
        username = "test_user"
        data = {"key": "value"}

        session_store.create_session(session_id=session_id, username=username, data=data)
        dumped = session_store.dump_session(session_id)

        assert dumped is not None
        assert isinstance(dumped, str)
        assert len(dumped) > 0
        assert session_id in dumped
        assert username in dumped

    def test_dump_store_empty(self, session_store):
        """Test dumping an empty store."""
        dumped = session_store.dump_store()

        assert dumped is not None
        assert isinstance(dumped, str)
        assert "Session store:" in dumped

    def test_dump_store_with_sessions(self, session_store):
        """Test dumping store with multiple sessions."""
        session_store.create_session("session_1", "user1", {"data": "value1"})
        session_store.create_session("session_2", "user2", {"data": "value2"})

        dumped = session_store.dump_store()

        assert dumped is not None
        assert isinstance(dumped, str)
        assert "Session store:" in dumped
        assert "session_1" in dumped
        assert "session_2" in dumped
        assert "user1" in dumped
        assert "user2" in dumped

    def test_cleanup_expired_sessions(self, session_store):
        """Test that expired sessions are cleaned up."""
        # Create sessions
        session_id1 = "expired_session_1"
        session_id2 = "valid_session_1"
        session_store.create_session(session_id1, "user1", {})
        session_store.create_session(session_id2, "user2", {})

        # Manually expire one session
        with session_store._lock:
            if session_id1 in session_store._store:
                session_store._store[session_id1]["expire_at"] = time.time() - 100

        # Wait a bit for cleanup to run (cleanup_interval is 1 second)
        time.sleep(1.5)

        # Expired session should be removed
        assert session_store.get_session(session_id1) is None
        # Valid session should still exist
        assert session_store.get_session(session_id2) is not None
