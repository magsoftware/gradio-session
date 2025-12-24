"""Tests for middleware utility functions."""

from unittest.mock import MagicMock, patch

from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse
import pytest

from gradioapp.api.middleware.utils import (
    create_unauthorized_response,
    is_browser_request,
    is_path_allowed,
)


class TestIsPathAllowed:
    """Tests for is_path_allowed function."""

    def test_is_path_allowed_login(self):
        """Test that /login path is allowed."""
        assert is_path_allowed("/login") is True

    def test_is_path_allowed_logout(self):
        """Test that /logout path is allowed."""
        assert is_path_allowed("/logout") is True

    def test_is_path_allowed_healthz(self):
        """Test that /healthz path is allowed."""
        assert is_path_allowed("/healthz") is True

    def test_is_path_allowed_static(self):
        """Test that /static/* paths are allowed."""
        assert is_path_allowed("/static/css/style.css") is True
        assert is_path_allowed("/static/js/app.js") is True

    def test_is_path_allowed_manifest(self):
        """Test that /manifest.json path is allowed."""
        assert is_path_allowed("/manifest.json") is True

    def test_is_path_allowed_protected(self):
        """Test that protected paths are not allowed."""
        assert is_path_allowed("/protected") is False
        assert is_path_allowed("/api/data") is False


class TestIsBrowserRequest:
    """Tests for is_browser_request function."""

    def test_is_browser_request_with_html_accept(self):
        """Test that request with text/html in Accept header is browser request."""
        mock_request = MagicMock(spec=Request)
        mock_request.headers.get.return_value = "text/html,application/xhtml+xml"

        assert is_browser_request(mock_request) is True

    def test_is_browser_request_with_json_accept(self):
        """Test that request with application/json in Accept header is not browser request."""
        mock_request = MagicMock(spec=Request)
        mock_request.headers.get.return_value = "application/json"

        assert is_browser_request(mock_request) is False

    def test_is_browser_request_without_accept(self):
        """Test that request without Accept header is not browser request."""
        mock_request = MagicMock(spec=Request)
        mock_request.headers.get.return_value = ""

        assert is_browser_request(mock_request) is False


class TestCreateUnauthorizedResponse:
    """Tests for create_unauthorized_response function."""

    def test_create_unauthorized_response_browser(self):
        """Test that browser request returns RedirectResponse."""
        mock_request = MagicMock(spec=Request)
        mock_request.headers.get.return_value = "text/html"

        response = create_unauthorized_response(mock_request, "Access denied")

        assert isinstance(response, RedirectResponse)
        assert response.status_code == 302
        assert response.headers["location"] == "/login"

    def test_create_unauthorized_response_api(self):
        """Test that API request returns JSONResponse."""
        mock_request = MagicMock(spec=Request)
        mock_request.headers.get.return_value = "application/json"

        response = create_unauthorized_response(mock_request, "Access denied")

        assert isinstance(response, JSONResponse)
        assert response.status_code == 401
        # Check response content
        import json

        content = json.loads(response.body.decode())
        assert content["error"] == "Access denied"
        assert content["redirect_to"] == "/login"

    def test_create_unauthorized_response_custom_redirect(self):
        """Test that custom redirect URL is used."""
        mock_request = MagicMock(spec=Request)
        mock_request.headers.get.return_value = "text/html"

        response = create_unauthorized_response(mock_request, "Access denied", redirect_url="/custom")

        assert isinstance(response, RedirectResponse)
        assert response.headers["location"] == "/custom"
