"""Programmatic ODF (OpenDocument Text) report generation as a package.

The original single module was split into focused submodules:

- :mod:`._namespaces` — ODF XML namespace constants and helper.
- :mod:`.styles` — document style XML generation.
- :mod:`.package` — ODT zip package assembly.
- :mod:`.builder` — the in-memory ODF document builder.
- :mod:`.labels` — localised label catalog.
- :mod:`.report` — public high-level report construction.

``build_statistical_report`` is re-exported here so existing
``from app.shared import odt_report`` imports keep working unchanged.
"""

from .report import build_statistical_report

__all__ = ['build_statistical_report']
