from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    """
    Application settings loaded from environment variables.

    Attributes:
        version: Application version string.
        projectname: Project name string.
        reload: Enable auto-reload in development mode.
        home_as_html: Serve home page as HTML.
        jwt_secret: Secret key for JWT token signing (minimum 32 characters).
        secret_key: Secret key for general use.
        csrf_secret: Secret key for CSRF token generation.
    """

    version: str
    projectname: str
    reload: bool = False
    home_as_html: bool = False
    jwt_secret: str = ""
    secret_key: str = ""
    csrf_secret: str = ""

    def __post_init__(self) -> None:
        """
        Validate settings after initialization.

        Raises:
            ValueError: If JWT_SECRET is missing or too short.
        """
        if not self.jwt_secret:
            raise ValueError("JWT_SECRET environment variable is required")
        if len(self.jwt_secret) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long for security reasons")


def load_settings() -> Settings:
    """
    Load settings from environment variables.

    Returns:
        Settings: Configured settings instance.

    Raises:
        ValueError: If required settings are invalid.
    """
    return Settings(
        version=os.getenv("VERSION", ""),
        projectname=os.getenv("PROJECTNAME", ""),
        reload=os.getenv("RELOAD", "False").lower() == "true",
        home_as_html=os.getenv("HOME_AS_HTML", "False").lower() == "true",
        jwt_secret=os.getenv("JWT_SECRET", ""),
        secret_key=os.getenv("SECRET_KEY", ""),
        csrf_secret=os.getenv("CSRF_SECRET", ""),
    )


# Create settings instance
_settings = load_settings()


def get_settings() -> Settings:
    """
    Get the application settings instance.

    Returns:
        Settings: The configured settings instance.
    """
    return _settings
