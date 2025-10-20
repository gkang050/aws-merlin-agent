import logging
import os


def get_logger(name: str) -> logging.Logger:
    """Configure a namespaced logger with level controlled by MERLIN_LOG_LEVEL."""
    level = os.getenv("MERLIN_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(name)s [%(levelname)s] %(message)s",
    )
    return logging.getLogger(name)
