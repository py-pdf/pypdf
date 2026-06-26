"""Build and load per-user metrics snapshots synced to reports/users/."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import REPORTS_DIR
from metrics.config import MetricsConfig
from metrics.git_milestones import _days_between, extract_milestones, first_customer_code_for_user
from metrics.identity import current_user_id, email_domain, git_user_email
from metrics.log import read_events
from metrics.schema import (
    EVENT_SCRIPT_RUN,
    USER_SNAPSHOT_SCHEMA_VERSION,
)

USERS_DIR = REPORTS_DIR / "users"


def filter_events_for_user(events: list[dict[str, Any]], user_id: str) -> list[dict[str, Any]]:
    return [event for event in events if event.get("user_id") == user_id]


def _onboarding_from_events(events: list[dict[str, Any]], config: MetricsConfig) -> dict[str, Any]:
    onboarding: dict[str, Any] = {
        "first_query": None,
        "first_doctor_pass": None,
        "first_customer_code": None,
        "days_to_first_query": None,
    }
    for event in sorted(events, key=lambda item: item.get("ts", "")):
        if event.get("event") != EVENT_SCRIPT_RUN:
            continue
        script = event.get("script")
        passed = event.get("exit_code") == 0
        if script == "doctor.py" and passed and onboarding["first_doctor_pass"] is None:
            onboarding["first_doctor_pass"] = {"date": event.get("ts", "")}
        if script == "query.py" and passed and onboarding["first_query"] is None:
            onboarding["first_query"] = {"date": event.get("ts", "")}

    email = git_user_email()
    customer_milestone = first_customer_code_for_user(email, config)
    if customer_milestone:
        onboarding["first_customer_code"] = customer_milestone.to_dict()

    anchor = extract_milestones(config)
    scaffold = (anchor.get("milestones") or {}).get("scaffold_adopted")
    first_query = onboarding.get("first_query")
    if scaffold and first_query:
        onboarding["days_to_first_query"] = _days_between(scaffold["date"], first_query["date"])

    return onboarding


def build_user_snapshot(config: MetricsConfig, user_id: str | None = None) -> dict[str, Any]:
    uid = user_id or current_user_id()
    email = git_user_email()
    all_events = read_events(retention_days=config.event_retention_days)
    user_events = filter_events_for_user(all_events, uid)

    from metrics.aggregate import events_in_window, team_benefit_window

    return {
        "schema_version": USER_SNAPSHOT_SCHEMA_VERSION,
        "user_id": uid,
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "git_email_domain": email_domain(email),
        "onboarding": _onboarding_from_events(user_events, config),
        "activity": {
            "window_7d": team_benefit_window(events_in_window(user_events, 7)),
            "window_30d": team_benefit_window(events_in_window(user_events, 30)),
            "all_time": team_benefit_window(user_events),
        },
    }


def user_snapshot_path(user_id: str) -> Path:
    return USERS_DIR / f"{user_id}.json"


def write_user_snapshot(snapshot: dict[str, Any]) -> Path:
    USERS_DIR.mkdir(parents=True, exist_ok=True)
    path = user_snapshot_path(snapshot["user_id"])
    path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    return path


def load_user_snapshots() -> list[dict[str, Any]]:
    if not USERS_DIR.exists():
        return []
    snapshots: list[dict[str, Any]] = []
    for path in sorted(USERS_DIR.glob("*.json")):
        if path.name == "README.md":
            continue
        try:
            snapshots.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return snapshots


def is_user_active_30d(snapshot: dict[str, Any]) -> bool:
    window = (snapshot.get("activity") or {}).get("window_30d") or {}
    if window.get("query_runs", 0) > 0:
        return True
    if window.get("sessions_ended", 0) > 0:
        return True
    intents = window.get("skill_intents") or {}
    return sum(intents.values()) > 0
