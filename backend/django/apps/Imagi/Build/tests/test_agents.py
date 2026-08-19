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
import time
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
from apps.Imagi.Build.models import AgentCheckIn, AgentConversation, AgentMessage
from apps.Imagi.Build.services.base_agent import (
    CAPPED_NOTE_MAX_PAGES,
    LEAD_DISPATCH_FAILED_NOTE,
    LEAD_DISPATCH_RETRY_PROMPT,
    MAX_AGENT_TURNS,
    TASK_AUTO_CONTINUE_ROUNDS,
    TASK_MAX_TURNS,
    AgentContext,
    ImagiAgentService,
    RunBudgetExceeded,
    RunDeadlineExceeded,
    _capped_run_note,
    compact_history,
    extract_run_metadata,
    lead_claims_unmade_dispatch,
    make_run_bounds_hook,
)
from apps.Imagi.Build.services.models_service import compute_cost_usd
from apps.Imagi.Build.services.coding_agent import (
    INITIAL_BUILD_INSTRUCTIONS,
    INITIAL_BUILD_REASONING_EFFORT,
    INITIAL_BUILD_TIME_BUDGET_S,
    LEAD_AGENT_INSTRUCTIONS,
    PROJECT_MEMORY_MAX_CHARS,
    create_coding_agent,
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
from apps.Payments.models import UsageEvent
from apps.Payments.services.plans import PLANS


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

        # The run's usage also feeds Payments' rolling-window metering.
        usage_event = UsageEvent.objects.get(user=self.user)
        self.assertEqual(usage_event.input_tokens, 1_000_000)
        self.assertEqual(usage_event.output_tokens, 100_000)
        self.assertEqual(usage_event.total_tokens, 1_100_000)
        self.assertEqual(usage_event.conversation_id, 7)
        # Metering is by cost, so the run's computed price — not its token
        # count — is what draws down the plan allowance.
        self.assertEqual(
            float(usage_event.cost_usd),
            compute_cost_usd(self.service.model, 1_000_000, 100_000),
        )

    def test_done_event_omits_usage_when_unavailable(self):
        # The fake run exposes no context_wrapper, mirroring an SDK result
        # without tracked usage: the field must be absent, not zeroed.
        events = self._run(_FakeStreamedRun([_delta_event('hi')]))

        self.assertNotIn('usage', events[-1])
        # A plain reply with no run artifacts persists NULL metadata.
        self.assertEqual(self.persisted_metadata, [None])
        # Unknown usage is never metered as zero tokens.
        self.assertFalse(UsageEvent.objects.exists())

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

    def test_interrupted_run_still_meters_usage(self):
        # A run cut off mid-stream has already spent tokens; skipping the
        # UsageEvent would make plan limits bypassable by stopping runs.
        class Exploding(_FakeStreamedRun):
            async def stream_events(self):
                yield _delta_event('I started ')
                raise RuntimeError('model exploded')

        run = Exploding([])
        run.context_wrapper = SimpleNamespace(
            usage=SimpleNamespace(input_tokens=5_000, output_tokens=250)
        )

        self._run(run)

        usage_event = UsageEvent.objects.get(user=self.user)
        self.assertEqual(usage_event.input_tokens, 5_000)
        self.assertEqual(usage_event.output_tokens, 250)
        self.assertEqual(usage_event.total_tokens, 5_250)
        self.assertEqual(usage_event.conversation_id, 7)
        # The persisted partial reply still omits usage from its metadata
        # (a mid-stream reading is a lower bound — display keeps "unknown").
        self.assertEqual(self.persisted, ['I started'])
        self.assertIsNone(self.persisted_metadata[0])

    def test_max_turns_run_meters_usage(self):
        class HitsTurnCap(_FakeStreamedRun):
            async def stream_events(self):
                yield _delta_event('Working on it ')
                raise MaxTurnsExceeded('Max turns (30) exceeded')

        run = HitsTurnCap([])
        run.context_wrapper = SimpleNamespace(
            usage=SimpleNamespace(input_tokens=2_000_000, output_tokens=90_000)
        )

        self._run(run)

        usage_event = UsageEvent.objects.get(user=self.user)
        self.assertEqual(usage_event.total_tokens, 2_090_000)

    def test_interrupted_run_without_usage_records_nothing(self):
        # No context_wrapper usage: absent means unknown — never a zero row.
        class Exploding(_FakeStreamedRun):
            async def stream_events(self):
                yield _delta_event('I started ')
                raise RuntimeError('model exploded')

        self._run(Exploding([]))

        self.assertFalse(UsageEvent.objects.exists())


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

    def test_rejects_run_when_over_usage_limit(self):
        # Free-plan weekly window exhausted -> refused before the stream opens,
        # with the same pre-stream JSON contract as agent_busy. The user has no
        # Subscription row, so their plan is the default 'free' tier.
        UsageEvent.objects.create(
            user=self.user, model_name='gpt-5.6-terra',
            input_tokens=1_000_000, output_tokens=0, total_tokens=1_000_000,
            cost_usd=PLANS['free']['weekly_usd'],
        )
        token = Token.objects.create(user=self.user)
        resp = self.client.post(
            self.url, data='{"message": "hi", "project_id": 1}',
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {token.key}',
        )
        self.assertEqual(resp.status_code, 429)
        body = resp.json()
        self.assertEqual(body['error'], 'usage_limit_exceeded')
        self.assertEqual(body['window'], 'week')
        self.assertIn('detail', body)
        self.assertIsNotNone(body['resets_at'])


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


class ConversationSummarySerializationTests(TestCase):
    """A task's closing summary travels whole to the dispatch card.

    last_message_preview is a list-row gist and stays tightly capped, but the
    main thread's dispatch card renders the finished task's sign-off (or a
    blocked task's question) in full — cutting the summary's last sentence
    off was exactly the complaint. That text travels separately, generously
    capped, as last_assistant_summary.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='summarizer', password='pw123456')
        self.conversation = ImagiAgentService().create_conversation(
            self.user, 'gpt-5.6-terra', kind='task'
        )

    def test_summary_is_the_whole_sign_off_where_the_preview_clips(self):
        from apps.Imagi.Build.api.views import PREVIEW_LIMIT, _serialize_conversation

        sentence = (
            'Your site now has a contact page that checks addresses before '
            'sending, so you get fewer dead replies. '
        )
        sign_off = (sentence * 6).strip()  # comfortably past the preview cap
        self.assertGreater(len(sign_off), PREVIEW_LIMIT)
        AgentMessage.objects.create(
            conversation=self.conversation, role='assistant', content=sign_off
        )

        data = _serialize_conversation(self.conversation)
        self.assertEqual(data['last_assistant_summary'], sign_off)
        # The list-row preview stays clipped — the card must not rely on it.
        self.assertEqual(len(data['last_message_preview']), PREVIEW_LIMIT)

    def test_summary_tracks_the_last_assistant_message(self):
        from apps.Imagi.Build.api.views import _serialize_conversation

        AgentMessage.objects.create(
            conversation=self.conversation, role='assistant',
            content='Should the form email you or open a ticket?',
        )
        AgentMessage.objects.create(
            conversation=self.conversation, role='user', content='Email me.'
        )

        data = _serialize_conversation(self.conversation)
        # The preview follows the very last message (the user's answer); the
        # summary keeps pointing at what the agent last said.
        self.assertEqual(data['last_message_preview'], 'Email me.')
        self.assertEqual(
            data['last_assistant_summary'],
            'Should the form email you or open a ticket?',
        )

    def test_summary_is_empty_before_the_agent_has_spoken(self):
        from apps.Imagi.Build.api.views import _serialize_conversation

        AgentMessage.objects.create(
            conversation=self.conversation, role='user', content='the brief'
        )
        self.assertEqual(
            _serialize_conversation(self.conversation)['last_assistant_summary'], ''
        )


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


class ConversationTotalTokensTests(TestCase):
    """Serialized conversations aggregate token usage across their messages."""

    def setUp(self):
        self.user = User.objects.create_user(username='tokens', password='pw123456')
        self.client.force_login(self.user)

    def _conversation(self):
        return AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=1
        )

    def test_total_tokens_sums_usage_across_messages(self):
        conversation = self._conversation()
        AgentMessage.objects.create(
            conversation=conversation, role='user', content='hi',
            metadata={'checkpoint': 'abc123'},  # non-usage metadata is ignored
        )
        AgentMessage.objects.create(
            conversation=conversation, role='assistant', content='one',
            metadata={'usage': {'input_tokens': 1000, 'output_tokens': 200}},
        )
        # A run whose usage was never captured contributes nothing.
        AgentMessage.objects.create(
            conversation=conversation, role='assistant', content='untracked',
        )
        AgentMessage.objects.create(
            conversation=conversation, role='assistant', content='two',
            metadata={'usage': {'input_tokens': 50, 'output_tokens': 5, 'cost_usd': 0.01}},
        )

        resp = self.client.get(
            reverse('conversations_list_create'), {'project_id': 1}
        )

        self.assertEqual(resp.status_code, 200)
        [conversation_data] = resp.json()
        self.assertEqual(conversation_data['total_tokens'], 1255)

    def test_total_tokens_null_when_no_message_has_usage(self):
        # Absent usage means unknown — null, never 0.
        conversation = self._conversation()
        AgentMessage.objects.create(conversation=conversation, role='user', content='hi')
        AgentMessage.objects.create(conversation=conversation, role='assistant', content='yo')

        resp = self.client.get(reverse('conversation_detail', args=[conversation.id]))

        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.json()['total_tokens'])


class CheckpointTests(TestCase):
    """Per-message checkpoints: stamp on the user message, restore rewinds
    files + conversation together."""

    def setUp(self):
        self.user = User.objects.create_user(username='ckpt', password='pw123456')
        self.client.force_login(self.user)
        # A real git repo the checkpoint/restore code can drive.
        self.repo = tempfile.mkdtemp(prefix='ckpt_repo_')
        self.addCleanup(lambda: shutil.rmtree(self.repo, ignore_errors=True))
        import subprocess
        subprocess.run(['git', 'init'], cwd=self.repo, capture_output=True, check=True)
        subprocess.run(['git', 'config', 'user.email', 't@t.co'], cwd=self.repo, capture_output=True, check=True)
        subprocess.run(['git', 'config', 'user.name', 'T'], cwd=self.repo, capture_output=True, check=True)

    def _write_commit(self, name, content, message):
        import subprocess
        with open(os.path.join(self.repo, name), 'w') as f:
            f.write(content)
        subprocess.run(['git', 'add', '.'], cwd=self.repo, capture_output=True, check=True)
        subprocess.run(['git', 'commit', '-m', message], cwd=self.repo, capture_output=True, check=True)
        return subprocess.run(
            ['git', 'rev-parse', 'HEAD'], cwd=self.repo, capture_output=True, text=True, check=True
        ).stdout.strip()

    def test_ensure_checkpoint_returns_head_when_clean(self):
        from apps.Imagi.Build.services.version_control_service import VersionControlService
        head = self._write_commit('a.txt', 'one', 'first')
        result = VersionControlService().ensure_checkpoint(self.repo, 'noop')
        # Nothing to commit → the checkpoint is the current HEAD.
        self.assertTrue(result['success'])
        self.assertEqual(result['commit_hash'], head)

    def test_ensure_checkpoint_commits_dirty_tree(self):
        from apps.Imagi.Build.services.version_control_service import VersionControlService
        head = self._write_commit('a.txt', 'one', 'first')
        with open(os.path.join(self.repo, 'a.txt'), 'w') as f:
            f.write('two')  # uncommitted change
        result = VersionControlService().ensure_checkpoint(self.repo, 'snapshot')
        self.assertTrue(result['success'])
        self.assertNotEqual(result['commit_hash'], head)  # a new commit captured it

    def _conversation_with_project(self):
        from apps.Imagi.ProjectManager.models import Project
        project = Project.objects.create(
            user=self.user, name='P', project_path=self.repo, is_active=True
        )
        conversation = AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-sol', project_id=project.id
        )
        return project, conversation

    def test_restore_rewinds_files_and_truncates_conversation(self):
        project, conversation = self._conversation_with_project()
        checkpoint = self._write_commit('page.txt', 'original', 'v1')
        self._write_commit('page.txt', 'edited by agent', 'v2')

        first = AgentMessage.objects.create(
            conversation=conversation, role='user', content='make a change',
            metadata={'checkpoint': checkpoint},
        )
        AgentMessage.objects.create(conversation=conversation, role='assistant', content='done')
        AgentMessage.objects.create(conversation=conversation, role='user', content='another')

        resp = self.client.post(
            reverse('conversation_restore_checkpoint', args=[conversation.id]),
            data={'message_id': first.id}, content_type='application/json',
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['prompt'], 'make a change')
        # Files rewound to the checkpoint...
        with open(os.path.join(self.repo, 'page.txt')) as f:
            self.assertEqual(f.read(), 'original')
        # ...and the restored-to message plus everything after it are gone.
        self.assertEqual(conversation.messages.count(), 0)

    def test_restore_rejected_without_checkpoint(self):
        project, conversation = self._conversation_with_project()
        msg = AgentMessage.objects.create(
            conversation=conversation, role='user', content='no checkpoint here'
        )
        resp = self.client.post(
            reverse('conversation_restore_checkpoint', args=[conversation.id]),
            data={'message_id': msg.id}, content_type='application/json',
        )
        self.assertEqual(resp.status_code, 400)

    def test_restore_blocked_while_project_busy(self):
        project, conversation = self._conversation_with_project()
        checkpoint = self._write_commit('page.txt', 'original', 'v1')
        msg = AgentMessage.objects.create(
            conversation=conversation, role='user', content='x',
            metadata={'checkpoint': checkpoint},
        )
        # Another conversation in the same project is mid-run.
        AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-sol', project_id=project.id,
            run_started_at=timezone.now(),
        )
        resp = self.client.post(
            reverse('conversation_restore_checkpoint', args=[conversation.id]),
            data={'message_id': msg.id}, content_type='application/json',
        )
        self.assertEqual(resp.status_code, 409)
        self.assertEqual(resp.json()['detail'], 'agent_busy')


class ComputeCostTests(SimpleTestCase):
    def test_computes_from_suite_pricing(self):
        # Sol: $6/M input + $30/M output
        self.assertEqual(compute_cost_usd('gpt-5.6-sol', 1_000_000, 1_000_000), 36.0)
        # Luna: $1/M input + $5/M output
        self.assertEqual(compute_cost_usd('gpt-5.6-luna', 500_000, 200_000), 1.5)

    def test_unknown_model_returns_none(self):
        self.assertIsNone(compute_cost_usd('gpt-oops', 1000, 1000))


class RunBoundsHookTests(SimpleTestCase):
    """The cost and wall-clock bounds that stop a long run."""

    def _fire(self, hook, input_tokens=0, output_tokens=0, response=None):
        context = SimpleNamespace(
            usage=SimpleNamespace(
                input_tokens=input_tokens, output_tokens=output_tokens
            )
        )
        async_to_sync(hook.on_llm_end)(context, None, response)

    def _start_turn(self, hook):
        async_to_sync(hook.on_llm_start)(None, None, None, [])

    @staticmethod
    def _response_with_tool_call():
        return SimpleNamespace(output=[
            SimpleNamespace(type='reasoning'),
            SimpleNamespace(type='function_call'),
        ])

    def test_no_bounds_means_no_hook(self):
        self.assertIsNone(make_run_bounds_hook('gpt-5.6-sol'))

    def test_run_within_both_bounds_is_left_alone(self):
        hook = make_run_bounds_hook(
            'gpt-5.6-sol', budget_usd=10.0, deadline_at=time.monotonic() + 300
        )
        self._fire(hook, input_tokens=1000, output_tokens=100)

    def test_passed_deadline_stops_the_run(self):
        hook = make_run_bounds_hook(
            'gpt-5.6-sol', deadline_at=time.monotonic() - 1
        )
        with self.assertRaises(RunDeadlineExceeded):
            self._fire(hook)

    def test_deadline_is_checked_before_cost(self):
        # A run that is both over time and over budget reports the deadline:
        # for the initial build, time is the bound that matters.
        hook = make_run_bounds_hook(
            'gpt-5.6-sol', budget_usd=0.01, deadline_at=time.monotonic() - 1
        )
        with self.assertRaises(RunDeadlineExceeded):
            self._fire(hook, input_tokens=1_000_000, output_tokens=1_000_000)

    def test_spent_budget_stops_the_run(self):
        hook = make_run_bounds_hook('gpt-5.6-sol', budget_usd=1.0)
        with self.assertRaises(RunBudgetExceeded):
            self._fire(hook, input_tokens=1_000_000, output_tokens=0)

    def test_pending_tool_calls_run_before_the_stop(self):
        # The turn that ends over the deadline is usually the turn that wrote
        # the page. Stopping on the spot would discard it, so its tool calls
        # are executed and the run stops before the next model turn instead.
        hook = make_run_bounds_hook(
            'gpt-5.6-sol', deadline_at=time.monotonic() - 1
        )
        self._fire(hook, response=self._response_with_tool_call())
        with self.assertRaises(RunDeadlineExceeded):
            self._start_turn(hook)

    def test_stop_is_deferred_only_past_the_bound(self):
        hook = make_run_bounds_hook(
            'gpt-5.6-sol', deadline_at=time.monotonic() + 300
        )
        self._fire(hook, response=self._response_with_tool_call())
        self._start_turn(hook)

    def test_a_deferred_stop_still_fires_without_on_llm_start(self):
        # Belt and braces for an SDK that never calls on_llm_start: the next
        # turn's end raises rather than letting the run continue unbounded.
        hook = make_run_bounds_hook(
            'gpt-5.6-sol', deadline_at=time.monotonic() - 1
        )
        self._fire(hook, response=self._response_with_tool_call())
        with self.assertRaises(RunDeadlineExceeded):
            self._fire(hook, response=self._response_with_tool_call())


class InitialBuildAgentTests(SimpleTestCase):
    """The first-build role's own configuration, which trades depth for speed."""

    def test_initial_build_has_no_web_search_tool(self):
        # A hosted search can eat a large share of a half-minute budget, and
        # its schema costs every later turn prompt tokens.
        agent = create_coding_agent(kind='initial_build')
        self.assertNotIn(
            'WebSearchTool', [type(tool).__name__ for tool in agent.tools]
        )

    def test_chat_keeps_web_search(self):
        agent = create_coding_agent(kind='chat')
        self.assertIn(
            'WebSearchTool', [type(tool).__name__ for tool in agent.tools]
        )

    def test_initial_build_can_still_write_files(self):
        agent = create_coding_agent(kind='initial_build')
        names = {getattr(tool, 'name', '') for tool in agent.tools}
        self.assertTrue({'create_file', 'update_file'} <= names, names)

    def test_prompt_quotes_the_real_time_budget(self):
        # The agent paces itself by the number in its prompt, so that number is
        # read from the same setting that stops the run.
        self.assertIn(
            f"about {INITIAL_BUILD_TIME_BUDGET_S} seconds",
            INITIAL_BUILD_INSTRUCTIONS,
        )

    def test_prompt_scopes_each_subagent_to_a_single_file(self):
        # Half a minute buys one good write. Anything split across files can be
        # cut off mid-way holding a dangling import, which discards the page —
        # and with several subagents running at once, a stray edit outside your
        # own file also collides with a sibling's work at merge time.
        self.assertIn('Your job is ONE file', INITIAL_BUILD_INSTRUCTIONS)
        for rule in (
            'Do NOT create component files',
            'do NOT add other pages',
            'do NOT add routes',
        ):
            self.assertIn(rule, INITIAL_BUILD_INSTRUCTIONS)

    def test_every_first_build_page_is_described_in_the_shared_prompt(self):
        # Each subagent needs to know the other pages exist and where they
        # live, so it can link them in its own header and footer without
        # touching a file it does not own.
        from apps.Imagi.ProjectManager.services.initial_build_service import (
            PAGE_BRIEFS,
        )

        for page in PAGE_BRIEFS:
            self.assertIn(page.view_path, INITIAL_BUILD_INSTRUCTIONS)

    def test_the_home_brief_wires_in_the_prebuilt_auth_pages(self):
        # The auth app is prebuilt and left untouched; bringing its two pages
        # into the site is the home page's job specifically, so it lives in
        # that page's brief rather than in the prompt every page shares.
        from apps.Imagi.ProjectManager.services.initial_build_service import (
            PAGE_BRIEFS,
        )

        home = PAGE_BRIEFS[0]
        self.assertEqual(home.slug, 'home')
        for path in ("'/auth/signin'", "'/auth/register'"):
            self.assertIn(path, home.requirements)
        self.assertIn('useAuthStore', home.requirements)
        self.assertIn(
            "Do NOT open, restyle, or modify anything under "
            "'frontend/vuejs/src/apps/auth/'",
            home.requirements,
        )

    def test_the_other_pages_are_told_to_leave_auth_to_home(self):
        # Two pages both writing an auth header is duplicated work at best; at
        # worst the about page invents its own sign-in flow.
        from apps.Imagi.ProjectManager.services.initial_build_service import (
            PAGE_BRIEFS,
        )

        for page in PAGE_BRIEFS[1:]:
            self.assertIn('Do not import the auth store', page.requirements)

    def test_initial_build_runs_at_its_configured_effort(self):
        # Set explicitly for the role, so a per-request effort meant for the
        # interactive builders cannot slow the first build down.
        agent = create_coding_agent(
            kind='initial_build', reasoning_effort='xhigh'
        )
        self.assertEqual(
            agent.model_settings.reasoning.effort, INITIAL_BUILD_REASONING_EFFORT
        )


class LeadAgentConfigurationTests(SimpleTestCase):
    """The coordinator role's own configuration."""

    def test_the_lead_calls_its_tools_one_at_a_time(self):
        # dispatch_task creates a subagent that starts editing the project, and
        # the model cannot see that until the call returns. Left parallel, one
        # assistant message can carry the same dispatch twice — two subagents
        # on one job, each merging over the other.
        agent = create_coding_agent(kind='lead')
        self.assertIs(agent.model_settings.parallel_tool_calls, False)

    def test_builders_still_call_tools_in_parallel(self):
        # Their tools read and edit files; batching those is the whole point.
        for kind in ('chat', 'task', 'initial_build'):
            agent = create_coding_agent(kind=kind)
            self.assertIsNot(agent.model_settings.parallel_tool_calls, False, kind)

    def test_the_lead_is_told_one_job_is_one_subagent(self):
        self.assertIn(
            'ONE job, ONE dispatch_task call, ONE subagent', LEAD_AGENT_INSTRUCTIONS
        )

    def test_the_lead_is_told_never_to_narrate_an_unmade_dispatch(self):
        # A lead was observed replying "Done — I've kicked off a subagent…"
        # with no dispatch_task call at all, so the request went nowhere. The
        # prompt now says the claim is only ever made after the call.
        self.assertIn('Saying it does not make it so', LEAD_AGENT_INSTRUCTIONS)


class LeadDispatchClaimTests(SimpleTestCase):
    """The predicate behind the unbacked-kickoff guard."""

    def setUp(self):
        self.lead = SimpleNamespace(id=1, kind='lead')
        self.context = AgentContext(user_id=1, project_id=1, conversation_kind='lead')

    def test_kickoff_claims_without_a_dispatch_are_caught(self):
        for text in (
            # The observed failure, verbatim shape (dev conversation 69).
            "Done — I've kicked off a subagent to add a concise note about "
            "free local delivery on orders over $40 to the Home page. I'll "
            "report back once it's complete.",
            "On it — kicking off a subagent to redesign your home page.",
            "Handing that to a subagent now.",
            "I've dispatched a background task for this.",
            "Spinning up a background job to fix the nav.",
        ):
            self.assertTrue(
                lead_claims_unmade_dispatch(self.lead, self.context, text), text
            )

    def test_plain_replies_pass(self):
        for text in (
            "The hero heading is a rich coffee brown (around #4B3221).",
            "Quick check: which page should the note go on?",
            "Your app has three pages: home, about and contact.",
            "",
            None,
        ):
            self.assertFalse(
                lead_claims_unmade_dispatch(self.lead, self.context, text), text
            )

    def test_a_backed_claim_passes(self):
        self.context.dispatched_tasks.append(
            {'conversation_id': 99, 'title': 'Add note', 'brief': 'add the note'}
        )
        self.assertFalse(lead_claims_unmade_dispatch(
            self.lead, self.context, "On it — kicked off a subagent to add the note."
        ))

    def test_only_lead_replies_are_guarded(self):
        # Builders talk about their own work directly; "kicked off" in a chat
        # or task reply claims nothing about dispatching.
        for kind in ('chat', 'task', None):
            conversation = SimpleNamespace(id=1, kind=kind)
            self.assertFalse(lead_claims_unmade_dispatch(
                conversation, self.context, "Kicked off a subagent."
            ), kind)


class LeadDispatchGuardTests(TestCase):
    """The run loop's server-side guard for the unbacked-kickoff reply.

    Reproduced on dev conversation 69: the lead answered "Done — I've kicked
    off a subagent to add a concise note…" while making no dispatch_task call,
    so no task conversation existed and the request silently went nowhere.
    The guard gives the model one corrective turn to make the real call, and
    if it still claims without dispatching, persists an honest failure note.
    """

    CLAIM = "Done — I've kicked off a subagent to add the delivery note."

    def setUp(self):
        self.user = User.objects.create_user(username='leadguard', password='pw123456')
        self.service = ImagiAgentService()
        self.conversation = SimpleNamespace(id=69, kind='lead')
        self.context = AgentContext(
            user_id=self.user.id, project_id=1, conversation_kind='lead'
        )
        self.persisted = []
        self.service._prepare_run = lambda **kwargs: (
            self.conversation,
            self.context,
            [{'role': 'user', 'content': kwargs['user_input']}],
        )
        self.service.add_assistant_message = (
            lambda conv, content, metadata=None: self.persisted.append(content)
        )

    def _dispatching_run(self, text):
        """A fake retry run that actually stages a task, like dispatch_task."""
        context = self.context

        class Dispatching(_FakeStreamedRun):
            async def stream_events(inner):
                context.dispatched_tasks.append(
                    {'conversation_id': 89, 'title': 'Add note', 'brief': 'add the note'}
                )
                for event in inner._events:
                    yield event

        return Dispatching([_delta_event(text)], final_output=text)

    async def _collect(self):
        return [
            event async for event in self.service.process_stream(
                user_input='Add a delivery note to the home page.',
                user=self.user, project_id=1,
            )
        ]

    def _run(self, runs):
        with patch.object(type(self.service), 'agent', new_callable=PropertyMock) as mock_agent, \
                patch('apps.Imagi.Build.services.base_agent.Runner') as mock_runner:
            mock_agent.return_value = SimpleNamespace()
            mock_runner.run_streamed.side_effect = runs
            events = async_to_sync(self._collect)()
            return events, mock_runner

    def test_unbacked_claim_gets_a_corrective_turn_that_dispatches(self):
        confirmation = 'On it — kicked off a subagent to add the delivery note.'
        events, runner = self._run([
            _FakeStreamedRun([_delta_event(self.CLAIM)], final_output=self.CLAIM),
            self._dispatching_run(confirmation),
        ])

        self.assertEqual(runner.run_streamed.call_count, 2)
        # The corrective turn carries the false reply and the retry prompt.
        retry_input = runner.run_streamed.call_args_list[1][1]['input']
        self.assertEqual(
            retry_input[-2], {'role': 'assistant', 'content': self.CLAIM}
        )
        self.assertEqual(
            retry_input[-1], {'role': 'user', 'content': LEAD_DISPATCH_RETRY_PROMPT}
        )
        # The retry's (now backed) confirmation is what the thread keeps.
        done = events[-1]
        self.assertEqual(done['type'], 'done')
        self.assertEqual(done['response'], confirmation)
        self.assertEqual(done['dispatched_tasks'], self.context.dispatched_tasks)
        self.assertEqual(self.persisted, [confirmation])

    def test_persistent_false_claim_is_replaced_with_honest_note(self):
        events, runner = self._run([
            _FakeStreamedRun([], final_output=self.CLAIM),
            _FakeStreamedRun([], final_output='Kicked off a subagent to handle it.'),
        ])

        self.assertEqual(runner.run_streamed.call_count, 2)
        # The false promise never lands in the transcript; the honest note
        # does, and it also reaches the live stream.
        self.assertEqual(self.persisted, [LEAD_DISPATCH_FAILED_NOTE])
        self.assertEqual(events[-1]['response'], LEAD_DISPATCH_FAILED_NOTE)
        self.assertIn(
            '\n\n' + LEAD_DISPATCH_FAILED_NOTE,
            [e.get('text') for e in events if e['type'] == 'delta'],
        )

    def test_backed_dispatch_runs_once(self):
        confirmation = 'On it — kicked off a subagent to add the delivery note.'
        events, runner = self._run([self._dispatching_run(confirmation)])

        self.assertEqual(runner.run_streamed.call_count, 1)
        self.assertEqual(events[-1]['response'], confirmation)
        self.assertEqual(self.persisted, [confirmation])

    def test_plain_lead_reply_runs_once(self):
        reply = 'Your home page has a hero, a menu and an FAQ section.'
        events, runner = self._run([_FakeStreamedRun([], final_output=reply)])

        self.assertEqual(runner.run_streamed.call_count, 1)
        self.assertEqual(self.persisted, [reply])


class CappedRunNoteTests(SimpleTestCase):
    """What a capped run tells the user it built.

    A time-bounded first build ends at its cap as a matter of course, so this
    note is the normal completion message in the subagent's thread — read by
    the app's owner, so it names pages and never the files behind them.
    """

    def test_note_names_the_pages_that_were_built(self):
        note = _capped_run_note([
            'frontend/vuejs/src/apps/home/views/HomeView.vue',
            'frontend/vuejs/src/apps/home/views/ContactUsView.vue',
        ])
        self.assertIn('Home and Contact Us', note)
        self.assertNotIn('.vue', note)
        self.assertNotIn('frontend', note)

    def test_supporting_files_are_not_named(self):
        note = _capped_run_note([
            'frontend/vuejs/src/apps/home/views/HomeView.vue',
            'frontend/vuejs/src/apps/home/router/index.ts',
            'backend/django/apps/home/models.py',
        ])
        self.assertIn('Home page is built', note)
        self.assertIn('holds them together', note)
        self.assertNotIn('router', note)
        self.assertNotIn('models', note)

    def test_a_build_with_no_finished_page_says_so(self):
        note = _capped_run_note(['frontend/vuejs/src/apps/home/router/index.ts'])
        self.assertIn('groundwork', note)
        self.assertNotIn('router', note)

    def test_long_page_lists_are_summarized(self):
        files = [f'frontend/vuejs/src/apps/home/views/Page{i}View.vue' for i in range(20)]
        note = _capped_run_note(files)
        self.assertIn('Page0', note)
        self.assertIn(f'and {20 - CAPPED_NOTE_MAX_PAGES} more pages are built', note)

    def test_a_run_that_built_nothing_says_so(self):
        # Must not claim work it did not do — this is the message the user reads.
        note = _capped_run_note([])
        self.assertIn('ran out of build time', note)
        self.assertNotIn("here's what", note.lower())


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


class MessagePreviewTests(SimpleTestCase):
    """The one-line gist the main thread's dispatch card reports as a result."""

    def _preview(self, text):
        from apps.Imagi.Build.api.views import _message_preview
        return _message_preview(text)

    def test_reads_past_a_heading_line_to_the_substance(self):
        # A subagent's sign-off routinely opens with a header and puts what it
        # actually did underneath — stopping at line one would report nothing.
        preview = self._preview(
            "Here's what I built:\n\n"
            "- A pricing page with three tiers\n"
            "- A contact form that validates on submit\n"
        )
        self.assertIn('A pricing page with three tiers', preview)
        self.assertIn('A contact form', preview)

    def test_strips_markdown_chrome(self):
        preview = self._preview("## Done\n\n**Added** the `/contact` route.\n---\n")
        self.assertEqual(preview, 'Done Added the /contact route.')

    def test_caps_the_length(self):
        from apps.Imagi.Build.api.views import PREVIEW_LIMIT
        preview = self._preview('word ' * 400)
        self.assertLessEqual(len(preview), PREVIEW_LIMIT)

    def test_empty_message_previews_as_empty(self):
        self.assertEqual(self._preview(''), '')
        self.assertEqual(self._preview('\n\n---\n'), '')


class ConversationBriefTests(TestCase):
    """What a task was asked to do — the line its card shows while it runs."""

    def setUp(self):
        self.user = User.objects.create_user(username='briefs', password='pw123456')
        self.client.force_login(self.user)

    def _task(self, **kwargs):
        return AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=1,
            kind='task', **kwargs
        )

    def _brief(self, conversation):
        resp = self.client.get(reverse('conversation_detail', args=[conversation.id]))
        self.assertEqual(resp.status_code, 200)
        return resp.json()['brief']

    def test_the_leads_goal_is_what_the_user_reads(self):
        # The whole point of the field: the brief may be an engineer's ticket
        # naming files, and the card must never show that when a goal exists.
        task = self._task(
            goal='Adding a contact page so customers can reach you.',
            queued_prompt='Create apps/contact/views/ContactView.vue with a form',
        )
        self.assertEqual(
            self._brief(task), 'Adding a contact page so customers can reach you.'
        )

    def test_brief_comes_from_the_queued_prompt_before_the_run_fires(self):
        task = self._task(queued_prompt='Add a contact page so customers can reach you.')
        self.assertEqual(
            self._brief(task), 'Add a contact page so customers can reach you.'
        )

    def test_brief_survives_the_run_that_clears_the_queued_prompt(self):
        # queued_prompt is cleared the moment the run starts, which is exactly
        # when the card needs the brief — so the opening message is the copy
        # that has to answer.
        task = self._task(queued_prompt='')
        AgentMessage.objects.create(
            conversation=task, role='user',
            content='Add a contact page so customers can reach you.',
        )
        AgentMessage.objects.create(
            conversation=task, role='assistant', content='Working on it.'
        )
        self.assertEqual(
            self._brief(task), 'Add a contact page so customers can reach you.'
        )

    def test_brief_is_trimmed_to_a_status_line(self):
        from apps.Imagi.Build.api.views import BRIEF_LIMIT
        task = self._task(queued_prompt='Goal: ' + 'x' * 400)
        self.assertLessEqual(len(self._brief(task)), BRIEF_LIMIT)

    def test_chat_threads_have_no_brief(self):
        # An ordinary thread's opening message is the user talking, which is
        # not a status line about anything.
        chat = AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=1, kind='chat'
        )
        AgentMessage.objects.create(conversation=chat, role='user', content='hey')
        self.assertEqual(self._brief(chat), '')


class FailedTaskRunTests(TestCase):
    """A run that dies has to leave the task somewhere the user can act on.

    A background task nobody is watching must not be left at 'active' when its
    run raises: the Subagents pane and its dispatch card would go on reporting
    work in progress forever, its worktree would never be freed, and the only
    trace would be an error card in the main thread that cannot clear it.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='failing', password='pw123456')
        self.service = ImagiAgentService()
        self.lead = AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=1, kind='lead',
        )

    def _task(self, review_status='active'):
        return AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=1, kind='task',
            parent=self.lead, review_status=review_status,
            worktree_path='/tmp/project--wt-1',
        )

    def _context(self):
        return AgentContext(
            user_id=self.user.id, project_id=1, conversation_kind='task',
        )

    def _stream(self, conversation, error):
        """Run process_stream with a stream that raises, and return its events."""
        class Exploding(_FakeStreamedRun):
            async def stream_events(self):
                yield _delta_event('I started ')
                raise error

        async def collect():
            return [
                event async for event in self.service.process_stream(
                    user_input='go', user=self.user, project_id=1,
                    conversation_id=conversation.id,
                )
            ]

        with patch.object(
            self.service, '_prepare_run',
            return_value=(conversation, self._context(), [{'role': 'user', 'content': 'go'}]),
        ), patch.object(
            type(self.service), 'agent', new_callable=PropertyMock
        ) as mock_agent, patch(
            'apps.Imagi.Build.services.base_agent.Runner'
        ) as mock_runner:
            mock_agent.return_value = SimpleNamespace()
            mock_runner.run_streamed.return_value = Exploding([])
            return async_to_sync(collect)()

    def test_streamed_failure_parks_the_task_and_queues_the_error(self):
        task = self._task()

        events = self._stream(task, RuntimeError('model exploded'))

        self.assertEqual(events[-1]['type'], 'error')
        task.refresh_from_db()
        # Not 'active': the run is over and nothing was merged.
        self.assertEqual(task.review_status, 'failed')
        # The worktree stays until the user dismisses the task — whatever the
        # run managed to write is still in it.
        self.assertNotEqual(task.worktree_path, '')
        check_in = AgentCheckIn.objects.get(conversation=task)
        self.assertEqual(check_in.kind, 'error')
        self.assertEqual(check_in.status, 'pending')
        self.assertEqual(check_in.lead_id, self.lead.id)
        self.assertIn('model exploded', check_in.body)

    def test_blocking_run_failure_parks_the_task(self):
        task = self._task()

        with patch.object(
            self.service, '_prepare_run',
            return_value=(task, self._context(), [{'role': 'user', 'content': 'go'}]),
        ), patch(
            'apps.Imagi.Build.services.base_agent.Runner.run_sync',
            side_effect=RuntimeError('worker died'),
        ):
            result = self.service.process(
                user_input='go', user=self.user, project_id=1,
                conversation_id=task.id,
            )

        self.assertFalse(result['success'])
        task.refresh_from_db()
        self.assertEqual(task.review_status, 'failed')
        self.assertIn('worker died', AgentCheckIn.objects.get(conversation=task).body)

    def test_a_failed_task_holds_one_queue_slot(self):
        task = self._task()

        self._stream(task, RuntimeError('first failure'))
        self._stream(task, RuntimeError('second failure'))

        pending = AgentCheckIn.objects.filter(conversation=task, status='pending')
        self.assertEqual(pending.count(), 1)
        self.assertIn('second failure', pending.first().body)

    def test_accepted_work_is_never_relabelled_by_a_later_failure(self):
        # The task's changes are already in the app; calling it failed would
        # make the record lie about where that work went.
        task = self._task(review_status='accepted')

        self.service._park_failed_task(task, 'The task hit an error: boom')

        task.refresh_from_db()
        self.assertEqual(task.review_status, 'accepted')

    def test_canonical_threads_are_left_alone(self):
        # A chat/lead failure is reported to the user who is sitting there
        # watching it; there is no review lifecycle to park.
        chat = AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=1, kind='chat',
        )

        self.service._park_failed_task(chat, 'The task hit an error: boom')

        chat.refresh_from_db()
        self.assertEqual(chat.review_status, '')
        self.assertEqual(AgentCheckIn.objects.count(), 0)


class TaskTurnCapTests(TestCase):
    """A background task's turn cap: continue the work, then ask the user.

    Nobody is watching a task thread, so reaching the cap there is a place to
    pick back up rather than a place to stop. Only a task still unfinished
    after its continuations reaches the user, and it arrives as a question in
    the main thread's queue — never as a task stranded mid-run.
    """

    def setUp(self):
        self.user = User.objects.create_user(username='capper', password='pw123456')
        self.service = ImagiAgentService()
        self.conversation = SimpleNamespace(id=11, kind='task')
        self.context = AgentContext(user_id=self.user.id, project_id=1)
        self.prompts = []
        self.parked = []

        def prepare(**kwargs):
            self.prompts.append(kwargs['user_input'])
            return (
                self.conversation,
                self.context,
                [{'role': 'user', 'content': kwargs['user_input']}],
            )

        self.service._prepare_run = prepare
        self.service.add_assistant_message = lambda conv, content, metadata=None: None
        self.service._finalize_task_run = lambda conv, ctx, content: None
        self.service._clear_run_started = lambda conv: None
        self.service._record_usage_event = lambda *a, **kw: None
        self.service.autoname_from_first_reply = lambda *a, **kw: ''
        self.service._continuation_allowed = lambda user: True
        self.service._park_capped_task = lambda cid: self.parked.append(cid)

    def _capping_run(self, text):
        class HitsTurnCap(_FakeStreamedRun):
            async def stream_events(inner):
                yield _delta_event(text)
                raise MaxTurnsExceeded('Max turns (60) exceeded')

        return HitsTurnCap([])

    async def _collect(self):
        return [
            event async for event in self.service.process_stream(
                user_input='add a contact page', user=self.user, project_id=1
            )
        ]

    def _run(self, runs):
        with patch.object(type(self.service), 'agent', new_callable=PropertyMock) as mock_agent, \
                patch('apps.Imagi.Build.services.base_agent.Runner') as mock_runner:
            mock_agent.return_value = SimpleNamespace()
            mock_runner.run_streamed.side_effect = runs
            self.mock_runner = mock_runner
            return async_to_sync(self._collect)()

    def test_capped_task_continues_itself_and_finishes(self):
        events = self._run([
            self._capping_run('Started the page '),
            _FakeStreamedRun([_delta_event('and finished it.')], final_output='Done.'),
        ])

        # The cap never reaches the client: the run simply kept going.
        self.assertNotIn('error', [e['type'] for e in events])
        self.assertEqual(events[-1]['type'], 'done')
        self.assertEqual(events[-1]['response'], 'Done.')
        # One run, as far as the user's thread is concerned.
        self.assertEqual([e['type'] for e in events].count('start'), 1)
        # The second round resumed the same conversation, unprompted.
        self.assertEqual(len(self.prompts), 2)
        self.assertNotEqual(self.prompts[1], self.prompts[0])
        self.assertEqual(self.parked, [])

    def test_task_asks_the_user_once_its_continuations_run_out(self):
        rounds = TASK_AUTO_CONTINUE_ROUNDS + 1
        events = self._run([self._capping_run('Still going ') for _ in range(rounds)])

        self.assertEqual(len(self.prompts), rounds)
        error = events[-1]
        self.assertEqual(error['type'], 'error')
        self.assertEqual(error['code'], 'max_turns')
        # Parked for the user rather than left mid-run.
        self.assertEqual(self.parked, [self.conversation.id])

    def test_a_spent_usage_allowance_stops_the_continuations(self):
        self.service._continuation_allowed = lambda user: False
        events = self._run([self._capping_run('One round only ')])

        # No second run: continuing would spend past a limit the user has hit.
        self.assertEqual(len(self.prompts), 1)
        self.assertEqual(events[-1]['code'], 'max_turns')
        self.assertEqual(self.parked, [self.conversation.id])

    def test_chat_run_reports_its_cap_immediately(self):
        # The user is sitting in front of a chat thread, so its cap is theirs
        # to see and act on — no silent continuation.
        self.conversation.kind = 'chat'
        events = self._run([self._capping_run('Thinking ')])

        self.assertEqual(len(self.prompts), 1)
        self.assertEqual(events[-1]['code'], 'max_turns')
        self.assertEqual(self.parked, [])

    def test_tasks_get_a_bigger_loop_than_chat(self):
        self.assertEqual(
            self.service._max_turns_for(SimpleNamespace(kind='task')), TASK_MAX_TURNS
        )
        self.assertEqual(
            self.service._max_turns_for(SimpleNamespace(kind='chat')), MAX_AGENT_TURNS
        )
        self.assertGreater(TASK_MAX_TURNS, MAX_AGENT_TURNS)


class ParkCappedTaskTests(TestCase):
    """A task out of continuations lands where the user can answer it."""

    def setUp(self):
        self.user = User.objects.create_user(username='parker', password='pw123456')
        self.service = ImagiAgentService()
        self.lead = AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=1, kind='lead'
        )
        self.task = AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=1, kind='task',
            parent=self.lead, review_status='active',
            goal='add a contact page so visitors can reach you',
            worktree_path='/tmp/project--wt-1',
        )

    def test_parking_queues_a_question_and_keeps_the_worktree(self):
        self.service._park_capped_task(self.task.id)
        self.task.refresh_from_db()

        self.assertEqual(self.task.review_status, 'input')
        # The worktree is what the user's answer resumes into: merging or
        # dropping it here would throw the unfinished work away.
        self.assertEqual(self.task.worktree_path, '/tmp/project--wt-1')
        check_in = AgentCheckIn.objects.get(conversation=self.task, status='pending')
        # A question, not an error: the card it renders takes an answer, and
        # the answer is what resumes the task.
        self.assertEqual(check_in.kind, 'question')
        self.assertIn('keep going', check_in.body)
        self.assertEqual(check_in.lead, self.lead)

    def test_parking_replaces_an_earlier_entry_from_the_same_task(self):
        # A task holds at most one live queue slot, so an earlier round's
        # entry must not sit alongside this one.
        AgentCheckIn.objects.create(
            user=self.user, project_id=1, conversation=self.task, lead=self.lead,
            kind='error', body='an earlier round',
        )
        self.service._park_capped_task(self.task.id)

        pending = AgentCheckIn.objects.filter(conversation=self.task, status='pending')
        self.assertEqual([c.kind for c in pending], ['question'])


class CheckInQueueOrderTests(TestCase):
    """Queue order: what blocks a subagent comes before what blocks nobody."""

    def setUp(self):
        self.user = User.objects.create_user(username='queuer', password='pw123456')
        self.token = Token.objects.create(user=self.user)
        self.lead = AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=1, kind='lead'
        )

    def _check_in(self, kind, minutes_ago):
        task = AgentConversation.objects.create(
            user=self.user, model_name='gpt-5.6-terra', project_id=1, kind='task',
            parent=self.lead, review_status='active',
        )
        check_in = AgentCheckIn.objects.create(
            user=self.user, project_id=1, conversation=task, lead=self.lead,
            kind=kind, body=f'{kind} body',
        )
        # created_at is auto_now_add, so age is set after the fact.
        AgentCheckIn.objects.filter(id=check_in.id).update(
            created_at=timezone.now() - timedelta(minutes=minutes_ago)
        )
        return check_in

    def _queue(self):
        response = self.client.get(
            reverse('check_ins_list'),
            {'project_id': 1},
            HTTP_AUTHORIZATION=f'Token {self.token.key}',
        )
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_a_question_jumps_ahead_of_older_finished_work(self):
        self._check_in('ready', minutes_ago=30)
        self._check_in('error', minutes_ago=20)
        question = self._check_in('question', minutes_ago=1)

        queue = self._queue()
        self.assertEqual(queue[0]['id'], question.id)
        self.assertEqual([c['kind'] for c in queue], ['question', 'error', 'ready'])

    def test_questions_among_themselves_stay_fifo(self):
        first = self._check_in('question', minutes_ago=10)
        second = self._check_in('question', minutes_ago=5)

        self.assertEqual([c['id'] for c in self._queue()], [first.id, second.id])
