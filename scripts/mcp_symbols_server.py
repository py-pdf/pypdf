#!/usr/bin/env python3
"""MCP server for Newbie — symbol validation and library search (Cursor-native, no Chroma).

Transports:

* ``stdio`` (default) — for the desktop IDE / local plugin install.
* ``http``            — streamable HTTP, for Cloud Agents where stdio servers
  cannot be spawned. Enable with ``--transport http`` or ``NB_MCP_TRANSPORT=http``.

The HTTP host/port come from ``--host``/``--port`` or ``NB_MCP_HOST``/``NB_MCP_PORT``
(default ``127.0.0.1:8848``).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import PROJECT_ROOT, load_libraries_config, read_manifest, read_symbols_manifest, repo_dir_for  # noqa: E402
from library_search import format_hits, search_library  # noqa: E402

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:
    raise SystemExit(
        "Install MCP dependencies: pip install -r requirements-mcp.txt"
    ) from exc

_DEFAULT_HOST = os.environ.get("NB_MCP_HOST", "127.0.0.1")
_DEFAULT_PORT = int(os.environ.get("NB_MCP_PORT", "8848"))

mcp = FastMCP("nb-symbols", host=_DEFAULT_HOST, port=_DEFAULT_PORT)


def _manifest_or_error(library: str) -> dict | str:
    manifest = read_symbols_manifest(library)
    if manifest is None:
        return (
            f"No symbols manifest for {library!r}. "
            f"Run: python scripts/index.py --library {library}"
        )
    return manifest


@mcp.tool()
def list_libraries() -> str:
    """List libraries configured in config/libraries.yaml."""
    libraries = load_libraries_config()
    payload = [
        {
            "name": lib.name,
            "ref": lib.ref,
            "language": lib.language,
            "source_root": repo_dir_for(lib).relative_to(PROJECT_ROOT).as_posix(),
        }
        for lib in libraries
    ]
    return json.dumps(payload, indent=2)


@mcp.tool()
def get_library_path(library: str) -> str:
    """Return the workspace path Cursor should search for library source."""
    lib = next((item for item in load_libraries_config() if item.name == library), None)
    if lib is None:
        return f"Unknown library {library!r}."
    path = repo_dir_for(lib)
    payload = {
        "library": library,
        "source_root": str(path.relative_to(PROJECT_ROOT)),
        "exists": path.exists(),
        "ref": (read_manifest(library) or {}).get("ref", lib.ref),
        "cursor_hint": f"Use Cursor Codebase Search scoped to repos/{library}/",
    }
    return json.dumps(payload, indent=2)


@mcp.tool()
def search_library_code(library: str, query: str, limit: int = 8) -> str:
    """Search library source and chunk cache for API patterns matching a prompt."""
    manifest = read_manifest(library)
    if manifest is None:
        return (
            f"No manifest for {library!r}. Run: python scripts/index.py --library {library}"
        )
    hits = search_library(library, query, top_k=max(1, min(limit, 20)), prefer_public=True)
    return format_hits(library, query, hits, manifest=manifest)


@mcp.tool()
def lookup_symbol(library: str, symbol: str) -> str:
    """Return whether a symbol is a public indexed API for the given library."""
    manifest = _manifest_or_error(library)
    if isinstance(manifest, str):
        return manifest

    symbols = set(manifest.get("symbols", []))
    modules = set(manifest.get("modules", []))
    is_public = symbol in symbols
    payload = {
        "library": library,
        "symbol": symbol,
        "is_public": is_public,
        "ref": manifest.get("ref"),
        "symbol_count": manifest.get("symbol_count", len(symbols)),
    }
    if symbol in modules:
        payload["is_module"] = True
    return json.dumps(payload, indent=2)


@mcp.tool()
def search_symbols(library: str, query: str, limit: int = 20) -> str:
    """Search public symbols by substring (case-insensitive)."""
    manifest = _manifest_or_error(library)
    if isinstance(manifest, str):
        return manifest

    needle = query.lower()
    matches = [
        symbol
        for symbol in manifest.get("symbols", [])
        if needle in symbol.lower()
    ][: max(1, min(limit, 100))]
    payload = {
        "library": library,
        "query": query,
        "matches": matches,
        "match_count": len(matches),
    }
    return json.dumps(payload, indent=2)


@mcp.tool()
def verify_imports(library: str, symbols: list[str]) -> str:
    """Verify a list of imported symbol names against the public index."""
    manifest = _manifest_or_error(library)
    if isinstance(manifest, str):
        return manifest

    known = set(manifest.get("symbols", []))
    results = [
        {"symbol": symbol, "is_public": symbol in known}
        for symbol in symbols
    ]
    invalid = [item["symbol"] for item in results if not item["is_public"]]
    payload = {
        "library": library,
        "results": results,
        "pass": not invalid,
        "invalid_symbols": invalid,
    }
    return json.dumps(payload, indent=2)


def _resolve_transport(cli_value: str | None) -> str:
    transport = (cli_value or os.environ.get("NB_MCP_TRANSPORT") or "stdio").lower()
    if transport in ("http", "streamable-http", "streamable_http"):
        return "streamable-http"
    if transport == "sse":
        return "sse"
    return "stdio"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the nb-symbols MCP server.")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse"],
        default=None,
        help="Transport to serve on (default: stdio, or NB_MCP_TRANSPORT).",
    )
    parser.add_argument("--host", default=None, help="HTTP host (NB_MCP_HOST).")
    parser.add_argument("--port", type=int, default=None, help="HTTP port (NB_MCP_PORT).")
    args = parser.parse_args()

    if args.host:
        mcp.settings.host = args.host
    if args.port:
        mcp.settings.port = args.port

    mcp.run(transport=_resolve_transport(args.transport))


if __name__ == "__main__":
    main()
