"""
TARS Logging Utilities
Provides consistent logging across the application.
"""

import logging
import sys
from rich.logging import RichHandler
from rich.console import Console

from .config import get_config


def setup_logger(name: str = "tars") -> logging.Logger:
    """
    Set up a logger with rich formatting.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    config = get_config()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create rich handler for beautiful console output
    console = Console()
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        rich_tracebacks=True,
        markup=True
    )
    rich_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(rich_handler)
    
    return logger


# Default logger instance
logger = setup_logger()


def log_tars_response(response: str) -> None:
    """Log a TARS response with special formatting."""
    logger.info(f"[bold cyan]TARS:[/bold cyan] {response}")


def log_user_input(user_input: str) -> None:
    """Log user input with special formatting."""
    logger.info(f"[bold green]User:[/bold green] {user_input}")


def log_system_event(event: str) -> None:
    """Log system events."""
    logger.info(f"[bold yellow]System:[/bold yellow] {event}")
