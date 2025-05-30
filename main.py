from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import gradio as gr
from loguru import logger
import uvicorn

from middleware import AuthMiddleware, LoggingMiddleware, SessionMiddleware
from routes import health_router, home_router, login_router, static_router
from session import InMemorySessionStore, initialize_session_store
import settings
from ui import create_gradio_app
from core.logging import logger

# Setup session store
initialize_session_store(InMemorySessionStore())

# Main FastAPI application
app = FastAPI(title=settings.PROJECTNAME, version=settings.VERSION)

# Middleware are executed in reverse order of their addition
app.add_middleware(LoggingMiddleware)
app.add_middleware(SessionMiddleware)
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(login_router)
app.include_router(health_router)
app.include_router(home_router)
app.include_router(static_router)

# Add static files for serving Gradio assets
app.mount("/static", StaticFiles(directory="static"), name="static")

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
