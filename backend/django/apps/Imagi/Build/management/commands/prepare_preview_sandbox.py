"""One-time volume prep for the deprivileged preview (PREVIEW_SANDBOX_USER).

New project files created after the sandbox is switched on are already made
group-owned and group-writable (the server's umask plus the setgid bit on the
project dirs). Files that existed *before* the switch were created root-owned
and not group-writable, so the deprivileged preview can read but not overwrite
them. This command fixes the existing tree once: it points PROJECTS_ROOT and the
frontend dependency store at the sandbox group, turns on group read/write (and
the setgid bit on directories, so new children keep inheriting the group), and
leaves ownership otherwise untouched.

Run it once, as root, on the workspace tier after setting PREVIEW_SANDBOX_USER:

    python manage.py prepare_preview_sandbox

Idempotent — safe to run again. With --dry-run it only reports what it would
change.
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.Imagi.Build.services import sandbox


class Command(BaseCommand):
    help = "Prepare existing preview files for the deprivileged preview sandbox."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true',
                            help="Report what would change without changing it.")

    def handle(self, *args, **options):
        identity = sandbox.sandbox_identity()
        if identity is None:
            raise CommandError(
                "The preview sandbox is not active here: set PREVIEW_SANDBOX_USER "
                "to an existing user and run this as root on the workspace tier."
            )
        uid, gid, name = identity
        dry = options['dry_run']
        self.stdout.write(f"Preparing preview files for sandbox user {name!r} (gid {gid}).")

        roots = [settings.PROJECTS_ROOT]
        dep_store = getattr(settings, 'FRONTEND_DEP_STORE_ROOT', '')
        if dep_store:
            roots.append(dep_store)

        changed = 0
        for root in roots:
            if not root or not os.path.isdir(root):
                self.stdout.write(f"  skipping {root!r} (not a directory)")
                continue
            self.stdout.write(f"  {root}")
            changed += self._prepare(root, gid, dry)
        verb = "would change" if dry else "changed"
        self.stdout.write(self.style.SUCCESS(f"Done: {verb} {changed} path(s)."))

    def _prepare(self, root, gid, dry):
        changed = 0
        for current, dirs, files in os.walk(root):
            for name in [current] + [os.path.join(current, f) for f in files]:
                if self._fix(name, gid, os.path.isdir(name), dry):
                    changed += 1
        return changed

    def _fix(self, path, gid, is_dir, dry):
        try:
            st = os.lstat(path)
        except OSError:
            return False
        # Leave symlinks alone: follow neither their ownership nor their target.
        if not (is_dir or os.path.isfile(path)):
            return False
        want_mode = (st.st_mode & 0o7777) | (0o2770 if is_dir else 0o660)
        needs = st.st_gid != gid or (st.st_mode & 0o7777) != want_mode
        if not needs:
            return False
        if not dry:
            try:
                os.chown(path, -1, gid)
                os.chmod(path, want_mode)
            except OSError as exc:
                self.stderr.write(f"    could not fix {path}: {exc}")
                return False
        return True
