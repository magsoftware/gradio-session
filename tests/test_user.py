import pytest

from services.database import User, authenticate_user, hash_password, init_user_db


class TestHashPassword:
    """Tests for hash_password function."""

    def test_hash_password_creates_hash(self):
        """Test that hash_password creates a hash."""
        password = "test_password"
        hashed = hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Should be different from original

    def test_hash_password_different_hashes(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "test_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different due to salt
        assert hash1 != hash2


class TestUser:
    """Tests for User class."""

    def test_user_verify_password_correct(self):
        """Test verifying correct password."""
        password = "test_password"
        password_hash = hash_password(password)
        user = User(username="test_user", password_hash=password_hash)

        assert user.verify_password(password) is True

    def test_user_verify_password_incorrect(self):
        """Test verifying incorrect password."""
        password = "test_password"
        password_hash = hash_password(password)
        user = User(username="test_user", password_hash=password_hash)

        assert user.verify_password("wrong_password") is False

    def test_user_verify_password_empty(self):
        """Test verifying empty password."""
        password = "test_password"
        password_hash = hash_password(password)
        user = User(username="test_user", password_hash=password_hash)

        assert user.verify_password("") is False


class TestAuthenticateUser:
    """Tests for authenticate_user function."""

    def test_authenticate_user_success(self):
        """Test successful authentication."""
        # Reinitialize user DB to ensure clean state
        init_user_db()
        user = authenticate_user("john@test.com", "secret")

        assert user is not None
        assert user.username == "john@test.com"

    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password."""
        init_user_db()
        user = authenticate_user("john@test.com", "wrong_password")

        assert user is None

    def test_authenticate_user_nonexistent_user(self):
        """Test authentication with nonexistent user."""
        init_user_db()
        user = authenticate_user("nonexistent@test.com", "secret")

        assert user is None

