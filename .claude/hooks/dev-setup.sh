#!/usr/bin/env bash
#
# Per-worktree dev environment setup, shared by the SessionStart hook and
# launch.json. Targets:
#   symlink        - point this worktree's db.sqlite3 at the main checkout's DB
#   frontend       - npm install
#   backend        - link DB + pipenv install + migrate
#   all            - everything (used by the SessionStart hook to pre-warm)
#   serve-frontend - install, then run the Vite dev server (launch.json)
#   serve-backend  - install, then run uvicorn and publish its port (launch.json)
#
# Installs are guarded by an atomic mkdir lock so the background hook run and a
# foreground preview_start run can't clobber each other's node_modules / venv.
#
# PORTS / RUNNING SEVERAL CLAUDE CODE INSTANCES AT ONCE
#
# The harness assigns each preview server a free port at launch — 5173/8000 when
# they happen to be free, an arbitrary high port when another instance already
# holds them — and passes it in as $PORT. That already gives every instance its
# own frontend, but it does not tell the frontend where *its* backend landed, so
# the Vite proxy used to send /api to whatever was on the hardcoded port 8000 —
# i.e. straight into another instance's Django.
#
# Fix: serve-backend records the port it actually bound to in
# .claude/.dev-ports.json, and vite.config.ts reads that file on every proxied
# request. The file lives inside this worktree, so each checkout has its own and
# instances never see each other's.

set -uo pipefail

# Worktree root (this file lives in <root>/.claude/hooks/).
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Canonical checkout = parent of the shared .git dir. Worktrees resolve to the
# main checkout; the main checkout resolves to itself.
GIT_COMMON="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)"
if [ -n "$GIT_COMMON" ]; then
  MAIN_ROOT="$(dirname "$GIT_COMMON")"
else
  MAIN_ROOT="$ROOT"
fi

LOCK_DIR="$ROOT/.claude/.locks"
mkdir -p "$LOCK_DIR"

# Where serve-backend publishes its port for vite.config.ts to pick up.
PORTS_FILE="$ROOT/.claude/.dev-ports.json"

log() { echo "[dev-setup] $*"; }

with_lock() { # with_lock <name> <command...>
  local name="$1"; shift
  local lock="$LOCK_DIR/$name"
  local waited=0
  until mkdir "$lock" 2>/dev/null; do
    sleep 1; waited=$((waited + 1))
    if [ "$waited" -ge 600 ]; then
      log "timed out waiting for '$name' lock; running anyway"
      break
    fi
  done
  "$@"; local rc=$?
  rmdir "$lock" 2>/dev/null || true
  return $rc
}

link_db() {
  # The main checkout owns the real file; nothing to link.
  if [ "$ROOT" = "$MAIN_ROOT" ]; then
    return 0
  fi
  local target="$MAIN_ROOT/backend/django/db.sqlite3"
  local link="$ROOT/backend/django/db.sqlite3"
  # Don't destroy a real DB someone created directly in this worktree.
  if [ -e "$link" ] && [ ! -L "$link" ]; then
    log "WARNING: $link is a real file, not a symlink — leaving it untouched."
    log "         Delete it and re-run to share the main checkout's DB instead."
    return 0
  fi
  ln -sfn "$target" "$link"
  log "db.sqlite3 -> $target"
}

install_frontend() {
  with_lock frontend bash -c "cd '$ROOT/frontend/vuejs' && npm install"
}

link_env() {
  # Share the main checkout's backend .env so secrets are available everywhere.
  if [ "$ROOT" = "$MAIN_ROOT" ]; then
    return 0
  fi
  local target="$MAIN_ROOT/backend/django/.env"
  local link="$ROOT/backend/django/.env"
  if [ ! -e "$target" ]; then
    return 0  # no shared .env to link; backend falls back to dev defaults
  fi
  if [ -e "$link" ] && [ ! -L "$link" ]; then
    log "WARNING: $link is a real file, not a symlink — leaving it untouched."
    return 0
  fi
  ln -sfn "$target" "$link"
  log ".env -> $target"
}

install_backend() {
  link_db
  link_env
  with_lock backend bash -c "cd '$ROOT/backend/django' && pipenv install && pipenv run python manage.py migrate"
}

serve_frontend() {
  install_frontend
  cd "$ROOT/frontend/vuejs"
  # PORT comes from the harness (launch.json autoPort); vite.config.ts honors it
  # and resolves the matching backend from PORTS_FILE.
  exec npm run dev
}

# Not local: the EXIT trap below can fire after this function's scope is gone.
BACKEND_PID=""

serve_backend() {
  install_backend
  local port="${PORT:-8000}"
  cd "$ROOT/backend/django"
  pipenv run uvicorn imagi.asgi:application --reload --port "$port" &
  BACKEND_PID=$!
  # Publish before waiting so a frontend that started first picks this up on its
  # next proxied request. The pid lets vite.config.ts ignore a stale file left
  # behind by a crash — without that check a dead port could later be recycled
  # by another instance and we'd be back to cross-wired backends.
  printf '{\n  "backend": { "port": %s, "pid": %s }\n}\n' "$port" "$BACKEND_PID" > "$PORTS_FILE"
  log "backend on port $port (pid $BACKEND_PID) -> .claude/.dev-ports.json"
  trap 'rm -f "$PORTS_FILE"; [ -n "${BACKEND_PID:-}" ] && kill "$BACKEND_PID" 2>/dev/null' EXIT INT TERM
  wait "$BACKEND_PID"
}

case "${1:-all}" in
  symlink)        link_db; link_env ;;
  frontend)       install_frontend ;;
  backend)        install_backend ;;
  all)            link_db; link_env; install_frontend; install_backend ;;
  serve-frontend) serve_frontend ;;
  serve-backend)  serve_backend ;;
  *)              log "unknown target: ${1:-}"; exit 1 ;;
esac
