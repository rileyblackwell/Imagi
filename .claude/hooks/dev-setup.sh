#!/usr/bin/env bash
#
# Per-worktree dev environment setup, shared by the SessionStart hook and
# launch.json. Targets:
#   symlink   - point this worktree's db.sqlite3 at the main checkout's DB
#   frontend  - npm install
#   backend   - link DB + pipenv install + migrate
#   all       - everything (used by the SessionStart hook to pre-warm)
#
# Installs are guarded by an atomic mkdir lock so the background hook run and a
# foreground preview_start run can't clobber each other's node_modules / venv.

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

case "${1:-all}" in
  symlink)  link_db; link_env ;;
  frontend) install_frontend ;;
  backend)  install_backend ;;
  all)      link_db; link_env; install_frontend; install_backend ;;
  *)        log "unknown target: ${1:-}"; exit 1 ;;
esac
