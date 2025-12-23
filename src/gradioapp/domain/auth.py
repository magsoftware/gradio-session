import datetime
from typing import TypedDict
import uuid

import jwt

from ..config import get_settings

ALGORITHM = "HS256"


class TokenPayload(TypedDict):
    """
    Type definition for JWT token payload.

    Attributes:
        sub (str): Subject - the user ID.
        session_id (str): The session ID associated with the token.
        exp (int): Expiration time as Unix timestamp.
        iat (int): Issued at time as Unix timestamp.
    """

    sub: str
    session_id: str
    exp: int
    iat: int


def create_access_token(
    data: dict[str, str | int], expires_delta: datetime.timedelta
) -> str:
    """
    Generates a JSON Web Token (JWT) access token with an expiration time.

    JWT Attributes:
        - exp (Expiration Time): The timestamp when the token will expire.
        - iat (Issued At): The timestamp when the token was issued.
        - (other attributes): Any additional key-value pairs provided in the
          `data` argument will be included as custom claims in the JWT payload.

    Args:
        data (dict): The payload data to include in the token.
        expires_delta (datetime.timedelta): The time duration after which the token will expire.

    Returns:
        str: The encoded JWT access token as a string.
    """
    to_encode: dict[str, str | int | datetime.datetime] = dict(data)
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode["exp"] = expire
    to_encode["iat"] = datetime.datetime.utcnow()
    settings = get_settings()
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)


def create_session_token(
    user_id: str, expires_delta: datetime.timedelta
) -> tuple[str, str]:
    """
    Creates a new session token and session ID for a given user.

    Args:
        user_id (str): The unique identifier of the user for whom the session is being created.
        expires_delta (datetime.timedelta): The duration after which the session token will expire.

    Returns:
        tuple[str, str]: A tuple containing the generated access token and the session ID.
    """
    session_id = str(uuid.uuid4())
    token = create_access_token(
        {"sub": user_id, "session_id": session_id}, expires_delta
    )
    return token, session_id


def verify_token(token: str) -> TokenPayload | None:
    """
    Verifies and decodes a JWT token.

    Args:
        token (str): The JWT token to verify.

    Returns:
        TokenPayload | None: The decoded payload if the token is valid, otherwise None.

    Raises:
        None: All exceptions are handled internally.
    """
    try:
        settings = get_settings()
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        # Type cast to TokenPayload - jwt.decode returns dict[str, Any]
        return payload  # type: ignore[return-value]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
