from typing import Optional, Protocol


class SessionStore(Protocol):
    def create_session(self, session_id: str, data: dict, ttl: int): ...
    def get_session(self, session_id: str) -> Optional[dict]: ...
    def delete_session(self, session_id: str): ...
    def dump_session(self, session_id: str) -> str: ...
    def dump_store(self) -> str: ...


# Singleton
_session_store = None


def initialize_session_store(store: SessionStore) -> None:
    """
    Initialize the global session store.

    This function sets the global `_session_store` variable to the provided store.
    """
    global _session_store
    _session_store = store


def get_session_store() -> Optional[SessionStore]:
    """
    Retrieve the global session store.

    Returns the global `_session_store` variable.
    """
    return _session_store
