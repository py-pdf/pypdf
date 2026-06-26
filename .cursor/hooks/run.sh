#!/usr/bin/env bash
# Newbie hook launcher — runs a hook script under the repo virtualenv when present.
#
# Cursor invokes hooks with cwd = workspace root. In a Cloud Agent the system
# python3 may lack Newbie's deps (pyyaml, gitpython, ...), so prefer .venv built
# by .cursor/environment.json. Falls back to python3 if there is no venv.
# Fails open: a hook must never block the agent, so we always exit 0 on launch
# errors and let the hook script itself handle its own try/except.
set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="python3"
if [ -x "$REPO_ROOT/.venv/bin/python" ]; then
  PY="$REPO_ROOT/.venv/bin/python"
fi

exec "$PY" "$@"
