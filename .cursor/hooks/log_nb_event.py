#!/usr/bin/env python3
"""Cursor project hook: log Newbie usage events for onboarding metrics."""

from __future__ import annotations

import hashlib
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

from _project_root import find_project_root, find_scripts_dir

PROJECT_ROOT = find_project_root(start=Path(__file__))
os.environ.setdefault("NB_PROJECT_ROOT", str(PROJECT_ROOT))
SCRIPTS_DIR = find_scripts_dir(start=Path(__file__))
sys.path.insert(0, str(SCRIPTS_DIR))

from metrics.config import load_metrics_config  # noqa: E402
from metrics.identity import current_user_id  # noqa: E402
from metrics.log import append_event  # noqa: E402
from metrics.schema import (  # noqa: E402
    EVENT_SCRIPT_RUN,
    EVENT_SESSION_END,
    EVENT_SESSION_START,
    EVENT_SKILL_INTENT,
    SKILL_KEYWORDS,
    TRACKED_SCRIPTS,
)


def _read_stdin_json() -> dict:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _current_git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return "local"


def _hash_prompt(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _base_event() -> dict:
    return {"user_id": current_user_id(), "commit": _current_git_commit()}


def _parse_script_command(command: str) -> dict | None:
    if not command:
        return None
    matched_script = None
    for script in TRACKED_SCRIPTS:
        if script in command:
            matched_script = script
            break
    if matched_script is None:
        return None

    payload: dict = {
        "event": EVENT_SCRIPT_RUN,
        "script": matched_script,
        **_base_event(),
    }
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()

    config = load_metrics_config()
    library = None
    prompt_value = None
    for index, token in enumerate(tokens):
        if token in ("--library", "-l") and index + 1 < len(tokens):
            library = tokens[index + 1]
        if token.startswith("--library="):
            library = token.split("=", 1)[1]
        if token == "--prompt" and index + 1 < len(tokens):
            prompt_value = tokens[index + 1]
        if token.startswith("--prompt="):
            prompt_value = token.split("=", 1)[1]

    if library:
        payload["library"] = library
    if prompt_value:
        if config.redact_prompts:
            payload["prompt_hash"] = _hash_prompt(prompt_value)
        else:
            payload["prompt"] = prompt_value[:200]

    return payload


def _detect_skill_intent(prompt: str) -> str | None:
    lower = prompt.lower()
    for keyword, skill_id in SKILL_KEYWORDS.items():
        if keyword in lower:
            return skill_id
    return None


def _sync_user_snapshot_write_only() -> None:
    sync_script = SCRIPTS_DIR / "sync_metrics.py"
    if not sync_script.exists():
        return
    subprocess.run(
        [sys.executable, str(sync_script), "--write"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=False,
    )


def handle_after_shell_execution(payload: dict) -> None:
    command = payload.get("command") or payload.get("shellCommand") or ""
    exit_code = payload.get("exitCode", payload.get("exit_code", payload.get("code", 0)))
    duration_ms = payload.get("durationMs", payload.get("duration_ms"))
    event = _parse_script_command(str(command))
    if event is None:
        return
    event["exit_code"] = exit_code
    if duration_ms is not None:
        event["duration_ms"] = duration_ms
    append_event(event)


def handle_before_submit_prompt(payload: dict) -> None:
    prompt = payload.get("prompt") or payload.get("userPrompt") or payload.get("text") or ""
    skill = _detect_skill_intent(str(prompt))
    if skill is None:
        return
    append_event({"event": EVENT_SKILL_INTENT, "skill": skill, **_base_event()})


def handle_session_start(payload: dict) -> None:
    append_event({"event": EVENT_SESSION_START, **_base_event()})


def handle_stop(payload: dict) -> None:
    duration_ms = payload.get("durationMs", payload.get("duration_ms"))
    event = {"event": EVENT_SESSION_END, **_base_event()}
    if duration_ms is not None:
        event["duration_ms"] = duration_ms
    append_event(event)
    _sync_user_snapshot_write_only()


def main() -> None:
    hook_event = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    payload = _read_stdin_json()
    try:
        if hook_event == "afterShellExecution":
            handle_after_shell_execution(payload)
        elif hook_event == "beforeSubmitPrompt":
            handle_before_submit_prompt(payload)
        elif hook_event == "sessionStart":
            handle_session_start(payload)
        elif hook_event == "stop":
            handle_stop(payload)
    except Exception:
        # Fail open — never block engineering work.
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
