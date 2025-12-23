from typing import Any, Optional, Protocol, TypedDict


class SessionData(TypedDict):
    """
    Type definition for session data stored in the session store.

    Attributes:
        username (str): The username associated with the session.
        data (dict[str, Any]): Additional data stored in the session.
        expire_at (float): Expiration timestamp as Unix time.
    """

    username: str
    data: dict[str, Any]
    expire_at: float


class SessionStore(Protocol):
    """
    Protocol for a session store, defining the required methods for managing user sessions.

    Methods:
        create_session(session_id: str, username: str, data: dict) -> SessionData:
            Create a new session with the given session ID, username, and associated data.
            Returns the created session as a SessionData dictionary.

        get_session(session_id: str) -> Optional[SessionData]:
            Retrieve the session data for the given session ID.
            Returns the session as a SessionData dictionary if found, otherwise None.

        delete_session(session_id: str) -> None:
            Delete the session associated with the given session ID.

        dump_session(session_id: str) -> str:
            Serialize and return the session data for the given session ID as a string.

        dump_store() -> str:
            Serialize and return the entire session store as a string.
    """

    def create_session(
        self, session_id: str, username: str, data: dict
    ) -> SessionData: ...
    def get_session(self, session_id: str) -> Optional[SessionData]: ...
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
