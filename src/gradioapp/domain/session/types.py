from typing import Any, TypedDict


class SessionData(TypedDict):
    """
    Type definition for session data stored in the session store.

    Attributes:
        username (str): The username associated with the session.
        data (dict[str, Any]): Additional data stored in the session.
        expire_at (float): Expiration timestamp as Unix time.
    """

    username: str
    data: dict[str, Any]
    expire_at: float
