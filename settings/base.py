import os

from dotenv import load_dotenv

load_dotenv()

VERSION = os.getenv("VERSION")
PROJECTNAME = os.getenv("PROJECTNAME")

RELOAD = os.getenv("RELOAD", "False").lower() == "true"
HOME_AS_HTML = os.getenv("HOME_AS_HTML", "False").lower() == "true"

# JWT
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable is required")
if len(JWT_SECRET) < 32:
    raise ValueError(
        "JWT_SECRET must be at least 32 characters long for security reasons"
    )

# CSRF
SECRET_KEY = os.getenv("SECRET_KEY")
CSRF_SECRET = os.getenv("CSRF_SECRET")
