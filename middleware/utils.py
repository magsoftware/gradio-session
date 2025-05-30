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
    spec = pathspec.PathSpec.from_lines("gitwildmatch", ALLOWED_PATHS)
    match = spec.match_file(path)
    logger.trace(f"Checking if path {path} matches allowed patterns: {match}")
    return match
