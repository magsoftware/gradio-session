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
