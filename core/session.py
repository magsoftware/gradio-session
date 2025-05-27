import gradio as gr
from loguru import logger


def get_session_id(request: gr.Request) -> str | None:
    session_id = getattr(request.state, "session_id", None)
    if not session_id:
        logger.error("Session ID not found in request state.")
        return None
    return session_id
