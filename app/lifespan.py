"""Plugin lifecycle utilities (startup/shutdown)."""

import logging

logger = logging.getLogger(__name__)


def on_startup() -> None:
    logger.info("RNA plugin starting up")


def on_shutdown() -> None:
    logger.info("RNA plugin shutting down")
