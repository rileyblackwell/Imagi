"""
Home app prebuilt template.
Generates frontend (Vue) and backend (Django) files for the home app.
"""
from __future__ import annotations

from typing import Dict, List

from .shared import _frontend_scaffold, _backend_scaffold


def home_app_files() -> List[Dict[str, str]]:
    app_name = 'home'
    cap = 'Home'
    welcome = 'Welcome to your project home app.'
    files: List[Dict[str, str]] = []
    files += _frontend_scaffold(app_name, cap, welcome)
    files += _backend_scaffold(app_name, cap)
    return files
