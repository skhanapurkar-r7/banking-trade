"""Logging configuration for the application."""

import logging
import sys

from .config import settings


def setup_logging() -> None:
    """
    Configure application-wide logging with structured format.

    Sets up console handler with formatted output including timestamp,
    log level, module name, and message.
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=settings.get_log_level(),
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the specified module.

    Args:
        name: Module name for the logger

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
