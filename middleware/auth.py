from typing import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from middleware.utils import is_path_allowed
from services import verify_token


class AuthMiddleware(BaseHTTPMiddleware):
    """
    AuthMiddleware is a FastAPI middleware for handling authentication via access tokens.

    This middleware intercepts incoming HTTP requests and performs the following actions:
    - Logs the incoming request method and path.
    - Checks if the request path is allowed to bypass authentication using `is_path_allowed`.
    - Attempts to retrieve the "access_token" from the request cookies.
    - Verifies the access token using `verify_token`.
    - On successful verification, attaches the user ID and session ID from the token payload
      to `request.state`.
    - Logs the successful authentication and forwards the request to the next handler.

    Attributes:
        None

    Methods:
        dispatch(request, call_next)
            Handles the authentication logic for each incoming request.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        logger.info(f"Processing request: {request.method} {request.url.path}")

        if is_path_allowed(request.url.path):
            logger.info(
                f"Path {request.url.path} matches allowed patterns. Skipping auth."
            )
            return await call_next(request)

        token = request.cookies.get("access_token")
        if not token:
            logger.warning("No access token found. Redirecting to /login.")
            return JSONResponse(
                status_code=401,
                content={"error": "Missing access token", "redirect_to": "/login"},
            )

        payload = verify_token(token)
        if not payload:
            logger.warning("Invalid access token. Redirecting to /login.")
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid or expired token", "redirect_to": "/login"},
            )

        request.state.user_id = payload.get("sub")
        request.state.session_id = payload.get("session_id")

        logger.info(
            f"Access token verified for user {request.state.user_id}, session_id {request.state.session_id}, proceeding with the request."
        )

        return await call_next(request)
