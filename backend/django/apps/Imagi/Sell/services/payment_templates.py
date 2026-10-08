"""
Prebuilt payments the Sell console drops into a user's generated project.

Like the prebuilt sign-in (Build.services.codegen.prebuilt_apps.auth), the
payment flow is code Imagi maintains, never code a model writes: the files
live as real files under ``Build/services/codegen/prebuilt_apps/
payments_template/``, laid out exactly as they land in the project, and the
build agents can't change them (Build.services.protected_paths). Two files
stay open, and they are the whole of the pages' look: ``styles/payments.css``
and the copy in ``brand.ts``. After an install, a thread restyles those two to
match the site and links the new pages from its navigation.

What lands in the project:

* ``frontend/vuejs/src/apps/payments/`` — a plans page (/pricing) for
  subscriptions and pay-as-you-go, and a store (/store) for one-time
  purchases, each with its checkout return page. ``config.ts`` decides which
  pages exist, from the payment models chosen in the console. The pages read
  prices from Imagi and send customers to Stripe's hosted checkout, so the
  app never holds Stripe keys and never sees a card.
* ``backend/django/apps/payments/`` — ``report_usage`` and
  ``has_active_plan`` for the app's own backend, authenticated with the
  project's server key, which Imagi passes to the app as an environment
  variable rather than writing it into code.
"""

import json
import logging
import os

from django.conf import settings as django_settings

from apps.Imagi.Build.models import ProjectFile
from apps.Imagi.Build.services.create_file_service import CreateFileService
from apps.Imagi.Build.services.project_files_service import ensure_working_copy

from ..models import SellSettings
from .sell_service import SellServiceError

logger = logging.getLogger(__name__)

TEMPLATE_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'Build', 'services', 'codegen', 'prebuilt_apps', 'payments_template',
)

FRONTEND_DIR = 'frontend/vuejs/src/apps/payments'
BACKEND_DIR = 'backend/django/apps/payments'

PROJECT_ID_PLACEHOLDER = '__IMAGI_PROJECT_ID__'
API_BASE_PLACEHOLDER = '__IMAGI_API_BASE__'
PAGES_PLACEHOLDER = '__PAYMENT_PAGES__'

# Files the restyle may rewrite; installing again keeps the project's
# versions of these rather than resetting its look.
RESTYLE_FILES = (f'{FRONTEND_DIR}/styles/payments.css', f'{FRONTEND_DIR}/brand.ts')

_EXT_TYPES = {'.py': 'python', '.ts': 'typescript', '.vue': 'vue', '.css': 'css'}

PAGES = {
    'pricing': {
        'route': '/pricing',
        'name': 'Plans page',
        'description': 'Your subscription and pay-as-you-go plans, with Subscribe buttons.',
    },
    'store': {
        'route': '/store',
        'name': 'Store',
        'description': 'Your one-time products, with Buy buttons.',
    },
}


def storefront_api_base() -> str:
    base = getattr(django_settings, 'SELL_STOREFRONT_API_BASE', '') or 'http://localhost:8000'
    return base.rstrip('/')


def template_files() -> dict:
    """Every template file, keyed by its project-relative path, unstamped."""
    files = {}
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


def pages_for(payment_models) -> dict:
    """Which pages the app gets for the chosen ways to charge."""
    models = set(payment_models or [])
    return {
        'pricing': bool(models & {'subscription', 'usage'}),
        'store': 'one_time' in models,
    }


def payments_files(project, payment_models) -> list:
    """The template, stamped for this project."""
    pages = pages_for(payment_models)
    stamps = {
        PROJECT_ID_PLACEHOLDER: str(int(project.id)),
        # json.dumps gives a valid, escaped string literal for both TS and
        # Python; the placeholder sits inside quotes, so drop dumps' own.
        API_BASE_PLACEHOLDER: json.dumps(storefront_api_base())[1:-1],
        PAGES_PLACEHOLDER: json.dumps(pages),
    }
    files = []
    for path, content in template_files().items():
        for placeholder, value in stamps.items():
            content = content.replace(placeholder, value)
        files.append({
            'name': path,
            'type': _EXT_TYPES.get(os.path.splitext(path)[1], ''),
            'content': content,
        })
    return files


def _project_has(project, path: str) -> bool:
    if ProjectFile.objects.filter(project=project, path=path).exists():
        return True
    project_path = project.project_path or ''
    return bool(project_path) and os.path.exists(os.path.join(project_path, path))


def _installed_pages(project) -> dict | None:
    """The pages config.ts currently turns on, or None when not installed."""
    config_path = f'{FRONTEND_DIR}/config.ts'
    row = ProjectFile.objects.filter(project=project, path=config_path).first()
    content = row.content if row else ''
    if not content and project.project_path:
        disk = os.path.join(project.project_path, config_path)
        if os.path.exists(disk):
            with open(disk, 'r', encoding='utf-8') as f:
                content = f.read()
    if not content:
        return None
    pages = {}
    for key in PAGES:
        pages[key] = f'"{key}": true' in content
    return pages


def app_payments_state(project) -> dict:
    """What the console shows about the app's payment pages."""
    config = SellSettings.objects.filter(project=project).first()
    chosen = config.payment_models if config else []
    installed_pages = _installed_pages(project)
    wanted = pages_for(chosen)
    return {
        'installed': installed_pages is not None,
        'installed_pages': installed_pages or {},
        'pages': [
            {'key': key, **meta, 'enabled': wanted[key],
             'installed': bool(installed_pages and installed_pages.get(key))}
            for key, meta in PAGES.items()
        ],
        # Installed, but the chosen ways to charge have changed since.
        'out_of_date': installed_pages is not None and installed_pages != wanted,
        'frontend_dir': FRONTEND_DIR,
        'backend_dir': BACKEND_DIR,
    }


def install_payments(project, start_restyle=True) -> dict:
    """
    Write the payments app into the project (disk + database copy), for the
    ways to charge chosen in the console. Reinstalling refreshes Imagi's
    files and keeps the project's own look (payments.css, brand.ts).
    """
    config, _ = SellSettings.objects.get_or_create(project=project)
    if not config.payment_models:
        raise SellServiceError('Choose how you want to charge first.')

    before = _installed_pages(project)
    ensure_working_copy(project)
    file_service = CreateFileService(project=project)
    written = []
    for file_data in payments_files(project, config.payment_models):
        if file_data['name'] in RESTYLE_FILES and _project_has(project, file_data['name']):
            continue
        result = file_service.create_file(file_data)
        written.append(result['path'])

    after = pages_for(config.payment_models)
    new_pages = [key for key, on in after.items() if on and not (before or {}).get(key)]
    restyle_started = False
    if start_restyle and new_pages:
        from .payments_restyle_service import queue_payments_restyle
        restyle_started = queue_payments_restyle(
            project.id, project.user_id, [PAGES[key]['route'] for key in new_pages]
        ) is not None

    return {
        'files_written': written,
        'routes': [PAGES[key]['route'] for key, on in after.items() if on],
        'restyle_started': restyle_started,
        **app_payments_state(project),
    }
