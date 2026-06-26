"""Aggregate git milestones, hook events, and CI stats into a metrics report."""

from __future__ import annotations

import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

from common import load_libraries_config, read_manifest, read_symbols_manifest
from metrics.config import MetricsConfig
from metrics.git_milestones import (
    _days_between,
    build_checklist,
    extract_milestones,
    repo_info,
)
from metrics.github_ci import fetch_ci_stats
from metrics.identity import resolve_display_name
from metrics.log import read_events
from metrics.schema import (
    EVENT_SCRIPT_RUN,
    EVENT_SESSION_END,
    EVENT_SKILL_INTENT,
    REPORT_SCHEMA_VERSION,
)


def events_in_window(events: list[dict[str, Any]], days: int) -> list[dict[str, Any]]:
    return _events_in_window(events, days)


def team_benefit_window(events: list[dict[str, Any]]) -> dict[str, Any]:
    return _team_benefit_window(events)


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        ts = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        return ts
    except ValueError:
        return None


def _events_in_window(events: list[dict[str, Any]], days: int) -> list[dict[str, Any]]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    filtered: list[dict[str, Any]] = []
    for event in events:
        ts = _parse_ts(event.get("ts"))
        if ts is None or ts >= cutoff:
            filtered.append(event)
    return filtered


def _extract_violation_symbol(error: str) -> str | None:
    match = re.search(r"'([^']+)' imported from", error)
    if match:
        return match.group(1)
    return None


def _index_health() -> dict[str, Any]:
    libraries_payload: list[dict[str, Any]] = []
    for library in load_libraries_config():
        manifest = read_manifest(library.name) or {}
        symbols = read_symbols_manifest(library.name) or {}
        libraries_payload.append(
            {
                "name": library.name,
                "ref": library.ref,
                "chunk_count": manifest.get("chunk_count"),
                "symbol_count": symbols.get("symbol_count"),
            }
        )
    return {"libraries": libraries_payload}


def _recalculate_deltas(milestones: dict[str, Any]) -> dict[str, int | None]:
    anchor = milestones.get("scaffold_adopted") or milestones.get("first_library_configured")
    if not anchor:
        return {}
    anchor_date = anchor["date"]
    deltas: dict[str, int | None] = {}
    for target_key, delta_key in (
        ("first_index", "to_first_index"),
        ("first_customer_code", "to_first_customer_code"),
        ("first_doctor_pass", "to_first_doctor_pass"),
        ("first_query", "to_first_query"),
    ):
        target = milestones.get(target_key)
        deltas[delta_key] = _days_between(anchor_date, target["date"]) if target else None
    return deltas


def _apply_event_milestones(
    milestones: dict[str, Any],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    result = dict(milestones)
    ms = dict(result.get("milestones") or {})
    for event in sorted(events, key=lambda item: item.get("ts", "")):
        if event.get("event") != EVENT_SCRIPT_RUN:
            continue
        script = event.get("script")
        passed = event.get("exit_code") == 0
        if script == "doctor.py" and passed and ms.get("first_doctor_pass") is None:
            ms["first_doctor_pass"] = {
                "date": event.get("ts", ""),
                "commit": event.get("commit", "local"),
            }
        if script == "query.py" and passed and ms.get("first_query") is None:
            ms["first_query"] = {
                "date": event.get("ts", ""),
                "commit": event.get("commit", "local"),
            }
    result["milestones"] = ms
    return result


def _team_benefit_window(events: list[dict[str, Any]]) -> dict[str, Any]:
    query_runs = 0
    query_by_library: Counter[str] = Counter()
    skill_intents: Counter[str] = Counter()
    symbol_runs = 0
    symbol_passes = 0
    violations: Counter[str] = Counter()

    for event in events:
        event_type = event.get("event")
        if event_type == EVENT_SCRIPT_RUN:
            script = event.get("script")
            if script == "query.py":
                query_runs += 1
                library = event.get("library")
                if library:
                    query_by_library[str(library)] += 1
            if script == "verify_symbols.py":
                symbol_runs += 1
                if event.get("exit_code") == 0:
                    symbol_passes += 1
                for error in event.get("errors") or []:
                    symbol = _extract_violation_symbol(str(error))
                    if symbol:
                        violations[symbol] += 1
        elif event_type == EVENT_SKILL_INTENT:
            skill = event.get("skill")
            if skill:
                skill_intents[str(skill)] += 1

    top_violations = [
        {"symbol": symbol, "count": count}
        for symbol, count in violations.most_common(10)
    ]

    return {
        "query_runs": query_runs,
        "query_by_library": dict(query_by_library),
        "skill_intents": dict(skill_intents),
        "symbol_checks": {
            "runs": symbol_runs,
            "pass_rate": round(symbol_passes / symbol_runs, 3) if symbol_runs else None,
            "top_violations": top_violations,
        },
        "sessions_ended": sum(1 for event in events if event.get("event") == EVENT_SESSION_END),
    }


def _merge_team_windows(windows: list[dict[str, Any]]) -> dict[str, Any]:
    if not windows:
        return _team_benefit_window([])

    query_by_library: Counter[str] = Counter()
    skill_intents: Counter[str] = Counter()
    violations: Counter[str] = Counter()
    query_runs = 0
    symbol_runs = 0
    symbol_passes = 0
    sessions_ended = 0

    for window in windows:
        query_runs += int(window.get("query_runs", 0))
        query_by_library.update(window.get("query_by_library") or {})
        skill_intents.update(window.get("skill_intents") or {})
        sessions_ended += int(window.get("sessions_ended", 0))
        checks = window.get("symbol_checks") or {}
        runs = int(checks.get("runs", 0))
        symbol_runs += runs
        rate = checks.get("pass_rate")
        if runs and rate is not None:
            symbol_passes += round(rate * runs)
        for item in checks.get("top_violations") or []:
            symbol = item.get("symbol")
            if symbol:
                violations[symbol] += int(item.get("count", 0))

    return {
        "query_runs": query_runs,
        "query_by_library": dict(query_by_library),
        "skill_intents": dict(skill_intents),
        "symbol_checks": {
            "runs": symbol_runs,
            "pass_rate": round(symbol_passes / symbol_runs, 3) if symbol_runs else None,
            "top_violations": [
                {"symbol": symbol, "count": count}
                for symbol, count in violations.most_common(10)
            ],
        },
        "sessions_ended": sessions_ended,
    }


def _build_users_section(
    snapshots: list[dict[str, Any]],
    config: MetricsConfig,
) -> dict[str, Any]:
    from metrics.user_snapshot import is_user_active_30d

    roster: list[dict[str, Any]] = []
    active_30d = 0
    for snapshot in snapshots:
        if is_user_active_30d(snapshot):
            active_30d += 1
        uid = snapshot.get("user_id", "unknown")
        roster.append(
            {
                "user_id": uid,
                "display_name": resolve_display_name(str(uid), config),
                "last_synced": snapshot.get("synced_at"),
                "git_email_domain": snapshot.get("git_email_domain"),
                "window_30d": (snapshot.get("activity") or {}).get("window_30d") or {},
                "onboarding": snapshot.get("onboarding") or {},
            }
        )

    return {
        "synced_count": len(snapshots),
        "active_30d": active_30d,
        "roster": sorted(roster, key=lambda item: item.get("last_synced") or "", reverse=True),
    }


def _coverage_gaps(
    events: list[dict[str, Any]],
    ci_stats: dict[str, Any] | None,
    user_snapshots: list[dict[str, Any]],
) -> list[str]:
    gaps: list[str] = []
    if not user_snapshots:
        gaps.append(
            "No synced user files in reports/users/ — each engineer should run "
            "python scripts/sync_metrics.py --write --push"
        )
    elif events:
        gaps.append(
            "Local hook events exist on this machine; team totals use synced user files in reports/users/."
        )
    elif not events:
        gaps.append(
            "No local hook events on this machine — enable Cursor project hooks to capture usage."
        )

    gaps.append(
        "Local repos/ checkouts are not visible to GitHub — doctor_pass relies on hook events."
    )
    if ci_stats is None:
        gaps.append(
            "CI workflow stats unavailable — set GITHUB_TOKEN in scheduled workflow or run locally."
        )
    return gaps


def build_report(config: MetricsConfig) -> dict[str, Any]:
    from metrics.user_snapshot import load_user_snapshots

    all_events = read_events(retention_days=config.event_retention_days)
    user_snapshots = load_user_snapshots()
    onboarding = extract_milestones(config)
    onboarding = _apply_event_milestones(onboarding, all_events)
    onboarding["deltas_days"] = _recalculate_deltas(onboarding.get("milestones") or {})

    ci_30d = fetch_ci_stats(config.ci_workflow_name, days=30)

    if user_snapshots:
        window_7d = _merge_team_windows(
            [(s.get("activity") or {}).get("window_7d") or {} for s in user_snapshots]
        )
        window_30d = _merge_team_windows(
            [(s.get("activity") or {}).get("window_30d") or {} for s in user_snapshots]
        )
        all_time = _merge_team_windows(
            [(s.get("activity") or {}).get("all_time") or {} for s in user_snapshots]
        )
    else:
        window_7d = _team_benefit_window(_events_in_window(all_events, 7))
        window_30d = _team_benefit_window(_events_in_window(all_events, 30))
        all_time = _team_benefit_window(all_events)

    if ci_30d:
        window_30d["ci"] = ci_30d

    users_section = _build_users_section(user_snapshots, config)

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo": repo_info(config),
        "onboarding": {
            **onboarding,
            "checklist": build_checklist(config),
        },
        "team_benefit": {
            "window_7d": window_7d,
            "window_30d": window_30d,
            "all_time": all_time,
            "index": _index_health(),
        },
        "users": users_section,
        "coverage_gaps": _coverage_gaps(all_events, ci_30d, user_snapshots),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = [
        "# Newbie onboarding metrics",
        "",
        f"Generated: {report.get('generated_at', '')}",
        "",
        "## Onboarding milestones",
        "",
    ]

    milestones = (report.get("onboarding") or {}).get("milestones") or {}
    for key, value in milestones.items():
        if value:
            lines.append(f"- **{key}**: {value.get('date', '?')} ({value.get('commit', '?')})")
        else:
            lines.append(f"- **{key}**: not reached")

    lines.extend(["", "## Time to milestone (days)", ""])
    deltas = (report.get("onboarding") or {}).get("deltas_days") or {}
    for key, value in deltas.items():
        lines.append(f"- **{key}**: {value if value is not None else 'n/a'}")

    lines.extend(["", "## Checklist", ""])
    checklist = (report.get("onboarding") or {}).get("checklist") or {}
    for key, value in checklist.items():
        status = "yes" if value else "no"
        lines.append(f"- [{status}] {key}")

    lines.extend(["", "## Team benefit (30 days)", ""])
    window = ((report.get("team_benefit") or {}).get("window_30d") or {})
    lines.append(f"- Query runs: {window.get('query_runs', 0)}")
    lines.append(f"- Skill intents: {window.get('skill_intents', {})}")
    symbol_checks = window.get("symbol_checks") or {}
    lines.append(
        f"- Symbol checks: {symbol_checks.get('runs', 0)} runs, "
        f"pass rate {symbol_checks.get('pass_rate', 'n/a')}"
    )
    ci = window.get("ci")
    if ci:
        lines.append(
            f"- CI: {ci.get('workflow_runs', 0)} runs, "
            f"success rate {ci.get('success_rate', 'n/a')}"
        )

    users = report.get("users") or {}
    roster = users.get("roster") or []
    lines.extend(
        [
            "",
            "## Per-user roster (30 days)",
            "",
            f"Synced engineers: {users.get('synced_count', 0)} · "
            f"Active (30d): {users.get('active_30d', 0)}",
            "",
            "| Engineer | Domain | Query runs | Skill intents | First query (days) | Last synced |",
            "|----------|--------|------------|---------------|-------------------|-------------|",
        ]
    )
    if roster:
        for entry in roster:
            w30 = entry.get("window_30d") or {}
            onboarding_user = entry.get("onboarding") or {}
            intents = w30.get("skill_intents") or {}
            intent_total = sum(intents.values())
            days_q = onboarding_user.get("days_to_first_query")
            days_label = days_q if days_q is not None else "n/a"
            synced = (entry.get("last_synced") or "")[:10]
            lines.append(
                f"| {entry.get('display_name', entry.get('user_id'))} "
                f"| {entry.get('git_email_domain', '?')} "
                f"| {w30.get('query_runs', 0)} "
                f"| {intent_total} "
                f"| {days_label} "
                f"| {synced or 'n/a'} |"
            )
    else:
        lines.append("| _No synced users yet_ | | | | | |")

    lines.extend(["", "## Index health", ""])
    index = (report.get("team_benefit") or {}).get("index") or {}
    for library in index.get("libraries") or []:
        lines.append(
            f"- {library.get('name')}: {library.get('chunk_count', '?')} chunks, "
            f"{library.get('symbol_count', '?')} symbols @ {library.get('ref', '?')}"
        )

    lines.extend(["", "## Coverage gaps", ""])
    for gap in report.get("coverage_gaps") or []:
        lines.append(f"- {gap}")

    lines.append("")
    return "\n".join(lines)
