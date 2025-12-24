"""Tests for JavaScript code in UI."""

import pytest

from gradioapp.ui.javascript import redirect_js


class TestRedirectJS:
    """Tests for redirect_js JavaScript code."""

    def test_redirect_js_is_string(self):
        """Test that redirect_js is a string."""
        assert isinstance(redirect_js, str)
        assert len(redirect_js) > 0

    def test_redirect_js_contains_fetch_interceptor(self):
        """Test that redirect_js contains fetch interceptor logic."""
        assert "window.fetch" in redirect_js
        assert "originalFetch" in redirect_js

    def test_redirect_js_handles_401(self):
        """Test that redirect_js handles 401 responses."""
        assert "401" in redirect_js
        assert "redirect_to" in redirect_js

    def test_redirect_js_redirects_on_401(self):
        """Test that redirect_js redirects on 401."""
        assert "window.location.href" in redirect_js
        assert "setTimeout" in redirect_js

    def test_redirect_js_is_valid_syntax(self):
        """Test that redirect_js is valid JavaScript syntax."""
        # Basic syntax check - should be a function
        assert redirect_js.strip().startswith("() => {")
        assert redirect_js.strip().endswith("}")

    def test_redirect_js_contains_console_logs(self):
        """Test that redirect_js contains console logging."""
        assert "console.log" in redirect_js
        assert "[Interceptor]" in redirect_js

    def test_redirect_js_handles_json_parsing(self):
        """Test that redirect_js handles JSON parsing."""
        assert "json()" in redirect_js
        assert "clone()" in redirect_js

    def test_redirect_js_handles_errors(self):
        """Test that redirect_js handles errors gracefully."""
        assert "catch" in redirect_js or "try" in redirect_js
        assert "console.warn" in redirect_js

    def test_redirect_js_returns_response(self):
        """Test that redirect_js returns response."""
        assert "return" in redirect_js
        assert "Response" in redirect_js

    def test_redirect_js_has_delay(self):
        """Test that redirect_js has delay before redirect."""
        assert "1000" in redirect_js  # 1000ms delay
        assert "setTimeout" in redirect_js
