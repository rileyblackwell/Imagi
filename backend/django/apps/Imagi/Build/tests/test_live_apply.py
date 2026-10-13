"""
Threads' edits applied to the app as they are written (live_apply).
"""

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


class LiveApplyRepoMixin(GitRepoTestMixin):
    """A project repo with thread 5's worktree, as live apply sees them."""

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


class LiveApplyTests(LiveApplyRepoMixin, SimpleTestCase):
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

    def test_a_new_migration_is_applied_to_the_running_app(self):
        from apps.Imagi.Build.services import live_preview_service

        with patch.object(live_preview_service, 'schedule_migrate') as migrate:
            self._edit('backend/django/shop/models.py', 'class Order: pass')
            migrate.assert_not_called()
            self._edit('backend/django/shop/migrations/0002_order.py', '# migration')
            migrate.assert_called_once_with(None)

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


class CompileCheckOnWriteTests(LiveApplyRepoMixin, SimpleTestCase):
    """A thread's component that doesn't compile is answered with the errors
    and kept out of the app, which keeps its last good version."""

    def setUp(self):
        from apps.Imagi.Build.tests.test_frontend_integrity import _compiler_available

        if not _compiler_available():
            self.skipTest('node and @vue/compiler-sfc are not installed')
        super().setUp()
        self.ctx.live_held_back = {}

    def _tool_edit(self, name, content):
        import json
        from apps.Imagi.Build.services import tools

        before = tools._live_start(self.ctx, name)
        self._write(self.worktree, name, content)
        return json.loads(tools._live_finish(self.ctx, name, before, {'success': True, 'path': name}))

    def test_a_broken_component_is_answered_with_its_errors_and_held_back(self):
        result = self._tool_edit('src/Menu.vue', '<template><section></div></section></template>')
        self.assertEqual(result['compile_errors'], ['Invalid end tag. (line 1)'])
        self.assertFalse(result['applied_to_app'])
        self.assertIn('Fix these errors', result['instruction'])
        self.assertIsNone(self._read(self.repo, 'src/Menu.vue'))

    def test_the_fixed_component_then_goes_live(self):
        self._tool_edit('src/Menu.vue', '<template><section></div></section></template>')
        result = self._tool_edit('src/Menu.vue', '<template><section>Menu</section></template>')
        self.assertNotIn('compile_errors', result)
        self.assertTrue(result['applied_to_app'])
        self.assertEqual(self._read(self.repo, 'src/Menu.vue'), '<template><section>Menu</section></template>')
