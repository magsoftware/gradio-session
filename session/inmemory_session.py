from datetime import datetime
import time
from typing import Optional

from loguru import logger


class InMemorySessionStore:
    def __init__(self) -> None:
        self._store = {}

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
