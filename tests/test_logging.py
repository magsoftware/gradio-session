"""Tests for logging setup."""

import sys
from unittest.mock import MagicMock, patch

import pytest

from gradioapp.core.logging import _format_location, setup_logging


class TestFormatLocation:
    """Tests for _format_location function."""

    def test_format_location_short(self):
        """Test formatting location when it's shorter than MAX_LOC_LENGTH."""
        record = {
            "name": "test_module",
            "function": "test_function",
            "line": 42,
        }

        result = _format_location(record)

        assert result is True
        assert "location" in record
        location = record["location"]
        assert len(location) == 40  # MAX_LOC_LENGTH
        assert "test_module" in location
        assert "test_function" in location
        assert "42" in location

    def test_format_location_long(self):
        """Test formatting location when it's longer than MAX_LOC_LENGTH."""
        record = {
            "name": "very_long_module_name_that_exceeds_maximum_length",
            "function": "very_long_function_name_that_also_exceeds",
            "line": 12345,
        }

        result = _format_location(record)

        assert result is True
        assert "location" in record
        location = record["location"]
        assert len(location) == 40  # MAX_LOC_LENGTH
        # Should be truncated from the left
        assert location.endswith("12345")

    def test_format_location_exact_length(self):
        """Test formatting location when it's exactly MAX_LOC_LENGTH."""
        # Create a location string that's exactly 40 characters
        record = {
            "name": "mod",
            "function": "func",
            "line": 1,
        }
        # This will create "mod:func:1" which is 9 chars, padded to 40

        result = _format_location(record)

        assert result is True
        assert "location" in record
        location = record["location"]
        assert len(location) == 40


class TestSetupLogging:
    """Tests for setup_logging function."""

    @patch("gradioapp.core.logging.logger")
    def test_setup_logging_initializes(self, mock_logger):
        """Test that setup_logging initializes logging correctly."""
        # Mock logger.remove and logger.add
        mock_logger.remove.return_value = None
        mock_logger.add.return_value = None

        setup_logging()

        # Verify logger.remove was called
        mock_logger.remove.assert_called_once()
        # Verify logger.add was called with correct parameters
        mock_logger.add.assert_called_once()
        call_args = mock_logger.add.call_args
        assert call_args[0][0] == sys.stderr
        assert call_args[1]["level"] == "DEBUG"
        assert "format" in call_args[1]
        assert call_args[1]["filter"] == _format_location
        # Verify logger.info was called
        mock_logger.info.assert_called_once_with("Logging initialized with custom format and location handler")
