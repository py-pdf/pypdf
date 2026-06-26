#!/usr/bin/env python3
"""Reset Newbie workspace for a new customer project.

Removes demo-library config, manifests, and conventions so each customer repo
indexes only its own libraries. Does not touch shared skills, rules, or scripts.

Run from the project root after copying or cloning the template:

    python scripts/init_customer.py --yes
    python scripts/add_library.py --name <name> --repo <url> --ref <tag>
    python scripts/index.py --library <name>
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    CHUNKS_DIR,
    CONFIG_DIR,
    CONFIG_PATH,
    CONVENTIONS_DIR,
    MANIFESTS_DIR,
    PROJECT_ROOT,
    REPOS_DIR,
    delete_chunks_cache,
)

LIBRARIES_EXAMPLE = CONFIG_DIR / "libraries.yaml.example"


def load_config_raw() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def paths_for_library(name: str) -> list[Path]:
    return [
        CONVENTIONS_DIR / f"{name}.md",
        MANIFESTS_DIR / f"{name}.json",
        MANIFESTS_DIR / f"{name}.symbols.json",
        CHUNKS_DIR / f"{name}.jsonl",
        REPOS_DIR / name,
    ]


def delete_library_artifacts(library_name: str, dry_run: bool) -> bool:
    deleted = False
    if delete_chunks_cache(library_name):
        target = CHUNKS_DIR / f"{library_name}.jsonl"
        if dry_run:
            print(f"  would delete chunk cache: {target.relative_to(PROJECT_ROOT)}")
        else:
            print(f"  deleted chunk cache: {target.relative_to(PROJECT_ROOT)}")
        deleted = True
    return deleted


def reset_libraries_yaml(keep_names: set[str], dry_run: bool) -> None:
    config = load_config_raw()
    libraries = config.get("libraries") or []
    kept = [entry for entry in libraries if entry.get("name") in keep_names]
    new_config = {"libraries": kept}

    if dry_run:
        print(f"  would write {CONFIG_PATH} with {len(kept)} librar{'y' if len(kept) == 1 else 'ies'}")
        return

    CONFIG_PATH.write_text(
        yaml.safe_dump(new_config, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    print(f"  updated {CONFIG_PATH} ({len(kept)} librar{'y' if len(kept) == 1 else 'ies'})")


def bootstrap_empty_config(dry_run: bool) -> None:
    if LIBRARIES_EXAMPLE.exists():
        payload = {"libraries": []}
        if dry_run:
            print(f"  would reset {CONFIG_PATH} to empty libraries list")
            return
        CONFIG_PATH.write_text(
            yaml.safe_dump(payload, sort_keys=False, default_flow_style=False),
            encoding="utf-8",
        )
        print(f"  reset {CONFIG_PATH} to empty libraries list")
        print(f"  (see {LIBRARIES_EXAMPLE.name} for a commented starter)")
    else:
        reset_libraries_yaml(set(), dry_run)


def remove_path(path: Path, dry_run: bool) -> None:
    label = "would remove" if dry_run else "removed"
    if not path.exists():
        return
    if dry_run:
        print(f"  {label}: {path.relative_to(PROJECT_ROOT)}")
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()
    print(f"  {label}: {path.relative_to(PROJECT_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove demo library artifacts and prepare a customer-only Newbie repo."
    )
    parser.add_argument(
        "--demo-library",
        action="append",
        default=[],
        help="Demo library name to remove (default: pypdf). Repeatable.",
    )
    parser.add_argument(
        "--keep-library",
        default=[],
        help="Library name to keep in config/libraries.yaml (repeatable).",
        action="append",
    )
    parser.add_argument(
        "--purge-local",
        action="store_true",
        help="Delete chunk cache and repo checkouts for removed libraries.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned changes without writing or deleting.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Required to perform destructive changes.",
    )
    args = parser.parse_args()

    demo_libraries = args.demo_library or ["pypdf"]
    keep_names = set(args.keep_library)

    if not args.dry_run and not args.yes:
        raise SystemExit(
            "Refusing to change files without --yes. "
            "Run with --dry-run first to preview, then --yes to apply."
        )

    mode = "Dry run" if args.dry_run else "Applying"
    print(f"{mode} — project root: {PROJECT_ROOT}\n")

    for name in demo_libraries:
        if name in keep_names:
            print(f"Skipping {name} (--keep-library)")
            continue
        print(f"Removing demo library: {name}")
        for path in paths_for_library(name):
            remove_path(path, dry_run=args.dry_run)
        if args.purge_local:
            delete_library_artifacts(name, dry_run=args.dry_run)

    if keep_names:
        reset_libraries_yaml(keep_names, dry_run=args.dry_run)
    else:
        bootstrap_empty_config(dry_run=args.dry_run)

    print("\nNext steps:")
    print("  1. python scripts/add_library.py --name <name> --repo <url> --ref <tag>")
    print("  2. python scripts/index.py --library <name>")
    print("  3. python scripts/doctor.py")
    print("  4. Commit store/manifests/<name>.json and <name>.symbols.json")
    print("\nSee docs/customer-onboarding.md for the full checklist.")


if __name__ == "__main__":
    main()
