#!/usr/bin/env python3
"""Retrieve relevant library patterns using Cursor-native search (repos/ + chunk cache)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import get_library_config, read_manifest  # noqa: E402
from library_search import format_hits, hits_to_json, search_library  # noqa: E402


def query_library(
    name: str,
    prompt: str,
    top_k: int = 8,
    prefer_public: bool = True,
    json_output: bool = False,
) -> str:
    get_library_config(name)
    manifest = read_manifest(name)
    if manifest is None:
        raise SystemExit(
            f"No manifest found for '{name}'. Run: python scripts/index.py --library {name}"
        )

    hits = search_library(name, prompt, top_k=top_k, prefer_public=prefer_public)
    if json_output:
        return hits_to_json(name, prompt, hits, manifest)
    return format_hits(name, prompt, hits, manifest=manifest)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search indexed library patterns (Cursor codebase + chunk cache)."
    )
    parser.add_argument("--library", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument(
        "--include-internal",
        action="store_true",
        help="Do not prioritize public API symbols in result ordering.",
    )
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    output = query_library(
        args.library,
        args.prompt,
        top_k=args.top_k,
        prefer_public=not args.include_internal,
        json_output=args.json_output,
    )
    print(output)


if __name__ == "__main__":
    main()
