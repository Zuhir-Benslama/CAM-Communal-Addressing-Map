# RNA Plugin — Code Quality & Bug Fix Tracking

## Priority Legend
- **P0**: Critical (will crash or corrupt data)
- **P1**: High (major functionality or correctness)
- **P2**: Medium (code quality, maintainability)
- **P3**: Low (nice to have)

---

## 1. Cross-Platform Paths (P0) ✅

- [x] Replace ALL Windows backslash paths (`\`) with `os.path.join()` or forward slashes
- [x] Audit every file for hardcoded Windows paths
- [x] **Still needed**: Verify `MOD_SPATIALITE_DLL` env var resolution works on Linux (mod_spatialite.so)

## 2. SQL Injection & Query Security (P0) ✅

- [x] Rewrite `nbr_num()`, `nbr_pan()`, `query_missing_pan()`, `query_missing_num()`, `query_missing_rep()` to use parameterized queries
- [x] Replace `text()` with parameterized `text("...", params={})`

## 3. Duplicate Code (P1) ✅

- [x] Remove duplicate `add_type_voie`, `add_type_zone`, `add_type_city` functions
- [x] Verify all callers reference the first (kept) instance

## 4. Session / Connection Management (P1) ✅

- [x] Cache the SQLAlchemy engine (avoid recreating on every `get_session()` call)
- [x] Fix SpatiaLite double `load_extension` in connect event
- [x] **Still needed**: Add session context manager for automatic closing
- [x] **Still needed**: Audit all functions that call `get_session()` without `.close()`

## 5. Imports Cleanup (P1) ✅

- [x] Replace wildcard imports in `models.py`, `schema.py`, `core.py` with explicit imports
- [x] Remove unused imports (`qgis.utils.iface` from core.py)
- [x] Clean up RNA_dialog.py imports (from `from .core import *` to explicit)

## 6. SpatiaLite on Linux (P1) ✅

- [x] Merge double `connect` event listeners into one
- [x] Remove redundant `from geoalchemy2 import load_spatialite` and `from geoalchemy2 import shape`
- [x] `find_mod_spatialite_dll()` now provides sensible defaults per OS (.so/.dll/.dylib)
- [x] Added try/except fallback in `connect_spatialite` (load_extension API vs SQL)
- [x] **Still needed**: Test on actual Linux QGIS installation

## 7. Model & Geometry Fixes (P1) ✅

- [x] Fix `export_model()` — was using `shape.from_wkb()` incorrectly, now uses `to_shape()`
- [x] Audit `ST_Within` argument order in all models — all correct

## 8. Error Handling (P2) ✅

- [x] Fix `print(f"An error occurred: ")` with missing variable
- [x] `nbr_num()` and `nbr_pan()` now handle empty results (return 0)

## 9. Code Quality (P2) ✅

- [x] Remove dead code (commented-out `run()` method in `RNA.py`)
- [x] Clean up imports (deduplicate, consolidate)
- [x] Extract dark theme QSS blocks (`DARK_QSS`, `DARK_QSS_DIALOG` constants)
- [x] DRY: merge `get_user_location()` / `get_user_location_2()` via `_get_authenticated_user()`
- [x] Fix `get_current_user()` — close session after use
- [x] **Extract `db_ops.py`** — 12 pure DB functions moved out of `core.py`:
  - Auth: `create_cookie`, `hash_password`, `verify_password`, `_get_authenticated_user`, `get_user_location`, `get_user_location_2`
  - Config: `qgis_config`
  - Queries: `nbr_num`, `nbr_pan`, `query_missing_pan`, `query_missing_num`, `query_missing_rep`
  - Export: `export_model`
- [x] Type hints added to all `db_ops.py` function signatures
- [x] **Still needed**: Add type hints to remaining functions in `core.py`, `models.py`
- [x] **Still needed**: Consistent naming: `snake_case` for functions

## 10. QGIS Plugin Deployment ✅

- [x] Update `Makefile` for Linux paths (QGISDIR auto-detection, pyrcc5 fallback)
- [x] Update `metadata.txt` with proper description
- [x] Create `run-env-linux.sh` script

## 11. Windows-Specific Fixes (P1) ✅

- [x] Replace `subprocess.CREATE_NO_WINDOW` with cross-platform `_SUBPROCESS_FLAGS`
- [x] Replace `PYTHON_QGIS_BAT` with `_get_qgis_python()` (cross-platform fallback)

## 12. Testing

- [x] Verify existing `test/` directory contents and make tests runnable
- [x] Ensure `make test` works on Linux
- [x] Test database creation: `create_db.py` — works on Linux SQLite/SpatiaLite

## 13. Reporting & External Tools

- [x] Document LibreOffice headless (`SOFFICE_EXE`) requirement for PDF conversion
- [x] Verify `py3o.template` paths for ODT templates on Linux
- [x] Test chart generation (matplotlib Arabic text rendering) on Linux

---

## 14. Critical Bugs — P0 ✅

- [x] **Fix JWT authentication** — `core.py:176` uses `secrets.token_hex(16)` as HMAC key on every call but never stores it, making all issued tokens permanently unverifiable. Auth system is entirely non-functional. Fix: use a fixed secret from config/env.
- [x] **Fix non-existent attribute writes on `Numerotation`** — `models.py:623-625` sets `instance.idLoc` and `instance.parent` on `Numerotation`, which has neither column. `models.py:654` sets `self.parent`. Data is silently discarded. Fix: remove assignments or add columns.
- [x] **Fix non-existent attribute write on `RefOrg`** — `models.py:536` sets `instance.parent` but `RefOrg` has `pkuid_poly`, not `parent`. Fix: use `pkuid_poly`.
- [x] **Close all leaked DB sessions** — ~25 `get_session()` calls without `.close()` across `core.py`, `models.py`, `RNA_dialog.py`, `schema.py`, `ListeELT.py`, `decorator.py`. Fix: audit every call, add `session.close()` or use context manager.
- [x] **Fix QGIS thread-safety violations** — `core.py:885-950` uses `ThreadPoolExecutor` to call `boot()`, `cat()`, `uncat()` which manipulate `QgsProject`/`QgsVectorLayer` off the main thread. Fix: run layer operations on main thread.
- [x] **Fix wrong widget assignment** — `PopupDialog.py:129` calls `self.type_org.setCurrentIndex(index)` in the `'التجزئات'` branch; should be `self.type_city`.

## 15. Major Issues — P1 ✅

- [x] **Stop shadowing `dict` built-in** — 12 occurrences in `models.py` use `dict` as variable name. Fix: rename to `data`, `params`, `payload`.
- [x] **Don't overwrite `session` parameter** — `models.py:279,369,457,649` silently discard the caller-provided `session` with `get_session()`, breaking transactional scope.
- [x] **Replace bare `except Exception:` with targeted handling** — ~20+ bare excepts across all files swallow errors silently. Fix: log the error, use specific exception types.
- [x] **Validate `setattr` keys in `update()`** — `models.py:240-241` and all `update()` methods allow setting arbitrary attributes (including `api_key`, `password`) via unvalidated `**kwargs`. Fix: whitelist allowed column names.
- [x] **Guard `mapLayersByName(name)[0]`** — `core.py:460,502,781,846,878` crash with `IndexError` if layer not found. Fix: check list length first.
- [x] **Close leaked session in `schema.py`** — `schema.py:43` calls `get_session()` without closing on every username validation. Fix: add `session.close()` in `finally`.
- [x] **Fix `globals().get(model_name)` fragility** — `db_ops.py:88` and `ListeELT.py:31` return `None` if model not imported in module globals, causing downstream `AttributeError`. Fix: use `models` module attribute lookup.
- [x] **Fix duplicate signal connections** — `RNA_dialog.py:768,774,781,787,793,799` connect `layer.geometryChanged` without ever disconnecting. Fix: disconnect before reconnecting.
- [x] **Fix `DetachedInstanceError` risk** — `db_ops.py:74` accesses `result.geometry` after `session.close()`. Fix: inline the WKT query before closing.
- [x] **Fix injectable QGIS expression** — `QgsMapTool.py:108` uses f-string in `setFilterExpression`. Fix: use parameterized `QgsExpression`.
- [x] **Remove duplicate `startEditing()` call** — `core.py:392-395` calls `startEditing()` twice on the same layer.
- [x] **Move `commitChanges()` outside feature loop** — `core.py:817-839` starts editing and commits for every single feature. Fix: start once, add all features, commit once.
- [x] **Remove dead `else` branch** — `schema.py:47` `else: raise ValidationError(...)` is unreachable.
- [x] **Remove duplicate imports** — `PopupDialog.py:16-26` is an exact duplicate of lines 5-15.
- [x] **Add DB restore validation** — `RNA_dialog.py:1052-1071` copies arbitrary `.sqlite` files over `database.sqlite` with zero validation. Fix: verify file header/SQLite magic bytes.

## 16. Code Quality — P2 ✅

- [x] **Fix line length violations** (~50+ lines over 100 chars)
- [x] **Add type hints** to ~80+ functions missing them (`RNA_dialog.py`, `RNA.py`, `core.py`, `QgsMapTool.py`, etc.)
- [x] **Add docstrings** to all functions (~95% missing)
- [x] **Remove ~30+ unused imports** across all files (matplotlib, shapely, json, etc.)
- [x] **Remove `get_user_location_2()`** — dead code in `db_ops.py`
- [x] **Remove unused matplotlib imports** in `core.py:8,12,13` (`plt`, `rcParams`, `MaxNLocator`)
- [x] **Extract hardcoded constants** — SRID 4326 (7×), layer names (بلديتي), file paths, colors, durations
- [x] **Replace wildcard imports** in `PopupDialog.py`, `ListeELT.py`, `QgsMapTool.py`, `decorator.py` with explicit imports (QgsMapTool2.py merged into QgsMapTool.py)
- [x] **Remove implicit `from shapely import *`** in `decorator.py:6`
- [x] **Make `export_model` model lookup safe** — `db_ops.py:88` should use `models` module reference
- [x] **Replace `print()` with proper logging** throughout the codebase
- [x] **Move `echo=True` to config** — `models.py:758` hardcodes SQL logging in production
- [x] **Remove redundant `f` string** — `reporting.py:41` `f'north_arrow.svg'` needs no interpolation
- [x] **Remove `os.makedirs("./", exist_ok=True)`** — `reporting.py:57,110` the CWD always exists
- [x] **Fix `_2` suffixed function names** — `core.py` functions with `_2` suffix should have descriptive names
- [x] **Rename cryptic functions** — `boot`, `cat`, `uncat`, `add_num`, `add_org`
- [x] **Remove commented-out dead code** — `ListeELT.py:64-103`
- [x] **Add pagination to `ListeELT.populate_table()`** — loads all records into memory
- [x] **Fix `qgis_config()` — no error handling** for `FileNotFoundError` or `json.JSONDecodeError`
- [x] **Fix `create_cookie()` — no error handling** for file write failures

## 17. Minor Issues — P3 ✅

- [x] **Remove `# -*- coding: utf-8 -*-`** — unnecessary in Python 3
- [x] **Replace `from sqlalchemy.ext.declarative import declarative_base`** — deprecated in SQLAlchemy 2.0, use `from sqlalchemy.orm import declarative_base`
- [x] **Replace `raise EnvironmentError`** — `reporting.py:48,101` deprecated since Python 3.4, use `OSError`
- [x] **Move `import argparse`** inside `if __name__ == '__main__'` guard in `reporting.py`
- [x] **Remove module-level imports inside methods** — `RNA_dialog.py:1290,1835-1837,1911-1913`
- [x] **Remove duplicate `import json` and `import os`** in `RNA_dialog.py`
- [x] **Remove unused `Date`, `DateTime`, `SmallInteger`, `UniqueConstraint` imports** in `models.py:6`
- [x] **Remove unused `from sqlalchemy.orm import class_mapper`** in `models.py:788`
- [x] **Remove unused `QSettings`, `QPointF`** in `RNA_dialog.py:27`
- [x] **Remove unused `from PyQt5.uic.properties import *`** in `RNA_dialog.py:30`
- [x] **Remove unused `import re`** in `RNA_dialog.py:35`
- [x] **Remove unused `QShortcut`, `QKeySequence`** in `RNA_dialog.py:49-50`
- [x] **Remove unused `QgsRasterLayer` from core.py imports**
- [x] **Remove unused `secrets` import** in `db_ops.py`
- [x] **Remove unused `from geoalchemy2.elements import WKTElement`** in `db_ops.py`

## 18. Security — Resolved ✅

- [x] **Fix non-functional JWT auth** — secret key is ephemeral and never stored, making verification impossible (`core.py:176`)
- [x] **Hash JWT tokens before storage** — `core.py:176` stores raw JWT token as `current_user.api_key`. Fix: hash before storing.
- [x] **Encrypt cookie.toml on disk** — session cookies (`api_key`, `uid`) stored in plaintext TOML file with no encryption. World-readable on Linux.
- [x] **Add DB restore validation** — `RNA_dialog.py:1052-1071` copies arbitrary `.sqlite` files over `database.sqlite`. Fix: verify SQLite magic bytes.
- [x] **Whitelist settable attributes in `update()`** — `models.py` all `update()` methods allow setting `api_key`, `password`, etc. via unvalidated `**kwargs`. Fix: column whitelist.
- [x] **Fix injectable QGIS expression** — `QgsMapTool.py:108` uses f-string for filter expression. Fix: use `QgsExpression` with bound values.
- [x] **Validate env var inputs** — `PYTHON_QGIS_BAT` and `SOFFICE_EXE` read from env vars and passed to `subprocess.run` without validation.
- [x] **Remove or guard `echo=True`** — `models.py:758` hardcodes SQL logging, leaking query data in production.
- [x] **Add input validation** — no validation on user text fields (`nom_voie`, `nom_org`, etc.) throughout `RNA_dialog.py`
- [x] **Add file permission checks** — `core.py:224,228` reads/writes `cookie.toml` without checking file permissions.
- [x] **Replace `print()` with logger** — `core.py:191,358,385,538,567,900,930,950` may leak sensitive info via stdout.
- [x] **Add permission check on `cookie.toml`** — readable by any process on the system. Fix: set 0600 permissions.

---

## 19. Future Work

*(All completed — see sections 20–25)*

## 20. Post-Refactoring Bug Fixes — 2026-05-14 ✅

- [x] **Fix `test/test_db_ops.py:90` indentation error** — `create_cookie()` call was not indented under `with` block, causing `IndentationError` on test collection
- [x] **Fix `db/operations.py` incomplete fallback imports** — `except ImportError` block imported `User`, `Localite`, `get_session` but omitted `COOKIE_FILE` and `QGIS_CONFIG_FILE`, causing `AttributeError` when running outside the `plans_adressage` package context. Added `from constants import COOKIE_FILE, QGIS_CONFIG_FILE` to fallback.
- [x] **Fix test pollution in `TestGetAuthenticatedUser`** — missing `setUp()` with `_clean_tmpdir()` meant cookie file from `test_create_cookie_writes_file` persisted, causing `test_no_cookie_file_returns_none` to find a stale file and proceed to DB query instead of returning `None`.
- [x] **Clean duplicate imports in `test/test_db_ops.py`** — `import os`, `import json`, `import sys` appeared twice (lines 1-3 and 8-10).
- [x] **All 12 tests pass** — `test/test_db_ops.py`: 12/12 passed after fixes.

## 21. Initial Future Improvements — P2/P3 ✅

- [x] **Replace empty `ValueError('')` with descriptive messages** — `models/spatial.py` methods (`Zone.update`, `Road.update`, etc.) raise `ValueError('')` — replaced with descriptive messages
- [x] **Fix candidate path typo in `find_mod_spatialite_dll()`** — `/usr/libspatialite50/` → `/usr/lib/spatialite50/`
- [x] **Add CI configuration** — created `.github/workflows/ci.yml` (Python 3.10–3.12, Linux)
- [x] **Pin dependency versions in `requirements.txt`** — confirmed already pinned (no change needed)
- [x] **DRY up cookie reading logic** — `_get_authenticated_user()` now delegates to `get_current_user()`

## 22. Post-Refactoring Code Quality — 2026-05-14 ✅

- [x] **Add module/class/function docstrings** — ~250+ docstrings added across all source files (models, mixins, db, gui, layer, auth, core)
- [x] **Fix import ordering in `models/base.py`** — moved `from sqlalchemy import inspect` to module level; removed duplicate inline import
- [x] **Convert `.format()` to f-strings** — 13 instances in `plugin_upload.py`, `RNA.py`
- [x] **Remove superfluous parentheses** — 41 instances across `create_db.py`, `db/schema.py`, `gui/popup_dialog.py`
- [x] **Add explicit encoding to `open()` calls** — 15 `unspecified-encoding` fixes across `create_db.py`, `auth/operations.py`, `auth/decorators.py`, `layer/utils.py`, `db/operations.py`, `models/base.py`
- [x] **Fix no-else-return** — 6 instances removed across `mixins/auth_mixin.py`, `mixins/symbol_export_mixin.py`, `mixins/layer_edit_mixin.py`
- [x] **Fix singleton comparison** — 2 instances (`== True` → `is True`) in `RNA.py`, `layer/utils.py`
- [x] **Remove redundant `u''` prefix** — 3 instances in `RNA.py`
- [x] **Fix dangerous mutable default arg** — `fill_org_category(combobox, cat=[])` → `cat=None` with `cat = cat or []`
- [x] **Remove pointless statement** — `model_class.__table__.columns` (no-op) in `layer/utils.py`
- [x] **Fix remaining line length violations** — 226 violations reduced to 2 (both in auto-generated `resources.py`)
- [x] **Fix indentation bug from no-else-return auto-fix** — `mixins/layer_edit_mixin.py:175` had broken indentation after automated edit
- [x] **Fix chart_mixin.py corruption** — restored missing chart generation body in `carte_pano1()` and added local imports to `get_zone_chart()` after automated line-wrapping broke the file
- [x] **Fix remaining unused imports** — `Numbering` from `mixins/chart_mixin.py`
- [x] **Remove unused `Numbering` import** — `mixins/chart_mixin.py`
- [x] **Final quality scores: Pylint 7.68/10** (from 5.56), **Pyflakes 0 errors**, **12/12 tests pass**

## 23. Performance Fixes — Layer Refresh & Writer Bottlenecks ✅

- [x] **`refresh_all_layers()` no longer called on every add** — previously every `add_numbering()`, `add_road()`, etc. called `refresh_all_layers()` which deleted all features from all 6 layers and re-queried every DB record (O(n²) growth). Now uses `add_feature_to_layer()` which inserts a single QgsFeature into the specific changed layer only — O(1) per add.
- [x] **`list(layer.getFeatures())[-1]` eliminated** — All 6 `add_*()` functions in `db/writers.py` called `list(layer.getFeatures())` to get the last drawn feature's geometry, loading ALL features into memory. Now geometry is captured once at draw time in `on_feature_added()` via `self._last_feature_wkt` and passed directly.
- [x] **N+1 geometry queries fixed in `refresh_layer_from_db()`** — Each feature previously required a separate `SELECT ST_AsText(geometry)` query. Now geometry WKT is eagerly loaded in the main query (`SELECT model.*, ST_AsText(geom)`), reducing N+1 queries to 1.
- [x] **`db/writers.py` signatures changed** — all 6 `add_*()` functions now accept `geometry_wkt: str` instead of `iface`, and return the saved model instance. Updated all callers in `mixins/layer_edit_mixin.py`.
- [x] **`add_feature_to_layer()` added to `layer/refresh.py`** — inserts a single model instance into a QGIS layer without delete/re-add. Accepts optional `geometry_wkt` to avoid DB round-trip.
- [x] **Null-check bug in `save_changes()`** — `layer.startEditing()` was called before `if not layer` guard in `layer/editing.py:56`, causing `AttributeError` on null active layer. Fixed.
- [x] **Performance characteristics**: Adding a feature is now O(1) per operation instead of O(N_total_features) — no degradation as feature count grows.
- [x] **Tests still pass**: 12/12, pyflakes 0 errors, pylint 7.67/10.

## 24. Phase 4 — Edit Session & Duplicate Feature Fix ✅

- [x] **Eliminated duplicate feature on every add** — `on_feature_added()` committed the feature to the layer (good), then `add_feature_to_layer()` added a *second copy* with a different auto-generated pkuid (bad). Now the layer feature's pkuid is captured and passed to the DB writer, so both share the same pkuid. No duplicates.
- [x] **`add_feature_to_layer()` removed from hot path** — feature is already committed to the layer by `on_feature_added()`. The DB write uses the same pkuid, so no re-adding is needed.
- [x] **`_last_feature_pkuid` stored** — alongside `_last_feature_wkt` in `on_feature_added()`; passed through all 6 `add_*()` functions to ensure DB ↔ layer pkuid consistency.
- [x] **All 6 `add_*()` writers accept `pkuid` param** — `add_numbering`, `add_road`, `add_organization`, `add_subdivision`, `add_zone`, `add_panel_sign` all pass the layer feature's pkuid to the model constructor. Falls back to auto-generated UUID if not provided.
- [x] **Tests still pass**: 12/12, pyflakes 0 errors, pylint 7.67/10.

## 25. Phase 5 — Post-Refactoring Bug Fixes 2026-05-15 ✅

### Login & Auth
- [x] **Signup silently failing** — `submit_add_usr()` always navigated to the login page even when `sign_up()` failed (ValidationError was caught internally, never re-raised). User thought signup succeeded but no user was created. Fix: `sign_up()` now returns `bool`, `submit_add_usr()` checks it before calling `public_route('login')`.
- [x] **Password mismatch after `make install`** — Password hash updated in deployed auth DB but NOT in dev auth DB. Running `make install` overwrites deployed databases with dev copies, restoring the old hash. Fix: updated password hash in all databases (dev and deployed).

### Map Features Not Appearing
- [x] **`NameError` in `init_allowed_zone()`** — When `localite` was `None` (user's affectation_id not in localite table), `wkt` was never defined but `QgsGeometry.fromWkt(wkt)` was still reached, causing `NameError`. Fix: structured the function so `localite` is always defined and `wkt` is only accessed when `localite` is truthy.
- [x] **`create_other_layers()` only called when municipality layer was first created** — If the municipality layer already existed (e.g., from a previous session or edge case), data layers (الطرق, المناطق, etc.) were never created, so no features appeared. Fix: `create_other_layers()` is now called unconditionally after `init_allowed_zone()` completes, regardless of whether the municipality layer already existed.
- [x] **Map canvas not zooming to municipality extent after login** — After successful login, the map stayed at full-world extent. Features existed in the database but were not visible at that zoom level. Fix: added `iface.mapCanvas().zoomToFeatureExtent(multipolygon.boundingBox())` after creating the municipality boundary layer.

## 26. Future Work — Unsolved

- [x] **Fix feature theming to match previous look** — `style/` dir was missing from `EXTRA_DIRS` in Makefile, so `.qml` files were never deployed. Also 4 `.qml` files had stray font changes (`MS Shell Dlg 2` → `Arial`). Reverted files and added `style` to `EXTRA_DIRS`.
- [ ] **Create migration script for old databases** — write a standalone Python script that migrates old-format `database.sqlite` (monolithic, pre-split) to the new structure (`auth.sqlite` + `database.sqlite` with split schema). Must handle existing `migrate_split_db.py` as a base and extend it for production use.
- [ ] **Minor UI fixes and improvements** — sweep of small UI issues: alignment, label truncation, missing tooltips, inconsistent button sizing, RTL layout glitches, and any visual regressions from the refactor.

## 27. Code Quality Review — 2026-05-16 ✅

### P0 — Critical ✅

- [x] **Hardcoded JWT fallback secret** — `auth/operations.py:19-21`: `JWT_SECRET` defaults to `'change-me-in-production-rna-default-secret'` when `RNA_JWT_SECRET` env var is unset. Fix: raise `RuntimeError` if env var is unset.
- [x] **`is True` singleton comparison fragility** — `models/base.py:93`, `auth/operations.py:185-186`, `auth/decorators.py:39`, `layer/utils.py:88`: `User.active is True` uses identity comparison. Fix: use `== True`.

### P1 — High ✅

- [x] **DRY: Consolidate duplicate layer draw handlers** — `mixins/layer_draw_mixin.py`: 6 nearly identical methods (`draw_road_handler`, `draw_org_handler`, `draw_pan_handler`, etc.) differ only by layer name. Extracted into a single `_draw_handler(layer_name: str) -> None`.
- [x] **DRY: Consolidate duplicate layer update methods** — `mixins/layer_edit_mixin.py`: 6 nearly identical methods (`update_road`, `update_organization`, `update_city`, etc.) differ only by layer name. Extracted into a single `_update_handler(layer_name: str) -> None`.
- [x] **DRY: Consolidate duplicate selection activators** — `mixins/map_tools_mixin.py`: 6 nearly identical methods (`set_zone_selection`, `set_pan_selection`, `set_num_selection`, etc.) differ only by layer name. Extracted into a single `_selection_handler(layer=None)`.
- [x] **DRY: Consolidate duplicate `save()` methods in lookup models** — `models/lookup.py`: 8 model classes with identical `save()`. Extracted `_BaseLookup` base class.
- [x] **DRY: Consolidate duplicate `edit_line_layer` and `start_editing_layer`** — `layer/editing.py`: extracted `_activate_add_feature(iface, layer)` shared helper.
- [x] **`on_feature_added` parameter naming** — `mixins/layer_ops_mixin.py:161`: parameter renamed from `feature` to `fid`.
- [x] **`on_geometry_changed` uses `if` instead of `elif`** — `mixins/layer_ops_mixin.py:238-247`: changed `if` to `elif` for geometry type checks.
- [x] **Undefined `layer2` risk in `map_situation()`** — `mixins/symbol_export_mixin.py:133-137`: added `layer2 = None` initializer and `elif` to ensure at most one assignment, with early return guard.
- [x] **Inefficient layer refresh** — `layer/refresh.py:57-60`: merged delete, add-fields, and add-features into a single edit session (one `startEditing()` / one `commitChanges()`).
- [x] **Bare `except: pass`** — `mixins/import_export_mixin.py:161`: replaced with `logger.exception(...)`.

### P2 — Medium ✅

- [x] **Inconsistent Qt imports** — `RNA.py`: merged `PyQt5` imports into `qgis.PyQt`.
- [x] **Duplicate chart generation code** — `mixins/chart_mixin.py`: extracted `_render_bar_chart()` and `_toggle_layer_visibility()` shared helpers.
- [x] **Magic number in map export** — `mixins/import_export_mixin.py`: replaced `QSize(2200, 2200)` with `EXPORT_MAP_SIZE` constant.
- [x] **`qgis_config()` called repeatedly** — `db/operations.py`: added `_qgis_config_cache` module-level cache with global flag.
- [x] **Line length violations** — fixed 16 remaining E501 violations across 7 source files. Now zero violations on `pycodestyle --max-line-length=80 --select=E501`.
- [x] **Add tests for DB ops and writers** — added `test/test_writers.py` (11 tests) and `test/test_operations.py` (8 tests). 30/30 tests pass.
- [x] **Global mutable module state** — `models/base.py`: added `reset_connection_pool()` for test isolation.

### P2 — Medium (still open)

- [x] **`try/except ImportError` fallback pattern** — Used in 6 modules for QGIS plugin test compatibility. This is an accepted QGIS plugin pattern: relative imports work when loaded by QGIS (as `plans_adressage.models`), while absolute fallbacks work when modules are imported standalone for testing. **Intentionally kept** for dual-mode compatibility.
- [x] **Auth flow tests** — added `test/test_auth.py`: 9 tests covering sign_up (success, validation error), sign_in (success, unknown user, wrong password, validation error, exception rollback), logout (with cookie, without cookie, missing session key). 40/40 tests pass.
- [x] **Global mutable module state** — `models/base.py:114-117`: `_engine`, `_Session`, `_auth_engine`, `_AuthSession` are module-level globals. Added `reset_connection_pool()` for test isolation.

### P3 — Low

- [x] **Consider `dataclass` for lookup models** — `models/lookup.py`: 8 simple lookup models with identical structure. Already consolidated via `_BaseLookup` abstract base with `save()` in P1. Further `dataclass` conversion is a low-value refactor at this point.
- [x] **`num_decision` naming consistency** — `models/spatial.py:78`: column is named `num_decision` (French "numéro de décision"). All internal references are consistent. Rename would touch SQL column, queries, and UI labels — not worth the churn for a bilingual codebase.
- [x] **Add context manager for DB sessions** — added `session_scope()` and `auth_session_scope()` context managers in `models/base.py:120-143`. Usage: `with session_scope() as session:`.

## 28. Internationalization (i18n) — 🔴 UNFINISHED

### Done
- [x] **Translation caching rewritten** — replaced Python dicts keyed by `objectName` with Qt dynamic properties (`setProperty("_rna_src", ...)`) stored directly on widgets. `_cache_originals()` is additive; `_apply_translations()` iterates `findChildren` directly.
- [x] **Root cause of whitespace mismatch fixed** — `.ui` label text has leading space (`" : اسم المستخدم"`) but `.ts` sources had none. `gen_translations.py` now uses exact `.ui` strings.
- [x] **All frames set to NoFrame** — all 38 QFrames across `RNA_dialog_base.ui`, `liste.ui`, `PopupDialog.ui` changed to `NoFrame` via Python XML script.
- [x] **Fully translated dialogs**: `EntityListDialog`, `PopupDialog`, `RNADialog.setup_settings_ui()`
- [x] **Database seed data translated** — `gui/ui_fillers.py` all `fill_*` functions translate combo items via `_locale()` + `_i18n_tr()`.
- [x] **`_on_locale_changed` re-populates combos** — re-calls `fill_road_type`, `fill_zone_type`, etc. on locale switch.
- [x] **44 seed data translations added** — road types, zone types, subdivision types, mounting statuses, numbering states.
- [x] **Code-generated strings translated** — `db/writers.py`, `popup_dialog.py`, all mixins (`layer_edit_mixin`, `map_tools_mixin`, `auth_mixin`, `backup_mixin`, `import_export_mixin`, `report_mixin`, `chart_mixin`, `symbol_export_mixin`) wrap Arabic strings via `self._tr()` or `_i18n_tr()`.
- [x] **286 entries in `.ts` files** — generated by `scripts/gen_translations.py`, covers `.ui` strings + code strings + seed data.
- [x] **`style/` directory added to `EXTRA_DIRS`** — Makefile and pb_tool.cfg now deploy `.qml` style files.
- [x] **QTabWidget translation removed** — tab texts double as QGIS layer name identifiers; translating them breaks `on_opt_selected()` layer lookups.

### Remaining
- [ ] **Verify all `.ts` translations are correct** — Arabic→English and Arabic→French translations for all 286 entries need human review. Some may have incorrect/placeholder translations.
- [ ] **Complete `_on_locale_changed` signal robustness** — `QComboBox.currentIndexChanged` has overloaded signals; verify the `*args` + `currentData()` approach works across all Qt/PyQt5 versions (currently handles 1-arg and 2-arg signal variants).
- [ ] **Ensure `_cache_originals()` captures all dynamic widgets** — any widget created after `setupUi()` must be created before the second `_cache_originals()` call (line 252). Verify no widgets slip through.
- [ ] **Test locale switch on every dialog/message** — verify all translated strings switch correctly (labels, buttons, tooltips, combo items, message boxes) without partial translation artifacts.
- [ ] **Handle RTL layout on locale change** — when switching to Arabic (`ar`), the entire UI should mirror to RTL. Currently layout direction is not toggled.
