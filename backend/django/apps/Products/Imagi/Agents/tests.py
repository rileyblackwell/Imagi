"""
Tests for the Agents app harness.

Covers the coding-agent tool implementations (read/edit/grep/glob, path
safety, plan tracking), conversation history compaction, and project memory
loading. The tools are tested through their plain implementation functions so
no OpenAI calls are made.
"""

import os
import shutil
import tempfile
from types import SimpleNamespace

from django.test import SimpleTestCase

from apps.Products.Imagi.Agents.services.base_agent import (
    AgentContext,
    compact_history,
    extract_run_metadata,
)
from apps.Products.Imagi.Agents.services.coding_agent import (
    PROJECT_MEMORY_MAX_CHARS,
    load_project_memory,
)
from apps.Products.Imagi.Agents.services.tools import (
    edit_file_impl,
    glob_impl,
    grep_impl,
    normalize_file_path,
    read_file_impl,
    resolve_safe_path,
    set_plan,
)


class ToolTestBase(SimpleTestCase):
    """Create a throwaway dual-stack project tree on disk."""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='agents_tools_')
        self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))
        # A minimal Project stand-in: the impls only use .project_path
        self.project = SimpleNamespace(project_path=self.root)

        self._write('frontend/vuejs/src/App.vue', '<template>\n  <div>App</div>\n</template>\n')
        self._write(
            'frontend/vuejs/src/apps/home/router/index.ts',
            "import { createRouter } from 'vue-router'\n\nconst routes = []\n\nexport default routes\n",
        )
        self._write('backend/django/manage.py', "#!/usr/bin/env python\nprint('manage')\n")

    def _write(self, rel_path, content):
        full = os.path.join(self.root, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w', encoding='utf-8') as f:
            f.write(content)
        return full


class PathSafetyTests(ToolTestBase):
    def test_resolve_safe_path_allows_project_files(self):
        full = resolve_safe_path(self.project, 'frontend/vuejs/src/App.vue')
        self.assertTrue(full.startswith(os.path.realpath(self.root)))

    def test_resolve_safe_path_blocks_traversal(self):
        with self.assertRaises(ValueError):
            resolve_safe_path(self.project, '../outside.txt')
        with self.assertRaises(ValueError):
            resolve_safe_path(self.project, 'frontend/../../etc/passwd')

    def test_normalize_adds_frontend_prefix_for_dual_stack(self):
        self.assertEqual(
            normalize_file_path(self.project, 'src/apps/home/views/About.vue'),
            'frontend/vuejs/src/apps/home/views/About.vue',
        )

    def test_normalize_adds_backend_prefix_for_python(self):
        self.assertEqual(
            normalize_file_path(self.project, 'apps/blog/models.py'),
            'backend/django/apps/blog/models.py',
        )

    def test_normalize_keeps_prefixed_paths(self):
        self.assertEqual(
            normalize_file_path(self.project, 'frontend/vuejs/src/App.vue'),
            'frontend/vuejs/src/App.vue',
        )


class ReadFileTests(ToolTestBase):
    def test_read_returns_line_numbered_output(self):
        out = read_file_impl(self.project, 'frontend/vuejs/src/App.vue')
        self.assertIn('[file: frontend/vuejs/src/App.vue | lines 1-3 of 3]', out)
        self.assertIn('1\t<template>', out)
        self.assertIn('3\t</template>', out)

    def test_read_supports_offset_and_limit(self):
        self._write('notes.md', '\n'.join(f'line {i}' for i in range(1, 11)))
        out = read_file_impl(self.project, 'notes.md', offset=4, limit=2)
        self.assertIn('lines 4-5 of 10', out)
        self.assertIn('4\tline 4', out)
        self.assertIn('5\tline 5', out)
        self.assertNotIn('6\tline 6', out)
        self.assertIn('more lines below', out)

    def test_read_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            read_file_impl(self.project, 'frontend/vuejs/src/Nope.vue')


class EditFileTests(ToolTestBase):
    def test_edit_replaces_unique_string(self):
        result = edit_file_impl(
            self.project,
            'frontend/vuejs/src/App.vue',
            '<div>App</div>',
            '<div>Updated</div>',
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['replacements'], 1)
        with open(os.path.join(self.root, 'frontend/vuejs/src/App.vue')) as f:
            self.assertIn('<div>Updated</div>', f.read())

    def test_edit_rejects_missing_old_string(self):
        with self.assertRaises(ValueError) as cm:
            edit_file_impl(self.project, 'frontend/vuejs/src/App.vue', 'nonexistent', 'x')
        self.assertIn('not found', str(cm.exception))

    def test_edit_rejects_ambiguous_old_string(self):
        self._write('dup.txt', 'foo\nfoo\n')
        with self.assertRaises(ValueError) as cm:
            edit_file_impl(self.project, 'dup.txt', 'foo', 'bar')
        self.assertIn('2 times', str(cm.exception))

    def test_edit_replace_all(self):
        self._write('dup.txt', 'foo\nfoo\n')
        result = edit_file_impl(self.project, 'dup.txt', 'foo', 'bar', replace_all=True)
        self.assertEqual(result['replacements'], 2)
        with open(os.path.join(self.root, 'dup.txt')) as f:
            self.assertEqual(f.read(), 'bar\nbar\n')

    def test_edit_rejects_identical_strings(self):
        with self.assertRaises(ValueError):
            edit_file_impl(self.project, 'frontend/vuejs/src/App.vue', 'same', 'same')

    def test_edit_normalizes_bare_frontend_path(self):
        result = edit_file_impl(
            self.project, 'src/App.vue', '<div>App</div>', '<div>Normalized</div>'
        )
        self.assertEqual(result['path'], 'frontend/vuejs/src/App.vue')


class GrepGlobTests(ToolTestBase):
    def test_grep_finds_matches_with_line_numbers(self):
        result = grep_impl(self.project, r'createRouter')
        self.assertEqual(result['match_count'], 1)
        match = result['matches'][0]
        self.assertEqual(match['file'], os.path.join('frontend', 'vuejs', 'src', 'apps', 'home', 'router', 'index.ts'))
        self.assertEqual(match['line'], 1)
        self.assertIn('createRouter', match['text'])

    def test_grep_respects_include_filter(self):
        result = grep_impl(self.project, r'.', include='*.py')
        files = {m['file'] for m in result['matches']}
        self.assertTrue(all(f.endswith('.py') for f in files))

    def test_grep_scoped_to_subdirectory(self):
        result = grep_impl(self.project, r'print', path='backend')
        self.assertEqual(result['match_count'], 1)

    def test_grep_skips_node_modules(self):
        self._write('frontend/vuejs/node_modules/pkg/index.js', 'createRouter\n')
        result = grep_impl(self.project, r'createRouter')
        self.assertEqual(result['match_count'], 1)

    def test_glob_recursive_pattern(self):
        result = glob_impl(self.project, 'frontend/**/*.vue')
        self.assertEqual(result['files'], ['frontend/vuejs/src/App.vue'])

    def test_glob_basename_pattern(self):
        result = glob_impl(self.project, '*.py')
        self.assertEqual(result['files'], ['backend/django/manage.py'])

    def test_glob_double_star_segment(self):
        result = glob_impl(self.project, '**/router/index.ts')
        self.assertEqual(result['files'], ['frontend/vuejs/src/apps/home/router/index.ts'])


class PlanTests(SimpleTestCase):
    def test_set_plan_stores_validated_steps(self):
        ctx = AgentContext(user_id=1)
        result = set_plan(ctx, [
            {'step': 'Find the router', 'status': 'completed'},
            {'step': 'Add the route', 'status': 'in_progress'},
            {'step': 'Create the view', 'status': 'pending'},
        ])
        self.assertEqual(result['steps'], 3)
        self.assertEqual(ctx.plan[1], {'step': 'Add the route', 'status': 'in_progress'})

    def test_set_plan_normalizes_bad_input(self):
        ctx = AgentContext(user_id=1)
        set_plan(ctx, [
            {'step': '  ', 'status': 'pending'},          # dropped: empty step
            {'step': 'Do work', 'status': 'bogus'},        # status coerced
        ])
        self.assertEqual(ctx.plan, [{'step': 'Do work', 'status': 'pending'}])

    def test_set_plan_replaces_previous_plan(self):
        ctx = AgentContext(user_id=1)
        set_plan(ctx, [{'step': 'old', 'status': 'pending'}])
        set_plan(ctx, [{'step': 'new', 'status': 'in_progress'}])
        self.assertEqual(len(ctx.plan), 1)
        self.assertEqual(ctx.plan[0]['step'], 'new')


class CompactHistoryTests(SimpleTestCase):
    def test_short_history_unchanged(self):
        messages = [
            {'role': 'user', 'content': 'hello'},
            {'role': 'assistant', 'content': 'hi'},
        ]
        self.assertEqual(compact_history(messages, max_chars=1000), messages)

    def test_long_history_is_compacted(self):
        messages = [
            {'role': 'user', 'content': f'message number {i} ' + 'x' * 200}
            for i in range(20)
        ]
        compacted = compact_history(messages, max_chars=1000)
        self.assertLess(len(compacted), len(messages))
        # First message is the compaction summary
        self.assertIn('Conversation compacted', compacted[0]['content'])
        self.assertIn('message number 0', compacted[0]['content'])
        # Most recent message survives verbatim
        self.assertEqual(compacted[-1], messages[-1])

    def test_compaction_always_keeps_latest_message(self):
        messages = [
            {'role': 'user', 'content': 'a' * 5000},
            {'role': 'assistant', 'content': 'b' * 5000},
        ]
        compacted = compact_history(messages, max_chars=100)
        self.assertEqual(compacted[-1]['content'], 'b' * 5000)


class ExtractRunMetadataTests(SimpleTestCase):
    def test_extracts_tool_calls_and_changed_files(self):
        # Shapes mirror the Agents SDK RunItems: ToolCallItem exposes the tool
        # name on raw_item; ToolCallOutputItem exposes the tool's return value
        # as .output (type 'tool_call_output_item').
        items = [
            SimpleNamespace(type='tool_call_item', raw_item=SimpleNamespace(name='read_file')),
            SimpleNamespace(type='tool_call_output_item', output='[file: a.vue | lines 1-1 of 1]\n1\tx'),
            SimpleNamespace(type='tool_call_item', raw_item=SimpleNamespace(name='edit_file')),
            SimpleNamespace(
                type='tool_call_output_item',
                output='{"success": true, "path": "frontend/vuejs/src/App.vue", "replacements": 1}',
            ),
            SimpleNamespace(type='message_output_item'),
        ]
        metadata = extract_run_metadata(SimpleNamespace(new_items=items))
        self.assertEqual(metadata['tool_calls'], ['read_file', 'edit_file'])
        self.assertEqual(metadata['files_changed'], ['frontend/vuejs/src/App.vue'])

    def test_deduplicates_changed_files_and_ignores_failures(self):
        success = '{"success": true, "path": "a.py"}'
        failure = '{"success": false, "path": "b.py", "error": "nope"}'
        items = [
            SimpleNamespace(type='tool_call_output_item', output=success),
            SimpleNamespace(type='tool_call_output_item', output=success),
            SimpleNamespace(type='tool_call_output_item', output=failure),
        ]
        metadata = extract_run_metadata(SimpleNamespace(new_items=items))
        self.assertEqual(metadata['files_changed'], ['a.py'])

    def test_handles_empty_result(self):
        metadata = extract_run_metadata(SimpleNamespace(new_items=[]))
        self.assertEqual(metadata, {'tool_calls': [], 'files_changed': []})


class ProjectMemoryTests(SimpleTestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='agents_memory_')
        self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))

    def _write(self, name, content):
        with open(os.path.join(self.root, name), 'w', encoding='utf-8') as f:
            f.write(content)

    def test_returns_none_without_memory_file(self):
        self.assertIsNone(load_project_memory(self.root))
        self.assertIsNone(load_project_memory(None))
        self.assertIsNone(load_project_memory('/nonexistent/path'))

    def test_loads_agents_md(self):
        self._write('AGENTS.md', 'Always use TypeScript.')
        memory = load_project_memory(self.root)
        self.assertIn('AGENTS.md', memory)
        self.assertIn('Always use TypeScript.', memory)

    def test_agents_md_wins_over_claude_md(self):
        self._write('AGENTS.md', 'from agents file')
        self._write('CLAUDE.md', 'from claude file')
        memory = load_project_memory(self.root)
        self.assertIn('from agents file', memory)
        self.assertNotIn('from claude file', memory)

    def test_falls_back_to_claude_md(self):
        self._write('CLAUDE.md', 'claude instructions')
        memory = load_project_memory(self.root)
        self.assertIn('claude instructions', memory)

    def test_truncates_oversized_memory(self):
        self._write('AGENTS.md', 'y' * (PROJECT_MEMORY_MAX_CHARS + 500))
        memory = load_project_memory(self.root)
        self.assertIn('[truncated]', memory)
        self.assertLess(len(memory), PROJECT_MEMORY_MAX_CHARS + 200)
