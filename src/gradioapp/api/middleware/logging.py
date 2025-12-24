import time
from typing import Awaitable, Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses in a FastAPI application.

    Logs the HTTP method, request path, user ID, session ID, response status code,
    and request duration in milliseconds.

    If an exception occurs during request processing, logs the exception details
    along with the same contextual information.

    Attributes:
        None

    Methods:
        dispatch(request: Request, call_next) -> Response
            Handles the incoming request, logs relevant information before and
            after processing, and ensures exceptions are logged with context.
    """

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start_time = time.perf_counter()
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
        except Exception:
            # Catching generic Exception is intentional here for logging middleware:
            # - Must catch ALL exceptions to log them with context before re-raising
            # - Cannot use specific exceptions as we don't know what exceptions handlers may raise
            # - Re-raises the exception after logging to maintain normal error propagation
            duration = (time.perf_counter() - start_time) * 1000
            user_id = getattr(request.state, "user_id", "anonymous")
            session_id = getattr(request.state, "session_id", "n/a")

            logger.exception(
                f"[{method}] {path} | user_id={user_id} session_id={session_id} | Exception after {duration:.2f} ms"
            )
            raise

        duration = (time.perf_counter() - start_time) * 1000
        user_id = getattr(request.state, "user_id", "anonymous")
        session_id = getattr(request.state, "session_id", "n/a")

        logger.debug(
            f"[{method}] {path} | status={response.status_code} | "
            f"user_id={user_id} session_id={session_id} | {duration:.2f} ms"
        )

        return response
