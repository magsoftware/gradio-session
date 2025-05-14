from fastapi import Request
from itsdangerous import URLSafeTimedSerializer

import settings

serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


def generate_csrf_token(request: Request) -> str:
    return serializer.dumps(request.client.host, salt=settings.CSRF_SECRET)


def validate_csrf_token(token: str, request: Request) -> bool:
    try:
        data = serializer.loads(
            token, salt=settings.CSRF_SECRET, max_age=3600
        )  # Token valid for 1 hour
        return data == request.client.host
    except Exception:
        return False
