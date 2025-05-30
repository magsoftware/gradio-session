
import sys
from loguru import logger

MAX_LOC_LENGTH = 40


def format_location(record) -> bool:
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
