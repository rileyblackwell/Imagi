"""
Prebuilt app templates for Imagi Builder.
Generates both frontend (Vue) and backend (Django) files for default apps: home, auth.

'about' and 'contact' are prebuilt too, but as frontend-only PAGE apps: they
are static marketing pages with nothing to serve, and they exist mainly so the
initial build can hand each of its parallel subagents a single file to rewrite
(see pages.py). They are kept out of PREBUILT_MAP/DEFAULT_APPS because that
path also registers a Django app in INSTALLED_APPS, which these do not have.

Payment pages are intentionally not scaffolded here: users install them
from the Sell workspace's template gallery (apps.Imagi.Sell.services
.payment_templates), which drops in secure, Stripe-hosted checkout pages
keyed to their project.

All file paths returned are relative to the project's root, so they can be written
with FileService.create_file as-is.
"""
from __future__ import annotations

from typing import Dict, List

from .home import home_app_files
from .auth import auth_app_files
from .pages import about_app_files, contact_app_files


PREBUILT_MAP = {
    'home': home_app_files,
    'auth': auth_app_files,
}

# Frontend-only page apps, scaffolded alongside the default apps.
PAGE_APP_MAP = {
    'about': about_app_files,
    'contact': contact_app_files,
}


def generate_prebuilt_app_files(app_name: str, app_description: str | None = None) -> List[Dict[str, str]]:
    key = (app_name or '').lower()
    func = PREBUILT_MAP.get(key)
    if not func:
        return []
    return func()


def generate_page_app_files(app_name: str) -> List[Dict[str, str]]:
    """Frontend-only files for a prebuilt page app ('about', 'contact')."""
    func = PAGE_APP_MAP.get((app_name or '').lower())
    if not func:
        return []
    return func()


__all__ = [
    'home_app_files',
    'auth_app_files',
    'about_app_files',
    'contact_app_files',
    'PREBUILT_MAP',
    'PAGE_APP_MAP',
    'generate_prebuilt_app_files',
    'generate_page_app_files',
]
