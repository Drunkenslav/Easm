"""
Logging configuration using loguru
"""
import sys
from loguru import logger
from app.core.config import settings


def setup_logging():
    """Configure logging for the application"""

    # Remove default handler
    logger.remove()

    # Add stdout handler with custom format
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
    )

    # Add file handler for production
    if not settings.debug:
        logger.add(
            "logs/easm_{time:YYYY-MM-DD}.log",
            rotation="00:00",
            retention="30 days",
            compression="zip",
            level=settings.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        )

    return logger
