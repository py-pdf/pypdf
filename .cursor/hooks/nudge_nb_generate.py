#!/usr/bin/env python3
"""beforeSubmitPrompt hook: nudge engineers toward nb-generate when skipping query.py."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from _project_root import find_project_root, find_scripts_dir

PROJECT_ROOT = find_project_root(start=Path(__file__))
os.environ.setdefault("NB_PROJECT_ROOT", str(PROJECT_ROOT))
SCRIPTS_DIR = find_scripts_dir(start=Path(__file__))
sys.path.insert(0, str(SCRIPTS_DIR))

from common import load_libraries_config  # noqa: E402
from metrics.identity import current_user_id  # noqa: E402
from metrics.log import append_event, read_events  # noqa: E402
from metrics.schema import EVENT_SKILL_INTENT, SKILL_KEYWORDS  # noqa: E402

CODEGEN_VERBS = (
    "write",
    "create",
    "generate",
    "implement",
    "build",
    "add",
    "scaffold",
    "script",
    "module",
    "function",
    "class",
)
REVIEW_VERBS = (
    "review",
    "check",
    "validate",
    "audit",
    "test plan",
    "coverage",
    "explain",
    "what tests",
    "does this follow",
)


def _read_stdin_json() -> dict:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _prompt_text(payload: dict) -> str:
    return str(
        payload.get("prompt")
        or payload.get("userPrompt")
        or payload.get("text")
        or ""
    )


def _configured_libraries() -> list[str]:
    return [library.name for library in load_libraries_config()]


def _mentions_library(prompt: str, libraries: list[str]) -> list[str]:
    lower = prompt.lower()
    matched: list[str] = []
    for name in libraries:
        if re.search(rf"\b{re.escape(name)}\b", lower):
            matched.append(name)
    return matched


def _has_skill_intent(prompt: str) -> bool:
    lower = prompt.lower()
    return any(keyword in lower for keyword in SKILL_KEYWORDS)


def _looks_like_codegen(prompt: str) -> bool:
    lower = prompt.lower()
    if any(keyword in lower for keyword in REVIEW_VERBS):
        return False
    return any(verb in lower for verb in CODEGEN_VERBS)


def _recent_query_run(*, hours: int = 24) -> bool:
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    user_id = current_user_id()
    for event in reversed(read_events(since=since)):
        if event.get("user_id") != user_id:
            continue
        if event.get("script") != "query.py":
            continue
        if event.get("exit_code", 0) == 0:
            return True
    return False


def _strict_nudge_enabled() -> bool:
    return os.getenv("NB_STRICT_NUDGE", "").strip().lower() in {"1", "true", "yes"}


def main() -> None:
    payload = _read_stdin_json()
    prompt = _prompt_text(payload)
    libraries = _configured_libraries()
    mentioned = _mentions_library(prompt, libraries)

    if not mentioned or not _looks_like_codegen(prompt):
        print(json.dumps({"continue": True}))
        sys.exit(0)

    if _has_skill_intent(prompt) or _recent_query_run():
        print(json.dumps({"continue": True}))
        sys.exit(0)

    library_hint = mentioned[0]
    append_event(
        {
            "event": EVENT_SKILL_INTENT,
            "skill": "nb-generate",
            "user_id": current_user_id(),
            "suggested": True,
            "libraries": mentioned,
        }
    )

    message = (
        "This prompt looks like library code generation without a recent `query.py` run.\n\n"
        f"Recommended: run `python scripts/query.py --library {library_hint} --prompt \"<your intent>\"` "
        "or add **use nb-generate** to your prompt.\n\n"
        "Set NB_STRICT_NUDGE=0 in your environment to disable this gate."
    )

    if _strict_nudge_enabled():
        print(json.dumps({"continue": False, "user_message": message}))
    else:
        # Non-blocking: allow submission; sessionStart health context covers standing guidance.
        print(json.dumps({"continue": True}))
    sys.exit(0)


if __name__ == "__main__":
    main()
