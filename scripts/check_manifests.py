#!/usr/bin/env python3
#Simple CI check. Ensures metadata matches files.
"""Validate approved library boundaries without calling OpenAI."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    load_libraries_config,
    read_manifest,
    read_symbols_manifest,
)

REQUIRED_MANIFEST_FIELDS = (
    "library",
    "ref",
    "commit",
    "chunk_count",
    "index_backend",
    "source_root",
    "indexed_at",
)

REQUIRED_SYMBOLS_FIELDS = (
    "library",
    "ref",
    "symbols",
    "modules",
    "symbol_count",
)


def run_check() -> dict[str, object]:
    errors: list[str] = []
    libraries = load_libraries_config()
    library_names = [library.name for library in libraries]

    if not libraries:
        return {
            "libraries": library_names,
            "errors": errors,
            "pass": True,
            "message": "no libraries configured",
        }

    for library in libraries:
        manifest = read_manifest(library.name)
        if manifest is None:
            errors.append(f"{library.name}: missing manifest at store/manifests/{library.name}.json")
            continue

        for field in REQUIRED_MANIFEST_FIELDS:
            if field not in manifest:
                errors.append(f"{library.name}: manifest missing required field '{field}'")

        if manifest.get("library") != library.name:
            errors.append(
                f"{library.name}: manifest library field is {manifest.get('library')!r}, expected {library.name!r}"
            )

        if manifest.get("ref") != library.ref:
            errors.append(
                f"{library.name}: manifest ref {manifest.get('ref')!r} != config ref {library.ref!r}"
            )

        chunk_count = manifest.get("chunk_count")
        if not isinstance(chunk_count, int) or chunk_count <= 0:
            errors.append(f"{library.name}: chunk_count must be a positive integer")

        symbols = read_symbols_manifest(library.name)
        if symbols is None:
            errors.append(
                f"{library.name}: missing symbols manifest at "
                f"store/manifests/{library.name}.symbols.json"
            )
        else:
            for field in REQUIRED_SYMBOLS_FIELDS:
                if field not in symbols:
                    errors.append(
                        f"{library.name}: symbols manifest missing required field '{field}'"
                    )
            if symbols.get("library") != library.name:
                errors.append(
                    f"{library.name}: symbols library field is {symbols.get('library')!r}, "
                    f"expected {library.name!r}"
                )
            if symbols.get("ref") != library.ref:
                errors.append(
                    f"{library.name}: symbols ref {symbols.get('ref')!r} != config ref {library.ref!r}"
                )
            symbol_count = symbols.get("symbol_count")
            if not isinstance(symbol_count, int) or symbol_count <= 0:
                errors.append(f"{library.name}: symbol_count must be a positive integer")

            if not isinstance(symbol_count, int) or symbol_count <= 0:
                errors.append(f"{library.name}: symbol_count must be a positive integer")

    return {
        "libraries": library_names,
        "errors": errors,
        "pass": not errors,
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Validate library manifest boundaries.")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    result = run_check()
    if args.json_output:
        print(json.dumps(result, indent=2))
        if not result["pass"]:
            raise SystemExit(1)
        return

    if result.get("message") == "no libraries configured":
        print("No libraries configured in config/libraries.yaml — nothing to check.")
        return

    errors = result["errors"]
    if errors:
        print("Boundary check failed:\n")
        for error in errors:
            print(f"  - {error}")
        raise SystemExit(1)

    count = len(result["libraries"])
    print(f"Boundary check passed ({count} librar{'y' if count == 1 else 'ies'}).")


if __name__ == "__main__":
    main()
