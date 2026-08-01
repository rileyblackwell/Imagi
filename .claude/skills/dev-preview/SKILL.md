---
name: dev-preview
description: Sign in to the Imagi dev app without typing a password and open a project's build workspace in the preview browser. Use this whenever you need to see the running Imagi app — "navigate to the build workspace", "open the workspace", "log in to the dev app", "check this in the browser", "screenshot the project hub", or any time you're verifying a frontend change against the real app. Also use it when a `/imagi/...` URL bounces you back to the projects list, since that is almost always the project-slug gotcha documented here.
---

# Signing in and opening the build workspace

The goal is almost always the same: get signed in, then land on
`/imagi/workspace/<project-slug>`. Four things have to be true — servers up, a
token, that token seeded into `localStorage` on the frontend origin, and a
**slugified** project name in the URL.

The failure mode that costs the most time is that a bad slug and a bad token
look identical: both end in a silent `router.replace` to `/imagi/projects`. So
the steps below front-load the things that make the difference visible.

## 1. Start both servers

```
preview_start { name: "backend-django" }
preview_start { name: "frontend-vite" }
```

Never `npm run dev` or `manage.py runserver` in a shell — the harness owns these
processes. Both entries set `autoPort`, so read the real port out of each result
rather than assuming 8000/5173. This doc writes `$BE` and `$FE` for those two.
The backend must be up before the next step.

Each `preview_start` returns a `tabId` and makes that tab active, so starting the
backend can move you off the tab you were using. Since the next steps write to
`localStorage` and then read `location.href`, they all have to happen on the same
tab. Call `tabs_context` to see what's open and pass `tabId` explicitly rather
than relying on which tab happens to be fronted.

## 2. Get the token and the workspace URL in one shot

```bash
bash .claude/skills/dev-preview/scripts/dev-session.sh $BE $FE
```

It prints the two `localStorage.setItem` lines to paste, then every project on
the account with its ready-made workspace URL already slugified, and warns you
about slug collisions. It's read-only — it fetches the dev token and lists
projects, and touches neither the database nor the browser.

Run it from the worktree root — the Bash tool keeps its working directory
between calls, so after an earlier `cd frontend/vuejs` this fails with `No such
file or directory`; `cd` back in the same command.

Underneath it calls `bash .claude/hooks/dev-setup.sh dev-token`, which reads the
dev account without modifying it and recreates it from
`~/.config/imagi/test-credentials.env` if the DB was reset, then lists projects
from `/api/v1/project-manager/projects/`. Reach for those directly only if you
need something the script doesn't print.

That endpoint is worth remembering, because guessing it wastes a round trip: the
frontend module is `apps/imagi/build`, but there is no `/api/v1/build/` — the
projects API is under `project-manager` for both halves of the app.

A successful run is also your liveness and auth check. If it prints a token and
a project list, the backend is up and the token is good — which means a later
bounce to `/imagi/projects` is a slug problem, not an auth one.

Don't drive the sign-in form. It's slower, it can trip rate limiting, and typing
a real password into a form is worth avoiding regardless.

## 3. Seed storage on the frontend origin, then navigate

`localStorage` is per-origin, so you have to be *on* the frontend origin before
writing to it. `shared/stores/auth.ts` reads both keys when the store
initializes, so a page loaded before both keys exist comes up signed out.

```
navigate { url: "http://localhost:$FE" }      # origin first
javascript_tool: <the two setItem lines from step 2>
navigate { url: "http://localhost:$FE/imagi/workspace/<slug>" }
```

## 4. Confirm you landed

`navigate` reports the origin it opened, not the path the SPA settled on — its
success message reads the same whether or not the router bounced you. Ask the
page:

```
javascript_tool: location.href
```

`location.href` is the only thing that tells you the truth here. `get_page_text`
prints a `URL:` line in its own header that shows the origin too, so it will
happily report `http://localhost:$FE` on a page that bounced — don't read the
destination off it.

Where you landed names the failure:

- `/imagi/projects` + console `Project not found for slug: <x>` → the slug is
  wrong, or that project isn't on this account. See below.
- `/imagi/project/<slug>` (the hub) + a toast about still building → not a
  failure. `Workspace.vue` redirects here while `generation_status` is
  `generating` and opens the workspace once the initial build finishes.
- `/auth/signin`, or a 401 in the network log → the token is missing, stale, or
  was written on the wrong origin or tab. Redo step 3.

Then confirm the view actually rendered. Reach for `get_page_text` or
`read_page` for content: a screenshot can come back solid black on a page that
rendered fine — the app is dark-themed and a capture can catch it mid-paint or
land on an empty stretch of a scrolled view. If you need the screenshot itself,
wait a couple of seconds and retake it rather than concluding the page is
broken.

Two things about the console that will otherwise mislead you: it keeps messages
from earlier navigations, so a `Project not found for slug` you're staring at
may be from the attempt before last, and Vue logs each message twice in dev.
Check that an error belongs to the load you just did before acting on it.

## The slug rule

Every `:projectName` route param is a slug derived from the display name — never
the display name itself. `/imagi/workspace/Agent%20Manager%20Test` doesn't 404
and doesn't throw; it logs, toasts, and redirects to `/imagi/projects`.

From [`toSlug`](../../../frontend/vuejs/src/apps/imagi/build/utils/slug.ts):
lowercase, trim, spaces and underscores to hyphens, drop anything outside
`[a-z0-9-]`, collapse repeated hyphens, strip leading/trailing hyphens.

| Project name | Slug |
| --- | --- |
| `Agent Manager Test` | `agent-manager-test` |
| `My Cool App` | `my-cool-app` |
| `Hello, World! @2024` | `hello-world-2024` |
| `  --Edge--  ` | `edge` |

Resolution happens client-side in `projectStore.getProjectBySlug`, matching
against the project list the store holds — so a project the account can't see
fails exactly like a misspelled slug.

### Slugs are not unique

`toSlug` is lossy, so distinct projects can collide — `Agent Manager Test` and
`Agent-Manager Test` both give `agent-manager-test`. `getProjectBySlug` uses
`.find()`, so one of them silently wins and you get a workspace that looks right
but belongs to the other project.

Which one wins isn't predictable from the API listing; the store may match
against a cached list in a different order. Don't reason about it — read the
numeric id off the network calls, which carry it in the path:

```
read_network_requests { urlPattern: "projects/" }
   → GET /api/v1/project-manager/projects/31/status/     ← project id 31
```

The helper script flags collisions and prints each project's id so you have
something to check that against. This matters more than it sounds: the dev DB is
symlinked across worktrees, so projects other sessions create show up here.

## Routes

`:projectName` is the slug in all of these. The build half lives at
`/imagi/workspace/...` (`apps/imagi/build`); everything under `/imagi/project/...`
is the run half, owned by `project-manager` and the tool modules.

| Page | Path |
| --- | --- |
| Build workspace | `/imagi/workspace/:projectName` |
| Project library | `/imagi/projects` |
| Project hub | `/imagi/project/:projectName` |
| Marketing | `/imagi/project/:projectName/marketing` |
| Sell | `/imagi/project/:projectName/sales` |
| Operate | `/imagi/project/:projectName/operations` |

## Reusing a session

Servers and `localStorage` both survive navigation, so once you're in, later
pages are one `navigate` plus a `location.href` check. Re-seed only if the token
expired (24h here), the DB was reset, or you cleared storage. If the frontend
restarted but the tab didn't, reload before trusting what's on screen.
