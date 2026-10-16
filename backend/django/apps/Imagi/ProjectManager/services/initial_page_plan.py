"""
Which pages a new project's first build makes, and the scaffold they land in.

The first build used to make three fixed pages (home, about, contact). Which
pages a business needs depends on the business, so the pages after home are
now planned for it: one quick model call reads the founder's brief and picks
them, usually five to twenty in all and never more than MAX_PAGES. The home
page does not wait for the plan. It starts building the moment the project
exists, and the plan is made while it runs.

Every planned page gets a route and a placeholder view before its thread
starts, written here rather than by any agent, so each thread still rewrites
exactly one file it already owns and no two threads ever touch the router.

The pages link to each other through one generated list, 'site-pages.ts' in
the home app. It names every planned page from the start, so the home page's
navigation is whole the moment it lands; a page that is still being built
shows a "still being generated" notice and swaps itself for the real page when
that lands. Pages the build couldn't make are taken back out at the end.
"""

import html
import json
import logging
import os
import re
from typing import Iterable, List, Optional

logger = logging.getLogger(__name__)

# The whole first build, home page included.
MAX_PAGES = 20
# What the plan aims for; the model may go lower for a very small business.
TARGET_PAGES = (5, 20)

HOME_APP = 'frontend/vuejs/src/apps/home'
SITE_PAGES_PATH = f'{HOME_APP}/site-pages.ts'
ROUTER_PATH = f'{HOME_APP}/router/index.ts'
VIEWS_INDEX_PATH = f'{HOME_APP}/views/index.ts'

# Paths other parts of the app own: the prebuilt sign-in pages, and the
# prebuilt Sell pages a founder installs later. A planned page never takes one.
RESERVED_SLUGS = frozenset({
    'home', 'index', 'auth', 'signin', 'sign-in', 'login', 'log-in', 'logout',
    'signup', 'sign-up', 'register', 'account', 'profile', 'api', 'admin',
    'static', 'assets', 'media', 'store', 'shop-checkout', 'pricing', 'checkout',
    'cart', 'payments', 'billing', 'subscribe',
})

_SLUG_RE = re.compile(r'^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$')

# Appended to every planned page's own requirements: the shared layout
# carries the header (with the sign-in links) and the footer.
PAGE_RULES = (
    "Do not add a header, navigation, footer or sign-in links, which the site's "
    "shared layout provides, and do not import the auth store."
)

PLAN_SCHEMA = {
    'type': 'object',
    'properties': {
        'pages': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'slug': {'type': 'string'},
                    'label': {'type': 'string'},
                    'summary': {'type': 'string'},
                    'requirements': {'type': 'string'},
                },
                'required': ['slug', 'label', 'summary', 'requirements'],
                'additionalProperties': False,
            },
        },
    },
    'required': ['pages'],
    'additionalProperties': False,
}


def view_name(slug: str) -> str:
    """'opening-hours' -> 'OpeningHoursView'."""
    return ''.join(part.capitalize() for part in slug.split('-')) + 'View'


def view_path(slug: str) -> str:
    return f'{HOME_APP}/views/{view_name(slug)}.vue'


def _plan_prompt(name, description, app_details='', design_preferences='') -> str:
    low, high = TARGET_PAGES
    prompt = f"""Plan the first version of this business's web app. A home page is already being built; choose the other pages it needs.

Business name: {name}

What it does (from the founder):
{description}"""
    if (app_details or '').strip():
        prompt += f"\n\nHow the app should work (from the founder):\n{app_details.strip()}"
    if (design_preferences or '').strip():
        prompt += f"\n\nLook and feel (from the founder):\n{design_preferences.strip()}"
    prompt += f"""

Rules:
- Pick what a visitor to this business would expect, plus its product's core screens if it has one. Usually {low - 1} to {high - 1} pages besides home, never more than {MAX_PAGES - 1}; fewer, solid pages beat many thin ones.
- Each page is built on its own, at the same time as the others, so pages can't depend on each other's code.
- Leave out sign-in, account, pricing, checkout, cart and payment pages; Imagi provides those.
- slug: the page's URL path, lowercase and hyphenated, unique. label: one or two words for the navigation. summary: "the <name> page — <what it is for>". requirements: three to five sentences on what the page contains and does for this business. Pages are presentational: no backend calls, and forms confirm inline."""
    return prompt


def _clean(raw_pages, page_brief_cls) -> list:
    """Model output -> PageBriefs: valid, unique, unreserved slugs, capped."""
    pages = []
    seen = set()
    for raw in raw_pages or []:
        if not isinstance(raw, dict):
            continue
        slug = str(raw.get('slug', '')).strip().lower().strip('/')
        slug = re.sub(r'[^a-z0-9-]+', '-', slug).strip('-')
        if not slug or not _SLUG_RE.match(slug) or slug in RESERVED_SLUGS or slug in seen:
            continue
        label = re.sub(r'\s+', ' ', str(raw.get('label') or slug.replace('-', ' ').title())).strip()[:30]
        summary = re.sub(r'\s+', ' ', str(raw.get('summary') or f'the {label} page')).strip()[:200]
        requirements = str(raw.get('requirements') or '').strip()[:1500]
        if not requirements:
            continue
        seen.add(slug)
        page = page_brief_cls(
            slug=slug,
            title=f'{label} page',
            view_path=view_path(slug),
            route=f'/{slug}',
            summary=summary,
            requirements=f'{requirements}\n\n{PAGE_RULES}',
        )
        page.label = label
        pages.append(page)
        if len(pages) >= MAX_PAGES - 1:
            break
    return pages


def plan_pages(name, description, app_details='', design_preferences='', builder=None,
               page_brief_cls=None) -> Optional[list]:
    """The pages after home for this business, or None if no plan could be made.

    None means "use the fixed fallback pages": no API key, the call failed, or
    the answer had no usable page in it.
    """
    from apps.Imagi.Build.services import base_agent
    from apps.Imagi.Build.services.models_service import get_backend_model_id

    builder = builder or {}
    if not base_agent.ANTHROPIC_API_KEY:
        return None
    model = builder.get('INITIAL_BUILD_PLANNER_MODEL') or 'claude-sonnet-5-5'
    try:
        import anthropic

        client = anthropic.Anthropic(
            api_key=base_agent.ANTHROPIC_API_KEY,
            timeout=builder.get('INITIAL_BUILD_PLANNER_TIMEOUT_S', 30),
            max_retries=1,
        )
        response = client.messages.create(
            model=get_backend_model_id(model),
            max_tokens=8000,
            messages=[{
                'role': 'user',
                'content': _plan_prompt(name, description, app_details, design_preferences),
            }],
            output_config={
                'effort': 'low',
                'format': {'type': 'json_schema', 'schema': PLAN_SCHEMA},
            },
        )
        if response.stop_reason in ('refusal', 'max_tokens'):
            logger.warning("First-build page plan stopped early (%s)", response.stop_reason)
            return None
        text = next(
            (b.text for b in response.content if getattr(b, 'type', '') == 'text'), ''
        )
        pages = _clean(json.loads(text).get('pages'), page_brief_cls)
    except Exception as e:
        logger.warning("Could not plan the first build's pages: %s", e)
        return None
    return pages or None


# --- The scaffold --------------------------------------------------------------

def site_pages_ts(pages: Iterable) -> str:
    entries = '\n'.join(
        f"  {{ path: {json.dumps(p.route)}, label: {json.dumps(_label(p))} }},"
        for p in pages
    )
    return f"""// Kept by Imagi: the site's pages that are ready, in navigation order.
// Build navigation from this list instead of hard-coding links.
export interface SitePage {{
  path: string
  label: string
}}

export const sitePages: SitePage[] = [
{entries}
]
"""


def _label(page) -> str:
    label = getattr(page, 'label', None)
    if label:
        return label
    return 'Home' if page.slug == 'home' else page.title.replace(' page', '')


def router_ts(pages: Iterable) -> str:
    """The home router: every page nested under the shared SiteLayout."""
    pages = list(pages)
    imports = '\n'.join(
        f"import {view_name(p.slug) if p.slug != 'home' else 'HomeView'} from "
        f"'../views/{os.path.basename(p.view_path)}'"
        for p in pages
    )
    routes = ',\n'.join(
        f"""      {{
        path: {json.dumps(p.route)},
        name: '{p.slug}-view',
        component: {os.path.splitext(os.path.basename(p.view_path))[0]},
        meta: {{ requiresAuth: false, title: {json.dumps(_label(p))} }}
      }}"""
        for p in pages
    )
    return f"""import type {{ RouteRecordRaw }} from 'vue-router'
import SiteLayout from '../layouts/SiteLayout.vue'
{imports}

// Every page renders inside SiteLayout, which holds the shared header,
// navigation and footer.
const routes: RouteRecordRaw[] = [
  {{
    path: '/',
    component: SiteLayout,
    children: [
{routes}
    ]
  }}
]

export {{ routes }}
"""


def views_index_ts(pages: Iterable) -> str:
    return ''.join(
        f"export {{ default as {os.path.splitext(os.path.basename(p.view_path))[0]} }} "
        f"from './{os.path.basename(p.view_path)}'\n"
        for p in pages
    )


# Marks a view as Imagi's stand-in rather than a built page.
PLACEHOLDER_MARKER = 'imagi-page-placeholder'


def _template_text(text: str) -> str:
    """A page label as literal template text: HTML-escaped, and with no
    ``{{`` for Vue to read as an interpolation."""
    return html.escape(text, quote=False).replace('{', '&#123;').replace('}', '&#125;')


def placeholder_view(page) -> str:
    """What a planned page shows until its thread lands.

    The page is in the navigation from the start, so a visitor can click it
    early; this says it is still being generated. It checks its own module
    every few seconds and reloads once the real page has replaced it, so it
    turns up even where the dev server's hot reload can't reach the browser.
    """
    label = _template_text(_label(page))
    return f"""<template>
  <section class="max-w-xl mx-auto px-4 sm:px-6 lg:px-8 py-24 text-center" data-{PLACEHOLDER_MARKER}>
    <div class="mx-auto mb-6 h-10 w-10 rounded-full border-4 animate-spin" style="border-color: var(--site-border); border-top-color: var(--site-accent)" aria-hidden="true"></div>
    <h1 class="text-3xl font-bold mb-3" style="font-family: var(--site-font-heading)">{label} is still being generated</h1>
    <p class="text-lg" style="color: var(--site-muted)">This page is still being built. It will appear here on its own as soon as it's ready.</p>
    <router-link to="/" class="inline-block mt-8 text-sm font-medium underline">Back to the home page</router-link>
  </section>
</template>

<script setup lang="ts">
import {{ onBeforeUnmount, onMounted }} from 'vue'

// Reload once the real page has been written over this one.
let timer: number | undefined
onMounted(() => {{
  timer = window.setInterval(async () => {{
    try {{
      const source = await (await fetch(import.meta.url.split('?')[0], {{ cache: 'no-store' }})).text()
      if (!source.includes('{PLACEHOLDER_MARKER}')) window.location.reload()
    }} catch {{
      // Offline for a moment; try again on the next tick.
    }}
  }}, 3000)
}})
onBeforeUnmount(() => window.clearInterval(timer))
</script>
"""


def unbuilt_view(page) -> str:
    """What a planned page shows when its thread could not build it."""
    label = _template_text(_label(page))
    return f"""<template>
  <section class="max-w-xl mx-auto px-4 sm:px-6 lg:px-8 py-24 text-center">
    <h1 class="text-3xl font-bold mb-3" style="font-family: var(--site-font-heading)">{label}</h1>
    <p class="text-lg" style="color: var(--site-muted)">This page isn't built yet.</p>
  </section>
</template>

<script setup lang="ts">
</script>
"""


def _write(root: str, relative: str, content: str) -> None:
    path = os.path.join(root, relative)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def _locked_write(project_path: str, files: dict, remove: Iterable = (), message: str = '') -> None:
    """Write (and remove) scaffold files and commit them, all under the
    project's repo lock, so a page merging at the same moment never
    checkpoints a half-written file."""
    from apps.Imagi.Build.services.version_control_service import (
        VersionControlService,
        canonical_repo_lock,
    )

    with canonical_repo_lock(project_path):
        for relative in remove:
            try:
                os.remove(os.path.join(project_path, relative))
            except FileNotFoundError:
                pass
        for relative, content in files.items():
            _write(project_path, relative, content)
        result = VersionControlService().commit_changes(project_path, message)
    if not result.get('success'):
        logger.warning("Could not commit the first build's scaffold: %s", result.get('message'))


def scaffold_pages(project_path: str, pages: List, ready: List) -> bool:
    """Route every planned page and give each one a placeholder view.

    ``pages`` is the whole plan, home first; ``ready`` the pages already in
    the navigation. A page whose view is already on disk keeps it (home is
    mid-build in its own worktree, and the fixed pages ship a placeholder at
    project creation). Scaffold views the plan left out are removed, so the
    project carries no page nobody routes. Committed, so the threads about to
    fork from the project see it. Returns whether it was written.
    """
    if not project_path or not os.path.isdir(project_path):
        return False
    planned = {os.path.normpath(p.view_path) for p in pages}
    views_dir = os.path.join(project_path, HOME_APP, 'views')
    remove = [
        f'{HOME_APP}/views/{filename}'
        for filename in (os.listdir(views_dir) if os.path.isdir(views_dir) else [])
        if filename.endswith('View.vue')
        and os.path.normpath(f'{HOME_APP}/views/{filename}') not in planned
    ]
    files = {
        page.view_path: placeholder_view(page)
        for page in pages
        if not os.path.isfile(os.path.join(project_path, page.view_path))
    }
    files[ROUTER_PATH] = router_ts(pages)
    files[VIEWS_INDEX_PATH] = views_index_ts(pages)
    files[SITE_PAGES_PATH] = site_pages_ts(ready)
    _locked_write(project_path, files, remove, 'Route the pages of the first build')
    return True


def publish_ready_pages(project_path: str, ready: List) -> bool:
    """Set the site's navigation to these pages.

    The preview's dev server hot-reloads the list, so the change shows up in
    the app without anyone reloading it.
    """
    if not project_path or not os.path.isdir(project_path):
        return False
    _locked_write(
        project_path, {SITE_PAGES_PATH: site_pages_ts(ready)},
        message='Update the navigation',
    )
    return True


def settle_unbuilt_pages(project_path: str, ready: List, unbuilt: List) -> bool:
    """Take the pages the first build couldn't make out of the navigation.

    Every planned page was listed from the start; one whose thread failed
    would otherwise say "still being generated" forever. Its route stays, now
    saying plainly that it isn't built, and the founder can ask for it.
    """
    if not unbuilt or not project_path or not os.path.isdir(project_path):
        return False
    files = {SITE_PAGES_PATH: site_pages_ts(ready)}
    for page in unbuilt:
        path = os.path.join(project_path, page.view_path)
        try:
            with open(path, encoding='utf-8') as f:
                still_placeholder = PLACEHOLDER_MARKER in f.read()
        except OSError:
            still_placeholder = False
        if still_placeholder:
            files[page.view_path] = unbuilt_view(page)
    _locked_write(project_path, files, message='Mark the pages that were not built')
    return True
