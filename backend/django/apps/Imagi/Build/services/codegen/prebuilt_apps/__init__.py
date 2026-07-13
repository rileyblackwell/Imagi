"""
Prebuilt app templates for Imagi Builder.
Generates both frontend (Vue) and backend (Django) files for default apps: home, auth.

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


PREBUILT_MAP = {
    'home': home_app_files,
    'auth': auth_app_files,
}


def generate_prebuilt_app_files(app_name: str, app_description: str | None = None) -> List[Dict[str, str]]:
    key = (app_name or '').lower()
    func = PREBUILT_MAP.get(key)
    if not func:
        return []
    return func()


__all__ = [
    'home_app_files',
    'auth_app_files',
    'PREBUILT_MAP',
    'generate_prebuilt_app_files',
]
