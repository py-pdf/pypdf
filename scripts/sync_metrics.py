#!/usr/bin/env python3
"""Sync local Newbie metrics to a per-user file in reports/users/."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import PROJECT_ROOT  # noqa: E402
from metrics.config import load_metrics_config  # noqa: E402
from metrics.identity import current_user_id, git_user_email  # noqa: E402
from metrics.user_snapshot import build_user_snapshot, user_snapshot_path, write_user_snapshot  # noqa: E402


def _git_commit_user_file(user_id: str) -> bool:
    """Stage and commit only this user's metrics file (no push).

    Used by the pre-push git hook so the engineer's ``git push`` carries their
    metrics snapshot alongside their code in a single push. Fails open.
    """
    snapshot_path = user_snapshot_path(user_id)
    try:
        rel_path = snapshot_path.relative_to(PROJECT_ROOT)
    except ValueError:
        rel_path = snapshot_path

    add = subprocess.run(
        ["git", "add", str(rel_path)], cwd=PROJECT_ROOT, check=False
    )
    if add.returncode != 0:
        return False

    status = subprocess.run(
        ["git", "diff", "--staged", "--quiet"],
        cwd=PROJECT_ROOT,
        check=False,
    )
    if status.returncode == 0:
        return False

    commit = subprocess.run(
        ["git", "commit", "-m", f"chore(metrics): sync stats for {user_id}", "--no-verify"],
        cwd=PROJECT_ROOT,
        check=False,
    )
    if commit.returncode != 0:
        print("Metrics commit skipped — commit your user metrics file manually.")
        return False
    print(f"Committed {rel_path} (will push with your branch)")
    return True


def _git_push_user_file(user_id: str) -> bool:
    """Commit and push only this user's metrics file.

    Fails open: in a Cloud Agent or CI the push can fail (detached HEAD, no
    upstream, protected branch) and that must never abort the run. Returns True
    on a successful push, False otherwise, and prints a hint instead of raising.
    """
    snapshot_path = user_snapshot_path(user_id)
    try:
        rel_path = snapshot_path.relative_to(PROJECT_ROOT)
    except ValueError:
        rel_path = snapshot_path

    add = subprocess.run(
        ["git", "add", str(rel_path)], cwd=PROJECT_ROOT, check=False
    )
    if add.returncode != 0:
        print(f"Skipped push: git add failed for {rel_path} (not a git repo?).")
        return False

    status = subprocess.run(
        ["git", "diff", "--staged", "--quiet"],
        cwd=PROJECT_ROOT,
        check=False,
    )
    if status.returncode == 0:
        print("No changes to commit for your user metrics file.")
        return False

    commit = subprocess.run(
        ["git", "commit", "-m", f"chore(metrics): sync stats for {user_id}"],
        cwd=PROJECT_ROOT,
        check=False,
    )
    if commit.returncode != 0:
        print("git commit failed — commit your user metrics file manually.")
        return False

    push = subprocess.run(["git", "push"], cwd=PROJECT_ROOT, check=False)
    if push.returncode != 0:
        print(
            "git push failed — the metrics file is committed locally. "
            "Run `git push` manually (or let CI push) after resolving remote issues."
        )
        return False
    print(f"Pushed {rel_path}")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync local Newbie hook metrics to reports/users/<user_id>.json"
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write reports/users/<user_id>.json from local hook events",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Git commit and push only your user metrics file (requires --write)",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Git commit only your user metrics file (requires --write; used by pre-push hook)",
    )
    parser.add_argument(
        "--show-id",
        action="store_true",
        help="Print hashed user_id for git user.email (for metrics.yaml aliases)",
    )
    args = parser.parse_args()

    if args.show_id:
        uid = current_user_id()
        print(f"git user.email: {git_user_email()}")
        print(f"user_id: {uid}")
        return

    if not args.write:
        parser.print_help()
        raise SystemExit(0)

    config = load_metrics_config()
    snapshot = build_user_snapshot(config)
    path = write_user_snapshot(snapshot)
    print(f"Wrote {path.relative_to(PROJECT_ROOT)}")

    if args.push:
        _git_push_user_file(snapshot["user_id"])
    elif args.commit:
        _git_commit_user_file(snapshot["user_id"])


if __name__ == "__main__":
    main()
