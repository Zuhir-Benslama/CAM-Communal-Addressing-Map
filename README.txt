RNA - Plans d'Adressage (Addressing Plans Management)
=====================================================

QGIS plugin for managing Algerian municipal addressing plans.
Handles streets, subdivisions, organizations, zones, numbering, and signage.


Installation
------------

Install via the QGIS Plugin Manager (ZIP deployable with `make zip`).


Development
-----------

- Run tests:  ``make test``
- Pylint:     ``make pylint``
- Build:      ``make build``
- Install:   ``make install``


Project Structure
-----------------

- ``app/``       — Core application logic (models, services, repository)
- ``gui/``       — UI dialogs and map tools
- ``mixins/``    — Mixin classes for the main dialog
- ``layer/``     — QGIS layer management
- ``models/``    — Shim re-exports for QGIS compatibility
- ``db/``        — Database operations (shim)
- ``auth/``      — Authentication (shim)
- ``scripts/``   — Utility scripts (migration, reporting, etc.)
- ``test/``      — Test suite (155+ tests)
- ``i18n/``      — Internationalization (ar, fr, en)
- ``resources/`` — Icons and static assets


License
-------

GNU General Public License v2 or later.
