"""
Application configuration using Pydantic Settings.
Loads configuration from environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Pydantic settings class to manage environment variables.
    """
    # API prefix
    API_V1_STR: str = "/api/v1"
    
    # Database URL
    # For SQLite: "sqlite+aiosqlite:///./test.db"
    # For PostgreSQL: "postgresql+asyncpg://user:pass@host/db"
    DATABASE_URL: str = "sqlite+aiosqlite:///./default.db"
    
    # API Keys
    ADMIN_API_KEY: str = "default_admin_secret"
    CLIENT_API_KEY: str = "default_client_secret"

    # Scheduler settings
    SCHEDULER_INTERVAL_MINUTES: int = 240 # 4 hours

    model_config = SettingsConfigDict(
        env_file=".env",  # Load from .env file
        env_file_encoding='utf-8',
        case_sensitive=True,
    )

settings = Settings()
