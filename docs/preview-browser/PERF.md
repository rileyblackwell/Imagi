# Performance

## Start-up

Measured locally (cloud container, project "Live Demo", cold: no servers
running, dependencies already linked):

| Stage | Time |
| --- | --- |
| Migrate (first run) | 767 ms |
| Django ready | 808 ms |
| Vite ready | 649 ms |
| **Servers up** | **~1.8 s** |
| First paint in the iframe (bridge ready) | ~2.5 s from opening the workspace |

Django and Vite start in parallel; migrate is skipped on later starts while
the migration files are unchanged. A warm open (servers already running)
returns from the start call immediately and the iframe paints as fast as Vite
serves the page. The start veil shows each stage with its time, so a slow
start says where it is slow.

The screenshot preview's cold start in production was 11 to 16 s (PRs #241,
#243), most of it Chromium; the live preview has no Chromium on that path.

## Edits

Agent edits reach the app through Vite HMR: the changed module swaps in
without a reload and the page keeps its state. The toolbar notes "Updated
AboutView.vue". Python edits restart Django; the edge holds API requests
for up to 8 s meanwhile instead of failing them.

## Memory and cost

Measured on the demo project (process tree RSS); larger apps grow mostly in Vite.

| Item | Measured |
| --- | --- |
| Django runserver (with autoreloader) | 102 MB |
| Vite dev server | 180 MB (heap capped at 768 MB) |
| Edge | 66 MB, one per host |
| Headless Chromium | none for viewing; only while the agent uses its preview tool, 120 s idle limit |

Budget: `PREVIEW_MEMORY_BUDGET_MB` (2 GB) across all sessions, measured from
the process trees' RSS. Idle sessions stop after 10 minutes (5 if prewarmed
and never opened); only the most recently opened project is prewarmed.

Railway bills about $10 per GB-month of memory. One user previewing for a few
hours a day keeps well under 1 GB-month; the 2 GB ceiling held for a whole
month would be about $20, the brief's cap, and only if previews ran
continuously at the budget. Set a usage alert at $15 in Railway (Project
Settings → Usage) to catch anything unexpected.
