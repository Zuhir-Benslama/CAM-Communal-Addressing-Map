#!/usr/bin/env python3
"""Cross-platform installer for the CAM QGIS plugin.

Usage:
    python scripts/install_rna.py [--plugin-dir DIR] [--qgis-python PATH]
                                  [--skip-packages] [--skip-checks]

Checks for system dependencies, installs Python packages into QGIS's
Python environment, and copies the plugin to the QGIS plugins directory.

Works on Linux, macOS, and Windows.
"""

import argparse
import logging
import os
import platform
import shutil
import subprocess
import sys

logger = logging.getLogger('install_rna')
_log_handler = logging.StreamHandler(sys.stdout)
_log_handler.setFormatter(
    logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
    )
)
logger.addHandler(_log_handler)
logger.setLevel(logging.INFO)

PLUGIN_NAME = 'CAM'
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
REQUIREMENTS = os.path.join(PROJECT_ROOT, 'requirements.txt')

EXCLUDE_DIRS = {
    '__pycache__',
    '.git',
    '.github',
    '.gitignore',
    'test',
    '.mypy_cache',
    '.pytest_cache',
    '.ruff_cache',
    '.agents',
    '.codex',
    '.idea',
    '.vscode',
}

EXCLUDE_FILES = {
    'Makefile',
    'pb_tool.cfg',
    'pyproject.toml',
    'README.md',
    'SECURITY.md',
    'TODO.md',
    'WORK_RESUME.md',
    'requirements.txt',
    'resources.qrc',
    'symbology-style.db',
}

QGIS_PLUGIN_DIRS = {
    'Linux': os.path.expanduser(
        '~/.local/share/QGIS/QGIS3/profiles/default/python/plugins'
    ),
    'Darwin': os.path.expanduser(
        '~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins'
    ),
    'Windows': os.path.join(
        os.environ.get('APPDATA', ''),
        'QGIS',
        'QGIS3',
        'profiles',
        'default',
        'python',
        'plugins',
    ),
}

QGIS_PYTHON_CANDIDATES = {
    'Windows': [
        r'C:\Program Files\QGIS 3.34\bin\python3.exe',
        r'C:\Program Files\QGIS 3.36\bin\python3.exe',
        r'C:\Program Files\QGIS 3.38\bin\python3.exe',
        r'C:\OSGeo4W\bin\python3.exe',
    ],
    'Darwin': [
        '/Applications/QGIS.app/Contents/MacOS/bin/python3',
    ],
}


def get_os():
    system = platform.system()
    if system in ('Linux', 'Darwin', 'Windows'):
        return system
    logger.error('Unsupported OS: %s', system)
    sys.exit(1)


def find_qgis_python():
    os_name = get_os()
    python_env = os.environ.get('QGIS_PYTHON') or os.environ.get('PYTHON_QGIS_BAT')
    if python_env and os.path.isfile(python_env):
        return os.path.abspath(python_env)
    if os_name == 'Linux':
        for name in ('python3', 'python'):
            path = shutil.which(name)
            if path:
                return path
        return None
    for candidate in QGIS_PYTHON_CANDIDATES.get(os_name, []):
        if os.path.isfile(candidate):
            return candidate
    if os_name == 'Windows':
        for name in ('python3.exe', 'python.exe'):
            path = shutil.which(name)
            if path:
                return path
    return None


def check_qgis():
    qgis = shutil.which('qgis')
    if qgis:
        return True, qgis
    if get_os() == 'Darwin' and os.path.isdir('/Applications/QGIS.app'):
        return True, '/Applications/QGIS.app'
    if get_os() == 'Windows':
        for root in (
            r'C:\Program Files\QGIS 3.34',
            r'C:\Program Files\QGIS 3.36',
            r'C:\Program Files\QGIS 3.38',
            r'C:\OSGeo4W',
        ):
            exe = os.path.join(root, 'bin', 'qgis.exe')
            if os.path.isfile(exe):
                return True, exe
    return False, None


def check_libreoffice():
    soffice = shutil.which('soffice')
    if soffice:
        return True, soffice
    if get_os() == 'Windows':
        for path in (
            r'C:\Program Files\LibreOffice\program\soffice.exe',
            r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
        ):
            if os.path.isfile(path):
                return True, path
    if get_os() == 'Darwin':
        path = '/Applications/LibreOffice.app/Contents/MacOS/soffice'
        if os.path.isfile(path):
            return True, path
    return False, None


def install_python_packages(qgis_python):
    if not qgis_python:
        logger.warning(
            'No QGIS Python found. Install packages manually:\n  pip install -r %s',
            REQUIREMENTS,
        )
        return False
    pip_dir = os.path.dirname(qgis_python)
    pip_names = ['pip3', 'pip']
    pip_cmd = None
    for name in pip_names:
        exe = name + ('.exe' if get_os() == 'Windows' else '')
        path = os.path.join(pip_dir, exe)
        if os.path.isfile(path):
            pip_cmd = [path]
            break
    if not pip_cmd:
        pip_cmd = [qgis_python, '-m', 'pip']
    logger.info('Installing packages from %s ...', REQUIREMENTS)
    result = subprocess.run(
        [*pip_cmd, 'install', '-r', REQUIREMENTS],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        logger.info('Python packages installed successfully.')
        return True
    logger.error('Package install failed:\n%s', result.stderr)
    return False


def _ignore_patterns(dir_, files):
    skip = set()
    rel = os.path.relpath(dir_, PROJECT_ROOT)
    for f in files:
        if f in EXCLUDE_FILES:
            skip.add(f)
            continue
        if f in EXCLUDE_DIRS:
            skip.add(f)
            continue
        if f.endswith(('.pyc', '.pyo')):
            skip.add(f)
            continue
        full = os.path.join(dir_, f)
        if os.path.isdir(full):
            for d in EXCLUDE_DIRS:
                if os.path.join(rel, f) == d:
                    skip.add(f)
                    break
    return skip


def install_plugin(plugin_dir):
    target = os.path.join(plugin_dir, PLUGIN_NAME)
    if os.path.isdir(target):
        logger.info('Removing existing installation at %s', target)
        shutil.rmtree(target)
    shutil.copytree(
        PROJECT_ROOT,
        target,
        ignore=_ignore_patterns,
        symlinks=False,
    )
    logger.info('Plugin installed to: %s', target)
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Install CAM QGIS plugin',
    )
    parser.add_argument(
        '--plugin-dir',
        help='QGIS plugins directory (auto-detected by default)',
    )
    parser.add_argument(
        '--qgis-python',
        help='Path to QGIS Python interpreter',
    )
    parser.add_argument(
        '--skip-packages',
        action='store_true',
        help='Skip Python package installation',
    )
    parser.add_argument(
        '--skip-checks',
        action='store_true',
        help='Skip system dependency checks',
    )
    args = parser.parse_args()

    print('=== CAM QGIS Plugin Installer ===')
    print(f'Platform: {platform.system()} {platform.release()}')
    print()

    plugin_dir = args.plugin_dir or QGIS_PLUGIN_DIRS.get(get_os())
    if not plugin_dir:
        logger.error('Could not determine QGIS plugins directory for this OS.')
        sys.exit(1)

    if not args.skip_checks:
        print('--- System dependencies ---')
        ok, path = check_qgis()
        status = 'OK' if ok else 'NOT FOUND'
        print(f'  QGIS ....... {status}')
        if ok:
            print(f'               {path}')
        else:
            print('  (install QGIS 3.x from https://qgis.org)')

        ok, path = check_libreoffice()
        status = 'OK' if ok else 'NOT FOUND (optional — only needed for PDF reports)'
        print(f'  LibreOffice  {status}')
        if ok:
            print(f'               {path}')
        print()

    if not args.skip_packages:
        print('--- Python packages ---')
        qgis_python = args.qgis_python or find_qgis_python()
        if qgis_python:
            print(f'  Using Python: {qgis_python}')
        install_python_packages(qgis_python)
        print()

    print('--- Plugin installation ---')
    print(f'  Target: {plugin_dir}')
    install_plugin(plugin_dir)
    print()

    print('=== Done ===')
    print('Restart QGIS and enable CAM in:')
    print('  Plugins → Manage and Install Plugins → Installed')
    print('  (check the box next to CAM)')
    print()


if __name__ == '__main__':
    main()
