# RNA - Plans d'Adressage

QGIS plugin for managing Algerian municipal addressing plans. Handles streets, subdivisions, organizations, zones, numbering, and signage.

## Overview

RNA is a QGIS 3.x plugin that provides a complete workflow for creating and managing addressing plans (Plans d'Adressage) for Algerian municipalities. It was originally developed for Windows and has been ported to Linux with extensive fixes and improvements.

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
cp -r plans_adressage ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/
# Or use the new-style profile path
cp -r plans_adressage ~/.local/share/profiles/default/python/plugins/
```

Then enable the plugin in QGIS: Plugins → Manage and Install Plugins → Installed → RNA.

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
| **Import name error** — `RNAResourcesTest` in test file | Fixed to `RNADialogTest` |
| **`reporting.py` runs arg parser on import** — Code ran at module level | Moved inside `if __name__ == '__main__':` |

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
cd plans_adressage
python3 -m pytest test/test_db_ops.py -v
```

## Project Structure

```
plans_adressage/
├── RNA.py                       # Plugin entry point
├── RNA_dialog.py                # Main dialog (inherits mixins)
├── __init__.py                  # Plugin loader (classFactory)
├── constants.py                 # App-wide constants & utilities
├── resources.py / resources.qrc # Compiled Qt resources
├── metadata.txt                 # QGIS plugin metadata
├── Makefile / pb_tool.cfg       # Build/deploy automation
├── requirements.txt             # Python dependencies
├── SECURITY.md / TODO.md        # Docs
│
├── auth/                        # Authentication package
│   ├── operations.py            # sign_up, sign_in, logout, JWT
│   └── decorators.py            # login_required decorator
│
├── db/                          # Database operations package
│   ├── operations.py            # Queries, config, password hashing
│   ├── schema.py                # Marshmallow validation schemas
│   └── writers.py               # add_* functions for all layers
│
├── models/                      # SQLAlchemy ORM models
│   ├── base.py                  # Engine, session, Base
│   ├── user.py                  # User model
│   ├── lookup.py                # Lookup tables
│   └── spatial.py               # Spatial models (Road, Zone, etc.)
│
├── gui/                         # GUI components & UI definitions
│   ├── RNA_dialog_base.ui       # Main dialog UI (Qt Designer)
│   ├── PopupDialog.ui           # Popup editor UI
│   ├── liste.ui                 # Entity list UI
│   ├── popup_dialog.py          # Feature attribute editor
│   ├── entity_list_dialog.py    # Paginated entity list browser
│   ├── identify_tool.py         # Map identify tool
│   ├── measure_tool.py          # Distance measurement tool
│   └── ui_fillers.py            # ComboBox population functions
│
├── mixins/                      # RNADialog mixin classes
│   ├── auth_mixin.py            # Authentication UI
│   ├── backup_mixin.py          # DB backup/restore
│   ├── chart_mixin.py           # Chart generation
│   ├── import_export_mixin.py   # Map export, reporting
│   ├── layer_draw_mixin.py      # Drawing mode activation
│   ├── layer_edit_mixin.py      # Feature editing
│   ├── layer_ops_mixin.py       # Tab/layer management
│   ├── map_tools_mixin.py       # Map tool switching
│   ├── report_mixin.py          # Report generation
│   └── symbol_export_mixin.py   # Symbol style export
│
├── layer/                       # Layer utilities
│   ├── editing.py               # start/stop editing, save
│   ├── refresh.py               # Layer refresh, style apply
│   └── utils.py                 # Layer creation helpers
│
├── scripts/                     # Standalone scripts
│   ├── create_db.py             # Database creation
│   ├── reporting.py             # ODT report generation (subprocess)
│   ├── plugin_upload.py         # Plugin upload helper
│   ├── migrate_old_db.py        # Legacy DB migration
│   └── migrate_split_db.py      # Auth DB split migration
│
├── resources/                   # Static assets
│   ├── icon.png / map.png / situation.png
│   ├── chart.svg / north_arrow.svg / scale_bar.svg / symbols.svg
│   └── DejaVuSans.ttf
│
├── templates/                   # ODT report templates
│   ├── cmd.odt / rep.odt
│   └── map_a0.odt / map_a3.odt
│
├── data/                        # Runtime data
│   ├── database.sqlite          # Spatial database
│   ├── auth.sqlite              # Auth database
│   ├── qgis_config.json / cookie.toml / tmp.json
│   └── Views.sql
│
├── test/                        # Unit tests
│   ├── test_db_ops.py
│   ├── test_init.py
│   └── ...
├── i18n/ icons/ style/ help/ template_data/
└── README.md
```

## License

GPL v2 — See header comments in source files.
