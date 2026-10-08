"""
Threads' edits applied to the app as they are written (live_apply).
"""

import json
import os
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from apps.Imagi.Build.services import live_apply
from apps.Imagi.Build.services.version_control_service import (
    VersionControlService,
    task_worktree_path,
)
from apps.Imagi.Build.tests.test_task_worktrees import GitRepoTestMixin, _git


class LiveApplyTests(GitRepoTestMixin, SimpleTestCase):
    def setUp(self):
        self.repo = self._make_repo()
        self.vcs = VersionControlService()
        self.assertTrue(self.vcs.create_task_worktree(self.repo, 5)['success'])
        self.worktree = task_worktree_path(self.repo, 5)
        self.ctx = SimpleNamespace(
            project_id=None, project_path=self.repo,
            effective_project_path=self.worktree, live_apply=True,
        )
        no_logs = patch.object(live_apply, '_log_files', return_value=[])
        no_logs.start()
        self.addCleanup(no_logs.stop)

    def _write(self, root, name, content):
        path = os.path.join(root, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)

    def _read(self, root, name):
        path = os.path.join(root, name)
        return open(path).read() if os.path.exists(path) else None

    def _edit(self, name, content):
        """A thread's edit, as the file tools make it."""
        previous = live_apply.snapshot(self.ctx, name)
        if content is None:
            os.remove(os.path.join(self.worktree, name))
        else:
            self._write(self.worktree, name, content)
        return live_apply.mirror(self.ctx, name, previous)

    def test_an_edit_reaches_the_app_at_once(self):
        self.assertEqual(self._edit('app.txt', 'blue header'), {'live': True})
        self.assertEqual(self._read(self.repo, 'app.txt'), 'blue header')
        # The thread's later edits to its own file keep flowing through.
        self.assertEqual(self._edit('app.txt', 'bluer header'), {'live': True})
        self.assertEqual(self._read(self.repo, 'app.txt'), 'bluer header')

    def test_new_and_deleted_files_reach_the_app(self):
        self._edit('src/new.vue', '<template />')
        self.assertEqual(self._read(self.repo, 'src/new.vue'), '<template />')
        self._edit('app.txt', None)
        self.assertIsNone(self._read(self.repo, 'app.txt'))

    def test_a_file_someone_else_changed_waits_for_the_merge(self):
        self._write(self.repo, 'app.txt', 'another thread was here')
        outcome = self._edit('app.txt', 'mine')
        self.assertFalse(outcome['live'])
        self.assertEqual(self._read(self.repo, 'app.txt'), 'another thread was here')

    def test_the_merge_at_the_end_still_lands_cleanly(self):
        self._edit('app.txt', 'blue header')
        self._edit('src/new.vue', '<template />')
        result = self.vcs.merge_task_worktree(self.repo, 5)
        self.assertTrue(result['success'], result)
        self.assertEqual(self._read(self.repo, 'app.txt'), 'blue header')
        self.assertEqual(_git(self.repo, 'status', '--porcelain').stdout, '')

    def test_drafts_and_canonical_runs_are_not_copied(self):
        for ctx in (
            SimpleNamespace(**{**vars(self.ctx), 'live_apply': False}),
            SimpleNamespace(**{**vars(self.ctx), 'effective_project_path': self.repo}),
        ):
            with self.subTest(ctx=ctx):
                self.assertFalse(live_apply.applies_to(ctx))
                self.assertEqual(live_apply.mirror(ctx, 'app.txt', b'hello'), {})

    def test_a_discarded_thread_is_taken_back_out(self):
        self._edit('app.txt', 'blue header')
        self._edit('src/new.vue', '<template />')
        self._write(self.repo, 'other.txt', 'not the thread')
        conversation = SimpleNamespace(id=5)

        restored = live_apply.revert(conversation, self.repo, self.worktree)

        self.assertEqual(sorted(restored), ['app.txt', 'src/new.vue'])
        self.assertEqual(self._read(self.repo, 'app.txt'), 'hello')
        self.assertIsNone(self._read(self.repo, 'src/new.vue'))
        self.assertEqual(self._read(self.repo, 'other.txt'), 'not the thread')

    def test_errors_after_an_edit_go_back_to_the_thread(self):
        log = os.path.join(tempfile.mkdtemp(), 'p_frontend.log')
        with open(log, 'w') as f:
            f.write('[vite] old error from before\n')
        with patch.object(live_apply, '_log_files', return_value=[log]), \
                patch.object(live_apply, '_console_errors_since', return_value=[
                    "TypeError: Cannot read properties of undefined (reading 'name')",
                ]):
            mark = live_apply.Mark(self.ctx)
            previous = live_apply.snapshot(self.ctx, 'app.txt')
            self._write(self.worktree, 'app.txt', 'broken')
            with open(log, 'a') as f:
                f.write('  VITE ready\n[vite] Internal server error: Unexpected token (3:4)\n')
            with patch.object(live_apply, 'SETTLE_SECONDS', 0):
                result = live_apply.apply_edit(self.ctx, 'app.txt', previous, mark)

        self.assertTrue(result['applied_to_app'])
        self.assertEqual(result['preview_errors'], [
            '[frontend server] [vite] Internal server error: Unexpected token (3:4)',
            "[browser console] TypeError: Cannot read properties of undefined (reading 'name')",
        ])
        self.assertIn('fix them', result['instruction'])


class LiveApplyToolTests(GitRepoTestMixin, SimpleTestCase):
    """The file tools carry the live result back to the thread."""

    def test_update_file_reports_what_the_app_made_of_it(self):
        from apps.Imagi.Build.services import tools

        ctx = SimpleNamespace(live_apply=True)
        with patch.object(tools, '_live_start', return_value=(b'old', object())), \
                patch.object(live_apply, 'apply_edit', return_value={
                    'applied_to_app': True, 'preview_errors': ['[browser console] boom'],
                }):
            answer = json.loads(tools._live_finish(ctx, 'a.vue', (b'old', object()), {
                'success': True, 'path': 'a.vue',
            }))
        self.assertEqual(answer['preview_errors'], ['[browser console] boom'])
        self.assertTrue(answer['success'])
