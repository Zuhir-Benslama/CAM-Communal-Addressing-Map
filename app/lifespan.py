"""Plugin lifecycle utilities (startup/shutdown)."""

import logging

logger = logging.getLogger(__name__)


def on_startup() -> None:
    """Log plugin startup."""
    logger.info('RNA plugin starting up')


def on_shutdown() -> None:
    """Log plugin shutdown."""
    logger.info('RNA plugin shutting down')
