#!/usr/bin/env python3
"""Tree-sitter chunking router for indexed library sources."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from chunk.languages import get_language_spec  # noqa: E402
from chunk.treesitter import chunk_library_with_spec  # noqa: E402
from common import CodeChunk, get_library_config  # noqa: E402


def chunk_library(name: str) -> list[CodeChunk]:
    library = get_library_config(name)
    spec = get_language_spec(library.language)
    return chunk_library_with_spec(library, spec)


def main() -> None:
    parser = argparse.ArgumentParser(description="Chunk a library using tree-sitter parsing.")
    parser.add_argument("--library", required=True)
    args = parser.parse_args()
    chunks = chunk_library(args.library)
    print(f"Generated {len(chunks)} chunks for {args.library}")


if __name__ == "__main__":
    main()
