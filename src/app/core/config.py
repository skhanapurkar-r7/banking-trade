"""Application configuration settings."""

import logging
from typing import List

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        database_url: SQLite database connection string
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        cors_origins: List of allowed CORS origins
        api_v1_prefix: API version 1 route prefix
    """

    model_config = ConfigDict(env_file=".env", case_sensitive=False)

    database_url: str = "sqlite:///./src/db/trades.db"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    api_v1_prefix: str = "/api/v1"

    def get_cors_origins(self) -> List[str]:
        """
        Parse CORS origins from comma-separated string.

        Returns:
            list[str]: List of allowed origin URLs
        """
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def get_log_level(self) -> int:
        """
        Convert string log level to logging constant.

        Returns:
            int: Logging level constant
        """
        return getattr(logging, self.log_level.upper(), logging.INFO)


settings = Settings()
