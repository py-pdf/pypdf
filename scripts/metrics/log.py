"""Append-only local event log for Newbie metrics."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from common import EVENTS_DIR, LEGACY_EVENTS_DIR

EVENTS_PATH = EVENTS_DIR / "events.jsonl"
LEGACY_EVENTS_PATH = LEGACY_EVENTS_DIR / "events.jsonl"


def events_path() -> Path:
    return EVENTS_PATH


def append_event(payload: dict[str, Any]) -> None:
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        **payload,
    }
    with EVENTS_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


def _event_source_paths() -> list[Path]:
    """Read the current log plus the legacy ``.nb/metrics`` log if it differs."""
    paths = [EVENTS_PATH]
    if LEGACY_EVENTS_PATH != EVENTS_PATH:
        paths.append(LEGACY_EVENTS_PATH)
    return paths


def read_events(
    *,
    since: datetime | None = None,
    retention_days: int | None = None,
) -> list[dict[str, Any]]:
    source_paths = [path for path in _event_source_paths() if path.exists()]
    if not source_paths:
        return []

    cutoff = since
    if cutoff is None and retention_days is not None:
        cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)

    lines: list[str] = []
    for path in source_paths:
        lines.extend(path.read_text(encoding="utf-8").splitlines())

    events: list[dict[str, Any]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if cutoff is not None:
            ts_raw = event.get("ts")
            if ts_raw:
                try:
                    ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=timezone.utc)
                    if ts < cutoff:
                        continue
                except ValueError:
                    pass
        events.append(event)
    return events
