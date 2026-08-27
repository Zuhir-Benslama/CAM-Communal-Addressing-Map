# CAM - Communal Addressing Map

QGIS plugin for managing Algerian municipal addressing plans. Handles streets, subdivisions, organizations, zones, numbering, and signage.

## Overview

CAM is a QGIS 3.x plugin that provides a complete workflow for creating and managing communal addressing maps for Algerian municipalities. It was originally developed for Windows and has been ported to Linux with extensive fixes and improvements.

## Features

- Draw and edit roads, subdivisions (tranches), organizations, zones, numbering, and signage layers
- Generate standardized reports (ODT format)
- User authentication and session management
- PostgreSQL/PostGIS backend with SpatiaLite fallback
- Dark/Light theme toggle (Settings tab)
- Language/locale selector (Settings tab)
- Arabic text support (with arabic_reshaper + bidi)

## Settings

Open the plugin, navigate to the **الإعدادات** (Settings) tab to:

- **Toggle theme**: Switch between داكن (Dark) and فاتح (Light) themes.
- **Change language**: Select العربية, Français, or English. Requires QGIS restart.

Themes are applied immediately. Language change requires restarting QGIS.

## Installation

### Prerequisites

- QGIS 3.x (tested on 3.44.9)
- Python 3.x with packages: `sqlalchemy`, `geoalchemy2`, `py3o.template`, `arabic_reshaper`, `python-bidi`, `shapely`, `psycopg2`
- SpatiaLite (`mod_spatialite.so` / `mod_spatialite.dll`)

### Linux

```bash
# Copy plugin to QGIS profile
cp -r CAM ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
# Or use the new-style profile path
cp -r CAM ~/.local/share/profiles/default/python/plugins/
```

Then enable the plugin in QGIS: Plugins → Manage and Install Plugins → Installed → CAM.

### Windows

Copy the plugin folder to `%APPDATA%/QGIS/QGIS3/profiles/default/python/plugins/`.

## Porting History: Windows → Linux

This plugin was originally developed on Windows and required significant changes to run on Linux. Below is a categorized summary of all fixes applied.

### P0 — Critical (crashes / data loss)

| Issue | Fix |
|-------|-----|
| **Backslash paths** — 5 locations used hardcoded `\` separators | Replaced with `os.path.join()` |
| **SQL injection** — 5 DB functions used f-string interpolation | Switched to parameterized queries |
| **SpatiaLite not found on Linux** — Hardcoded Windows DLL name + paths | `find_mod_spatialite_dll()` now searches: env var → `/usr/lib/spatialite` → `/usr/lib/spatialite50/` → `ldconfig -p` → `mod_spatialite.so` fallback |
| **Qgis enum missing** — `from qgis.core import Qgis` not imported | Added explicit import in `core.py` |
| **QGIS_BASE_PATH None** — `TypeError` when env var not set | Default to `/usr` |
| **Locale crash** — `QSettings.value()` returning `None` subscripted with `[0:2]` | Added `None` guard before slicing |
| **Export crash** — Called nonexistent `from_wkb()` | Replaced with `to_shape()` |
| **marshmallow 4.x incompatibility** — `@validates` method signature too strict | Added `**kwargs` to `validate_username()` |

### P1 — Correctness & Maintainability

| Issue | Fix |
|-------|-----|
| **Duplicate functions** — 3 identical pairs (`add_type_voie/zone/city`) | Removed one copy of each |
| **Duplicate functions** — 2 identical `get_user_location` variants | Merged into one |
| **Session pool exhaustion** — 12 query functions created engines/sessions without closing | Cached engine globally; cached sessionmaker; added `session.close()` to all query functions |
| **Wildcard imports** (`from .module import *`) | All modules use explicit imports |
| **Function name typo** — `sauvegarderModifications` | Normalized to `sauvegarder_modifications` |
| **Import name error** — `CAMResourcesTest` in test file | Fixed to `CAMDialogTest` |

### P2 — Code Quality

| Issue | Fix |
|-------|-----|
| **Duplicated QSS** — 36 inline style blocks repeated across methods | Extracted to `DARK_QSS` / `DARK_QSS_DIALOG` constants |
| **Bloated `core.py`** — 12 pure DB functions mixed with QGIS code | Extracted to `db_ops.py` |
| **Missing type hints** — No type annotations | Added to all functions in `db_ops.py`, `models.py`, and major `core.py` functions |
| **Dead code** — Commented-out `run()` method; unused import `plot_data` | Removed |
| **Unused imports** — `qgis.utils.iface`, duplicate `import jwt`, `from_wkb` | Cleaned |
| **Makefile hardcoded** — Windows-only QGISDIR | Added OS auto-detection |
| **Missing `run-env-linux.sh`** | Created for Linux QGIS environment setup |
| **Cross-platform subprocess** — Windows-specific `creationflags` | Wrapped in `os.name == 'nt'` guard |

### P3 — UI / Behavior

| Issue | Fix |
|-------|-----|
| **Right-click cancels drawing** — `customContextMenuRequested` signal fired during Add Feature tool digitizing, calling `stop()` which disrupted geometry creation | Draw handlers disconnect `on_edition_release` from `customContextMenuRequested` before activating Add Feature tool; reconnected via `_reconnect_context_menu()` on feature added or tool changed (Escape cancel) |
| **`on_edition_release` called `commitChanges()`** — Interfered with Add Feature tool's own editing cycle | Removed `layer.commitChanges()` from `stop()` |
| **Duplicate signal connections** — `featureAdded` could accumulate multiple connections after cancelled draws | Draw handlers now `disconnect()` before `connect()` |

## Running Tests

```bash
cd CAM
python3 -m pytest test/ -v
```

## Project Structure

```
CAM/
├── __init__.py                  # Plugin loader (classFactory)
├── constants.py                 # Theme/locale constants
├── resources.py / resources.qrc # Compiled Qt resources
├── metadata.txt                 # QGIS plugin metadata
├── Makefile / pb_tool.cfg       # Build/deploy automation
├── requirements.txt             # Python dependencies
├── SECURITY.md / TODO.md        # Docs
│
├── app/                         # Application logic (no QGIS coupling)
│   ├── main.py                  # CAM plugin class (entry point)
│   ├── core/
│   │   ├── base.py              # SQLAlchemy declarative Base
│   │   ├── config.py            # Theme QSS + mod_spatialite discovery
│   │   ├── database.py          # Engine/session ConnectionPool singleton
│   │   ├── migration.py         # DB migrations
│   │   ├── security.py          # bcrypt password hashing
│   │   └── _schema_migrations.py# Schema upgrade helpers
│   ├── orders/
│   │   ├── repository.py        # add_*/list queries for feature layers
│   │   └── models/              # SQLAlchemy ORM models (road, zone, ...)
│   ├── users/
│   │   ├── service.py           # sign_up, sign_in, logout, JWT
│   │   ├── repository.py        # User/cookie persistence
│   │   ├── models.py            # SQLAlchemy User model
│   │   └── schemas.py           # Marshmallow validation schemas
│   └── shared/
│       ├── constants.py         # App-wide constants
│       ├── exceptions.py        # Custom exceptions
│       ├── geo.py               # Geometry helpers
│       └── utils.py             # Locale + misc utilities
│
├── gui/                         # Qt Widgets UI
│   ├── main_dialog.py           # Main dialog (composes the mixins below)
│   ├── popup_dialog.py          # Feature attribute editor
│   ├── popup_handlers.py        # Popup save/edit logic
│   ├── entity_list_dialog.py    # Paginated entity list
│   ├── dialog_state.py          # Shared theme/locale/action state
│   ├── dialog_helpers.py        # Shared widget helpers
│   ├── form_specs.py            # Form field definitions
│   ├── identify_tool.py         # Map identify tool
│   ├── measure_tool.py          # Distance measurement tool
│   ├── ui_fillers.py            # ComboBox population functions
│   ├── pages/                   # Main dialog pages (login, add_user, main, settings)
│   └── popup_pages/             # Per-layer popup editors (road, zone, ...)
│
├── mixins/                      # MainDialog mixin classes
│   ├── auth_mixin.py            # Authentication UI
│   ├── backup_mixin.py          # DB backup/restore
│   ├── chart_mixin.py           # Chart generation
│   ├── import_export_mixin.py   # Map export
│   ├── layer_draw_mixin.py      # Drawing mode activation
│   ├── layer_edit_mixin.py      # Feature editing
│   ├── layer_ops_mixin.py       # Tab/layer management
│   ├── map_tools_mixin.py       # Map tool switching
│   ├── report_mixin.py          # Report generation
│   ├── symbol_export_mixin.py   # Symbol style export
│   └── _protocols.py            # Shared protocol definitions
│
├── layer/                       # Layer utilities
│   ├── editing.py               # start/stop editing, save
│   ├── refresh.py               # Layer refresh, style apply
│   └── utils.py                 # Layer creation helpers
│
├── scripts/                     # Standalone scripts
│   ├── widget_texts.py          # i18n string lookup
│   ├── lookup_data.py           # Lookup tables & i18n (active)
│   ├── migrate_db.py            # DB migration helper
│   ├── reporting.py             # Report generation helper
│   └── plugin_upload.py         # Plugin upload helper
│
├── resources/                   # Static assets (icons, QSS templates, fonts)
├── templates/                   # ODT report templates (cmd/rep/map_a0/map_a3)
├── data/                        # Runtime data
│   ├── database.sqlite          # Spatial database
│   ├── cookie.toml              # Session cookie
│   ├── qgis_config.json         # App configuration
│   └── Views.sql                # SQL view definitions
│
├── test/                        # Unit tests (mocked, no QGIS required)
├── i18n/ icons/ style/ help/ template_data/
└── README.md
```

## License

GPL v3 — See header comments in source files.
