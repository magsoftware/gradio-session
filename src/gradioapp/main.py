from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import gradio as gr
from loguru import logger
import uvicorn

from .api.middleware import AuthMiddleware, LoggingMiddleware, SessionMiddleware
from .api.routes import health_router, home_router, login_router, static_router
from .config import get_settings
from .core.logging import setup_logging
from .domain.session.backends.memory import InMemorySessionStore
from .domain.session.store import initialize_session_store
from .ui import create_gradio_app

# Get base directory
BASE_DIR = Path(__file__).parent

# Setup logging
setup_logging()

# Setup session store
initialize_session_store(InMemorySessionStore(ttl=300, cleanup_interval=60))

# Get settings
settings = get_settings()

# Main FastAPI application
app = FastAPI(title=settings.projectname, version=settings.version)

# Middleware are executed in reverse order of their addition
app.add_middleware(SessionMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(login_router)
app.include_router(health_router)
app.include_router(home_router)
app.include_router(static_router)

# Add static files for serving Gradio assets
static_dir = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Mount gradio app
gr.mount_gradio_app(app, create_gradio_app(), path="/gradio")


def main() -> None:
    """Main entry point for the application."""
    logger.info("Starting the application")
    settings = get_settings()
    uvicorn.run(
        "gradioapp.main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.reload,
        log_config=None,  # Disable uvicorn's default logging
    )


if __name__ == "__main__":
    main()
