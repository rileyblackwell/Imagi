"""
A first home page in a few seconds, while the real one is written.

The home page Sol writes from scratch takes it over ten seconds, and the
founder waits on it. So alongside that call, a much smaller one asks the same
model only for the words and colours of a landing page (a few hundred tokens
of JSON), and they are dropped into a ready-made layout. The answer is
streamed: the hero goes up (and the project opens) as soon as its words are
in, and the rest of the sections follow. The full page replaces it when it
lands, and the
quick page reloads itself into it (QUICK_HOME_MARKER, the same way an
unbuilt page's placeholder does).
"""

import json
import logging
import re
import threading
import time
from concurrent.futures import Future
from typing import Callable, Dict, Optional

logger = logging.getLogger(__name__)
timing_logger = logging.getLogger('imagi.timing')

QUICK_HOME_MARKER = 'imagi-quick-home'

_HEX = re.compile(r'^#[0-9a-fA-F]{6}$')

_INSTRUCTIONS = (
    "You write the words and colours for a small business's landing page, "
    "which a designer's layout then renders. Write for the business's "
    "visitors, specific to this business, in plain language. Pick colours "
    "that suit the business and any style the founder asked for: an accent "
    "for buttons and highlights, and a very light page background."
)

_SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'required': [
        'headline', 'subheadline', 'cta_label', 'accent', 'background',
        'features_title', 'features', 'steps_title', 'steps',
        'closing_headline', 'closing_body',
    ],
    'properties': {
        'headline': {'type': 'string', 'description': 'At most 8 words.'},
        'subheadline': {'type': 'string', 'description': 'One or two sentences.'},
        'cta_label': {'type': 'string', 'description': 'The sign-up button, 2-4 words.'},
        'accent': {'type': 'string', 'description': 'Hex colour like #1f6feb.'},
        'background': {'type': 'string', 'description': 'Very light hex colour.'},
        'features_title': {'type': 'string'},
        'features': {
            'type': 'array', 'minItems': 3, 'maxItems': 3,
            'items': {
                'type': 'object', 'additionalProperties': False,
                'required': ['title', 'body'],
                'properties': {'title': {'type': 'string'}, 'body': {'type': 'string'}},
            },
        },
        'steps_title': {'type': 'string'},
        'steps': {
            'type': 'array', 'minItems': 3, 'maxItems': 3,
            'items': {
                'type': 'object', 'additionalProperties': False,
                'required': ['title', 'body'],
                'properties': {'title': {'type': 'string'}, 'body': {'type': 'string'}},
            },
        },
        'closing_headline': {'type': 'string'},
        'closing_body': {'type': 'string'},
    },
}


# The hero's fields, which the schema puts first so they stream in first.
HERO_FIELDS = ('headline', 'subheadline', 'cta_label', 'accent', 'background')


class QuickCopy:
    """The words, as they arrive: ``hero`` resolves as soon as the hero's
    fields have streamed in, ``full`` once the whole answer has."""

    def __init__(self):
        self.hero: Future = Future()
        self.full: Future = Future()


def _string_field(text: str, key: str) -> Optional[str]:
    """A top-level string field from partial JSON, once its value is complete."""
    match = re.search(r'"%s"\s*:\s*"((?:[^"\\]|\\.)*)"' % re.escape(key), text)
    if not match:
        return None
    try:
        return json.loads(f'"{match.group(1)}"')
    except ValueError:
        return None


def hero_from(text: str) -> Optional[Dict]:
    """The hero's fields from a partial answer, or None until all are in."""
    hero = {}
    for key in HERO_FIELDS:
        value = _string_field(text, key)
        if value is None:
            return None
        hero[key] = value
    return hero


def request_copy(model: str, service_tier: Optional[str], name, description,
                 app_details='', design='', meter: Optional[Callable] = None) -> QuickCopy:
    """Ask for the landing page's words and colours, streamed, on a thread.

    ``meter(model, service_tier, usage)`` is called with the answer's usage.
    """
    from apps.Imagi.Build.services.api_keys import read_api_key
    from apps.Imagi.Build.services.models_service import get_backend_model_id

    brief = f"Business name: {name}\n\nWhat it is (from the founder):\n{description}"
    if (app_details or '').strip():
        brief += f"\n\nHow it works (from the founder):\n{app_details.strip()}"
    if (design or '').strip():
        brief += f"\n\nStyle the founder asked for:\n{design.strip()}"

    copy = QuickCopy()
    started = time.monotonic()

    def ask():
        from openai import OpenAI

        client = OpenAI(api_key=read_api_key('OPENAI_KEY'))
        kwargs = {}
        if service_tier:
            kwargs['service_tier'] = service_tier
        stream = client.responses.create(
            model=get_backend_model_id(model),
            instructions=_INSTRUCTIONS,
            input=brief,
            reasoning={'effort': 'low'},
            text={'format': {
                'type': 'json_schema', 'name': 'landing_page', 'strict': True, 'schema': _SCHEMA,
            }},
            stream=True,
            **kwargs,
        )
        text, usage, first_at = '', None, None
        for event in stream:
            kind = getattr(event, 'type', '')
            if kind == 'response.output_text.delta':
                first_at = first_at or time.monotonic()
                text += event.delta
                if not copy.hero.done():
                    hero = hero_from(text)
                    if hero is not None:
                        hero['_seconds'] = time.monotonic() - started
                        copy.hero.set_result(hero)
            elif kind == 'response.completed':
                usage = getattr(event.response, 'usage', None)
        if meter is not None and usage is not None:
            try:
                meter(model, service_tier, usage)
            except Exception as e:
                logger.warning("Could not meter the quick home words: %s", e)
        answer = json.loads(text)
        answer['_seconds'] = time.monotonic() - started
        timing_logger.info(
            'quick home words: first token %.1fs, hero %.1fs, all %.1fs, %s output tokens',
            (first_at or started) - started,
            copy.hero.result().get('_seconds', 0) if copy.hero.done() else answer['_seconds'],
            answer['_seconds'], getattr(usage, 'output_tokens', '?'),
        )
        return answer

    def run():
        try:
            answer = ask()
        except Exception as e:  # the full page still comes; this was a bonus
            for future in (copy.hero, copy.full):
                if not future.done():
                    future.set_exception(e)
            return
        if not copy.hero.done():
            copy.hero.set_result(answer)
        copy.full.set_result(answer)

    threading.Thread(target=run, name='quick-home', daemon=True).start()
    return copy


def _colour(value, fallback):
    return value if isinstance(value, str) and _HEX.match(value) else fallback


def theme(copy: Dict) -> str:
    """The site's shared theme in the colours the words came with."""
    from apps.Imagi.Build.services.codegen.prebuilt_apps.home import (
        DEFAULT_ACCENT,
        DEFAULT_BACKGROUND,
        theme_css,
    )

    return theme_css(
        _colour(copy.get('accent'), DEFAULT_ACCENT),
        _colour(copy.get('background'), DEFAULT_BACKGROUND),
    )


def render(name: str, copy: Dict) -> str:
    """The quick home page: the layout with this business's words in it."""
    content = {
        'name': name,
        'headline': copy.get('headline') or name,
        'subheadline': copy.get('subheadline') or '',
        'cta': copy.get('cta_label') or 'Get started',
        'featuresTitle': copy.get('features_title') or '',
        'features': (copy.get('features') or [])[:3],
        'stepsTitle': copy.get('steps_title') or '',
        'steps': (copy.get('steps') or [])[:3],
        'closingHeadline': copy.get('closing_headline') or '',
        'closingBody': copy.get('closing_body') or '',
    }
    accent = _colour(copy.get('accent'), '#2563eb')
    # json.dumps output is a valid TypeScript literal; '</' is split so the
    # text can never close the SFC's script block.
    literal = json.dumps(content, ensure_ascii=False, indent=2).replace('</', '<\\/')
    return QUICK_HOME_TEMPLATE.replace('__CONTENT__', literal).replace(
        '__ACCENT__', accent
    ).replace('__MARKER__', QUICK_HOME_MARKER)


QUICK_HOME_TEMPLATE = """<!-- __MARKER__: a first version of this page; the full one replaces it. -->
<template>
  <div>
      <section class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-20 text-center">
        <h1 class="text-4xl sm:text-6xl font-extrabold tracking-tight text-balance max-w-4xl mx-auto">{{ content.headline }}</h1>
        <p class="mt-6 text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto">{{ content.subheadline }}</p>
        <div class="mt-10 flex flex-wrap items-center justify-center gap-4">
          <router-link
            to="/auth/register"
            class="px-8 py-4 rounded-xl text-white font-semibold shadow-lg hover:opacity-90 transition"
            :style="{ backgroundColor: accent }"
          >{{ content.cta }}</router-link>
          <router-link to="/auth/signin" class="px-8 py-4 rounded-xl border border-slate-300 font-semibold hover:bg-white/60 transition">
            Sign in
          </router-link>
        </div>
      </section>

      <section v-if="content.features.length" class="bg-white/70 border-y border-slate-200/70">
        <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <h2 class="text-2xl sm:text-3xl font-bold text-center">{{ content.featuresTitle }}</h2>
          <div class="mt-10 grid gap-6 sm:grid-cols-3">
            <div v-for="item in content.features" :key="item.title" class="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
              <div class="h-10 w-10 rounded-xl mb-4" :style="{ backgroundColor: accent, opacity: 0.15 }"></div>
              <h3 class="text-lg font-semibold">{{ item.title }}</h3>
              <p class="mt-2 text-slate-600">{{ item.body }}</p>
            </div>
          </div>
        </div>
      </section>

      <section v-if="content.steps.length" class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 class="text-2xl sm:text-3xl font-bold text-center">{{ content.stepsTitle }}</h2>
        <ol class="mt-10 grid gap-6 sm:grid-cols-3">
          <li v-for="(step, i) in content.steps" :key="step.title" class="flex gap-4">
            <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-white font-bold" :style="{ backgroundColor: accent }">{{ i + 1 }}</span>
            <div>
              <h3 class="font-semibold">{{ step.title }}</h3>
              <p class="mt-1 text-slate-600">{{ step.body }}</p>
            </div>
          </li>
        </ol>
      </section>

      <section v-if="content.closingHeadline" class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        <div class="rounded-3xl px-8 py-14 text-center text-white" :style="{ backgroundColor: accent }">
          <h2 class="text-3xl font-bold">{{ content.closingHeadline }}</h2>
          <p class="mt-4 text-lg opacity-90 max-w-2xl mx-auto">{{ content.closingBody }}</p>
          <router-link to="/auth/register" class="mt-8 inline-block px-8 py-4 rounded-xl bg-white font-semibold text-slate-900 hover:opacity-90">
            {{ content.cta }}
          </router-link>
        </div>
      </section>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue'

const accent = '__ACCENT__'
const content = __CONTENT__

// Reload once the full page has been written over this one.
let timer: number | undefined
onMounted(() => {
  timer = window.setInterval(async () => {
    try {
      const source = await (await fetch(import.meta.url.split('?')[0], { cache: 'no-store' })).text()
      if (!source.includes('__MARKER__')) window.location.reload()
    } catch {
      // Offline for a moment; try again on the next tick.
    }
  }, 1500)
})
onBeforeUnmount(() => window.clearInterval(timer))
</script>
"""
