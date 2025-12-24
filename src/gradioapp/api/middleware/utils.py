from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from loguru import logger
import pathspec

ALLOWED_PATHS = [
    "/login",
    "/logout",
    "/healthz",
    "/favicon.ico",
    "/static/*",
    "/manifest.json",
]

# Cache for PathSpec instance
_pathspec_cache: pathspec.PathSpec | None = None


def is_path_allowed(path: str) -> bool:
    """
    Checks if the given path matches any of the allowed path patterns.

    Args:
        path (str): The file path to check against the allowed patterns.

    Returns:
        bool: True if the path matches any allowed pattern, False otherwise.

    Logs:
        Logs the result of the pattern matching at the trace level.
    """
    global _pathspec_cache
    if _pathspec_cache is None:
        _pathspec_cache = pathspec.PathSpec.from_lines("gitwildmatch", ALLOWED_PATHS)
    match = _pathspec_cache.match_file(path)
    logger.trace(f"Checking if path {path} matches allowed patterns: {match}")
    return match


def is_browser_request(request: Request) -> bool:
    """
    Checks if the request is from a browser (HTML request) or API.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        bool: True if the request is from a browser (Accept: text/html), False otherwise.
    """
    accept_header = request.headers.get("accept", "")
    return "text/html" in accept_header


def create_unauthorized_response(request: Request, error_message: str, redirect_url: str = "/login") -> Response:
    """
    Creates an appropriate unauthorized response based on the request type.

    For browser requests (Accept: text/html), returns a RedirectResponse.
    For API requests, returns a JSONResponse with error details.

    Args:
        request (Request): The incoming HTTP request.
        error_message (str): The error message to include in the response.
        redirect_url (str): The URL to redirect to for browser requests. Defaults to "/login".

    Returns:
        Response: Either a RedirectResponse (for browsers) or JSONResponse (for API).
    """
    if is_browser_request(request):
        return RedirectResponse(url=redirect_url, status_code=302)
    return JSONResponse(
        status_code=401,
        content={"error": error_message, "redirect_to": redirect_url},
    )
