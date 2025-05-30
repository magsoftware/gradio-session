import sys

from loguru import logger
from typing import Dict, Any

MAX_LOC_LENGTH = 40


def format_location(record: Dict[str, Any]) -> bool:
    """
    Formats the 'location' field in a log record dictionary by combining the record's
    'name', 'function', and 'line' fields into a single string. The resulting string is
    either truncated from the left or padded with spaces to ensure it matches the
    maximum allowed length (MAX_LOC_LENGTH). The formatted location is stored back in
    the record under the 'location' key.

    Args:
        record (dict): A dictionary representing a log record, expected to contain
            'name', 'function', and 'line' keys.

    Returns:
        bool: Always returns True after formatting the location.
    """
    location = f"{record['name']}:{record['function']}:{record['line']}"
    if len(location) > MAX_LOC_LENGTH:
        location = location[-MAX_LOC_LENGTH:]
    else:
        location = location.ljust(MAX_LOC_LENGTH)
    record["location"] = location
    return True


# Loguru logging setup
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level:<8}</level> | "
    "<cyan>{location}</cyan> - <level>{message}</level>",
    filter=format_location,
)

logger.info("Logging initialized with custom format and location handler.")
