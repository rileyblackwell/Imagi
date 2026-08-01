#!/usr/bin/env bash
# Prepare everything needed to sign in to the Imagi dev app and open a project's
# build workspace.
#
# Read-only: fetches the dev token and lists the account's projects. It does not
# modify the database or touch the browser.
#
# Usage (from anywhere in the worktree):
#   bash .claude/skills/dev-preview/scripts/dev-session.sh [BACKEND_PORT] [FRONTEND_PORT]
#
# Ports default to 8000/5173 only as a convenience. Both launch.json entries use
# autoPort, so pass the ports preview_start actually reported — against the wrong
# port this fails with a confusing "no response from backend" rather than
# anything that points at the port.

set -uo pipefail

BE_PORT="${1:-8000}"
FE_PORT="${2:-5173}"

# Resolve the worktree root from this script's own location so the caller's
# working directory doesn't matter.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

if [[ ! -f "$ROOT/.claude/hooks/dev-setup.sh" ]]; then
  echo "error: could not locate .claude/hooks/dev-setup.sh from $ROOT" >&2
  exit 1
fi

TOKEN_JSON="$(cd "$ROOT" && bash .claude/hooks/dev-setup.sh dev-token)" || {
  echo "error: dev-token failed. Is the backend reachable and the DB linked?" >&2
  exit 1
}

TOKEN="$(printf '%s' "$TOKEN_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')" || {
  echo "error: could not parse token out of: $TOKEN_JSON" >&2
  exit 1
}
USER_JSON="$(printf '%s' "$TOKEN_JSON" | python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin)["user"]))')"

PROJECTS="$(curl -s -H "Authorization: Token $TOKEN" \
  "http://localhost:$BE_PORT/api/v1/project-manager/projects/")"

if [[ -z "$PROJECTS" ]]; then
  echo "error: no response from backend on port $BE_PORT." >&2
  echo "       Start it with preview_start {name: 'backend-django'} and pass its real port." >&2
  exit 1
fi

export FE_PORT PROJECTS TOKEN USER_JSON

python3 <<'PY'
import json, os, re, sys

fe = os.environ["FE_PORT"]
token = os.environ["TOKEN"]
user_json = os.environ["USER_JSON"]

try:
    data = json.loads(os.environ["PROJECTS"])
except json.JSONDecodeError:
    sys.exit("error: backend did not return JSON. Check that it is running and the token is valid.")

if isinstance(data, dict) and "detail" in data:
    sys.exit(f"error: backend rejected the request: {data['detail']}")

projects = data.get("results", data) if isinstance(data, dict) else data


def to_slug(name):
    """Mirror of frontend/vuejs/src/apps/imagi/build/utils/slug.ts."""
    s = name.lower().strip()
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"[^a-z0-9-]", "", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


print("STEP 1 — paste into the preview browser while it is on the frontend origin")
print("         (navigate to http://localhost:%s FIRST; localStorage is per-origin):" % fe)
print()
print("localStorage.setItem('token', JSON.stringify({ value: %s, expires: Date.now() + 864e5 }));"
      % json.dumps(token))
print("localStorage.setItem('user', JSON.stringify(%s));" % user_json)
print()

if not projects:
    print("No projects on this account yet — create one at http://localhost:%s/imagi/projects" % fe)
    sys.exit(0)

print("STEP 2 — then navigate to the build workspace:")
print()
seen = {}
for p in projects:
    slug = to_slug(p["name"])
    seen.setdefault(slug, []).append(p)
    print("  %s  (id %s)" % (p["name"], p["id"]))
    print("    workspace  http://localhost:%s/imagi/workspace/%s" % (fe, slug))
    print("    hub        http://localhost:%s/imagi/project/%s" % (fe, slug))
print()

collisions = {s: ps for s, ps in seen.items() if len(ps) > 1}
if collisions:
    print("WARNING — slug collision. Different names can slugify to the same slug,")
    print("and the app resolves it with .find(), i.e. the first match in fetch order.")
    print("These URLs are ambiguous and may silently open a project you didn't mean:")
    for slug, ps in collisions.items():
        names = ", ".join("%s (id %s)" % (p["name"], p["id"]) for p in ps)
        print("  %s  <-  %s" % (slug, names))
    print()
    print("  Which one wins is not predictable from this list: the store matches")
    print("  against whatever project list it holds, which may be a cached one in a")
    print("  different order. Don't guess — after the page loads, read the numeric id")
    print("  off the API calls (read_network_requests, pattern 'projects/') and check")
    print("  it against the ids above.")
    print()
print("Verify with location.href afterward — navigate reports the origin, not the")
print("path the router settled on.")
PY
