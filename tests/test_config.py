import os

import pytest

from gradioapp.config import Settings, load_settings


class TestSettings:
    """Tests for Settings dataclass."""

    def test_load_settings_success(self, test_settings):
        """Test loading settings successfully."""
        assert test_settings is not None
        assert isinstance(test_settings, Settings)
        assert len(test_settings.jwt_secret) >= 32

    def test_jwt_secret_validation_missing(self, monkeypatch):
        """Test that missing JWT_SECRET raises ValueError."""
        monkeypatch.delenv("JWT_SECRET", raising=False)
        monkeypatch.setenv("VERSION", "test")
        monkeypatch.setenv("PROJECTNAME", "test")

        with pytest.raises(ValueError, match="JWT_SECRET environment variable is required"):
            load_settings()

    def test_jwt_secret_validation_too_short(self, monkeypatch):
        """Test that JWT_SECRET shorter than 32 chars raises ValueError."""
        monkeypatch.setenv("JWT_SECRET", "short")
        monkeypatch.setenv("VERSION", "test")
        monkeypatch.setenv("PROJECTNAME", "test")

        with pytest.raises(
            ValueError, match="JWT_SECRET must be at least 32 characters long"
        ):
            load_settings()

    def test_settings_frozen(self, test_settings):
        """Test that Settings is frozen (immutable)."""
        with pytest.raises(Exception):  # dataclass frozen raises FrozenInstanceError
            test_settings.jwt_secret = "new_value"

    def test_settings_defaults(self, monkeypatch):
        """Test that settings have correct defaults."""
        monkeypatch.setenv("JWT_SECRET", "a" * 32)
        monkeypatch.setenv("VERSION", "test")
        monkeypatch.setenv("PROJECTNAME", "test")
        # Remove optional env vars to test defaults
        monkeypatch.delenv("SECRET_KEY", raising=False)
        monkeypatch.delenv("CSRF_SECRET", raising=False)
        monkeypatch.delenv("RELOAD", raising=False)
        monkeypatch.delenv("HOME_AS_HTML", raising=False)

        settings = load_settings()

        assert settings.reload is False
        assert settings.home_as_html is False
        assert settings.secret_key == ""
        assert settings.csrf_secret == ""

