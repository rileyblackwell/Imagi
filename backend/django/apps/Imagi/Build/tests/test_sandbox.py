"""Tests for the deprivileged-preview helper (services/sandbox.py).

The disabled-path tests run everywhere. The live privilege-drop test needs to
be root with the sandbox user present (the production image and a root dev
container), so it skips elsewhere rather than failing.
"""

import os
import pwd
import subprocess
import tempfile
from unittest import skipUnless
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from apps.Imagi.Build.services import sandbox


def _reset_cache():
    sandbox._identity_cache = sandbox._IDENTITY_SENTINEL


SANDBOX_USER = 'imagipreview'


def _user_exists(name):
    try:
        pwd.getpwnam(name)
        return True
    except KeyError:
        return False


CAN_DROP = hasattr(os, 'geteuid') and os.geteuid() == 0 and _user_exists(SANDBOX_USER)


class SandboxDisabledTests(SimpleTestCase):
    """With no PREVIEW_SANDBOX_USER, every hook is inert."""

    def setUp(self):
        _reset_cache()
        self.addCleanup(_reset_cache)

    @override_settings(PREVIEW_SANDBOX_USER='')
    def test_inactive_when_unset(self):
        self.assertFalse(sandbox.is_active())
        self.assertEqual(sandbox.child_privilege_kwargs(), {})

    @override_settings(PREVIEW_SANDBOX_USER='')
    def test_prepare_tree_is_a_no_op_when_unset(self):
        with tempfile.TemporaryDirectory() as d:
            before = os.stat(d).st_mode
            sandbox.prepare_tree(d)  # must not raise or change anything
            self.assertEqual(os.stat(d).st_mode, before)

    @override_settings(PREVIEW_SANDBOX_USER='definitely-not-a-real-user')
    def test_inactive_when_user_is_missing(self):
        # A misconfigured name must fall back to today's behaviour, not crash.
        self.assertFalse(sandbox.is_active())
        self.assertEqual(sandbox.child_privilege_kwargs(), {})

    @override_settings(PREVIEW_SANDBOX_USER=SANDBOX_USER)
    def test_inactive_when_not_root(self):
        _reset_cache()
        with patch('os.geteuid', return_value=1000):
            self.assertFalse(sandbox.is_active())
            self.assertEqual(sandbox.child_privilege_kwargs(), {})


@skipUnless(CAN_DROP, 'needs root and the sandbox user to drop privileges')
@override_settings(PREVIEW_SANDBOX_USER=SANDBOX_USER)
class SandboxActiveTests(SimpleTestCase):
    """The real privilege drop, where the environment allows it."""

    def setUp(self):
        _reset_cache()
        self.addCleanup(_reset_cache)
        self.uid, self.gid, _ = pwd.getpwnam(SANDBOX_USER)[2], pwd.getpwnam(SANDBOX_USER)[3], None

    def test_kwargs_name_the_sandbox_user(self):
        kwargs = sandbox.child_privilege_kwargs()
        self.assertEqual(kwargs['user'], self.uid)
        self.assertEqual(kwargs['group'], self.gid)
        self.assertEqual(kwargs['umask'], sandbox.SANDBOX_UMASK)

    def test_child_runs_as_the_sandbox_user(self):
        out = subprocess.run(
            ['id', '-u'], capture_output=True, text=True,
            **sandbox.child_privilege_kwargs(),
        )
        self.assertEqual(out.stdout.strip(), str(self.uid))

    def test_child_cannot_read_a_root_only_file(self):
        # The /proc/<imagi-pid>/environ class of leak: a root-owned secret the
        # deprivileged child must not be able to read.
        with tempfile.NamedTemporaryFile('w', delete=False) as f:
            f.write('ANTHROPIC_KEY=secret')
            secret = f.name
        self.addCleanup(os.unlink, secret)
        os.chmod(secret, 0o600)  # root-owned, root-only
        result = subprocess.run(
            ['cat', secret], capture_output=True, text=True,
            **sandbox.child_privilege_kwargs(),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('secret', result.stdout)

    def test_prepare_tree_recursive_fixes_existing_files(self):
        # A project tree created before the sandbox was on: root-owned, not
        # group-writable. After the recursive prep the child can overwrite a
        # file inside it, and node_modules (a symlink) is left untouched.
        parent = tempfile.mkdtemp()
        os.chmod(parent, 0o755)
        self.addCleanup(lambda: subprocess.run(['rm', '-rf', parent]))
        proj = os.path.join(parent, 'proj')
        os.makedirs(os.path.join(proj, 'backend'))
        existing = os.path.join(proj, 'backend', 'app.py')
        with open(existing, 'w') as f:
            f.write('x = 1')
        os.chmod(existing, 0o644)  # root-owned, not group-writable
        sandbox.prepare_tree_recursive(proj)
        self.assertEqual(os.stat(existing).st_gid, self.gid)
        over = subprocess.run(
            ['sh', '-c', f'echo y > {existing}'],
            capture_output=True, text=True, **sandbox.child_privilege_kwargs(),
        )
        self.assertEqual(over.returncode, 0, over.stderr)

    def test_prepare_tree_lets_the_child_write(self):
        parent = tempfile.mkdtemp()
        os.chmod(parent, 0o755)  # traversable by the child
        self.addCleanup(lambda: subprocess.run(['rm', '-rf', parent]))
        proj = os.path.join(parent, 'proj')
        os.mkdir(proj)
        old = os.umask(sandbox.SANDBOX_UMASK)
        try:
            sandbox.prepare_tree(proj)
            self.assertEqual(os.stat(proj).st_gid, self.gid)
            wrote = subprocess.run(
                ['sh', '-c', f'echo hi > {proj}/w.txt'],
                capture_output=True, text=True,
                **sandbox.child_privilege_kwargs(),
            )
        finally:
            os.umask(old)
        self.assertEqual(wrote.returncode, 0, wrote.stderr)
        self.assertEqual(os.stat(os.path.join(proj, 'w.txt')).st_uid, self.uid)
