"""
Helper tools that run on Haiku, whatever model the agent itself is on.

Some of what the coordinator and threads do needs no judgment from the model
the user picked: searching the web and reading through the results, or
sweeping the project to find where something lives. Done by the agent itself,
every page of search results and every file it skims is billed at its own
rate and stays in its context for the rest of the run. These tools hand that
work to Haiku instead, and the agent gets back only the short answer.

- web_search: Haiku with Claude's server-side web search, answering one
  question with sources. The Anthropic SDK runs it directly, because the
  search count (billed per search) is only reported there.
- explore_project: Haiku as a read-only Agents SDK agent over the project's
  discovery tools, reporting where things are and what they do.

Each call's cost is metered against the user's allowance as its own usage
event, at Haiku's price, and added to the run's cost ceiling
(AgentContext.helper_cost_usd).
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

from agents import Agent, RunContextWrapper, Runner, function_tool
from asgiref.sync import sync_to_async
from django.conf import settings

from apps.Imagi.Build.services.api_keys import read_api_key
from apps.Imagi.Build.services.models_service import (
    compute_cost_usd,
    get_backend_model_id,
)

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = read_api_key('ANTHROPIC_KEY')

_BUILDER_SETTINGS = getattr(settings, 'IMAGI_BUILDER', {})

# The model every helper runs on (IMAGI_BUILDER in settings).
HELPER_MODEL = _BUILDER_SETTINGS.get('HELPER_MODEL', 'claude-haiku-5-5')

# Claude's server-side web search, the basic version: it runs on every model
# without code execution. max_uses bounds what one question can spend.
HELPER_WEB_SEARCH_TOOL = {
    'type': 'web_search_20250305',
    'name': 'web_search',
    'max_uses': 5,
}

# Anthropic bills web search per search, on top of tokens: $10 per 1,000.
WEB_SEARCH_PRICE_PER_SEARCH_USD = 0.01

# Room for a short answer with sources; the agent wants a summary, not pages.
HELPER_MAX_TOKENS = 4000

# A long server-tool loop can hand the turn back mid-way (stop_reason
# 'pause_turn'); the request is re-sent with the partial turn appended.
MAX_PAUSE_CONTINUATIONS = 3

# Turns one exploration may take: plenty to search, list and read.
EXPLORE_MAX_TURNS = 20

# Caps on what comes back to the calling agent.
ANSWER_MAX_CHARS = 6000
MAX_SOURCES = 8
QUESTION_MAX_CHARS = 2000

WEB_SEARCH_SYSTEM = """You research questions on the web for an AI agent that builds web apps for small businesses. Search, read what you find, and answer the question in a few short paragraphs or a tight list: the facts, numbers, names and code details the agent asked for, current as of today. Say plainly when sources disagree or you could not find something. Do not pad, and do not tell the agent what to build."""

EXPLORE_INSTRUCTIONS = """You explore a web app's codebase for another agent, read-only. Use the tools to find what the question asks about, then answer briefly: the relevant file paths, what each does, and the few lines that matter, quoted exactly with their line numbers. The project is a Vue 3 frontend under 'frontend/vuejs/' and a Django backend under 'backend/django/'. Search before reading (glob_files, grep_files), read only what you need, and say so when something does not exist. You cannot change files."""


def _clip(text: str, limit: int) -> str:
    text = (text or '').strip()
    return text if len(text) <= limit else text[:limit] + '\n… [truncated]'


def _error(message: str) -> str:
    return json.dumps({'success': False, 'error': message})


async def _meter(ctx: Any, input_tokens: int, output_tokens: int, cost_usd: Optional[float]) -> None:
    """Charge one helper call to the user, and to the run's cost ceiling."""
    if cost_usd is not None and hasattr(ctx, 'helper_cost_usd'):
        ctx.helper_cost_usd += cost_usd
    if not (input_tokens or output_tokens):
        return
    try:
        from django.contrib.auth import get_user_model
        from .usage_limits import record_usage

        def record():
            user = get_user_model().objects.filter(id=getattr(ctx, 'user_id', None)).first()
            if user is None:
                return
            record_usage(
                user,
                HELPER_MODEL,
                input_tokens,
                output_tokens,
                cost_usd=cost_usd,
                conversation_id=getattr(ctx, 'conversation_id', None),
            )

        await sync_to_async(record)()
    except Exception as e:  # metering must never fail the tool
        logger.warning(f"Could not record helper usage: {e}")


def _search_sources(content: List[Any]) -> List[Dict[str, str]]:
    """The pages the answer cites, in order and once each."""
    sources: List[Dict[str, str]] = []
    seen = set()
    for block in content or []:
        for citation in getattr(block, 'citations', None) or []:
            url = getattr(citation, 'url', None)
            if url and url not in seen:
                seen.add(url)
                sources.append({'title': getattr(citation, 'title', '') or url, 'url': url})
    return sources[:MAX_SOURCES]


async def run_web_search(question: str, client: Any = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Answer a question from the web on Haiku.

    Returns (result, usage): result is {'answer', 'sources'}; usage is
    {'input_tokens', 'output_tokens', 'cached_tokens', 'searches', 'cost_usd'}.
    """
    if client is None:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    messages: List[Dict[str, Any]] = [{'role': 'user', 'content': question}]
    usage = {'input_tokens': 0, 'output_tokens': 0, 'cached_tokens': 0, 'searches': 0}
    content: List[Any] = []
    for _ in range(MAX_PAUSE_CONTINUATIONS + 1):
        response = await client.messages.create(
            model=get_backend_model_id(HELPER_MODEL),
            max_tokens=HELPER_MAX_TOKENS,
            system=WEB_SEARCH_SYSTEM,
            messages=messages,
            tools=[dict(HELPER_WEB_SEARCH_TOOL)],
            # Finding and summarizing needs little reasoning.
            output_config={'effort': 'low'},
        )
        reading = getattr(response, 'usage', None)
        cache_read = getattr(reading, 'cache_read_input_tokens', 0) or 0
        cache_write = getattr(reading, 'cache_creation_input_tokens', 0) or 0
        usage['input_tokens'] += (getattr(reading, 'input_tokens', 0) or 0) + cache_read + cache_write
        usage['cached_tokens'] += cache_read
        usage['output_tokens'] += getattr(reading, 'output_tokens', 0) or 0
        server_tools = getattr(reading, 'server_tool_use', None)
        usage['searches'] += getattr(server_tools, 'web_search_requests', 0) or 0
        content.extend(response.content or [])
        if response.stop_reason != 'pause_turn':
            break
        messages.append({'role': 'assistant', 'content': response.content})

    token_cost = compute_cost_usd(
        HELPER_MODEL, usage['input_tokens'], usage['output_tokens'], usage['cached_tokens'],
    )
    usage['cost_usd'] = round(
        (token_cost or 0) + usage['searches'] * WEB_SEARCH_PRICE_PER_SEARCH_USD, 6
    )
    answer = ''.join(
        getattr(block, 'text', '') for block in content
        if getattr(block, 'type', '') == 'text'
    )
    return {'answer': _clip(answer, ANSWER_MAX_CHARS), 'sources': _search_sources(content)}, usage


def explore_agent() -> Agent:
    """The read-only Haiku agent behind explore_project."""
    from .base_agent import build_model_settings
    from .coding_agent import build_agent_model
    from .tools import LEAD_AGENT_READONLY_TOOLS

    kwargs = {}
    model_settings = build_model_settings('low')
    if model_settings is not None:
        kwargs['model_settings'] = model_settings
    return Agent(
        name="Imagi explorer",
        instructions=EXPLORE_INSTRUCTIONS,
        model=build_agent_model(HELPER_MODEL),
        tools=list(LEAD_AGENT_READONLY_TOOLS),
        **kwargs,
    )


@function_tool(name_override='web_search')
async def web_search(ctx: RunContextWrapper, question: str) -> str:
    """Look something up on the web. A fast research helper searches, reads the results and returns a short answer with its sources.

    Use it for current outside information — facts about the user's business or industry, prices, regulations, how a library or service works today — not for what you already know or what is in the project.

    Args:
        question: What you want to know, as a full question with any context that narrows it (place, date, product).
    """
    question = _clip(question, QUESTION_MAX_CHARS)
    if not question:
        return _error("Ask a question to search for.")
    try:
        result, usage = await run_web_search(question)
    except Exception as e:
        logger.warning(f"web_search failed: {e}")
        return _error(f"Search failed: {e}")
    await _meter(ctx.context, usage['input_tokens'], usage['output_tokens'], usage['cost_usd'])
    return json.dumps({'success': True, **result})


@function_tool(name_override='explore_project')
async def explore_project(ctx: RunContextWrapper, question: str) -> str:
    """Hand a codebase search to a fast helper that reads the project for you and reports back: which files matter, what they do, and the key lines with line numbers.

    Use it for broad questions that would take many searches and reads ("where is the booking form submitted, and what does the backend do with it?"). When you already know the file, read it yourself.

    Args:
        question: What to find out, specific enough to answer in a short report.
    """
    from .base_agent import usage_payload

    question = _clip(question, QUESTION_MAX_CHARS)
    if not question:
        return _error("Say what to look for.")
    try:
        result = await Runner.run(
            explore_agent(), question, context=ctx.context, max_turns=EXPLORE_MAX_TURNS,
        )
    except Exception as e:
        logger.warning(f"explore_project failed: {e}")
        return _error(f"Exploring failed: {e}")
    usage = usage_payload(result.context_wrapper.usage, HELPER_MODEL) or {}
    await _meter(
        ctx.context,
        usage.get('input_tokens') or 0,
        usage.get('output_tokens') or 0,
        usage.get('cost_usd'),
    )
    return json.dumps({
        'success': True,
        'answer': _clip(str(result.final_output or ''), ANSWER_MAX_CHARS),
    })


HELPER_TOOLS = [web_search, explore_project]
