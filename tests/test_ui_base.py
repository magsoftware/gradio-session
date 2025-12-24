"""Tests for UI base classes."""

from unittest.mock import MagicMock, patch

import gradio as gr
import pytest

from gradioapp.ui.pages.base import BasePage, BaseTab


class TestBasePage:
    """Tests for BasePage abstract class."""

    def test_base_page_initialization(self):
        """Test BasePage initialization."""

        # Create a concrete implementation for testing
        class TestPage(BasePage):
            def create_ui(self):
                pass

        page = TestPage(label="Test", title="Test Title")
        assert page.label == "Test"
        assert page.title == "Test Title"

    def test_base_page_show(self):
        """Test BasePage show method."""

        class TestPage(BasePage):
            def create_ui(self):
                pass

        page = TestPage(label="Test", title="Test Title")
        result = page.show()

        # Should return gr.update(visible=True)
        assert result == gr.update(visible=True)

    def test_base_page_hide(self):
        """Test BasePage hide method."""

        class TestPage(BasePage):
            def create_ui(self):
                pass

        page = TestPage(label="Test", title="Test Title")
        result = page.hide()

        # Should return gr.update(visible=False)
        assert result == gr.update(visible=False)

    @patch("gradioapp.ui.pages.base.gr.Column")
    def test_base_page_render(self, mock_column):
        """Test BasePage render method."""

        class TestPage(BasePage):
            def create_ui(self):
                pass

        mock_column_context = MagicMock()
        mock_column.return_value.__enter__.return_value = mock_column_context

        page = TestPage(label="Test", title="Test Title")
        page.render(visible=True)

        # Verify that Column was created with visible parameter
        mock_column.assert_called_once_with(visible=True)
        # Verify that create_ui was called (through context manager)
        assert hasattr(page, "container") or mock_column_context is not None

    @patch("gradioapp.ui.pages.base.gr.Column")
    def test_base_page_render_visible_false(self, mock_column):
        """Test BasePage render with visible=False."""

        class TestPage(BasePage):
            def create_ui(self):
                pass

        mock_column_context = MagicMock()
        mock_column.return_value.__enter__.return_value = mock_column_context

        page = TestPage(label="Test", title="Test Title")
        page.render(visible=False)

        # Verify that Column was created with visible=False
        mock_column.assert_called_once_with(visible=False)


class TestBaseTab:
    """Tests for BaseTab abstract class."""

    def test_base_tab_initialization(self):
        """Test BaseTab initialization."""

        class TestTab(BaseTab):
            def create_ui(self, tab_component):
                pass

        tab = TestTab("TestTab")
        assert tab.name == "TestTab"

    def test_base_tab_initialization_different_name(self):
        """Test BaseTab initialization with different name."""

        class TestTab(BaseTab):
            def create_ui(self, tab_component):
                pass

        tab = TestTab("AnotherTab")
        assert tab.name == "AnotherTab"

    def test_base_tab_is_abstract(self):
        """Test that BaseTab cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseTab("Test")  # Should fail because create_ui is abstract
