from datetime import datetime
import threading
import time
from typing import Optional

from loguru import logger


class InMemorySessionStore:
    def __init__(
        self, cleanup_interval: int = 60
    ) -> None:  # Cleanup interval in seconds (default: 10 minutes)
        self._store = {}
        self._cleanup_interval = cleanup_interval
        self._stop_cleanup_thread = threading.Event()
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_expired_sessions, daemon=True
        )
        self._cleanup_thread.start()

    def create_session(
        self, session_id: str, data: dict, ttl: int = 60
    ) -> None:  # TODO: set a proper TTL
        expire_at = time.time() + ttl
        self._store[session_id] = {"data": data, "expire_at": expire_at}
        logger.debug(self._format_session(session_id, self._store[session_id]))

    def get_session(self, session_id: str, ttl: int = 60) -> Optional[dict]:
        session = self._store.get(session_id)
        if not session:
            return None
        if session["expire_at"] < time.time():
            self._store.pop(session_id, None)
            return None
        # Reset TTL
        session["expire_at"] = time.time() + ttl
        logger.debug(self._format_session(session_id, session))
        return session["data"]

    def delete_session(self, session_id: str) -> None:
        self._store.pop(session_id, None)
        logger.debug(f"Session deleted: {session_id}")

    def dump_session(self, session_id: str) -> str:
        session = self._store.get(session_id)
        if not session:
            return ""
        s = self._format_session(session_id, session)
        logger.debug(s)
        return s

    def dump_store(self) -> str:
        sessions = [
            self._format_session(session_id, session)
            for session_id, session in self._store.items()
        ]
        s = "Session store:\n" + "\n".join(sessions)
        logger.debug(s)
        return s

    def _format_session(self, session_id: str, session: dict) -> str:
        expire_at_iso = datetime.fromtimestamp(session["expire_at"]).isoformat()
        return f"Session ID: {session_id}, Expire At: {expire_at_iso}, Data: {session['data']}"

    def _cleanup_expired_sessions(self) -> None:
        while not self._stop_cleanup_thread.is_set():
            current_time = time.time()
            expired_sessions = [
                session_id
                for session_id, session in self._store.items()
                if session["expire_at"] < current_time
            ]
            for session_id in expired_sessions:
                self._store.pop(session_id, None)
                logger.debug(f"Expired session removed: {session_id}")
            time.sleep(self._cleanup_interval)

    def stop_cleanup_thread(self) -> None:
        self._stop_cleanup_thread.set()
        self._cleanup_thread.join()
