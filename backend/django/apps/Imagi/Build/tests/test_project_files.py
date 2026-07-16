"""
Tests for the database copy of project files (ProjectFile) and the sync
layer in services.project_files_service.

Covers:
- write-through: create/update/edit/delete via the file services and agent
  tool implementations keep ProjectFile rows in sync with disk
- bulk sync: import_project_from_disk (backfill) and hydrate_project
  (materializing a working copy from the database)
- ensure_working_copy: production cold-start behaviour
"""

import os
import shutil
import tempfile

from django.contrib.auth.models import User
from django.test import TestCase

from apps.Imagi.ProjectManager.models import Project as PMProject
from apps.Imagi.Build.models import ProjectFile
from apps.Imagi.Build.services import project_files_service
from apps.Imagi.Build.services.create_file_service import CreateFileService
from apps.Imagi.Build.services.delete_file_service import DeleteFileService
from apps.Imagi.Build.services.directory_service import DirectoryService
from apps.Imagi.Build.services.view_file_service import ViewFileService
from apps.Imagi.Build.services.tools import _sync_db_mirror, edit_file_impl


class ProjectFilesTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='pfuser', password='testpass123')
        self.project_root = tempfile.mkdtemp(prefix='project_files_')
        self.project = PMProject.objects.create(
            user=self.user, name="PF Project", project_path=self.project_root
        )
        self.addCleanup(lambda: shutil.rmtree(self.project_root, ignore_errors=True))

    def _write_disk_file(self, rel_path, content):
        full = os.path.join(self.project_root, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w', encoding='utf-8') as f:
            f.write(content)
        return full

    def _db_content(self, rel_path):
        row = ProjectFile.objects.filter(project=self.project, path=rel_path).first()
        return row.content if row else None


class WriteThroughTests(ProjectFilesTestCase):
    def test_create_file_service_writes_db_copy(self):
        service = CreateFileService(project=self.project)
        service.create_file({
            'name': 'frontend/vuejs/src/apps/home/views/Home.vue',
            'content': '<template><div>Home</div></template>',
            'type': 'vue',
        })

        self.assertEqual(
            self._db_content('frontend/vuejs/src/apps/home/views/Home.vue'),
            '<template><div>Home</div></template>',
        )

    def test_update_file_service_writes_db_copy(self):
        self._write_disk_file('backend/django/apps/api/views.py', 'old = 1\n')
        service = ViewFileService(project=self.project)
        service.update_file('backend/django/apps/api/views.py', 'new = 2\n')

        self.assertEqual(self._db_content('backend/django/apps/api/views.py'), 'new = 2\n')

    def test_edit_file_impl_writes_db_copy(self):
        self._write_disk_file('frontend/vuejs/src/main.ts', "const app = 'imagi'\n")
        result = edit_file_impl(
            self.project, 'frontend/vuejs/src/main.ts',
            old_string="'imagi'", new_string="'imagi-app'",
        )

        self.assertTrue(result['success'])
        self.assertEqual(
            self._db_content('frontend/vuejs/src/main.ts'),
            "const app = 'imagi-app'\n",
        )

    def test_delete_file_service_removes_db_copy(self):
        self._write_disk_file('frontend/vuejs/src/old.ts', 'export {}\n')
        project_files_service.record_file(self.project, 'frontend/vuejs/src/old.ts')
        self.assertIsNotNone(self._db_content('frontend/vuejs/src/old.ts'))

        DeleteFileService(project=self.project).delete_file('frontend/vuejs/src/old.ts')

        self.assertIsNone(self._db_content('frontend/vuejs/src/old.ts'))

    def test_delete_directory_removes_db_copies_under_prefix(self):
        self._write_disk_file('frontend/vuejs/src/apps/blog/index.ts', 'export {}\n')
        self._write_disk_file('frontend/vuejs/src/apps/blog/views/Blog.vue', '<template/>')
        self._write_disk_file('frontend/vuejs/src/apps/home/index.ts', 'export {}\n')
        project_files_service.import_project_from_disk(self.project)
        self.assertEqual(self.project.files.count(), 3)

        DirectoryService(project=self.project).delete_directory(
            'frontend/vuejs/src/apps/blog', recursive=True
        )

        remaining = list(self.project.files.values_list('path', flat=True))
        self.assertEqual(remaining, ['frontend/vuejs/src/apps/home/index.ts'])

    def test_non_syncable_files_are_not_stored(self):
        row = project_files_service.record_file(
            self.project, 'frontend/vuejs/src/logo.png', content='binary-ish'
        )
        self.assertIsNone(row)
        self.assertEqual(self.project.files.count(), 0)


class SyncDbMirrorTests(ProjectFilesTestCase):
    """Disk is the source of truth: a mirror inconsistency after a successful
    disk operation is repaired in place, never surfaced as a tool failure."""

    def test_repairs_missing_row_after_disk_write(self):
        self._write_disk_file('frontend/vuejs/src/New.vue', '<template/>')

        _sync_db_mirror(self.project, 'frontend/vuejs/src/New.vue', should_exist=True)

        self.assertEqual(self._db_content('frontend/vuejs/src/New.vue'), '<template/>')

    def test_removes_stale_row_after_disk_delete(self):
        ProjectFile.objects.create(
            project=self.project, path='frontend/vuejs/src/Old.vue', content='stale'
        )

        _sync_db_mirror(self.project, 'frontend/vuejs/src/Old.vue', should_exist=False)

        self.assertIsNone(self._db_content('frontend/vuejs/src/Old.vue'))

    def test_ignores_non_syncable_paths(self):
        _sync_db_mirror(self.project, 'frontend/vuejs/src/logo.png', should_exist=True)
        self.assertEqual(self.project.files.count(), 0)

    def test_oversized_file_never_errors(self):
        # Files past the DB size cap stay disk-only; the sync must not raise.
        big = 'x' * (project_files_service.MAX_SYNCED_FILE_BYTES + 1)
        self._write_disk_file('frontend/vuejs/src/big.txt', big)

        _sync_db_mirror(self.project, 'frontend/vuejs/src/big.txt', should_exist=True)

        self.assertIsNone(self._db_content('frontend/vuejs/src/big.txt'))


class BulkSyncTests(ProjectFilesTestCase):
    def test_import_project_from_disk_backfills_and_prunes(self):
        self._write_disk_file('frontend/vuejs/src/App.vue', '<template/>')
        self._write_disk_file('backend/django/manage.py', '# manage\n')
        # A stale row whose file no longer exists on disk
        ProjectFile.objects.create(project=self.project, path='frontend/vuejs/src/Gone.vue', content='x')
        # Files inside skip dirs are never imported
        self._write_disk_file('frontend/vuejs/node_modules/pkg/index.js', 'skip me')

        result = project_files_service.import_project_from_disk(self.project)

        self.assertEqual(result['synced'], 2)
        self.assertEqual(result['pruned'], 1)
        self.assertEqual(
            sorted(self.project.files.values_list('path', flat=True)),
            ['backend/django/manage.py', 'frontend/vuejs/src/App.vue'],
        )

    def test_hydrate_project_materializes_files_from_db(self):
        ProjectFile.objects.create(
            project=self.project, path='frontend/vuejs/src/App.vue', content='<template/>'
        )
        ProjectFile.objects.create(
            project=self.project, path='backend/django/manage.py', content='# manage\n'
        )

        result = project_files_service.hydrate_project(self.project)

        self.assertEqual(result['written'], 2)
        with open(os.path.join(self.project_root, 'frontend/vuejs/src/App.vue')) as f:
            self.assertEqual(f.read(), '<template/>')

    def test_hydrate_does_not_clobber_existing_files_without_overwrite(self):
        self._write_disk_file('frontend/vuejs/src/App.vue', 'local edit')
        ProjectFile.objects.create(
            project=self.project, path='frontend/vuejs/src/App.vue', content='db copy'
        )

        result = project_files_service.hydrate_project(self.project)

        self.assertEqual(result['written'], 0)
        self.assertEqual(result['skipped'], 1)
        with open(os.path.join(self.project_root, 'frontend/vuejs/src/App.vue')) as f:
            self.assertEqual(f.read(), 'local edit')

    def test_ensure_working_copy_hydrates_empty_directory(self):
        ProjectFile.objects.create(
            project=self.project, path='frontend/vuejs/src/App.vue', content='<template/>'
        )
        # Simulate a production cold start: empty working directory
        shutil.rmtree(self.project_root)

        hydrated = project_files_service.ensure_working_copy(self.project)

        self.assertTrue(hydrated)
        self.assertTrue(
            os.path.isfile(os.path.join(self.project_root, 'frontend/vuejs/src/App.vue'))
        )

    def test_ensure_working_copy_noop_when_disk_populated(self):
        self._write_disk_file('frontend/vuejs/src/App.vue', 'on disk')
        ProjectFile.objects.create(
            project=self.project, path='frontend/vuejs/src/App.vue', content='db copy'
        )

        self.assertFalse(project_files_service.ensure_working_copy(self.project))
        with open(os.path.join(self.project_root, 'frontend/vuejs/src/App.vue')) as f:
            self.assertEqual(f.read(), 'on disk')


class ReadFallbackTests(ProjectFilesTestCase):
    def test_get_file_content_falls_back_to_db(self):
        ProjectFile.objects.create(
            project=self.project, path='frontend/vuejs/src/App.vue', content='db only'
        )

        service = ViewFileService(project=self.project)
        content = service.get_file_content('frontend/vuejs/src/App.vue')

        self.assertEqual(content, 'db only')
