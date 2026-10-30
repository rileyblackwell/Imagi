import os
import shutil
import tempfile
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from rest_framework.authtoken.models import Token

from apps.Imagi.ProjectManager.models import Project

User = get_user_model()


class DeleteAllUsersCommandTests(TestCase):
    """The clean-start wipe: every account that joined before the cutoff goes,
    with its projects' rows and files; anyone who joined after is untouched."""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='imagi_wipe_tests_')
        self.addCleanup(shutil.rmtree, self.root, True)
        override = override_settings(PROJECTS_ROOT=self.root)
        override.enable()
        self.addCleanup(override.disable)

        self.cutoff = '2026-10-27T17:00:00Z'
        self.old = User.objects.create_user(username='old', password='pw-12345')
        User.objects.filter(pk=self.old.pk).update(date_joined='2026-10-01T00:00:00Z')
        Token.objects.create(user=self.old)
        self.new = User.objects.create_user(username='new', password='pw-12345')
        User.objects.filter(pk=self.new.pk).update(date_joined='2026-10-28T00:00:00Z')

        self.old_dir = os.path.join(self.root, str(self.old.id), 'shop')
        os.makedirs(self.old_dir)
        os.makedirs(self.old_dir + '--wt-7')
        os.makedirs(os.path.join(self.root, str(self.old.id), 'soft-deleted-leftover'))
        Project.objects.create(user=self.old, name='Shop', project_dir=f'{self.old.id}/shop')
        Project.objects.create(user=self.old, name='Gone', is_active=False)
        self.new_dir = os.path.join(self.root, str(self.new.id), 'blog')
        os.makedirs(self.new_dir)
        self.new_project = Project.objects.create(
            user=self.new, name='Blog', project_dir=f'{self.new.id}/blog')

    def _run(self, *args):
        out = StringIO()
        call_command('delete_all_users', '--joined-before', self.cutoff, *args, stdout=out)
        return out.getvalue()

    def test_dry_run_deletes_nothing(self):
        out = self._run()

        self.assertIn('would delete 1 account(s) and 2 project(s)', out)
        self.assertEqual(User.objects.count(), 2)
        self.assertTrue(os.path.isdir(self.old_dir))

    def test_deletes_accounts_before_the_cutoff_with_their_projects_and_files(self):
        out = self._run('--yes')

        self.assertIn('deleted 1 account(s) and 2 project(s)', out)
        self.assertEqual(list(User.objects.values_list('username', flat=True)), ['new'])
        self.assertEqual(list(Project.objects.all()), [self.new_project])
        self.assertFalse(Token.objects.exists())
        self.assertFalse(os.path.exists(os.path.join(self.root, str(self.old.id))))
        self.assertTrue(os.path.isdir(self.new_dir))

    def test_a_second_run_leaves_later_signups_alone(self):
        self._run('--yes')
        out = self._run('--yes')

        self.assertIn('deleted 0 account(s)', out)
        self.assertEqual(User.objects.count(), 1)

    def test_rejects_a_cutoff_that_is_not_a_time(self):
        with self.assertRaises(CommandError):
            call_command('delete_all_users', '--joined-before', 'yesterday', stdout=StringIO())
