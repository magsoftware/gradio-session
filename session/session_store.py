from typing import Any, Optional, Protocol


class SessionStore(Protocol):
    """
    Protocol for a session store, defining the required methods for managing user sessions.

    Methods:
        create_session(session_id: str, username: str, data: dict) -> dict[str, Any]:
            Create a new session with the given session ID, username, and associated data.
            Returns the created session as a dictionary.

        get_session(session_id: str) -> Optional[dict[str, Any]]:
            Retrieve the session data for the given session ID.
            Returns the session as a dictionary if found, otherwise None.

        delete_session(session_id: str) -> None:
            Delete the session associated with the given session ID.

        dump_session(session_id: str) -> str:
            Serialize and return the session data for the given session ID as a string.

        dump_store() -> str:
            Serialize and return the entire session store as a string.
    """

    def create_session(
        self, session_id: str, username: str, data: dict
    ) -> dict[str, Any]: ...
    def get_session(self, session_id: str) -> Optional[dict[str, Any]]: ...
    def delete_session(self, session_id: str) -> None: ...
    def dump_session(self, session_id: str) -> str: ...
    def dump_store(self) -> str: ...


# Singleton
_session_store = None


def initialize_session_store(store: SessionStore) -> None:
    """
    Initializes the global session store with the provided SessionStore instance.

    Args:
        store (SessionStore): The session store instance to be used globally.

    Returns:
        None
    """
    global _session_store
    _session_store = store


def get_session_store() -> Optional[SessionStore]:
    """
    Retrieve the current session store instance.

    Returns:
        Optional[SessionStore]: The current session store instance if set, otherwise None.
    """
    return _session_store
