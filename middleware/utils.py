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
    spec = pathspec.PathSpec.from_lines("gitwildmatch", ALLOWED_PATHS)
    match = spec.match_file(path)
    logger.trace(f"Checking if path {path} matches allowed patterns: {match}")
    return match
