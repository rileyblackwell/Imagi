"""
Build services.

Builder workspace services (files, directories, preview, version control,
app creation, AI model definitions) and agent services (OpenAI Agents SDK)
merged from the former Builder and Agents sub-apps.

Import from the specific submodule, e.g.::

    from apps.Imagi.Build.services.base_agent import ImagiAgentService
    from apps.Imagi.Build.services.models_service import MODELS

This package intentionally has no eager re-exports: models.py imports
services.models_service at app-load time, and re-exporting base_agent here
(which imports models) would create a circular import.
"""
