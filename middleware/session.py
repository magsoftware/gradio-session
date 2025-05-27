from fastapi import Request, Response
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from middleware.utils import is_path_allowed
from session import get_session_store


class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        logger.info(f"Processing request: {request.method} {request.url.path}")

        if is_path_allowed(request.url.path):
            logger.info(
                f"Path {request.url.path} matches allowed patterns. Skipping session middleware."
            )
            return await call_next(request)

        session_id = getattr(request.state, "session_id", None)
        if not session_id:
            logger.info("Session ID not found in request state.")
            return JSONResponse(
                status_code=401,
                content={"error": "Missing session ID", "redirect_to": "/login"},
            )

        session_store = get_session_store()
        session_data = session_store.get_session(session_id)
        if not session_data:
            logger.info(f"Session data not found for session ID: {session_id}")
            return JSONResponse(
                status_code=401,
                content={
                    "error": "Session expired or not found",
                    "redirect_to": "/login",
                },
            )

        logger.debug(f"Session data retrieved for session {session_id}: {session_data}")

        return await call_next(request)
