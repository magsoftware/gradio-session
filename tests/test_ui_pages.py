"""Tests for UI page components."""

from unittest.mock import MagicMock, patch

import gradio as gr
import pytest

from gradioapp.domain.session.backends.memory import InMemorySessionStore
from gradioapp.domain.session.store import initialize_session_store
from gradioapp.ui.pages.home_page import HomePage, Tab1, Tab2


class TestTab1:
    """Tests for Tab1 component."""

    @pytest.fixture
    def session_store(self):
        """Create a fresh in-memory session store for testing."""
        store = InMemorySessionStore(ttl=300, cleanup_interval=1)
        initialize_session_store(store)
        yield store
        store.stop_cleanup_thread()

    def test_tab1_initialization(self):
        """Test Tab1 initialization."""
        tab = Tab1()
        assert tab.name == "Tab1"

    def test_tab1_show_session_with_session_id(self, session_store):
        """Test showing session when session_id exists."""
        session_id = "test_session"
        session_store.create_session(session_id=session_id, username="test_user", data={"key": "value"})

        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_state.session_id = session_id
        mock_request.state = mock_state

        tab = Tab1()
        result = tab.show_session(mock_request)

        assert session_id in result
        assert "test_user" in result

    def test_tab1_show_session_without_session_id(self):
        """Test showing session when session_id is None."""
        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_state.session_id = None
        mock_request.state = mock_state

        tab = Tab1()
        result = tab.show_session(mock_request)

        assert result == "No session ID found"

    def test_tab1_show_session_missing_state(self):
        """Test showing session when state is missing."""
        mock_request = MagicMock()
        mock_request.state = MagicMock()
        del mock_request.state.session_id

        tab = Tab1()
        result = tab.show_session(mock_request)

        assert result == "No session ID found"

    @patch("gradioapp.ui.pages.home_page.get_session_store")
    def test_tab1_show_session_store_error(self, mock_get_store):
        """Test showing session when store raises error."""
        mock_store = MagicMock()
        mock_store.get_session.return_value = None
        mock_get_store.return_value = mock_store

        mock_request = MagicMock()
        mock_state = MagicMock()
        mock_state.session_id = "test_session"
        mock_request.state = mock_state

        tab = Tab1()
        result = tab.show_session(mock_request)

        # Should handle gracefully
        assert isinstance(result, str)


class TestTab2:
    """Tests for Tab2 component."""

    @pytest.fixture
    def session_store(self):
        """Create a fresh in-memory session store for testing."""
        store = InMemorySessionStore(ttl=300, cleanup_interval=1)
        initialize_session_store(store)
        yield store
        store.stop_cleanup_thread()

    def test_tab2_initialization(self):
        """Test Tab2 initialization."""
        tab = Tab2()
        assert tab.name == "Tab2"

    def test_tab2_dump_sessions_empty(self, session_store):
        """Test dumping empty session store."""
        tab = Tab2()
        result = tab.dump_sessions()

        assert "Session store:" in result
        assert isinstance(result, str)

    def test_tab2_dump_sessions_with_data(self, session_store):
        """Test dumping session store with sessions."""
        session_store.create_session("session_1", "user1", {"data": "value1"})
        session_store.create_session("session_2", "user2", {"data": "value2"})

        tab = Tab2()
        result = tab.dump_sessions()

        assert "Session store:" in result
        assert "session_1" in result
        assert "session_2" in result
        assert "user1" in result
        assert "user2" in result


class TestHomePage:
    """Tests for HomePage component."""

    def test_home_page_initialization(self):
        """Test HomePage initialization."""
        page = HomePage()
        assert page.label == "Home"
        assert page.title == "Home Page"
        assert len(page.tabs) == 2

    def test_home_page_tabs_names(self):
        """Test that tabs have correct names."""
        page = HomePage()
        tab_names = [tab.name for tab in page.tabs]
        assert "Tab1" in tab_names
        assert "Tab2" in tab_names

    def test_home_page_tabs_are_instances(self):
        """Test that tabs are proper instances."""
        page = HomePage()
        assert all(isinstance(tab, (Tab1, Tab2)) for tab in page.tabs)

    @patch("gradioapp.ui.pages.home_page.gr.Tabs")
    @patch("gradioapp.ui.pages.home_page.gr.Tab")
    @patch("gradioapp.ui.pages.home_page.gr.Blocks")
    @patch("gradioapp.ui.pages.home_page.gr.Button")
    @patch("gradioapp.ui.pages.home_page.gr.Textbox")
    def test_home_page_create_ui(self, mock_textbox, mock_button, mock_blocks, mock_tab, mock_tabs):
        """Test that create_ui creates tabs structure."""
        # Mock Blocks context to avoid "outside of Blocks context" error
        mock_blocks_context = MagicMock()
        mock_blocks.return_value.__enter__.return_value = mock_blocks_context
        mock_tabs_context = MagicMock()
        mock_tabs.return_value.__enter__.return_value = mock_tabs_context
        mock_tab_context = MagicMock()
        mock_tab.return_value.__enter__.return_value = mock_tab_context
        mock_button_instance = MagicMock()
        mock_button.return_value = mock_button_instance

        # Create a Blocks context for the test
        import gradio as gr

        with gr.Blocks():
            page = HomePage()
            page.create_ui()

            # Verify tabs were created
            assert mock_tabs.called
            # Verify Tab was called for each tab
            assert mock_tab.call_count == 2
