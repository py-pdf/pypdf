#!/usr/bin/env python3
"""Smoke checks for Newbie setup."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    CONFIG_PATH,
    MANIFESTS_DIR,
    PROJECT_ROOT,
    chunks_cache_path,
    load_libraries_config,
    read_manifest,
    read_symbols_manifest,
    repo_dir_for,
    resolve_config_path,
    symbols_manifest_path,
)


def _current_git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return "local"


def run_doctor() -> dict[str, object]:
    issues: list[str] = []
    library_details: list[dict[str, object]] = []

    libraries = load_libraries_config()
    for library in libraries:
        manifest = read_manifest(library.name)
        symbols = read_symbols_manifest(library.name)
        repo_path = repo_dir_for(library)
        cache_path = chunks_cache_path(library.name)
        detail: dict[str, object] = {
            "name": library.name,
            "manifest_ok": manifest is not None,
            "symbols_ok": symbols is not None,
            "repo_ok": repo_path.exists(),
            "chunk_cache_ok": cache_path.exists(),
        }
        library_details.append(detail)

        if manifest is None:
            issues.append(
                f"{library.name}: missing manifest — run python scripts/index.py --library {library.name}"
            )
        elif manifest.get("ref") != library.ref:
            issues.append(
                f"{library.name}: config ref {library.ref!r} != manifest ref {manifest.get('ref')!r}"
            )

        if symbols is None:
            issues.append(
                f"{library.name}: missing symbols manifest — run python scripts/export_symbols.py --library {library.name}"
            )

        if not repo_path.exists():
            issues.append(
                f"{library.name}: source checkout missing at {repo_path} — run python scripts/index.py --library {library.name}"
            )

        if not cache_path.exists() and not repo_path.exists():
            issues.append(
                f"{library.name}: no search data — run python scripts/index.py --library {library.name}"
            )

    return {
        "issues": issues,
        "libraries": library_details,
        "pass": not issues,
        "commit": _current_git_commit(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke checks for Newbie setup.")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    result = run_doctor()

    if args.json_output:
        print(json.dumps(result, indent=2))
        if not result["pass"]:
            raise SystemExit(1)
        return

    issues = result["issues"]
    print(f"Project root: {PROJECT_ROOT}")
    config_path = resolve_config_path()
    print(f"Config: {config_path} ({'ok' if config_path.exists() else 'missing'})")
    print("Index backend: Cursor codebase (repos/ + store/chunks/)")

    libraries = load_libraries_config()
    print(f"Configured libraries: {', '.join(lib.name for lib in libraries) or '(none)'}")

    for library in libraries:
        manifest = read_manifest(library.name)
        symbols = read_symbols_manifest(library.name)
        repo_path = repo_dir_for(library)
        cache_path = chunks_cache_path(library.name)

        if manifest:
            backend = manifest.get("index_backend", "unknown")
            print(
                f"  - {library.name}: manifest ok — {manifest['chunk_count']} chunks "
                f"@ {manifest['ref']} ({manifest['commit'][:12]}, backend={backend})"
            )
        else:
            print(f"  - {library.name}: no manifest")

        if symbols:
            print(
                f"      symbols: {symbols.get('symbol_count', len(symbols.get('symbols', [])))} public"
            )
        else:
            print(f"      symbols: missing ({symbols_manifest_path(library.name).name})")

        print(f"      source: {'ok' if repo_path.exists() else 'missing'} ({repo_path})")
        print(f"      chunk cache: {'ok' if cache_path.exists() else 'missing'} ({cache_path.name})")

    if not MANIFESTS_DIR.exists() or not any(MANIFESTS_DIR.glob("*.json")):
        print("\nNext step: python scripts/index.py --library <name>")

    if issues:
        print("\nIssues found:")
        for issue in issues:
            print(f"  - {issue}")
        raise SystemExit(1)

    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
