"""Smoke test: load the plugin exactly like QGIS does, with REAL modules.

The rest of this suite injects mock ``qgis`` modules into ``sys.modules``
before importing plugin code (see ``test/helpers``), which hides real
import-time breakage such as importing a nonexistent symbol from
``qgis.gui``. This test runs a clean interpreter against the real QGIS
Python bindings and exercises the full startup chain:

1. ``import`` the plugin package under its deployed name (``CAM``),
2. call ``classFactory()`` (which pulls in ``app.main`` → dialogs → tools),
3. ``pkgutil.walk_packages`` every submodule so nothing escapes untested.

Skips cleanly when QGIS bindings are unavailable (e.g. minimal CI images).
"""

import pathlib
import subprocess
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

_EXIT_NO_QGIS = 42

_PROBE = r"""
import importlib
import os
import pathlib
import pkgutil
import sys
import tempfile
import unittest.mock

try:
    import qgis.core  # noqa: F401
except ImportError:
    print('NO-QGIS-BINDINGS')
    sys.exit(42)

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from qgis.core import QgsApplication  # noqa: E402

app = QgsApplication([], False)
QgsApplication.setPrefixPath(os.getenv('QGIS_BASE_PATH', '/usr'), True)
app.initQgis()

src = pathlib.Path(sys.argv[1]).resolve()
# QGIS loads plugins from a directory whose name is the plugin package
# name, so mirror that instead of importing the repo checkout directly.
with tempfile.TemporaryDirectory() as tmp:
    pathlib.Path(tmp, 'CAM').symlink_to(src, target_is_directory=True)
    sys.path.insert(0, tmp)
    pkg = importlib.import_module('CAM')

    plugin = pkg.classFactory(unittest.mock.MagicMock())
    if not callable(getattr(plugin, 'initGui', None)):
        raise AssertionError('classFactory() did not return a plugin instance')

    failures = []
    for info in pkgutil.walk_packages(pkg.__path__, prefix='CAM.'):
        try:
            importlib.import_module(info.name)
        except Exception as exc:  # pragma: no cover - reported below
            failures.append(f'{info.name}: {exc!r}')
    if failures:
        print('\n'.join(failures))
        sys.exit(1)
"""


def test_plugin_fully_imports_with_real_qgis():
    result = subprocess.run(
        [sys.executable, '-c', _PROBE, str(REPO_ROOT)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_ROOT,
        check=False,
    )
    if result.returncode == _EXIT_NO_QGIS and 'NO-QGIS-BINDINGS' in result.stdout:
        pytest.skip('QGIS Python bindings not available')
    assert result.returncode == 0, (
        f'Plugin failed to load under real QGIS bindings:\n'
        f'{result.stdout}\n{result.stderr}'
    )
