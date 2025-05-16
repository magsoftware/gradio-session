import sys

from fastapi import FastAPI
import gradio as gr
from loguru import logger
import uvicorn

from middleware import AuthMiddleware, LoggingMiddleware, SessionMiddleware
from routes import health_router, home_router, login_router
from session import InMemorySessionStore, initialize_session_store
import settings
from ui import create_gradio_app

MAX_LOC_LENGTH = 40

def format_location(record) -> bool:
    location = f"{record['name']}:{record['function']}:{record['line']}"
    if len(location) > MAX_LOC_LENGTH:
        location = location[-MAX_LOC_LENGTH:]
    else:
        location = location.ljust(MAX_LOC_LENGTH)
    record["location"] = location
    return True

# Loguru logging setup
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level:<8}</level> | "
           "<cyan>{location}</cyan> - <level>{message}</level>",
    filter=format_location,
)

# Setup session store
initialize_session_store(InMemorySessionStore())

# Main FastAPI application
app = FastAPI(title=settings.PROJECTNAME, version=settings.VERSION)

# The sequence is important
app.add_middleware(LoggingMiddleware)
app.add_middleware(SessionMiddleware)
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(login_router)
app.include_router(health_router)
app.include_router(home_router)

# Mount gradio app
gr.mount_gradio_app(app, create_gradio_app(), path="/gradio")

if __name__ == "__main__":
    logger.info("Starting the application")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.RELOAD,
        log_config=None,  # Disable uvicorn's default logging
    )
