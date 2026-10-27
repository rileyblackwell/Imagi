# Running the preview deprivileged (preview sandbox)

The build workspace runs each project's **own** code to preview it: the
generated Django backend under `runserver`, its Vite dev server, `npm`
lifecycle scripts, and a headless Chromium rendering the result. That code is
written by the user (through the file API, or by the agent on their behalf), so
it is untrusted.

`preview_service.child_env` already keeps Imagi's secrets out of the child's
*environment*. What it cannot prevent is the child reading them another way:
while the preview children run as the **same OS user as the Imagi server**
(root, in the container), they can read `/proc/<imagi-pid>/environ` and recover
every deployment secret the server holds — the model API keys, `DATABASE_URL`,
`DJANGO_SECRET_KEY` — and reach the database and other users' working copies.
On Linux a process may read another process's `environ` only when it shares the
owning uid (or is root), so running the preview as a *different, unprivileged*
user closes that path.

## What the code does

- `settings.PREVIEW_SANDBOX_USER` names the unprivileged user. **Unset by
  default**, so nothing changes until a deployment opts in.
- When it is set *and* the Imagi process is root, every preview child
  (`runserver`, Vite, `npm install`, `migrate`, the backend check, Chromium) is
  spawned with `user=`/`group=` so it runs as that user, with a `0o002` umask.
- Project files the server writes are made group-writable (the server sets its
  umask to `0o002` at startup) and the project directories carry the setgid bit
  (`sandbox.prepare_tree`), so the group is inherited and the deprivileged
  preview — sharing that group — can read and overwrite what the server wrote,
  and vice-versa.
- The `imagipreview` user and group are created in `backend/django/Dockerfile`.

When `PREVIEW_SANDBOX_USER` is unset, or the process is not root (local dev,
tests), every hook is inert and spawning behaves exactly as before.

## Enabling it in production (workspace tier)

1. Deploy an image that contains the `imagipreview` user (this change).
2. Set `PREVIEW_SANDBOX_USER=imagipreview` on the **workspace** tier (the tier
   that owns `PROJECTS_ROOT` and runs previews). Leave it off the web tier.
3. Fix the files already on the volume once, as root on the workspace tier:

   ```
   python manage.py prepare_preview_sandbox        # add --dry-run to preview
   ```

   New files created after step 2 are already group-writable; this fixes the
   ones created before it.
4. Smoke-test: open a project, confirm the preview boots (Vite + Django up,
   browser renders), create a file, run a backend check. Check the logs for
   `Permission denied`.

Kill switch: unset `PREVIEW_SANDBOX_USER` and redeploy; previews go back to
running as the server's user.

## Limits / next steps

All previews share one `imagipreview` user, so this isolates the preview from
the **Imagi server** but not one project's preview from another's files on the
volume. Per-project users (or a stronger sandbox — namespaces/seccomp) and
limiting the preview's outbound network are the next steps, tracked separately.
