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
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import PropertyMock, patch

from agents import MaxTurnsExceeded
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token

from apps.Imagi.Build.api.views import _project_has_running_conversation
from apps.Imagi.Build.models import AgentConversation, AgentMessage
from apps.Imagi.Build.services.base_agent import (
    AgentContext,
    ImagiAgentService,
    compact_history,
    extract_run_metadata,
)
from apps.Imagi.Build.services.models_service import compute_cost_usd
from apps.Imagi.Build.services.coding_agent import (
    PROJECT_MEMORY_MAX_CHARS,
    load_project_memory,
)
from apps.Imagi.Build.services.tools import (
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


class EditFileTests(TestCase):
    """Edit tests need the database: edit_file_impl writes through to the
    ProjectFile copy, so they run against a real Project row."""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix='agents_tools_')
        self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))
        self.user = User.objects.create_user(username='edituser', password='testpass123')

        from apps.Imagi.ProjectManager.models import Project as PMProject
        self.project = PMProject.objects.create(
            user=self.user, name="Edit Tools Project", project_path=self.root
        )

        self._write('frontend/vuejs/src/App.vue', '<template>\n  <div>App</div>\n</template>\n')
        self._write('backend/django/manage.py', "#!/usr/bin/env python\nprint('manage')\n")

    def _write(self, rel_path, content):
        full = os.path.join(self.root, rel_path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w', encoding='utf-8') as f:
            f.write(content)
        return full

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


class _FakeStreamedRun:
    """Stands in for the SDK's RunResultStreaming."""

    def __init__(self, events, final_output='All done.', new_items=None):
        self._events = events
        self.final_output = final_output
        self.new_items = new_items or []

    async def stream_events(self):
        for event in self._events:
            yield event


def _delta_event(text):
    return SimpleNamespace(
        type='raw_response_event',
        data=SimpleNamespace(type='response.output_text.delta', delta=text),
    )


def _tool_call_event(name):
    return SimpleNamespace(
        type='run_item_stream_event',
        item=SimpleNamespace(type='tool_call_item', raw_item=SimpleNamespace(name=name)),
    )


class ProcessStreamTests(TestCase):
    """The streaming run: event order, persistence, and failure handling."""

    def setUp(self):
        self.user = User.objects.create_user(username='streamer', password='pw123456')
        self.service = ImagiAgentService()

        conversation = SimpleNamespace(id=7)
        self.context = AgentContext(user_id=self.user.id, project_id=1)
        self.persisted = []
        self.persisted_metadata = []

        def record_assistant_message(conv, content, metadata=None):
            self.persisted.append(content)
            self.persisted_metadata.append(metadata)

        self.service._prepare_run = lambda **kwargs: (
            conversation, self.context, [{'role': 'user', 'content': kwargs['user_input']}]
        )
        self.service.add_assistant_message = record_assistant_message

    async def _collect(self, **overrides):
        kwargs = {'user_input': 'build me a page', 'user': self.user, 'project_id': 1}
        kwargs.update(overrides)
        return [event async for event in self.service.process_stream(**kwargs)]

    def _run(self, fake_run, **overrides):
        with patch.object(type(self.service), 'agent', new_callable=PropertyMock) as mock_agent, \
                patch('apps.Imagi.Build.services.base_agent.Runner') as mock_runner:
            mock_agent.return_value = SimpleNamespace()
            mock_runner.run_streamed.return_value = fake_run
            return async_to_sync(self._collect)(**overrides)

    def test_streams_deltas_then_done(self):
        events = self._run(_FakeStreamedRun([_delta_event('Hel'), _delta_event('lo')]))

        self.assertEqual(events[0], {'type': 'start', 'conversation_id': 7})
        self.assertEqual(
            [e['text'] for e in events if e['type'] == 'delta'], ['Hel', 'lo']
        )
        done = events[-1]
        self.assertEqual(done['type'], 'done')
        self.assertTrue(done['success'])
        self.assertEqual(done['response'], 'All done.')
        self.assertEqual(done['conversation_id'], 7)
        # The reply is persisted exactly once, from the run's final output.
        self.assertEqual(self.persisted, ['All done.'])

    def test_reports_tool_calls_and_plan(self):
        self.context.plan = [{'step': 'write the page', 'status': 'done'}]
        events = self._run(_FakeStreamedRun([
            _tool_call_event('read_file'), _tool_call_event('update_plan'),
        ]))

        self.assertEqual(
            [e['name'] for e in events if e['type'] == 'tool_call'],
            ['read_file', 'update_plan'],
        )
        # A plan event follows update_plan so the UI can redraw it mid-run.
        plans = [e for e in events if e['type'] == 'plan']
        self.assertEqual(len(plans), 1)
        self.assertEqual(plans[0]['plan'], [{'step': 'write the page', 'status': 'done'}])

    def test_falls_back_to_streamed_text_when_final_output_missing(self):
        events = self._run(
            _FakeStreamedRun([_delta_event('partial ')], final_output=None)
        )
        self.assertEqual(events[-1]['response'], 'partial ')
        self.assertEqual(self.persisted, ['partial '])

    def test_requires_message_and_project(self):
        self.assertEqual(
            self._run(_FakeStreamedRun([]), user_input='')[0],
            {'type': 'error', 'error': 'Message is required'},
        )
        self.assertEqual(
            self._run(_FakeStreamedRun([]), project_id=None)[0],
            {'type': 'error', 'error': 'Project ID is required'},
        )

    def test_mid_run_failure_persists_partial_reply(self):
        # The agent may already have edited files before blowing up, so the
        # text it produced must not be silently dropped.
        class Exploding(_FakeStreamedRun):
            async def stream_events(self):
                yield _delta_event('I started ')
                raise RuntimeError('model exploded')

        events = self._run(Exploding([]))

        self.assertEqual(events[-1]['type'], 'error')
        self.assertIn('model exploded', events[-1]['error'])
        self.assertEqual(self.persisted, ['I started'])

    def test_done_event_reports_usage_and_persists_metadata(self):
        run = _FakeStreamedRun(
            [_tool_call_event('edit_file')],
            new_items=[
                SimpleNamespace(
                    type='tool_call_item',
                    raw_item=SimpleNamespace(
                        name='edit_file',
                        arguments='{"path": "frontend/vuejs/src/App.vue"}',
                    ),
                ),
                SimpleNamespace(
                    type='tool_call_output_item',
                    output='{"success": true, "path": "frontend/vuejs/src/App.vue"}',
                ),
            ],
        )
        run.context_wrapper = SimpleNamespace(
            usage=SimpleNamespace(input_tokens=1_000_000, output_tokens=100_000)
        )
        self.context.plan = [{'step': 'edit the page', 'status': 'completed'}]

        events = self._run(run)

        done = events[-1]
        self.assertEqual(done['type'], 'done')
        self.assertEqual(done['usage']['input_tokens'], 1_000_000)
        self.assertEqual(done['usage']['output_tokens'], 100_000)
        self.assertEqual(
            done['usage']['cost_usd'],
            compute_cost_usd(self.service.model, 1_000_000, 100_000),
        )

        metadata = self.persisted_metadata[0]
        self.assertEqual(
            metadata['tool_calls'],
            [{'name': 'edit_file', 'args': {'path': 'frontend/vuejs/src/App.vue'}}],
        )
        self.assertEqual(metadata['files_changed'], ['frontend/vuejs/src/App.vue'])
        self.assertEqual(metadata['plan'], [{'step': 'edit the page', 'status': 'completed'}])
        self.assertEqual(metadata['usage'], done['usage'])

    def test_done_event_omits_usage_when_unavailable(self):
        # The fake run exposes no context_wrapper, mirroring an SDK result
        # without tracked usage: the field must be absent, not zeroed.
        events = self._run(_FakeStreamedRun([_delta_event('hi')]))

        self.assertNotIn('usage', events[-1])
        # A plain reply with no run artifacts persists NULL metadata.
        self.assertEqual(self.persisted_metadata, [None])

    def test_max_turns_emits_error_code_and_persists_partial(self):
        class HitsTurnCap(_FakeStreamedRun):
            async def stream_events(self):
                yield _delta_event('Working on it ')
                raise MaxTurnsExceeded('Max turns (30) exceeded')

        events = self._run(HitsTurnCap([]))

        error = events[-1]
        self.assertEqual(error['type'], 'error')
        self.assertEqual(error['code'], 'max_turns')
        # Friendlier than the SDK's raw message, so it can be shown as-is.
        self.assertNotIn('Max turns (30) exceeded', error['error'])
        self.assertEqual(self.persisted, ['Working on it'])


class AgentStreamEndpointTests(TestCase):
    """Auth on the SSE endpoint, which cannot use DRF's sync-only decorators."""

    def setUp(self):
        self.user = User.objects.create_user(username='api', password='pw123456')
        self.url = reverse('agent_stream')

    def test_rejects_unauthenticated_request(self):
        resp = self.client.post(
            self.url, data='{"message": "hi", "project_id": 1}',
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 401)

    def test_rejects_session_auth_without_token(self):
        # csrf_exempt + cookie auth would let any origin drive an agent run,
        # so a session alone must not authenticate this endpoint.
        self.client.force_login(self.user)
        resp = self.client.post(
            self.url, data='{"message": "hi", "project_id": 1}',
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 401)

    def test_rejects_get(self):
        token = Token.objects.create(user=self.user)
        resp = self.client.get(self.url, HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertEqual(resp.status_code, 405)

    def test_validates_body(self):
        token = Token.objects.create(user=self.user)
        resp = self.client.post(
            self.url, data='{"project_id": 1}', content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {token.key}',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn('Message is required', resp.json()['error'])

    def test_rejects_run_while_project_has_one_in_flight(self):
        AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-sol', project_id=1,
            run_started_at=timezone.now(),
        )
        token = Token.objects.create(user=self.user)
        resp = self.client.post(
            self.url, data='{"message": "hi", "project_id": 1}',
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {token.key}',
        )
        self.assertEqual(resp.status_code, 409)
        self.assertEqual(resp.json()['detail'], 'agent_busy')


class ProjectBusyGuardTests(TestCase):
    """The one-run-per-project guard behind the stream endpoint's 409."""

    def setUp(self):
        self.user = User.objects.create_user(username='busy', password='pw123456')

    def _conversation(self, **kwargs):
        return AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-sol', project_id=1, **kwargs
        )

    def test_fresh_run_in_project_blocks(self):
        self._conversation(run_started_at=timezone.now())
        self.assertTrue(_project_has_running_conversation(self.user, 1))

    def test_stale_or_absent_run_does_not_block(self):
        # A crashed worker never clears run_started_at; the staleness window
        # keeps it from wedging the project forever.
        self._conversation(run_started_at=timezone.now() - timedelta(minutes=11))
        self._conversation()
        self.assertFalse(_project_has_running_conversation(self.user, 1))

    def test_conversation_being_started_is_excluded(self):
        running = self._conversation(run_started_at=timezone.now())
        self.assertFalse(
            _project_has_running_conversation(
                self.user, 1, exclude_conversation_id=running.id
            )
        )

    def test_other_projects_and_users_do_not_block(self):
        self._conversation(run_started_at=timezone.now())  # project 1
        other = User.objects.create_user(username='busy2', password='pw123456')
        AgentConversation.objects.create(
            user=other, model_name='gpt-5.6-sol', project_id=2,
            run_started_at=timezone.now(),
        )
        self.assertFalse(_project_has_running_conversation(self.user, 2))
        self.assertFalse(_project_has_running_conversation(other, 1))


class ConversationMessagesMetadataTests(TestCase):
    """The messages endpoint returns persisted run metadata per message."""

    def setUp(self):
        self.user = User.objects.create_user(username='msguser', password='pw123456')
        self.client.force_login(self.user)

    def test_messages_include_metadata(self):
        conversation = ImagiAgentService().create_conversation(
            self.user, 'gpt-5.6-sol', project_id=1
        )
        AgentMessage.objects.create(conversation=conversation, role='user', content='hi')
        metadata = {
            'tool_calls': [{'name': 'edit_file', 'args': {'path': 'src/App.vue'}}],
            'files_changed': ['frontend/vuejs/src/App.vue'],
            'usage': {'input_tokens': 100, 'output_tokens': 10, 'cost_usd': 0.0009},
        }
        AgentMessage.objects.create(
            conversation=conversation, role='assistant', content='done',
            metadata=metadata,
        )

        resp = self.client.get(reverse('conversation_messages', args=[conversation.id]))

        self.assertEqual(resp.status_code, 200)
        messages = resp.json()
        self.assertIsNone(messages[0]['metadata'])
        self.assertEqual(messages[1]['metadata'], metadata)


class ComputeCostTests(SimpleTestCase):
    def test_computes_from_suite_pricing(self):
        # Sol: $6/M input + $30/M output
        self.assertEqual(compute_cost_usd('gpt-5.6-sol', 1_000_000, 1_000_000), 36.0)
        # Luna: $1/M input + $5/M output
        self.assertEqual(compute_cost_usd('gpt-5.6-luna', 500_000, 200_000), 1.5)

    def test_unknown_model_returns_none(self):
        self.assertIsNone(compute_cost_usd('gpt-oops', 1000, 1000))


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
