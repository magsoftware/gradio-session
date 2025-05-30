import gradio as gr
from loguru import logger

from session import get_session_store


def get_session_id(request: gr.Request) -> str | None:
    session_id = getattr(request.state, "session_id", None)
    if not session_id:
        logger.error("Session ID not found in request state.")
        return None
    return session_id


def get_session(request: gr.Request) -> dict | None:
    session_id = get_session_id(request)
    if not session_id:
        return None
    session = get_session_store().get_session(session_id)
    if not session:
        logger.error(f"Session data not found for session ID: {session_id}")
        return None
    return session
