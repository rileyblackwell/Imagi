"""
Check a project's Django backend the way a developer would before trying it.

A thread changing models used to write its migrations by hand and learn
whether they applied only when the preview's migrate failed, a while later
and in another place (preview logs). This runs the three commands a Django
developer runs instead, in the thread's own copy of the project:

1. makemigrations, so migrations are Django's own and match the models;
2. check, Django's system checks (bad URLs, models, settings, admin);
3. migrate, every migration from nothing, into a scratch database, so a
   migration that would break the preview fails here first.

The project's real database is never touched. It runs on Imagi's own Python,
the same interpreter the preview runs the project on, with the same trimmed
environment (preview_service.child_env), so nothing secret reaches the
project's code.
"""

import glob
import logging
import os
import subprocess
import sys
import tempfile

logger = logging.getLogger(__name__)

STEP_TIMEOUT_S = 90
# How much of a command's output goes back to the agent.
OUTPUT_TAIL_CHARS = 4000

BACKEND_DIR = os.path.join('backend', 'django')


def _settings_module(backend_path: str):
    names = sorted(
        d for d in os.listdir(backend_path)
        if os.path.isfile(os.path.join(backend_path, d, 'settings.py'))
    )
    return f'{names[0]}.settings' if names else None


def _migration_files(backend_path: str) -> dict:
    """Every migration file under the backend, with its contents."""
    found = {}
    for path in glob.glob(os.path.join(backend_path, '**', 'migrations', '*.py'), recursive=True):
        if os.sep + 'node_modules' + os.sep in path:
            continue
        try:
            with open(path, 'rb') as f:
                found[path] = f.read()
        except OSError:
            continue
    return found


def _scratch_settings(settings_module: str, db_path: str) -> str:
    return (
        f"from {settings_module} import *  # noqa: F401,F403\n\n"
        "DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', "
        f"'NAME': {db_path!r}}}}}\n"
    )


def _tail(text: str) -> str:
    text = (text or '').strip()
    return text if len(text) <= OUTPUT_TAIL_CHARS else '…' + text[-OUTPUT_TAIL_CHARS:]


def check_backend(project_root: str) -> dict:
    """Run makemigrations, check and a scratch migrate in ``project_root``.

    Returns {'ok', 'steps': [{'command', 'ok', 'output'}], 'new_migrations':
    [paths relative to project_root], 'changed_migrations': [...]}; on a
    project with no Django backend, {'ok': False, 'error': ...}.
    """
    from .preview_service import child_env

    backend_path = os.path.join(project_root, BACKEND_DIR)
    if not os.path.isfile(os.path.join(backend_path, 'manage.py')):
        return {'ok': False, 'error': f"There is no Django backend at {BACKEND_DIR}/manage.py."}
    settings_module = _settings_module(backend_path)
    if not settings_module:
        return {'ok': False, 'error': f"No Django settings module found under {BACKEND_DIR}."}

    before = _migration_files(backend_path)
    steps = []
    with tempfile.TemporaryDirectory(prefix='imagi-check-') as scratch:
        with open(os.path.join(scratch, 'imagi_check_settings.py'), 'w') as f:
            f.write(_scratch_settings(settings_module, os.path.join(scratch, 'check.sqlite3')))
        env = child_env(
            DJANGO_SETTINGS_MODULE='imagi_check_settings',
            PYTHONPATH=scratch,
        )
        for command in (
            ['makemigrations', '--noinput'],
            ['check'],
            ['migrate', '--noinput'],
        ):
            label = 'manage.py ' + ' '.join(command)
            try:
                result = subprocess.run(
                    [sys.executable, 'manage.py', *command],
                    cwd=backend_path, env=env, capture_output=True, text=True,
                    timeout=STEP_TIMEOUT_S,
                )
            except subprocess.TimeoutExpired:
                steps.append({'command': label, 'ok': False,
                              'output': f'Timed out after {STEP_TIMEOUT_S}s.'})
                break
            ok = result.returncode == 0
            output = (result.stdout or '') + (result.stderr or '')
            if ok and command[0] == 'migrate':
                # Dozens of "Applying ... OK" lines say nothing more than this.
                applied = output.count('... OK')
                output = f'Every migration applies to a fresh database ({applied} applied).'
            steps.append({'command': label, 'ok': ok, 'output': _tail(output)})
            if not ok:
                # The later commands only repeat the same failure.
                break

    after = _migration_files(backend_path)
    rel = lambda p: os.path.relpath(p, project_root)  # noqa: E731
    return {
        'ok': all(s['ok'] for s in steps) and len(steps) == 3,
        'steps': steps,
        'new_migrations': sorted(rel(p) for p in after if p not in before),
        'changed_migrations': sorted(
            rel(p) for p in after if p in before and after[p] != before[p]
        ),
    }
