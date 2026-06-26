#!/usr/bin/env python3
"""Sync library checkout, chunk cache, and manifests — no vector DB."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from git import Repo

sys.path.insert(0, str(Path(__file__).resolve().parent))

from chunk_ast import chunk_library  # noqa: E402
from common import (  # noqa: E402
    delete_chunks_cache,
    get_library_config,
    repo_dir_for,
    write_chunks_cache,
    write_manifest,
    write_symbols_manifest,
)
from crawl import crawl_library  # noqa: E402


def index_library(name: str, reset: bool = False, skip_crawl: bool = False) -> None:
    library = get_library_config(name)
    if not skip_crawl:
        crawl_library(name)

    if reset:
        delete_chunks_cache(name)

    chunks = chunk_library(name)
    if not chunks:
        raise SystemExit(f"No chunks produced for {name}. Check include/exclude paths.")

    chunks_path = write_chunks_cache(library, chunks)
    commit = Repo(repo_dir_for(library)).head.commit.hexsha
    manifest_path = write_manifest(library, commit, len(chunks))
    symbols_path = write_symbols_manifest(library, chunks)
    print(
        f"Indexed {len(chunks)} chunks for {name} "
        f"(source: repos/{name}, cache: {chunks_path}, "
        f"manifest: {manifest_path}, symbols: {symbols_path})"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Index a library for Cursor-native search (crawl + chunk + manifests)."
    )
    parser.add_argument("--library", required=True)
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete and recreate the chunk cache before indexing.",
    )
    parser.add_argument(
        "--skip-crawl",
        action="store_true",
        help="Skip git clone/update and chunk existing checkout.",
    )
    args = parser.parse_args()
    index_library(args.library, reset=args.reset, skip_crawl=args.skip_crawl)


if __name__ == "__main__":
    main()
