from typing import Optional

# In-memory user database
user_db = {}


class User:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


def init_user_db() -> None:
    """Initialize the user database with some sample users."""
    global user_db
    user_db = {
        "john@test.com": User(username="john@test.com", password="secret"),
        "jane@test.com": User(username="jane@test.com", password="secret"),
    }


def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password."""
    user = user_db.get(username)
    if user and user.password == password:
        return user
    return None


init_user_db()
