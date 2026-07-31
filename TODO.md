# RNA Plugin — Code Quality & Bug Fix Tracking

## Priority Legend
- **P0**: Critical (will crash or corrupt data)
- **P1**: High (major functionality or correctness)
- **P2**: Medium (code quality, maintainability)
- **P3**: Low (nice to have)

---

## 1. Crash on Feature Add / Edit (P0)

- [x] `mixins/layer_ops_mixin.py:278` — `wkt.loads(get_user_location())` has no None check. `get_user_location()` returns `None` (`app/users/repository.py:113`) whenever the user has no stored commune geometry, so `wkt.loads(None)` raises `TypeError` and every feature add (`on_feature_added`) / geometry edit (`on_geometry_changed`) crashes with a traceback instead of applying the intended "outside zone" handling. Fix: guard against `None` and fall back to a sensible default (e.g. no zone restriction).

## 2. Crash on Close with No Cookie (P0)

- [x] `app/users/service.py:152` — `logout()` opens `COOKIE_FILE` with no try/except. On a fresh install where `cookie.toml` has never been created, `FileNotFoundError` (or `TomlDecodeError` on a corrupt file) escapes `closeEvent` (`mixins/auth_mixin.py:195`) and the plugin crashes on close. Fix: wrap file read in try/except and treat a missing/invalid cookie as "no active session".

## 3. Edit Popup Discards User Changes on Failed Save (P0)

- [x] `gui/popup_handlers.py:150-152,175` — `_update_entity` calls `_finish_update` unconditionally after the try/except, so when the DB update fails the user sees the error box *and the dialog closes*, silently discarding their edits. Fix: only close the dialog on success (call `_finish_update` inside the success path).

## 4. Unhandled Exceptions in Restore Flow (P0)

- [x] `mixins/backup_mixin.py:144-145` — `restore_database` calls `_replace_db_file` / `reset_connection_pool` without the try/except that the equivalent `_replace_and_reset` path (`:113`) has, so any `OSError` / `shutil.Error` raises an unhandled exception in the GUI flow. Fix: reuse `_replace_and_reset` or add equivalent error handling.

## 5. Stale Features After Restoring an Empty DB (P1)

- [x] `layer/refresh.py:157-158` — `refresh_layer_from_db` early-returns when the query returns no rows, so after `restore_database` with an empty DB (or any out-of-band DB deletion) the map layer keeps showing stale features that no longer exist. Fix: clear the layer before the empty-result early return.

## 6. Raw Exceptions Escape Register/Login (P1)

- [x] `app/users/service.py:89-91` — `sign_up` re-raises `SQLAlchemyError` after `rollback()`, but `submit_add_usr` (`mixins/auth_mixin.py:50-66`) only handles the `(ok, errors)` return path, so a genuine DB failure surfaces as an unhandled exception from the Register button.
- [x] `app/users/service.py:122` + `app/users/repository.py:142-144` — `create_cookie` re-raises `OSError`/`PermissionError`, but `sign_in` only catches `SQLAlchemyError` (`service.py:124`), so a disk failure during login escapes unhandled. Fix: catch at the call sites and convert to the existing error-return path.

## 7. Inverted `loadNamedStyle` Success Check (P1)

- [x] `mixins/layer_ops_mixin.py:128-133` — the success check treats `True`/non-empty as failure and `False`/0/empty as success, which is inverted for QGIS 3 (`loadNamedStyle` returns `(bool, QString)` where `bool` is True on success). Every successful style load logs a spurious "Failed to load style" warning and real failures go unnoticed. Fix: `is_success = bool(success_val)`.

## 8. Edit Mode Is Dead Code (P1)

- [x] `gui/main_dialog.py:399` — `update_object: dict = {}` is initialized empty and never reassigned anywhere in production code, so the `if self.update_object:` guards in `mixins/layer_edit_mixin.py:120,338` are always falsy and the edit-vs-insert feature is broken. Fix: assign the object being edited, or remove the dead branches. Removed the dead guards, state attributes, and protocol entry (no edit flow sets it).

## 9. Identify Tool Crashes Without an Active Layer (P1)

- [x] `gui/identify_tool.py:68-70` — `get_id()` calls `self.get_active_layer().name()` with no None check; the active layer can be None, so `AttributeError` is possible. Fix: return a safe default / early-return when no active layer exists.

## 10. Report Export Assumes Municipality Layer Exists (P1)

- [x] `mixins/symbol_export_mixin.py:175-177` — `map_situation` assumes the municipality layer is `[0]`; if the layer is absent the empty list raises `IndexError` instead of a friendly message. Fix: check list length first (also guarded the `sat_view`/`rast` lookups).

## 11. i18n Gaps (P2)

- [x] `gui/popup_pages/city_page.py:31,35,40` (and `road_page.py`, `zone_page.py`, `org_page.py`, `pan_page.py`, `num_page.py`) use untranslated English labels ('Type:', 'Name:', 'Save'). Now routed through `get_string(label, dialog._tr_locale)`; added English source keys ('Type:', 'Name:', 'Save', 'Category:', 'Mount Status:', 'Ref Type:', 'Select Reference', 'Number:', 'Duplicated:', 'State:', 'Activity Cat:', 'Activity Type:') to `template_data/strings.json`.
- [x] `gui/dialog_state.py:43-54` hardcodes Arabic dictionaries (`ARABIC_ACTION_NAMES`, `ARABIC_THEME_NAMES`). Verified these are translation-key lookups into `strings.json` (all 7 Arabic keys resolve; same pattern as `LAYER_TRANSLATIONS`) — no user-visible gap; left as-is. `init_theme_locale` `theme_map` is legacy-settings migration (intentional).
- [x] `mixins/import_export_mixin.py:193` — untranslated 'Please select a paper size'. Now `self._tr('Please select a paper size')`; key added to `strings.json`.

## 12. Dead Code Cleanup (P2)

Removed (were unreferenced in production and tests):
- [x] `app/shared/utils.py:31` — `ensure()` removed.
- [x] `app/users/dependencies.py` — `login_required` + `_navigate_to_login` (only live code in module); module deleted.
- [x] `app/core/database.py:102` — `session_scope()` removed.
- [x] `app/core/security.py:13,19` — `reset_jwt_secret()` / `get_jwt_secret()` removed (JWT secret unused anywhere).
- [x] `app/orders/repository.py:48` — `export_model()` + `_model_class()` removed.
- [x] `mixins/backup_mixin.py:193` — `import_database()` + helpers `_select_auth_file()` / `_perform_migration()` / `_replace_and_reset()` removed.
- [x] `mixins/map_tools_mixin.py:137` — `ref_pan_selected()` removed (also `HasRefSelectContext` protocol).
- [x] `gui/popup_dialog.py:432,435` — `bridge()` and `_set_combo_value()` removed.
- [x] `mixins/layer_edit_mixin.py:215` — `key_press_event()` removed.
- [x] `app/users/repository.py:34` — `_get_commune_by_id()` removed.

Removed (dead in production, tests removed too):
- [x] `get_zone_chart()` (`mixins/chart_mixin.py`) + its 2 tests.
- [x] `populate_table()` public wrapper (`gui/entity_list_dialog.py`) + its test.
- [x] `set_ref_name()` / `ref_name` attr (`gui/identify_tool.py`) + 2 tests.
- [x] `edit_line_layer()` / `save_changes()` / `stop_editing_layer()` (`layer/editing.py`) + 7 tests.
- [x] `add_feature_to_layer()` / `apply_categorized_style()` / `remove_categorized_style()` / `apply_all_categorized_styles()` / `remove_all_categorized_styles()` (`layer/refresh.py`, incl. `_resolve_wkt()` / `_commit_feature()`) + 8 tests.

Corrected claims (NOT dead — verified in use):
- [x] `layer/refresh.py` — `remove_categorized_style()` was called by `remove_all_categorized_styles()`; both now removed.
- [x] `app/users/repository.py:105` — `_get_authenticated_user()` IS used internally by `get_user_location()`; kept.
- [x] `gui/identify_tool.py:48-68` — `get_active_layer()` / `get_iface()` / `set_active_layer()` are used internally; `feature_name` / `feature_type` / `ref_name` are attributes, not methods. Only `set_ref_name` was dead.

## 13. Unreachable Tab Branches (P2)

- [x] `mixins/layer_ops_mixin.py` — `on_opt_selected` simplified: removed Settings/Report branches and the now-dead `_handle_settings_tab()` / `_handle_report_tab()` (tab index is always 0 → 'Operations'). Cascaded removals: `_show_base_layers()`, `_show_always_shown_layers()` (+ their `HasTabSwitchContext` protocol entries) and the `CUSTOM_STYLE_DIR` import.
- [x] `mixins/layer_ops_mixin.py` — `hasattr(self.menu, '_rna_tab_src')` fallback removed from `on_opt_selected` and `on_feature_added` (`menu` is a `_TabWidget`, never a `QTabWidget`, so `apply_widget_texts` never sets it).

## 14. Wrong Property Label in Panel List (P2)

- [x] `gui/entity_list_dialog.py:116-119` — `property_labels` mapped `'pan_label'` (no such model attribute) which rendered as an empty 'Label' column for Panel Signs; now maps the real `label` property (`app/orders/models/panel_sign.py:73`).

## 15. Inconsistent Error Message (P2)

- [x] `mixins/layer_ops_mixin.py:322` — on DB failure the `QMessageBox` title used hardcoded French 'Erreur'; now `self._tr('Error')`, consistent with the rest of the codebase.

## 16. Duplicated Code (P3)

- [x] Cookie/session parsing duplicated in at least 4 places with subtly different error handling: `app/users/service.py:148-183`, `app/users/dependencies.py:25-58`, `app/users/repository.py:58-71,113-133`. Fix: extract a single helper. Extracted `load_session_cookie()` + `find_active_session_user()` in `app/users/repository.py`; `get_current_user()` and `service.logout()` now share them (`app/users/dependencies.py` was already deleted by fix #12).
- [x] Six near-identical form-page builders (`gui/popup_pages/{city,road,zone,org,pan,num}_page.py` — same `QFormLayout` + Save button + `_on_save` lambda). Fix: one parametrized builder. Added `gui/popup_pages/_builder.py::build_page()`; the six page files are now thin declarative row-spec wrappers.
- [x] Six near-identical `update()` / `save()` model methods (`app/orders/models/{numbering,organization,panel_sign,road,subdivision,zone}.py`). Fix: consolidate into the `BaseEntity` / `_BaseSpatialModel` base. Moved both into `_BaseSpatialModel` with an overridable `_refresh_derived()` hook; subclasses keep only their derived-column recompute (and `PanelSign.save` keeps its reference validation via `super().save()`).
- [x] Duplicated QVariant-fallback `IntEnum` class (`layer/refresh.py:22-31` vs `layer/utils.py:18-27`). Fix: share one definition. `layer/refresh.py` now imports `QVariant` from `layer/utils`.

## 17. God-Class / Architecture (P3)

- [x] `MainDialog` inherits 9 mixins (`gui/main_dialog.py`); the UI class is a god-class via `mixins/*`. Consider splitting or documenting the mixin responsibilities. Documented: the `MainDialog` docstring now lists each mixin's responsibility. Structural split deferred — mixins are the established composition pattern and work.

## 18. Misc Small Issues (P3)

- [x] `gui/main_dialog.py:361-368` — `_on_map_option_changed` just re-sets the index to itself (no-op slot). Removed the `setCurrentIndex` no-op; the slot is now log-only and connected directly to `currentIndexChanged` (dropping the lambda wrapper).
- [x] `gui/popup_dialog.py:206` — mutable default argument `self._current_form_data: dict = {}`; combined with `.update()` in `set_form`, data can leak between dialog instances. Fix: initialize in `__init__` / `set_form`. Already initialized per-instance in `__init__` (no class-level default exists); tightened the annotation to `dict[str, Any]`.
- [x] `app/shared/utils.py:78-85` — `current_theme()` compares a `Theme` enum to a QSettings string (always unequal), so it rewrites settings on every call. Now compares values (`value != theme`, valid for the `str`-enum) so canonical values are only written once.
- [x] `app/shared/utils.py:99-103` — `get_qgis_python()` returns `'python3'` in both final branches (dead ternary). Collapsed to a single `return 'python3'`; dropped the now-unused `shutil` import.
- [x] `gui/identify_tool.py:115` — `toMapCoordinates(event.pos())` result is unused in `canvasReleaseEvent`. Removed (the identify call uses canvas pixel coords).
- [x] `gui/ui_fillers.py:266-275` — `fill_subtype_combo` does `for t in data_list` with no type check, so an `AttributeError` escapes if the JSON root isn't a list; and `_save_new_type` (`gui/main_dialog.py:415-432`) gives zero feedback when `save_new_type_to_json` fails (e.g. read-only plugin install dir). `_fill_from_json` now guards against non-list data, and `_save_new_type` shows a warning box on failure.
