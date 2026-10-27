"""
Delete every account that joined before a cutoff, with everything it owns.

For a clean start while Imagi has no real users. Each account's projects go
through ProjectManagementService.delete_project, so their working copies,
task worktrees and preview sidecar files on PROJECTS_ROOT are removed along
with the rows; the account's own folder under PROJECTS_ROOT goes last, which
also catches soft-deleted projects' leftovers. Deleting the user then cascades
through every other row that points at it (usage, billing, tokens, threads).

Stripe is left alone: customers and subscriptions stay in Stripe.

The cutoff makes a repeat run harmless: an account registered after it is
never touched. Without --yes the command only reports what it would delete.

No one can reach a shell on Railway, so migrate_locked runs this on the
workspace tier (the one that owns the PROJECTS_ROOT volume) whenever
WIPE_USERS_JOINED_BEFORE is set there to an ISO 8601 time. Unset it after the
run.

Usage:
    python manage.py delete_all_users --joined-before 2026-10-27T17:00:00Z
    python manage.py delete_all_users --joined-before 2026-10-27T17:00:00Z --yes
"""

import datetime
import logging
import os
import shutil

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from apps.Imagi.ProjectManager.models import Project
from apps.Imagi.ProjectManager.services.project_management_service import ProjectManagementService

logger = logging.getLogger(__name__)


def parse_cutoff(value):
    """Parse an ISO 8601 time; a naive one is read as UTC."""
    cutoff = parse_datetime((value or '').strip())
    if cutoff is None:
        raise CommandError(f'Not an ISO 8601 time: {value!r}')
    if timezone.is_naive(cutoff):
        cutoff = timezone.make_aware(cutoff, datetime.timezone.utc)
    return cutoff


def delete_users_joined_before(cutoff):
    """Delete accounts that joined before ``cutoff``. Returns (users, projects)."""
    users = list(get_user_model().objects.filter(date_joined__lt=cutoff).order_by('id'))
    projects = 0
    for user in users:
        service = ProjectManagementService(user)
        # Soft-deleted projects too: their rows and files go the same way.
        for project in Project.objects.filter(user=user):
            service.delete_project(project)
            projects += 1
        user_root = os.path.join(settings.PROJECTS_ROOT, str(user.id))
        shutil.rmtree(user_root, ignore_errors=True)
        user.delete()
    return len(users), projects


class Command(BaseCommand):
    help = 'Delete every account that joined before a cutoff, with its projects and files.'

    def add_arguments(self, parser):
        parser.add_argument('--joined-before', required=True,
                            help='ISO 8601 time; accounts that joined before it are deleted.')
        parser.add_argument('--yes', action='store_true',
                            help='Actually delete. Without it, only report what would go.')

    def handle(self, *args, **options):
        cutoff = parse_cutoff(options['joined_before'])
        users = get_user_model().objects.filter(date_joined__lt=cutoff)
        projects = Project.objects.filter(user__in=users)
        if not options['yes']:
            self.stdout.write(
                f'delete_all_users: would delete {users.count()} account(s) and '
                f'{projects.count()} project(s) joined before {cutoff.isoformat()} '
                f'(dry run; pass --yes to delete)'
            )
            return
        deleted_users, deleted_projects = delete_users_joined_before(cutoff)
        message = (
            f'delete_all_users: deleted {deleted_users} account(s) and '
            f'{deleted_projects} project(s) joined before {cutoff.isoformat()}; '
            f'{get_user_model().objects.count()} account(s) remain'
        )
        logger.info(message)
        self.stdout.write(message)
