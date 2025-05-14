import datetime
import uuid

import jwt

import settings

ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: datetime.timedelta) -> str:
    """
    Create a JWT access token with an expiration time. Token has the following structure:
    {
        "sub": "user_id",
        "session_id": "abc123",
        "exp": ...,
        "iat": ...
    }
    :param data: The data to encode in the token.
    :param expires_delta: The expiration time delta.
    :return: The encoded JWT token as a string.
    """
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "iat": datetime.datetime.utcnow()})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)


def create_session_token(
    user_id: str, expires_delta: datetime.timedelta
) -> tuple[str, str]:
    session_id = str(uuid.uuid4())
    token = create_access_token(
        {"sub": user_id, "session_id": session_id}, expires_delta
    )
    return token, session_id


def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
