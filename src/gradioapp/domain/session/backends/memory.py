from datetime import datetime
import threading
import time
from typing import Optional

from loguru import logger

from ..types import SessionData


class InMemorySessionStore:
    """
    InMemorySessionStore provides an in-memory session management system with automatic expiration and cleanup.

    Attributes:
        _store (dict): Internal dictionary to store session data.
        _lock (threading.RLock): Reentrant lock for thread-safe access to the session store.
        _ttl (int): Time-to-live for each session in seconds.
        _cleanup_interval (int): Interval in seconds for running the cleanup thread.
        _stop_cleanup_thread (threading.Event): Event to signal the cleanup thread to stop.
        _cleanup_thread (threading.Thread): Background thread for cleaning up expired sessions.

    Methods:
        __init__(ttl: int = 60 * 30, cleanup_interval: int = 60) -> None:
            Initializes the session store with a default TTL and cleanup interval, and starts the cleanup thread.

        create_session(session_id: str, username: str, data: dict) -> dict[str, Any]:
            Creates a new session with the given session_id, username, and data. Returns the created session dictionary.

        get_session(session_id: str) -> Optional[dict]:
            Retrieves a session by its session_id. If the session is expired or does not exist, returns None.
            Resets the TTL on successful retrieval.

        delete_session(session_id: str) -> None:
            Deletes a session by its session_id.

        dump_session(session_id: str) -> str:
            Returns a string representation of a session for debugging purposes.

        dump_store() -> str:
            Returns a string representation of all sessions in the store for debugging purposes.

        _format_session(session_id: str, session: dict) -> str:
            Formats a session dictionary into a human-readable string.

        _cleanup_expired_sessions() -> None:
            Background method that periodically removes expired sessions from the store.

        stop_cleanup_thread() -> None:
            Stops the background cleanup thread gracefully.
    """

    def __init__(self, ttl: int = 60 * 30, cleanup_interval: int = 60) -> None:
        """
        Initializes the in-memory session store.

        Args:
            ttl (int, optional): Time-to-live for each session in seconds.
                Defaults to 1800 (30 minutes).
            cleanup_interval (int, optional): Interval in seconds at which expired
                sessions are cleaned up. Defaults to 60 seconds.

        Starts a background thread to periodically remove expired sessions.
        """
        self._store = {}
        self._lock = threading.RLock()
        self._ttl = ttl  # Default TTL for sessions in seconds
        self._cleanup_interval = cleanup_interval
        self._stop_cleanup_thread = threading.Event()
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_expired_sessions, daemon=True
        )
        self._cleanup_thread.start()

    def create_session(self, session_id: str, username: str, data: dict) -> SessionData:
        """
        Creates a new session with the given session ID, username, and associated data.

        Args:
            session_id (str): The unique identifier for the session.
            username (str): The username associated with the session.
            data (dict): Additional data to store in the session.

        Returns:
            dict[str, Any]: The session data stored, including username, data, and expiration timestamp.
        """
        expire_at = time.time() + self._ttl
        session_data: SessionData = {
            "username": username,
            "data": data,
            "expire_at": expire_at,
        }
        with self._lock:
            self._store[session_id] = session_data
        logger.debug(self._format_session(session_id, session_data))
        return session_data

    def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Retrieve a session by its session ID.

        Args:
            session_id (str): The unique identifier for the session.

        Returns:
            Optional[dict]: The session data as a dictionary if the session exists and has not expired;
                            otherwise, returns None.

        Side Effects:
            - If the session has expired, it is removed from the store.
            - If the session is valid, its expiration time (TTL) is reset.
        """
        current_time = time.time()
        with self._lock:
            session = self._store.get(session_id)
            if not session:
                return None
            if session["expire_at"] < current_time:
                self._store.pop(session_id, None)
                return None
            # Reset TTL
            session["expire_at"] = current_time + self._ttl
            # Copy session data before releasing lock
            session_data = session.copy()
        logger.debug(self._format_session(session_id, session_data))
        return session_data

    def delete_session(self, session_id: str) -> None:
        """
        Delete a session from the in-memory store.

        Args:
            session_id (str): The unique identifier of the session to be deleted.

        Returns:
            None
        """
        with self._lock:
            self._store.pop(session_id, None)
        logger.debug(f"Session deleted: {session_id}")

    def dump_session(self, session_id: str) -> str:
        """
        Serialize and return the session data for the given session ID.

        Args:
            session_id (str): The unique identifier of the session to be dumped.

        Returns:
            str: The formatted session data as a string. Returns an empty string if the session does not exist.
        """
        with self._lock:
            session = self._store.get(session_id)
            if not session:
                return ""
            # Copy session data before releasing lock
            session_data = session.copy()
        s = self._format_session(session_id, session_data)
        logger.debug(s)
        return s

    def dump_store(self) -> str:
        """
        Returns a string representation of the current session store.

        Iterates through all sessions in the internal store, formats each session using
        the `_format_session` method, and joins them into a single string. The resulting
        string is logged at the debug level and also returned.

        Returns:
            str: A formatted string listing all sessions in the store.
        """
        with self._lock:
            # Copy all sessions data before releasing lock
            sessions_data = {
                session_id: session.copy()
                for session_id, session in self._store.items()
            }
        sessions = [
            self._format_session(session_id, session)
            for session_id, session in sessions_data.items()
        ]
        s = "Session store:\n" + "\n".join(sessions)
        logger.debug(s)
        return s

    def _format_session(self, session_id: str, session: SessionData) -> str:
        """
        Formats the session information into a human-readable string.

        Args:
            session_id (str): The unique identifier for the session.
            session (dict): A dictionary containing session details. Expected keys are:
                - "username" (str): The username associated with the session.
                - "expire_at" (float): The expiration timestamp of the session.
                - "data" (Any): Additional session data.

        Returns:
            str: A formatted string containing the session ID, username, expiration time (ISO format), and session data.
        """
        expire_at_iso = datetime.fromtimestamp(session["expire_at"]).isoformat()
        return (
            f"Session ID: {session_id}, Username: {session['username']}, "
            f"Expire At: {expire_at_iso}, Data: {session['data']}"
        )

    def _cleanup_expired_sessions(self) -> None:
        """
        Continuously removes expired sessions from the in-memory session store.

        This method runs in a loop, checking for sessions whose expiration time has passed,
        removing them from the store, and logging their removal. The loop sleeps for a
        configured interval between cleanup cycles and stops when the cleanup thread is signaled.

        Returns:
            None
        """
        while not self._stop_cleanup_thread.is_set():
            current_time = time.time()
            with self._lock:
                expired_sessions = [
                    session_id
                    for session_id, session in self._store.items()
                    if session["expire_at"] < current_time
                ]
                for session_id in expired_sessions:
                    self._store.pop(session_id, None)
            # Log outside the lock
            for session_id in expired_sessions:
                logger.debug(f"Expired session removed: {session_id}")
            time.sleep(self._cleanup_interval)

    def stop_cleanup_thread(self) -> None:
        """
        Stops the background cleanup thread by signaling it to terminate and waiting for it to finish.

        This method sets an internal event to notify the cleanup thread to stop, and then joins the
        thread to ensure it has completed execution before proceeding.
        """
        self._stop_cleanup_thread.set()
        self._cleanup_thread.join()
