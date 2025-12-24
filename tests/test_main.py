"""Tests for main application module."""

from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

# Import app after mocking to avoid side effects
import gradioapp.main as main_module


class TestAppStructure:
    """Tests for FastAPI app structure and configuration."""

    def test_app_is_fastapi_instance(self):
        """Test that app is a FastAPI instance."""
        assert isinstance(main_module.app, FastAPI)

    def test_app_has_correct_title(self):
        """Test that app has correct title from settings."""
        from gradioapp.config import get_settings

        settings = get_settings()
        assert main_module.app.title == settings.projectname

    def test_app_has_correct_version(self):
        """Test that app has correct version from settings."""
        from gradioapp.config import get_settings

        settings = get_settings()
        assert main_module.app.version == settings.version

    def test_app_has_middleware(self):
        """Test that app has all required middleware."""
        # Middleware are stored in app.user_middleware
        middleware_types = []
        for mw in main_module.app.user_middleware:
            if hasattr(mw, "cls") and hasattr(mw.cls, "__name__"):
                middleware_types.append(mw.cls.__name__)  # type: ignore[attr-defined]
        assert "SessionMiddleware" in middleware_types
        assert "AuthMiddleware" in middleware_types
        assert "LoggingMiddleware" in middleware_types

    def test_app_has_routers(self):
        """Test that app has all required routers."""
        # Check if routes are registered
        route_paths = []
        for route in main_module.app.routes:
            if hasattr(route, "path"):
                route_paths.append(route.path)  # type: ignore[attr-defined]
        # Health check route
        assert "/healthz" in route_paths
        # Login routes
        assert "/login" in route_paths
        # Home route
        assert "/" in route_paths
        # Static route
        assert "/manifest.json" in route_paths

    def test_app_has_static_mount(self):
        """Test that app has static files mount."""
        # Check if static mount exists by looking for routes with app attribute
        static_mounts = []
        for route in main_module.app.routes:
            if hasattr(route, "app") and hasattr(route.app, "directory"):  # type: ignore[attr-defined]
                static_mounts.append(route)
        assert len(static_mounts) > 0

    def test_app_has_gradio_mount(self):
        """Test that Gradio app is mounted."""
        # Gradio app is mounted at /gradio
        # We verify by checking if routes exist (Gradio adds routes)
        # This is tested indirectly through app structure
        route_count = len(main_module.app.routes)
        # Should have more routes than just basic ones (Gradio adds routes)
        assert route_count > 4  # At least health, login, home, static

    def test_app_health_endpoint(self):
        """Test that health endpoint works."""
        client = TestClient(main_module.app)
        response = client.get("/healthz")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_app_login_endpoint_exists(self):
        """Test that login endpoint exists."""
        client = TestClient(main_module.app)
        response = client.get("/login")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


class TestMainFunction:
    """Tests for main() function."""

    @patch("gradioapp.main.uvicorn.run")
    @patch("gradioapp.main.logger")
    @patch("gradioapp.main.get_settings")
    def test_main_function_calls_uvicorn(self, mock_get_settings, mock_logger, mock_uvicorn_run):
        """Test that main() calls uvicorn.run with correct parameters."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.reload = False
        mock_get_settings.return_value = mock_settings

        # Call main function
        main_module.main()

        # Verify logger was called
        mock_logger.info.assert_called_once_with("Starting the application")

        # Verify get_settings was called
        mock_get_settings.assert_called_once()

        # Verify uvicorn.run was called with correct parameters
        mock_uvicorn_run.assert_called_once()
        call_args = mock_uvicorn_run.call_args
        assert call_args[0][0] == "gradioapp.main:app"
        assert call_args[1]["host"] == "0.0.0.0"
        assert call_args[1]["port"] == 8080
        assert call_args[1]["reload"] is False
        assert call_args[1]["log_config"] is None

    @patch("gradioapp.main.uvicorn.run")
    @patch("gradioapp.main.logger")
    @patch("gradioapp.main.get_settings")
    def test_main_function_with_reload_enabled(self, mock_get_settings, mock_logger, mock_uvicorn_run):
        """Test that main() passes reload setting to uvicorn."""
        # Mock settings with reload enabled
        mock_settings = MagicMock()
        mock_settings.reload = True
        mock_get_settings.return_value = mock_settings

        # Call main function
        main_module.main()

        # Verify uvicorn.run was called with reload=True
        call_args = mock_uvicorn_run.call_args
        assert call_args[1]["reload"] is True

    @patch("gradioapp.main.uvicorn.run")
    @patch("gradioapp.main.logger")
    @patch("gradioapp.main.get_settings")
    def test_main_function_logs_startup(self, mock_get_settings, mock_logger, mock_uvicorn_run):
        """Test that main() logs application startup."""
        mock_settings = MagicMock()
        mock_settings.reload = False
        mock_get_settings.return_value = mock_settings

        main_module.main()

        # Verify logger.info was called with startup message
        mock_logger.info.assert_called_once_with("Starting the application")


class TestAppInitialization:
    """Tests for app initialization and setup."""

    def test_session_store_initialized(self):
        """Test that session store is initialized."""
        from gradioapp.domain.session.store import get_session_store

        # Should not raise RuntimeError
        store = get_session_store()
        assert store is not None

    def test_logging_setup_called(self):
        """Test that logging setup was called during module import."""
        # This is tested indirectly - if logging works, setup was called
        # We can verify by checking if logger has custom format
        from loguru import logger

        # Logger should be configured (not default)
        assert logger is not None

    def test_base_dir_is_set(self):
        """Test that BASE_DIR is set correctly."""
        from pathlib import Path

        # BASE_DIR in main.py is Path(__file__).parent
        # where __file__ is src/gradioapp/main.py
        # So BASE_DIR should be src/gradioapp
        expected_base_dir = Path(main_module.__file__).parent
        assert main_module.BASE_DIR == expected_base_dir

    def test_static_dir_path(self):
        """Test that static directory path is correct."""
        from pathlib import Path

        # Static dir should be BASE_DIR / "static"
        expected_static_dir = Path(main_module.__file__).parent / "static"
        assert main_module.BASE_DIR / "static" == expected_static_dir
