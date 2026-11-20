"""
Delete one account with everything it owns.

Shared by the in-app "Delete account" action (Apple requires apps that let
people register to let them delete their account from inside the app) and the
``delete_all_users`` clean-start command.

Each project goes through ProjectManagementService.delete_project, so its
working copy, task worktrees and preview sidecar files on PROJECTS_ROOT are
removed with the row; the account's own folder under PROJECTS_ROOT goes last,
which also catches soft-deleted projects' leftovers. Deleting the user then
cascades through every other row that points at it (usage, billing, tokens,
threads). Stripe is left alone.
"""

import os
import shutil

from django.conf import settings

from apps.Imagi.ProjectManager.models import Project
from apps.Imagi.ProjectManager.services.project_management_service import ProjectManagementService


def delete_account(user):
    """Delete ``user``, their projects and their files. Returns the project count."""
    service = ProjectManagementService(user)
    projects = 0
    # Soft-deleted projects too: their rows and files go the same way.
    for project in Project.objects.filter(user=user):
        service.delete_project(project)
        projects += 1
    user_root = os.path.join(settings.PROJECTS_ROOT, str(user.id))
    shutil.rmtree(user_root, ignore_errors=True)
    user.delete()
    return projects
