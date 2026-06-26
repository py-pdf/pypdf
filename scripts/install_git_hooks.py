#!/usr/bin/env python3
"""Install Newbie git hooks so metrics sync on every push (fail-open)."""

from __future__ import annotations

import argparse
import os
import stat
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import PROJECT_ROOT, REPORTS_DIR  # noqa: E402

GITHOOKS_DIR = PROJECT_ROOT / ".githooks"
PRE_PUSH_HOOK = GITHOOKS_DIR / "pre-push"
USERS_README = REPORTS_DIR / "users" / "README.md"

# Managed hook body — kept in sync with .githooks/pre-push in the plugin bundle.
_PRE_PUSH_BODY = """#!/usr/bin/env bash
# Newbie pre-push — refresh and commit your metrics snapshot before your push.
#
# Runs on every ``git push``. Updates reports/users/<user_id>.json from local
# hook events, commits it if changed, then lets your push continue (metrics ride
# along with your code). Never blocks the push if metrics fail.
set +e

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$ROOT" || exit 0

PY="python3"
if [ -x "$ROOT/.venv/bin/python" ]; then
  PY="$ROOT/.venv/bin/python"
fi

if [ -f "$ROOT/scripts/sync_metrics.py" ]; then
  "$PY" "$ROOT/scripts/sync_metrics.py" --write --commit
  exit 0
fi

NB_CLI="${NB_CLI:-}"
if [ -z "$NB_CLI" ] && [ -f "${HOME}/.cursor/plugins/local/newbie/scripts/nb_cli.py" ]; then
  NB_CLI="${HOME}/.cursor/plugins/local/newbie/scripts/nb_cli.py"
fi
if [ -z "$NB_CLI" ]; then
  NB_CLI="$(find "${HOME}/.cursor/plugins/local" -path '*/newbie/scripts/nb_cli.py' 2>/dev/null | head -1)"
fi
if [ -n "$NB_CLI" ] && [ -f "$NB_CLI" ]; then
  "$PY" "$NB_CLI" sync-metrics --write --commit
fi

exit 0
"""

_USERS_README = """# Per-user metrics files

Each engineer who uses Newbie in Cursor gets **one file** in this directory:

```text
reports/users/<user_id>.json
```

`user_id` is a 12-character hash of `git config user.email` — no raw email is committed.

## Automatic sync

After `nb init`, a **pre-push git hook** refreshes your file and commits it whenever
you `git push` — no manual step required. Cursor project hooks must be enabled so
local usage is recorded.

Manual override:

```bash
python scripts/sync_metrics.py --show-id
python scripts/sync_metrics.py --write --push
```

## Manager aliases (optional)

Map hashed IDs to readable names in `config/metrics.yaml`:

```yaml
user_aliases:
  a1b2c3d4e5f6: "Alice"
```

## Privacy

- Raw hook events stay in `.newbie/metrics/events.jsonl` (gitignored)
- Only aggregated snapshots are committed here
- Each engineer commits **only their own file**
"""


def _is_git_repo(root: Path) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--git-dir"],
        cwd=root,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def _ensure_pre_push_hook() -> None:
    GITHOOKS_DIR.mkdir(parents=True, exist_ok=True)
    PRE_PUSH_HOOK.write_text(_PRE_PUSH_BODY, encoding="utf-8")
    PRE_PUSH_HOOK.chmod(PRE_PUSH_HOOK.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"  wrote {PRE_PUSH_HOOK.relative_to(PROJECT_ROOT)}")


def _ensure_users_readme() -> None:
    USERS_README.parent.mkdir(parents=True, exist_ok=True)
    if not USERS_README.is_file():
        USERS_README.write_text(_USERS_README, encoding="utf-8")
        print(f"  wrote {USERS_README.relative_to(PROJECT_ROOT)}")


def _configure_hooks_path(*, dry_run: bool) -> None:
    if not _is_git_repo(PROJECT_ROOT):
        print("  skip git hooksPath (not a git repository)")
        return

    rel_hooks = ".githooks"
    if dry_run:
        print(f"  would run: git config core.hooksPath {rel_hooks}")
        return

    result = subprocess.run(
        ["git", "config", "core.hooksPath", rel_hooks],
        cwd=PROJECT_ROOT,
        check=False,
    )
    if result.returncode == 0:
        print(f"  set git config core.hooksPath={rel_hooks}")
    else:
        print("  warning: could not set core.hooksPath — run manually:")
        print(f"    git config core.hooksPath {rel_hooks}")


def install(*, dry_run: bool = False) -> None:
    print(f"Installing Newbie git hooks at {PROJECT_ROOT}")
    if dry_run:
        print("  (dry run)")
        return

    _ensure_pre_push_hook()
    _ensure_users_readme()
    _configure_hooks_path(dry_run=dry_run)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install pre-push hook to sync Newbie metrics on every git push."
    )
    parser.add_argument("--dry-run", action="store_true", help="Print actions only")
    args = parser.parse_args()
    os.environ.setdefault("NB_PROJECT_ROOT", str(PROJECT_ROOT))
    install(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
