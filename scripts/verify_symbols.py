#!/usr/bin/env python3
#The star of the CI show. Parses your PR code changes and blocks the build if you import an unindexed API or a private method.
"""Verify indexed-library symbol usage in Python files (no OpenAI key required)."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_libraries_config, read_symbols_manifest  # noqa: E402


@dataclass
class LibraryUsage:
    library: str
    imported_names: set[str] = field(default_factory=set)
    module_imports: set[str] = field(default_factory=set)


def configured_library_names() -> set[str]:
    return {library.name for library in load_libraries_config()}


def git_changed_python_files(base_ref: str = "main") -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMR", f"{base_ref}...HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    paths = [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]
    return [path for path in paths if path.suffix == ".py" and path.exists()]


def collect_library_usage(tree: ast.Module, known_libraries: set[str]) -> dict[str, LibraryUsage]:
    usage: dict[str, LibraryUsage] = {}

    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in known_libraries:
                    entry = usage.setdefault(root, LibraryUsage(library=root))
                    entry.module_imports.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            if not node.module:
                continue
            root = node.module.split(".")[0]
            if root not in known_libraries:
                continue
            entry = usage.setdefault(root, LibraryUsage(library=root))
            for alias in node.names:
                if alias.name == "*":
                    entry.imported_names.add("*")
                else:
                    entry.imported_names.add(alias.asname or alias.name)

    return usage


def verify_file(path: Path, known_libraries: set[str]) -> list[str]:
    errors: list[str] = []
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return [f"{path}: syntax error — {exc}"]

    usage_by_library = collect_library_usage(tree, known_libraries)
    if not usage_by_library:
        return []

    for library_name, usage in usage_by_library.items():
        manifest = read_symbols_manifest(library_name)
        if manifest is None:
            errors.append(
                f"{path}: uses '{library_name}' but "
                f"store/manifests/{library_name}.symbols.json is missing "
                f"(run: python scripts/export_symbols.py --library {library_name})"
            )
            continue

        known_symbols = set(manifest.get("symbols", []))
        known_modules = set(manifest.get("modules", []))

        for symbol in usage.imported_names:
            if symbol == "*":
                continue
            if symbol not in known_symbols:
                errors.append(
                    f"{path}: '{symbol}' imported from '{library_name}' "
                    f"is not a public symbol in the index "
                    f"({manifest.get('ref', '?')}, {manifest.get('symbol_count', 0)} symbols)"
                )

        for module_name in usage.module_imports:
            root = module_name.split(".")[0]
            if root != library_name:
                continue
            if module_name not in known_modules and module_name != library_name:
                errors.append(
                    f"{path}: module '{module_name}' from '{library_name}' "
                    f"is not present in the indexed modules list"
                )

    return errors


def run_verification(
    files: list[Path],
    known_libraries: set[str],
) -> dict[str, object]:
    errors: list[str] = []
    checked = 0
    for path in files:
        if path.suffix != ".py":
            continue
        file_errors = verify_file(path, known_libraries)
        if file_errors:
            errors.extend(file_errors)
        checked += 1
    return {
        "checked": checked,
        "errors": errors,
        "pass": not errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify Python files only use indexed public library symbols."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Python files to check (default: changed files vs main)",
    )
    parser.add_argument(
        "--git-diff",
        action="store_true",
        help="Check Python files changed vs main (default when no files given).",
    )
    parser.add_argument(
        "--base-ref",
        default="main",
        help="Git base ref for --git-diff (default: main).",
    )
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    known_libraries = configured_library_names()
    if not known_libraries:
        payload = {"checked": 0, "errors": [], "pass": True, "message": "no libraries configured"}
        if args.json_output:
            print(json.dumps(payload, indent=2))
        else:
            print("No libraries configured in config/libraries.yaml — nothing to verify.")
        return

    if args.files:
        files = [Path(f) for f in args.files]
    else:
        files = git_changed_python_files(args.base_ref)

    if not files:
        payload = {"checked": 0, "errors": [], "pass": True, "message": "no python files"}
        if args.json_output:
            print(json.dumps(payload, indent=2))
        else:
            print("No Python files to verify.")
        return

    result = run_verification(files, known_libraries)
    if args.json_output:
        print(json.dumps(result, indent=2))
        if not result["pass"]:
            raise SystemExit(1)
        return

    errors = result["errors"]
    checked = result["checked"]
    if errors:
        print("Symbol verification failed:\n")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)

    print(f"Symbol verification passed ({checked} file{'s' if checked != 1 else ''}).")


if __name__ == "__main__":
    main()
