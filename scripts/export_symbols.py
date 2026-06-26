#!/usr/bin/env python3
"""Export symbol manifest from a library checkout without a full re-index."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from chunk_ast import chunk_library  # noqa: E402
from common import get_library_config, write_symbols_manifest  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write store/manifests/<library>.symbols.json from source chunks."
    )
    parser.add_argument("--library", required=True)
    args = parser.parse_args()

    library = get_library_config(args.library)
    chunks = chunk_library(args.library)
    if not chunks:
        raise SystemExit(
            f"No chunks produced for {args.library}. Check include/exclude paths."
        )

    path = write_symbols_manifest(library, chunks)
    print(f"Wrote {len(chunks)} chunks -> {path} ({path.read_text().count(chr(10))} lines)")


if __name__ == "__main__":
    main()
