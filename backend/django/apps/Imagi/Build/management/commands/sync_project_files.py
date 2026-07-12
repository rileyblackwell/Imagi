"""
Sync project files between the database copy and the working copy on disk.

Usage:
    # Backfill the database from disk for every active project
    python manage.py sync_project_files --to-db

    # Materialize working copies on disk from the database
    python manage.py sync_project_files --to-disk

    # Limit to one project
    python manage.py sync_project_files --to-db --project 42
"""

import os

from django.core.management.base import BaseCommand, CommandError

from apps.Imagi.ProjectManager.models import Project
from apps.Imagi.Build.services import project_files_service


class Command(BaseCommand):
    help = "Sync project files between the database copy and the on-disk working copy."

    def add_arguments(self, parser):
        direction = parser.add_mutually_exclusive_group(required=True)
        direction.add_argument(
            '--to-db', action='store_true',
            help='Import files from each project directory into the database (backfill).',
        )
        direction.add_argument(
            '--to-disk', action='store_true',
            help='Write database file copies out to each project directory.',
        )
        parser.add_argument(
            '--project', type=int, default=None,
            help='Only sync the project with this ID.',
        )
        parser.add_argument(
            '--overwrite', action='store_true',
            help='With --to-disk: overwrite files that already exist on disk.',
        )

    def handle(self, *args, **options):
        projects = Project.objects.filter(is_active=True)
        if options['project']:
            projects = projects.filter(id=options['project'])
            if not projects.exists():
                raise CommandError(f"No active project with id {options['project']}")

        for project in projects:
            if options['to_db']:
                if not project.project_path or not os.path.isdir(project.project_path):
                    self.stdout.write(self.style.WARNING(
                        f"[{project.id}] {project.name}: no directory on disk, skipped"
                    ))
                    continue
                result = project_files_service.import_project_from_disk(project)
                self.stdout.write(self.style.SUCCESS(
                    f"[{project.id}] {project.name}: {result['synced']} files -> db, "
                    f"{result['pruned']} stale rows pruned"
                ))
            else:
                if not project.files.exists():
                    self.stdout.write(self.style.WARNING(
                        f"[{project.id}] {project.name}: no database files, skipped"
                    ))
                    continue
                os.makedirs(project.project_path, exist_ok=True)
                result = project_files_service.hydrate_project(
                    project, overwrite=options['overwrite']
                )
                self.stdout.write(self.style.SUCCESS(
                    f"[{project.id}] {project.name}: {result['written']} files -> disk, "
                    f"{result['skipped']} already present"
                ))
