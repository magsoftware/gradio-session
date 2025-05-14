import time

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
        except Exception:
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
            f"[{method}] {path} | status={response.status_code} | user_id={user_id} session_id={session_id} | {duration:.2f} ms"
        )

        return response
