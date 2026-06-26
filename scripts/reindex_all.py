#!/usr/bin/env python3
"""Re-index all configured libraries (used by GitHub Action)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_libraries_config  # noqa: E402
from index import index_library  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Re-index all libraries from config/libraries.yaml.")
    parser.add_argument(
        "--library",
        help="Index only this library (default: all configured libraries).",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete and recreate each library chunk cache before indexing.",
    )
    args = parser.parse_args()

    libraries = load_libraries_config()
    if args.library:
        libraries = [lib for lib in libraries if lib.name == args.library]
        if not libraries:
            raise SystemExit(f"Library {args.library!r} not found in config/libraries.yaml")

    if not libraries:
        print("No libraries configured.")
        return

    for library in libraries:
        print(f"Indexing {library.name} @ {library.ref} ...")
        index_library(library.name, reset=args.reset, skip_crawl=False)

    print(f"Done — indexed {len(libraries)} librar{'y' if len(libraries) == 1 else 'ies'}.")


if __name__ == "__main__":
    main()
