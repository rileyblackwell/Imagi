# Railway deploy config

Production runs three Railway services from this one repository. Each has its
own config-as-code file here:

| File             | Service   | Builds from                | Notes                                     |
| ---------------- | --------- | -------------------------- | ----------------------------------------- |
| `frontend.json`  | frontend  | `frontend/vuejs/Dockerfile`  | nginx; routes `/api` by path to the tiers |
| `backend.json`   | backend   | `backend/django/Dockerfile`  | web tier                                  |
| `workspace.json` | workspace | `backend/django/Dockerfile`  | workspace tier (`IMAGI_ROLE=workspace`)   |

`backend.json` and `workspace.json` are intentionally identical — both watch
`backend/django/**` so one backend push redeploys both tiers. They drift apart
otherwise, and a stale tier serving old code is the cause of "my change isn't
live in prod, sometimes". Compare `/api/v1/ops/web/version/` against
`/api/v1/ops/workspace/version/` to check: same `commit` means no drift.

Those same two responses carry `missing_binaries`, which answers the other
question a healthy-looking-but-broken tier raises: whether the container has the
programs the build workspace shells out to (`git`, `node`, `npm`, `chromium`).
They come from the image, not the code, so a correct commit can still be unable
to build anything — which is what happened when `git` was absent and every
dispatched subagent died on `git worktree` with nothing visible in the UI. A
non-empty `missing_binaries` on the workspace tier means fix
`backend/django/Dockerfile`, not the deploy.

## Wiring these files to the services

Railway only picks a config file up automatically when it is `railway.json` or
`railway.toml` at the repository root. These are custom paths, so each service
names its file explicitly:

**Service → Settings → Config-as-code → Config file path**

- frontend → `railway/frontend.json`
- backend → `railway/backend.json`
- workspace → `railway/workspace.json`

That path is resolved from the repository root and deliberately does not follow
the service's Root Directory setting. The paths *inside* each file
(`dockerfilePath`, `watchPatterns`) are repo-root relative too, which is why
they are unchanged by where this directory sits.

Anything not pinned here still lives in the dashboard — notably `IMAGI_ROLE`
and the rest of each service's environment variables, which stay per-service.
