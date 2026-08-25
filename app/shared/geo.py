"""Lookup helpers for administrative geography reference data."""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any

from .constants import COMMUNES_DB, COMMUNES_JSON

logger = logging.getLogger(__name__)


def load_communes() -> list[dict[str, Any]]:
    """Load commune entries from communes.json ([] on read/parse failure)."""
    try:
        with Path(COMMUNES_JSON).open(encoding='utf-8') as f:
            return list(json.load(f).values())
    except (FileNotFoundError, json.JSONDecodeError):
        logger.exception('Failed to load %s', COMMUNES_JSON)
        return []


def find_commune_by_code(
    communes: list[dict[str, Any]],
    commune_code: str | int | None,
) -> dict[str, Any] | None:
    """Return the commune entry whose commune_code matches *commune_code*."""
    try:
        code = int(commune_code)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    for commune in communes:
        value = commune.get('commune_code')
        if value is not None and int(value) == code:
            return commune
    return None


def get_commune_wkt(commune_id: int) -> str | None:
    """Read the geometry WKT for *commune_id* from communes.db."""
    try:
        with sqlite3.connect(COMMUNES_DB) as conn:
            row = conn.execute(
                'SELECT wkt FROM geometries WHERE commune_id = ?', (commune_id,)
            ).fetchone()
    except sqlite3.Error:
        logger.exception('Failed to query %s', COMMUNES_DB)
        return None
    return row[0] if row else None
