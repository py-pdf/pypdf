#!/usr/bin/env python3
"""sessionStart hook: thin-init Newbie workspace state in the open repo (first open)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# Customer-owned config written by `nb init`. Its presence marks an
# already-initialized workspace, so the hook is a no-op on later sessions.
WORKSPACE_MARKER = Path(".newbie/libraries.yaml")


def _read_stdin_json() -> dict:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _is_plugin_install(path: Path) -> bool:
    """True if `path` is the Newbie plugin install dir itself (never init there)."""
    return (path / ".cursor-plugin" / "plugin.json").is_file()


def main() -> None:
    _read_stdin_json()

    # Cursor runs sessionStart hooks with cwd set to the open workspace root.
    # Target that repo directly rather than walking up into the plugin install.
    workspace = Path.cwd().resolve()
    if _is_plugin_install(workspace):
        print(json.dumps({}))
        return

    marker = workspace / WORKSPACE_MARKER
    if marker.is_file():
        print(json.dumps({}))
        return

    nb_cli = Path(__file__).resolve().parent / "nb_cli.py"
    if not nb_cli.is_file():
        print(json.dumps({}))
        return

    result = subprocess.run(
        [sys.executable, str(nb_cli), "init"],
        cwd=str(workspace),
        capture_output=True,
        text=True,
    )

    context = ""
    if result.returncode == 0 and marker.is_file():
        context = (
            "Newbie workspace state was initialized (.newbie/libraries.yaml, store/manifests). "
            "Plugin assets (scripts, rules, skills, commands, agents, MCP) run from the plugin "
            "install — no plugin files were copied into this repo."
        )

    payload: dict[str, str] = {}
    if context:
        payload["additional_context"] = f"## Newbie workspace setup\n{context}"
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
