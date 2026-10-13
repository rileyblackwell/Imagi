"""
A first home page in about two seconds, while the real one is written.

The home page Sol writes from scratch takes it over ten seconds, and the
founder waits on it. So alongside that call, a much smaller one asks the same
model only for the words and colours of a landing page (a few hundred tokens
of JSON), and they are dropped into a ready-made layout. That page goes up
and the project opens; the full page replaces it when it lands, and the
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


# The words are asked of the home page's own model and of a small fast one at
# once, and whichever answers first is used: a few hundred tokens of copy
# don't need the bigger model, but neither model is reliably the faster.
RACE_MODEL = ('gpt-6-luna', 'fast')


def request_copy(candidates, name, description, app_details='', design='',
                 meter: Optional[Callable] = None) -> Future:
    """Ask for the landing page's words and colours, on threads of their own.

    ``candidates`` is a list of (model, service_tier); each is asked at once
    and the future holds the first good answer. ``meter(model, service_tier,
    usage)`` is called for every answer, the losers' too, since each is paid
    for.
    """
    from apps.Imagi.Build.services.api_keys import read_api_key
    from apps.Imagi.Build.services.models_service import get_backend_model_id

    brief = f"Business name: {name}\n\nWhat it is (from the founder):\n{description}"
    if (app_details or '').strip():
        brief += f"\n\nHow it works (from the founder):\n{app_details.strip()}"
    if (design or '').strip():
        brief += f"\n\nStyle the founder asked for:\n{design.strip()}"

    started = time.monotonic()

    def ask(model, service_tier):
        from openai import OpenAI

        client = OpenAI(api_key=read_api_key('OPENAI_KEY'))
        kwargs = {}
        if service_tier:
            kwargs['service_tier'] = service_tier
        response = client.responses.create(
            model=get_backend_model_id(model),
            instructions=_INSTRUCTIONS,
            input=brief,
            reasoning={'effort': 'low'},
            text={'format': {
                'type': 'json_schema', 'name': 'landing_page', 'strict': True, 'schema': _SCHEMA,
            }},
            **kwargs,
        )
        if meter is not None:
            try:
                meter(model, service_tier, getattr(response, 'usage', None))
            except Exception as e:
                logger.warning("Could not meter the quick home words: %s", e)
        copy = json.loads(response.output_text)
        copy['_seconds'] = time.monotonic() - started
        copy['_model'] = model
        return copy

    future: Future = Future()
    lock = threading.Lock()
    outcomes = []

    def run(model, service_tier):
        try:
            result, error = ask(model, service_tier), None
        except Exception as e:  # the full page still comes; this was a bonus
            result, error = None, e
        with lock:
            outcomes.append(error)
            if future.done():
                return
            if error is None:
                future.set_result(result)
            elif len(outcomes) == len(candidates):
                future.set_exception(error)

    for model, service_tier in candidates:
        threading.Thread(
            target=run, args=(model, service_tier), name='quick-home', daemon=True,
        ).start()
    return future


def _colour(value, fallback):
    return value if isinstance(value, str) and _HEX.match(value) else fallback


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
    background = _colour(copy.get('background'), '#f8fafc')
    # json.dumps output is a valid TypeScript literal; '</' is split so the
    # text can never close the SFC's script block.
    literal = json.dumps(content, ensure_ascii=False, indent=2).replace('</', '<\\/')
    return QUICK_HOME_TEMPLATE.replace('__CONTENT__', literal).replace(
        '__ACCENT__', accent
    ).replace('__BACKGROUND__', background).replace('__MARKER__', QUICK_HOME_MARKER)


QUICK_HOME_TEMPLATE = """<!-- __MARKER__: a first version of this page; the full one replaces it. -->
<template>
  <div class="min-h-screen flex flex-col text-slate-900" :style="{ backgroundColor: background }">
    <header class="w-full">
      <nav class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-5 flex flex-wrap items-center justify-between gap-4">
        <router-link to="/" class="text-xl font-bold tracking-tight">{{ content.name }}</router-link>
        <div class="flex flex-wrap items-center gap-4">
          <router-link
            v-for="p in sitePages.filter((p) => p.path !== '/')"
            :key="p.path"
            :to="p.path"
            class="text-sm font-medium text-slate-600 hover:text-slate-900"
          >{{ p.label }}</router-link>
          <template v-if="authStore.isAuthenticated">
            <span class="text-sm text-slate-600">{{ authStore.user?.username }}</span>
            <button class="text-sm font-medium text-slate-700 hover:text-slate-900" @click="authStore.logout($router)">
              Sign out
            </button>
          </template>
          <template v-else>
            <router-link to="/auth/signin" class="text-sm font-medium text-slate-700 hover:text-slate-900">Sign in</router-link>
            <router-link
              to="/auth/register"
              class="text-sm font-semibold px-4 py-2 rounded-lg text-white shadow-sm hover:opacity-90"
              :style="{ backgroundColor: accent }"
            >Create account</router-link>
          </template>
        </div>
      </nav>
    </header>

    <main class="flex-grow">
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

      <section class="bg-white/70 border-y border-slate-200/70">
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

      <section class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
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

      <section class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        <div class="rounded-3xl px-8 py-14 text-center text-white" :style="{ backgroundColor: accent }">
          <h2 class="text-3xl font-bold">{{ content.closingHeadline }}</h2>
          <p class="mt-4 text-lg opacity-90 max-w-2xl mx-auto">{{ content.closingBody }}</p>
          <router-link to="/auth/register" class="mt-8 inline-block px-8 py-4 rounded-xl bg-white font-semibold text-slate-900 hover:opacity-90">
            {{ content.cta }}
          </router-link>
        </div>
      </section>
    </main>

    <footer class="border-t border-slate-200/70">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-sm text-slate-500">&copy; {{ new Date().getFullYear() }} {{ content.name }}</div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue'
import { useAuthStore } from '../../auth/stores/index'
import { sitePages } from '../site-pages'

const authStore = useAuthStore()
const accent = '__ACCENT__'
const background = '__BACKGROUND__'
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
