from fastapi import Request
from itsdangerous import URLSafeTimedSerializer

import settings

serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


def generate_csrf_token(request: Request) -> str:
    """
    Generates a CSRF token for the given request.

    The token is created by serializing the client's host address using a secret salt.

    Args:
        request (Request): The incoming HTTP request object.

    Returns:
        str: A CSRF token string unique to the client's host.
    """
    return serializer.dumps(request.client.host, salt=settings.CSRF_SECRET)


def validate_csrf_token(token: str, request: Request) -> bool:
    """
    Validates a CSRF token by deserializing it and comparing its data to the client's host.

    Args:
        token (str): The CSRF token to validate.
        request (Request): The incoming HTTP request object.

    Returns:
        bool: True if the token is valid and matches the client's host, False otherwise.
    """
    try:
        data = serializer.loads(
            token, salt=settings.CSRF_SECRET, max_age=3600
        )  # Token valid for 1 hour
        return data == request.client.host
    except Exception:
        return False
