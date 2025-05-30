import datetime
import uuid

import jwt

import settings

ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: datetime.timedelta) -> str:
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
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "iat": datetime.datetime.utcnow()})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)


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


def verify_token(token: str) -> dict | None:
    """
    Verifies and decodes a JWT token.

    Args:
        token (str): The JWT token to verify.

    Returns:
        dict | None: The decoded payload if the token is valid, otherwise None.

    Raises:
        None: All exceptions are handled internally.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
