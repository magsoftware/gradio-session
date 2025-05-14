from .health import router as health_router
from .home import router as home_router
from .login import router as login_router

__all__ = [
    "health_router",
    "home_router",
    "login_router",
]
