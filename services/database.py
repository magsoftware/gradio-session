from typing import Optional

import bcrypt

# In-memory user database
user_db = {}


class User:
    def __init__(self, username: str, password_hash: str):
        self.username = username
        self.password_hash = password_hash

    def verify_password(self, password: str) -> bool:
        """
        Verify a password against the stored hash.

        Args:
            password (str): The password to verify.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password as a string.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def init_user_db() -> None:
    """Initialize the user database with some sample users."""
    global user_db
    user_db = {
        "john@test.com": User(username="john@test.com", password_hash=hash_password("secret")),
        "jane@test.com": User(username="jane@test.com", password_hash=hash_password("secret")),
    }


def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate a user by verifying the provided username and password.

    Args:
        username (str): The username of the user attempting to authenticate.
        password (str): The password provided for authentication.

    Returns:
        Optional[User]: The authenticated User object if credentials are valid; otherwise, None.
    """
    user = user_db.get(username)
    if user and user.verify_password(password):
        return user
    return None


init_user_db()
