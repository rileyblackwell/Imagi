"""
Auth app prebuilt template.

Every generated project gets sign-in, registration and the auth API from
here, never from a model: Imagi maintains this code, so the security-relevant
parts are written once, reviewed and tested, instead of being generated anew
(and possibly wrong) in each project.

The files live as real files under ``auth_template/``, laid out exactly as
they land in the project, so they can be read, diffed and tested like any
other code. They come in three kinds (protected_paths holds the build agents
to this):

* The flow itself — the Django API (``backend/django/apps/auth``) and the Vue
  stores, services, composables, validation and types. These are copies of
  Imagi's own auth module, and the template tests keep them identical to it,
  so a fix to Imagi's auth reaches new projects in the same change. The only
  deviation is ``apps.py``, which declares ``label = 'user_auth'``: the app
  lives at ``apps.auth``, whose default label collides with
  ``django.contrib.auth`` (Imagi avoids that with its capitalized
  ``apps.Auth`` path).
* The pages — ``layouts/``, ``views/``, ``components/`` and ``router/``. One
  centered card, like Imagi's own sign-in page, but written for generated
  projects: no Imagi design tokens, no Imagi brand, and every visual decision
  pushed out to the stylesheet.
* The look — ``styles/auth.css`` and the copy in ``brand.ts``. These are the
  only auth files an agent may change: after the first build lands the home
  page, a thread rewrites them so the pages match the business's site
  (ProjectManager.services.auth_restyle_service).

The frontend relies on the project scaffold that ProjectCreationService always
writes: ``@/shared/services/api`` (axios client with token + CSRF
interceptors) and ``@/shared/stores/auth`` (global auth store).
"""
from __future__ import annotations

import json
import os
from typing import Dict, List

TEMPLATE_ROOT = os.path.join(os.path.dirname(__file__), 'auth_template')

# Stamped into brand.ts with the project's name at scaffold time.
BUSINESS_NAME_PLACEHOLDER = "'__BUSINESS_NAME__'"
DEFAULT_BUSINESS_NAME = 'Your Business'

_EXT_TYPES = {
    '.py': 'python',
    '.ts': 'typescript',
    '.vue': 'vue',
    '.css': 'css',
}


def template_files() -> Dict[str, str]:
    """Every template file, keyed by its project-relative path, unstamped."""
    files: Dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(TEMPLATE_ROOT):
        dirnames[:] = sorted(d for d in dirnames if d != '__pycache__')
        for filename in sorted(filenames):
            if filename.endswith('.pyc'):
                continue
            full = os.path.join(dirpath, filename)
            rel = os.path.relpath(full, TEMPLATE_ROOT).replace(os.sep, '/')
            with open(full, 'r', encoding='utf-8') as f:
                files[rel] = f.read()
    return files


def auth_app_files(project_name: str | None = None) -> List[Dict[str, str]]:
    """Generate the auth app files (frontend + backend) for a new project."""
    name = (project_name or '').strip() or DEFAULT_BUSINESS_NAME
    files = []
    for path, content in template_files().items():
        if path.endswith('/brand.ts'):
            # json.dumps gives a valid, fully escaped TypeScript string literal.
            content = content.replace(BUSINESS_NAME_PLACEHOLDER, json.dumps(name))
        files.append({
            'name': path,
            'type': _EXT_TYPES.get(os.path.splitext(path)[1], ''),
            'content': content,
        })
    return files
