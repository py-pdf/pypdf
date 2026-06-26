#!/usr/bin/env python3
"""Clone or update a configured library repository."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from git import Repo

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    REPOS_DIR,
    get_library_config,
    load_libraries_config,
    repo_dir_for,
)


def checkout_ref(repo: Repo, ref: str) -> str:
    repo.git.fetch("--tags", "--force")
    candidates = [ref]
    if not ref.startswith("v"):
        candidates.append(f"v{ref}")
    else:
        candidates.append(ref.lstrip("v"))

    last_error: Exception | None = None
    for candidate in candidates:
        try:
            repo.git.checkout(candidate)
            return repo.head.commit.hexsha
        except Exception as exc:  # noqa: BLE001 - surface all checkout failures
            last_error = exc
            continue

    raise SystemExit(f"Could not checkout ref '{ref}': {last_error}")


def crawl_library(name: str) -> str:
    library = get_library_config(name)
    REPOS_DIR.mkdir(parents=True, exist_ok=True)
    target = repo_dir_for(library)

    if target.exists():
        repo = Repo(target)
        commit = checkout_ref(repo, library.ref)
        action = "Updated"
    else:
        repo = Repo.clone_from(library.repo, target)
        commit = checkout_ref(repo, library.ref)
        action = "Cloned"

    print(f"{action} {library.name} @ {library.ref} ({commit[:12]}) -> {target}")
    return commit


def main() -> None:
    parser = argparse.ArgumentParser(description="Clone or update library source.")
    parser.add_argument(
        "--library",
        required=True,
        help="Library name from config/libraries.yaml",
    )
    args = parser.parse_args()
    crawl_library(args.library)


if __name__ == "__main__":
    main()
