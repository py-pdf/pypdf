#!/usr/bin/env python3
"""sessionStart hook: run doctor.py and inject health context for the agent."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from _project_root import find_project_root, find_scripts_dir

PROJECT_ROOT = find_project_root(start=Path(__file__))
os.environ.setdefault("NB_PROJECT_ROOT", str(PROJECT_ROOT))
SCRIPTS_DIR = find_scripts_dir(start=Path(__file__))
sys.path.insert(0, str(SCRIPTS_DIR))

from doctor import run_doctor  # noqa: E402
from metrics.identity import current_user_id  # noqa: E402
from metrics.log import append_event  # noqa: E402
from metrics.schema import EVENT_SCRIPT_RUN  # noqa: E402


def _read_stdin_json() -> dict:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _format_context(result: dict[str, object]) -> str:
    lines = ["## Newbie local health (sessionStart)"]
    if result.get("pass"):
        lines.append("All doctor checks passed. Indexed libraries are ready for query.py retrieval.")
    else:
        lines.append("Doctor found issues — fix these before relying on grounded library APIs:")
        for issue in result.get("issues", []):
            lines.append(f"- {issue}")
        lines.append("")
        lines.append("Run `python scripts/doctor.py` for details.")

    lines.extend(
        [
            "",
            "When writing customer code that uses an indexed library:",
            "1. Search `repos/<library>/` with Cursor Codebase Search, or call nb-symbols MCP `search_library_code`.",
            "2. Or run `python scripts/query.py --library <name> --prompt \"<intent>\"`.",
            "3. Use **nb-generate** → **nb-validate** before marking work complete.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    _read_stdin_json()
    result = run_doctor()
    append_event(
        {
            "event": EVENT_SCRIPT_RUN,
            "script": "doctor.py",
            "exit_code": 0 if result.get("pass") else 1,
            "user_id": current_user_id(),
            "commit": result.get("commit", "local"),
            "source": "sessionStart",
        }
    )
    print(json.dumps({"additional_context": _format_context(result)}))
    sys.exit(0)


if __name__ == "__main__":
    main()
