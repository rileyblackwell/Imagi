"""
Tests for the shared frontend dependency store (services.frontend_dependencies).

Covers:
- dependency_signature: identical dependency sets hash the same regardless of
  name/version/scripts; different sets hash differently
- link_frontend_dependencies: symlinks a project's node_modules at the shared
  store, projects with identical deps share one slot, real installs are left
  untouched, and callers get a fallback signal when the store can't be built

npm is stubbed so the tests stay hermetic and fast — the store install is
exercised through a fake that materializes node_modules the way npm would.
"""

import json
import os
import shutil
import tempfile
from unittest import mock

from django.test import SimpleTestCase, override_settings

from apps.Imagi.Build.services import frontend_dependencies as deps


def _fake_npm_install(cmd, cwd=None, **kwargs):
    """Stand in for `npm install`: create node_modules in the slot."""
    os.makedirs(os.path.join(cwd, 'node_modules', 'left-pad'), exist_ok=True)
    return mock.Mock(returncode=0, stdout='', stderr='')


class DependencySignatureTests(SimpleTestCase):
    def test_identical_deps_hash_the_same(self):
        a = {"name": "a", "version": "1.0.0", "dependencies": {"vue": "^3.5.0"}}
        b = {"name": "b", "version": "9.9.9", "scripts": {"x": "y"},
             "dependencies": {"vue": "^3.5.0"}}
        self.assertEqual(deps.dependency_signature(a), deps.dependency_signature(b))

    def test_dependency_order_does_not_matter(self):
        a = {"dependencies": {"vue": "^3", "axios": "^1"}}
        b = {"dependencies": {"axios": "^1", "vue": "^3"}}
        self.assertEqual(deps.dependency_signature(a), deps.dependency_signature(b))

    def test_different_deps_hash_differently(self):
        a = {"dependencies": {"vue": "^3.5.0"}}
        b = {"dependencies": {"vue": "^3.6.0"}}
        self.assertNotEqual(deps.dependency_signature(a), deps.dependency_signature(b))


class LinkFrontendDependenciesTests(SimpleTestCase):
    def setUp(self):
        self.store = tempfile.mkdtemp(prefix='depstore_')
        self.projroot = tempfile.mkdtemp(prefix='projroot_')
        self.addCleanup(lambda: shutil.rmtree(self.store, ignore_errors=True))
        self.addCleanup(lambda: shutil.rmtree(self.projroot, ignore_errors=True))
        self._settings = override_settings(FRONTEND_DEP_STORE_ROOT=self.store)
        self._settings.enable()
        self.addCleanup(self._settings.disable)

    def _make_frontend(self, package_json):
        fe = tempfile.mkdtemp(dir=self.projroot)
        with open(os.path.join(fe, 'package.json'), 'w') as f:
            json.dump(package_json, f)
        return fe

    def test_links_node_modules_to_shared_store(self):
        fe = self._make_frontend({"name": "one", "dependencies": {"left-pad": "1.3.0"}})
        with mock.patch('shutil.which', return_value='/usr/bin/npm'), \
                mock.patch('subprocess.run', side_effect=_fake_npm_install):
            self.assertTrue(deps.link_frontend_dependencies(fe))
        nm = os.path.join(fe, 'node_modules')
        self.assertTrue(os.path.islink(nm))
        self.assertTrue(os.path.isdir(os.path.join(os.path.realpath(nm), 'left-pad')))

    def test_identical_projects_share_one_slot(self):
        a = self._make_frontend({"name": "a", "dependencies": {"left-pad": "1.3.0"}})
        b = self._make_frontend({"name": "b", "version": "2",
                                  "dependencies": {"left-pad": "1.3.0"}})
        with mock.patch('shutil.which', return_value='/usr/bin/npm'), \
                mock.patch('subprocess.run', side_effect=_fake_npm_install):
            self.assertTrue(deps.link_frontend_dependencies(a))
            self.assertTrue(deps.link_frontend_dependencies(b))
        self.assertEqual(
            os.path.realpath(os.path.join(a, 'node_modules')),
            os.path.realpath(os.path.join(b, 'node_modules')),
        )
        slots = [s for s in os.listdir(self.store) if s.startswith('v1-')]
        self.assertEqual(len(slots), 1)

    def test_existing_real_node_modules_left_untouched(self):
        fe = self._make_frontend({"dependencies": {"left-pad": "1.3.0"}})
        os.makedirs(os.path.join(fe, 'node_modules', 'already-here'))
        with mock.patch('shutil.which', return_value='/usr/bin/npm'), \
                mock.patch('subprocess.run', side_effect=_fake_npm_install) as run:
            self.assertTrue(deps.link_frontend_dependencies(fe))
        self.assertFalse(os.path.islink(os.path.join(fe, 'node_modules')))
        run.assert_not_called()

    def test_missing_package_json_signals_fallback(self):
        fe = tempfile.mkdtemp(dir=self.projroot)
        self.assertFalse(deps.link_frontend_dependencies(fe))

    def test_npm_missing_signals_fallback(self):
        fe = self._make_frontend({"dependencies": {"left-pad": "1.3.0"}})
        with mock.patch('shutil.which', return_value=None):
            self.assertFalse(deps.link_frontend_dependencies(fe))

    def test_failed_install_signals_fallback_and_leaves_no_partial_store(self):
        fe = self._make_frontend({"dependencies": {"left-pad": "1.3.0"}})
        fail = mock.Mock(returncode=1, stdout='', stderr='boom')
        with mock.patch('shutil.which', return_value='/usr/bin/npm'), \
                mock.patch('subprocess.run', return_value=fail):
            self.assertFalse(deps.link_frontend_dependencies(fe))
        self.assertFalse(os.path.exists(os.path.join(fe, 'node_modules')))
