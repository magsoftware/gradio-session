from fastapi import Request
import gradio as gr
from loguru import logger

from session import SessionData, get_session_store


def get_session_id(request: gr.Request | Request) -> str | None:
    """
    Retrieve the session ID from the request state.

    Args:
        request (gr.Request | Request): The incoming request object, which should have a 'state' attribute.

    Returns:
        str | None: The session ID if present in the request state; otherwise, None.
    """
    session_id = getattr(request.state, "session_id", None)
    if not session_id:
        logger.error("Session ID not found in request state.")
        return None
    return session_id


def get_session(request: gr.Request | Request) -> SessionData | None:
    """
    Retrieve the session data associated with the given request.

    Args:
        request (gr.Request | Request): The incoming request object from which to extract the session ID.

    Returns:
        SessionData | None: The session data as a SessionData dictionary if found, otherwise None.
    """
    session_id = get_session_id(request)
    if not session_id:
        return None
    session = get_session_store().get_session(session_id)
    if not session:
        logger.error(f"Session data not found for session ID: {session_id}")
        return None
    return session
