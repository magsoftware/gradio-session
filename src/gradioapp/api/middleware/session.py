from fastapi import Request, Response
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from ...domain.session.store import get_session_store
from .utils import is_path_allowed


class SessionMiddleware(BaseHTTPMiddleware):
    """
    SessionMiddleware is a custom FastAPI middleware for managing user sessions.

    This middleware performs the following tasks:
    - Logs incoming requests and their paths.
    - Skips session validation for allowed paths as determined by `is_path_allowed`.
    - Checks for the presence of a session ID in the request state.
    - Retrieves session data from the session store using the session ID.
    - If a valid session is found, allows the request to proceed to the next handler.

    Args:
        request (Request): The incoming HTTP request.
        call_next (Callable): The next middleware or route handler in the chain.

    Returns:
        Response: The HTTP response, either from the next handler or an error response
            if session validation fails.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        logger.debug(f"Processing request: {request.method} {request.url.path}")

        if is_path_allowed(request.url.path):
            logger.debug(
                f"Path {request.url.path} matches allowed patterns. Skipping session middleware."
            )
            return await call_next(request)

        session_id = getattr(request.state, "session_id", None)
        if not session_id:
            logger.warning("Session ID not found in request state.")
            return JSONResponse(
                status_code=401,
                content={"error": "Missing session ID", "redirect_to": "/login"},
            )

        session = get_session_store().get_session(session_id)
        if not session:
            logger.warning(f"Session data not found for session ID: {session_id}")
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Session expired or not found",
                    "redirect_to": "/login",
                },
            )

        logger.debug(f"Session found retrieved for session {session_id}: {session}")

        return await call_next(request)
