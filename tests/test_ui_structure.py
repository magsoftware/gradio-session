"""Tests for UI structure and component creation."""

from unittest.mock import MagicMock, patch

import pytest

from gradioapp.ui.gradio_app import create_gradio_app
from gradioapp.ui.navbar import create_navbar


class TestGradioApp:
    """Tests for create_gradio_app function."""

    @patch("gradioapp.ui.gradio_app.gr.Blocks")
    @patch("gradioapp.ui.gradio_app.create_navbar")
    @patch("gradioapp.ui.gradio_app.HomePage")
    def test_create_gradio_app_structure(self, mock_home_page, mock_navbar, mock_blocks):
        """Test that create_gradio_app creates correct structure."""
        mock_app = MagicMock()
        mock_blocks.return_value.__enter__.return_value = mock_app
        mock_home_page_instance = MagicMock()
        mock_home_page.return_value = mock_home_page_instance

        result = create_gradio_app()

        # Verify Blocks was created with correct parameters
        mock_blocks.assert_called_once()
        call_kwargs = mock_blocks.call_args[1]
        assert call_kwargs["title"] == "Gradio App"
        assert call_kwargs["visible"] is True
        assert call_kwargs["fill_width"] is True
        # Verify navbar was created
        mock_navbar.assert_called_once()
        # Verify HomePage was created
        mock_home_page.assert_called_once()
        # Verify HomePage was rendered
        mock_home_page_instance.render.assert_called_once_with(visible=True)

    @patch("gradioapp.ui.gradio_app.gr.Blocks")
    @patch("gradioapp.ui.gradio_app.create_navbar")
    @patch("gradioapp.ui.gradio_app.HomePage")
    @patch("gradioapp.ui.gradio_app.logger")
    def test_create_gradio_app_logs(self, mock_logger, mock_home_page, mock_navbar, mock_blocks):
        """Test that create_gradio_app logs initialization."""
        mock_app = MagicMock()
        mock_blocks.return_value.__enter__.return_value = mock_app

        create_gradio_app()

        # Verify logger was called
        mock_logger.info.assert_called_once_with("Creating Gradio app UI")

    def test_create_gradio_app_returns_blocks(self):
        """Test that create_gradio_app returns gr.Blocks instance."""
        result = create_gradio_app()
        # Should return a Blocks instance (or mock in test environment)
        assert result is not None


class TestNavbar:
    """Tests for create_navbar function."""

    @patch("gradioapp.ui.navbar.gr.Row")
    @patch("gradioapp.ui.navbar.gr.Button")
    def test_create_navbar_structure(self, mock_button, mock_row):
        """Test that create_navbar creates correct structure."""
        mock_row_context = MagicMock()
        mock_row.return_value.__enter__.return_value = mock_row_context
        mock_button_instance = MagicMock()
        mock_button.return_value = mock_button_instance

        create_navbar()

        # Verify Row was created with equal_height
        mock_row.assert_called_once_with(equal_height=True)
        # Verify Button was created
        mock_button.assert_called_once_with("Logout")

    @patch("gradioapp.ui.navbar.gr.Row")
    @patch("gradioapp.ui.navbar.gr.Button")
    def test_create_navbar_logout_button_click(self, mock_button, mock_row):
        """Test that navbar logout button has correct click handler."""
        mock_row_context = MagicMock()
        mock_row.return_value.__enter__.return_value = mock_row_context
        mock_button_instance = MagicMock()
        mock_button.return_value = mock_button_instance

        create_navbar()

        # Verify button.click was called with correct parameters
        mock_button_instance.click.assert_called_once()
        click_call = mock_button_instance.click.call_args
        assert click_call[1]["fn"] is None
        assert click_call[1]["inputs"] == []
        assert click_call[1]["outputs"] == []
        assert "window.location.href = '/logout'" in click_call[1]["js"]

    @patch("gradioapp.ui.navbar.gr.Row")
    @patch("gradioapp.ui.navbar.gr.Button")
    def test_create_navbar_logout_button_js(self, mock_button, mock_row):
        """Test that logout button JavaScript redirects to /logout."""
        mock_row_context = MagicMock()
        mock_row.return_value.__enter__.return_value = mock_row_context
        mock_button_instance = MagicMock()
        mock_button.return_value = mock_button_instance

        create_navbar()

        # Get the JS from click call
        click_call = mock_button_instance.click.call_args
        js_code = click_call[1]["js"]

        # Verify JS contains redirect logic
        assert "/logout" in js_code
        assert "window.location.href" in js_code
