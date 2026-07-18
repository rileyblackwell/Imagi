"""Prewarm the shared frontend dependency store.

Installs the canonical generated-frontend dependency set into the shared store
(``settings.FRONTEND_DEP_STORE_ROOT``) so that later project creations and
previews link against it instantly instead of each running ``npm install``.

Run at Docker build time so the install is baked into the image and survives
every production redeploy:

    python manage.py warm_frontend_deps

The install slot is content-addressed by the dependency set, so this produces
exactly the slot that generated projects (which ship the same package.json)
resolve to at runtime — no hardcoded hash to keep in sync.
"""

import json
import os
import tempfile

from django.core.management.base import BaseCommand

from apps.Imagi.Build.services import frontend_dependencies as deps
from apps.Imagi.ProjectManager.services.codegen import templates as tpl


class Command(BaseCommand):
    help = "Install the canonical frontend dependency set into the shared store."

    def handle(self, *args, **options):
        package_json = tpl.frontend_package_json('imagi-template')
        signature = deps.dependency_signature(package_json)
        self.stdout.write(f"Warming frontend dependency store (slot {signature})...")
        self.stdout.write(f"Store root: {deps.store_root()}")

        # ensure_store reads a package.json off disk; stage the canonical one in
        # a temp file. The store slot it targets depends only on the dependency
        # set, so this warms the exact slot real projects will link to.
        with tempfile.TemporaryDirectory() as tmp:
            package_json_path = os.path.join(tmp, 'package.json')
            with open(package_json_path, 'w') as f:
                json.dump(package_json, f, indent=2)

            node_modules = deps.ensure_store(package_json_path)

        if not node_modules:
            # Non-fatal for an image build: runtime falls back to per-project
            # installs. Signal failure so a build can choose to fail loudly.
            self.stderr.write("Failed to warm frontend dependency store.")
            raise SystemExit(1)

        self.stdout.write(self.style.SUCCESS(f"Frontend dependency store ready: {node_modules}"))
