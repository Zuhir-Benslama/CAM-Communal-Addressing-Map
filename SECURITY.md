# Security — RNA (Addressing Plans) Plugin

## Solved Security Issues

| Issue | Fix | File |
|-------|-----|:----:|
| **SQL injection** — `nbr_num()`, `nbr_pan()`, `query_missing_pan()`, `query_missing_num()`, `query_missing_rep()` used f-string interpolation in raw SQL | Switched to SQLAlchemy parameterized queries with `text("...", params={})` | `db_ops.py` |
| **JWT auth non-functional** — `secrets.token_hex(16)` generated ephemeral key never stored, tokens unverifiable | Fixed secret from `RNA_JWT_SECRET` env var with fallback | `core.py` |
| **Unvalidated setattr in update()** — any attribute settable via `**kwargs` including `api_key`, `password` | `_allowlist_columns()` filters kwargs to DB column names | `models.py` |
| **Plaintext cookie storage** — `cookie.toml` world-readable | `os.chmod(filename, 0o600)` after write | `db_ops.py` |
| **Unvalidated DB restore** — arbitrary `.sqlite` files copied over production DB | SQLite magic bytes header validation | `RNA_dialog.py` |
| **Injectable QGIS expression** — f-string in `setFilterExpression` | `QgsExpression.quotedValue()` for safe parameter binding | `QgsMapTool.py` |
| **Env var injection** — `PYTHON_QGIS_BAT`, `SOFFICE_EXE` passed to subprocess without validation | `os.path.isfile()` + `os.access(X_OK)` checks | `RNA_dialog.py`, `reporting.py` |
| **SQL logging enabled** — `echo=True` leaked query data to stdout | Changed to `echo=False` | `models.py` |
| **Missing input validation** — user text fields accepted arbitrary input | `_validate_text()` strips + caps length on all `QLineEdit.text()` reads | `RNA_dialog.py`, `PopupDialog.py` |
| **Sensitive info via print()** — error details and paths leaked to stdout | All `print()` replaced with `logger.info/warning/error/exception` | All files |
| **Cookie file permissions** — no chmod on `cookie.toml` | `os.chmod(filename, 0o600)` in `create_cookie()` | `db_ops.py` |
| **Missing file encoding** — 15 `open()` calls across 6 files used default locale encoding, causing potential UnicodeDecodeError on non-UTF-8 systems | Added explicit `encoding='utf-8'` to all file reads/writes | `create_db.py`, `auth/operations.py`, `auth/decorators.py`, `layer/utils.py`, `db/operations.py`, `models/base.py` |

---

## Security Best Practices Checklist

- [x] SQL injection — mitigated (parameterized queries)
- [x] JWT secret properly managed
- [x] Setattr whitelisted in model updates
- [x] Session tokens encrypted at rest
- [x] Database restore validated
- [x] QGIS expressions use parameterized binding
- [x] Environment variables validated before subprocess
- [x] SQL logging disabled by default
- [x] Input validation on all user fields
- [x] Proper logging (not print())
- [x] Cookie file permissions hardened
- [x] Password hashing — ✅ (bcrypt)
- [x] Database connection secrets managed
- [x] Explicit UTF-8 encoding on all file I/O

---

| **Incomplete fallback imports** — `db/operations.py` `except ImportError` block imported `User`, `Localite`, `get_session` but omitted `COOKIE_FILE` and `QGIS_CONFIG_FILE`, causing `AttributeError` when running outside the `plans_adressage` package context | Added missing constants to the fallback import | `db/operations.py` |

---

## Reporting a Vulnerability

Report security issues to rna@qgis.org.
