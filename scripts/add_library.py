#!/usr/bin/env python3
#scale up (onboard a new repo)
"""Scaffold a new library entry and conventions file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from chunk.languages import IMPLEMENTED_LANGUAGES  # noqa: E402
from common import CONFIG_PATH, CONVENTIONS_DIR  # noqa: E402


def _resolve_template() -> Path:
    """Conventions template ships with the plugin bundle; fall back to it when the
    customer's .newbie/conventions/ doesn't have a local copy."""
    local = CONVENTIONS_DIR / "_template.md"
    if local.is_file():
        return local
    # runtime layout: <plugin>/scripts/runtime/add_library.py → <plugin>/bundle/...
    bundled = (
        Path(__file__).resolve().parents[2]
        / "bundle"
        / "config"
        / "conventions"
        / "_template.md"
    )
    if bundled.is_file():
        return bundled
    return local


TEMPLATE_PATH = _resolve_template()

LANGUAGE_INCLUDES: dict[str, list[str]] = {
    "python": ["{name}/*.py", "{name}/**/*.py"],
    "typescript": ["{name}/*.ts", "{name}/**/*.ts", "{name}/**/*.tsx"],
    "javascript": ["{name}/*.js", "{name}/**/*.js", "{name}/**/*.jsx"],
    "go": ["**/*.go"],
    "rust": ["src/**/*.rs", "**/*.rs"],
}


def load_config_raw() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def default_includes(language: str, name: str) -> list[str]:
    patterns = LANGUAGE_INCLUDES.get(language, LANGUAGE_INCLUDES["python"])
    return [pattern.format(name=name) for pattern in patterns]


def main() -> None:
    implemented = ", ".join(sorted(IMPLEMENTED_LANGUAGES))
    parser = argparse.ArgumentParser(description="Add a library to config/libraries.yaml.")
    parser.add_argument("--name", required=True, help="Library name (PyPI / import root).")
    parser.add_argument("--repo", required=True, help="Git repository URL.")
    parser.add_argument("--ref", required=True, help="Pinned tag or commit SHA.")
    parser.add_argument(
        "--language",
        default="python",
        choices=sorted(LANGUAGE_INCLUDES),
        help=f"Source language (default: python). Indexing implemented for: {implemented}.",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        help="Include glob (repeatable). Default depends on --language.",
    )
    args = parser.parse_args()

    includes = args.include or default_includes(args.language, args.name)

    exclude = ["**/tests/**", "**/__pycache__/**"]
    if args.language in {"typescript", "javascript"}:
        exclude.extend(["**/node_modules/**", "**/dist/**"])
    if args.language == "rust":
        exclude.extend(["**/target/**"])

    entry = {
        "name": args.name,
        "repo": args.repo,
        "ref": args.ref,
        "language": args.language,
        "include": includes,
        "exclude": exclude,
    }

    config = load_config_raw()
    libraries = config.setdefault("libraries", [])
    if any(lib.get("name") == args.name for lib in libraries):
        raise SystemExit(f"Library '{args.name}' already exists in {CONFIG_PATH}")

    libraries.append(entry)
    CONFIG_PATH.write_text(
        yaml.safe_dump(config, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    print(f"Added '{args.name}' to {CONFIG_PATH}")

    if args.language not in IMPLEMENTED_LANGUAGES:
        print(
            f"\nNote: indexing for '{args.language}' is not implemented yet "
            f"(implemented: {implemented})."
        )

    conventions_path = CONVENTIONS_DIR / f"{args.name}.md"
    if conventions_path.exists():
        print(f"Conventions file already exists: {conventions_path}")
    elif TEMPLATE_PATH.exists():
        text = TEMPLATE_PATH.read_text(encoding="utf-8").replace("<library>", args.name)
        conventions_path.parent.mkdir(parents=True, exist_ok=True)
        conventions_path.write_text(text, encoding="utf-8")
        print(f"Created {conventions_path}")
    else:
        print(f"Template missing at {TEMPLATE_PATH}; skip conventions scaffold.")

    print(
        f"\nNext steps:\n"
        f"  python scripts/index.py --library {args.name}\n"
        f"  python scripts/query.py --library {args.name} --prompt \"public API entry points\"\n"
        f"  Edit {conventions_path} with retrieved import style and deprecations"
    )


if __name__ == "__main__":
    main()
