"""C-level executive summary derived from onboarding metrics reports."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from metrics.config import ExecutiveTargets, MetricsConfig

MILESTONE_LABELS = {
    "scaffold_adopted": "Artifact adopted",
    "first_library_configured": "First library configured",
    "first_index": "First library indexed",
    "first_convention_doc": "Library conventions documented",
    "first_customer_code": "First production code",
    "first_doctor_pass": "Local setup verified",
    "first_query": "First grounded API lookup",
}

DELTA_LABELS = {
    "to_first_index": "Time to first indexed library",
    "to_first_customer_code": "Time to first production code",
    "to_first_doctor_pass": "Time to verified local setup",
    "to_first_query": "Time to first grounded API lookup",
}

STATUS_LABELS = {
    "on_track": "On track",
    "at_risk": "At risk",
    "unknown": "Not yet measured",
    "complete": "Complete",
}


def _parse_iso_date(value: str | None) -> str:
    if not value:
        return "not yet observed"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y")
    except ValueError:
        return value[:10]


def _format_days(value: int | None) -> str:
    if value is None:
        return "not yet observed"
    if value == 0:
        return "0 days (same day)"
    if value == 1:
        return "1 day"
    return f"{value} days"


def _format_percent(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.0f}%"


def _checklist_complete(checklist: dict[str, bool]) -> bool:
    required = (
        "libraries_configured",
        "manifests_committed",
        "conventions_filled",
        "ci_configured",
    )
    return all(checklist.get(key) for key in required)


def _has_synced_users(report: dict[str, Any]) -> bool:
    users = report.get("users") or {}
    return int(users.get("synced_count", 0)) > 0


def _has_hook_events(report: dict[str, Any]) -> bool:
    gaps = report.get("coverage_gaps") or []
    if _has_synced_users(report):
        return True
    return not any("No local hook events" in gap for gap in gaps)


def _has_ci_stats(report: dict[str, Any]) -> bool:
    window = ((report.get("team_benefit") or {}).get("window_30d") or {})
    return window.get("ci") is not None


def _data_confidence(report: dict[str, Any]) -> dict[str, str]:
    users = report.get("users") or {}
    synced = int(users.get("synced_count", 0))
    has_ci = _has_ci_stats(report)

    if synced > 0 and has_ci:
        return {
            "level": "High",
            "note": (
                f"{synced} engineer(s) have synced metrics; CI stats are available for this period."
            ),
        }
    if synced > 0:
        return {
            "level": "Medium",
            "note": (
                f"{synced} engineer(s) synced; more complete coverage as additional engineers "
                "run sync_metrics.py --write --push."
            ),
        }
    return {
        "level": "Low",
        "note": (
            "No per-engineer metrics synced yet — each user should run "
            "sync_metrics.py --write --push after enabling Cursor hooks."
        ),
    }


def _compare_trend(current: float | int | None, prior: float | int | None) -> str:
    if prior is None and current is None:
        return "unknown"
    if prior is None:
        return "new"
    if current is None:
        return "unknown"
    if current > prior:
        return "up"
    if current < prior:
        return "down"
    return "flat"


def _skill_intent_total(window: dict[str, Any]) -> int:
    intents = window.get("skill_intents") or {}
    return sum(int(value) for value in intents.values())


def _build_trends(report: dict[str, Any], prior_report: dict[str, Any] | None) -> list[dict[str, str]]:
    current_window = ((report.get("team_benefit") or {}).get("window_30d") or {})
    prior_window = (
        ((prior_report or {}).get("team_benefit") or {}).get("window_30d") or {}
        if prior_report
        else {}
    )

    current_pass = (current_window.get("symbol_checks") or {}).get("pass_rate")
    prior_pass = (prior_window.get("symbol_checks") or {}).get("pass_rate")

    trends = [
        {
            "metric": "Grounded API lookup activity",
            "direction": _compare_trend(
                current_window.get("query_runs"),
                prior_window.get("query_runs") if prior_report else None,
            ),
        },
        {
            "metric": "Skill-assisted workflows",
            "direction": _compare_trend(
                _skill_intent_total(current_window),
                _skill_intent_total(prior_window) if prior_report else None,
            ),
        },
        {
            "metric": "API boundary check quality",
            "direction": _compare_trend(current_pass, prior_pass if prior_report else None),
        },
    ]

    current_ci = (current_window.get("ci") or {}).get("success_rate")
    prior_ci = (prior_window.get("ci") or {}).get("success_rate") if prior_report else None
    if current_ci is not None or prior_ci is not None:
        trends.append(
            {
                "metric": "CI reliability",
                "direction": _compare_trend(current_ci, prior_ci),
            }
        )

    return trends


def _delta_status(
    key: str,
    value: int | None,
    targets: ExecutiveTargets,
) -> str:
    if value is None:
        return "unknown"
    if key == "to_first_index":
        return "on_track" if value <= targets.days_to_first_index else "at_risk"
    return "complete"


def _pass_rate_status(value: float | None, target: float) -> str:
    if value is None:
        return "unknown"
    return "on_track" if value >= target else "at_risk"


def _build_headline(
    report: dict[str, Any],
    checklist: dict[str, bool],
    window_30d: dict[str, Any],
    targets: ExecutiveTargets,
) -> str:
    symbol_pass = (window_30d.get("symbol_checks") or {}).get("pass_rate")
    setup_complete = _checklist_complete(checklist)
    users = report.get("users") or {}
    synced = int(users.get("synced_count", 0))
    active = int(users.get("active_30d", 0))

    if not checklist.get("manifests_committed") or not checklist.get("conventions_filled"):
        return "Onboarding is in progress — library indexing is not yet complete."

    if symbol_pass is not None and symbol_pass < targets.symbol_pass_rate_30d:
        return (
            "Newbie is adopted, but API boundary violations suggest an ongoing learning curve."
        )

    if synced > 0 and active > 0:
        return (
            f"{synced} engineer(s) synced; {active} active in the last 30 days — "
            "Newbie is delivering grounded development workflows."
        )

    if setup_complete and synced > 0:
        return (
            f"{synced} engineer(s) synced; enable regular usage or sync to increase active adoption."
        )

    if setup_complete and synced == 0:
        return (
            "Setup is complete; engineers should sync metrics to appear in the team roster."
        )

    if setup_complete:
        return "Newbie setup is complete; adoption signals are still emerging."

    return "Newbie onboarding is underway."


def _build_key_outcomes(
    report: dict[str, Any],
    targets: ExecutiveTargets,
) -> list[dict[str, str]]:
    onboarding = report.get("onboarding") or {}
    deltas = onboarding.get("deltas_days") or {}
    milestones = onboarding.get("milestones") or {}
    window_30d = ((report.get("team_benefit") or {}).get("window_30d") or {})
    symbol_pass = (window_30d.get("symbol_checks") or {}).get("pass_rate")
    ci_success = (window_30d.get("ci") or {}).get("success_rate")
    users = report.get("users") or {}

    first_index_days = deltas.get("to_first_index")
    first_index_date = _parse_iso_date((milestones.get("first_index") or {}).get("date"))
    first_customer_days = deltas.get("to_first_customer_code")

    outcomes = [
        {
            "label": DELTA_LABELS["to_first_index"],
            "value": f"{_format_days(first_index_days)} ({first_index_date})",
            "status": _delta_status("to_first_index", first_index_days, targets),
        },
        {
            "label": DELTA_LABELS["to_first_customer_code"],
            "value": _format_days(first_customer_days),
            "status": "complete" if first_customer_days is not None else "unknown",
        },
        {
            "label": "Active engineers (30d)",
            "value": f"{users.get('active_30d', 0)} of {users.get('synced_count', 0)} synced",
            "status": "on_track" if users.get("active_30d") else "unknown",
        },
        {
            "label": "Grounded API lookups (30d)",
            "value": str(window_30d.get("query_runs", 0)),
            "status": "on_track" if window_30d.get("query_runs") else "unknown",
        },
        {
            "label": "API boundary check pass rate (30d)",
            "value": _format_percent(symbol_pass),
            "status": _pass_rate_status(symbol_pass, targets.symbol_pass_rate_30d),
        },
        {
            "label": "CI success rate (30d)",
            "value": _format_percent(ci_success),
            "status": _pass_rate_status(ci_success, targets.ci_success_rate_30d),
        },
    ]
    return outcomes


def _build_narrative_bullets(
    report: dict[str, Any],
    targets: ExecutiveTargets,
) -> list[str]:
    bullets: list[str] = []
    onboarding = report.get("onboarding") or {}
    deltas = onboarding.get("deltas_days") or {}
    window_30d = ((report.get("team_benefit") or {}).get("window_30d") or {})
    checklist = onboarding.get("checklist") or {}

    to_first_index = deltas.get("to_first_index")
    if to_first_index is not None:
        bullets.append(
            f"Engineers indexed their first library **{_format_days(to_first_index)}** "
            "after adopting the artifact."
        )

    users = report.get("users") or {}
    roster = users.get("roster") or []
    for entry in roster[:2]:
        name = entry.get("display_name", entry.get("user_id"))
        days = (entry.get("onboarding") or {}).get("days_to_first_query")
        if days is not None:
            bullets.append(
                f"Engineer **{name}** reached first grounded lookup in **{_format_days(days)}**."
            )

    query_runs = window_30d.get("query_runs", 0)
    if query_runs:
        bullets.append(
            f"In the last 30 days, the team performed **{query_runs}** grounded API lookups "
            "before writing code."
        )
    elif _checklist_complete(checklist):
        bullets.append(
            "No engineers have synced metrics yet — each user should run "
            "`python scripts/sync_metrics.py --write --push` after enabling hooks."
        )

    symbol_pass = (window_30d.get("symbol_checks") or {}).get("pass_rate")
    symbol_runs = (window_30d.get("symbol_checks") or {}).get("runs", 0)
    if symbol_pass is not None and symbol_runs:
        if symbol_pass >= targets.symbol_pass_rate_30d:
            bullets.append(
                f"Automated API boundary checks passed **{_format_percent(symbol_pass)}** "
                "of the time, indicating teams are staying within indexed public APIs."
            )
        else:
            failure_pct = (1 - symbol_pass) * 100
            bullets.append(
                f"Automated checks flagged unapproved library usage in "
                f"**{failure_pct:.0f}%** of runs — additional convention coaching may help."
            )

    skill_total = _skill_intent_total(window_30d)
    if skill_total:
        bullets.append(
            f"Teams invoked Newbie-assisted workflows **{skill_total}** times "
            "in the last 30 days (generate, validate, test, or index)."
        )

    if not bullets:
        bullets.append(
            "Onboarding milestones are tracked from git history; "
            "enable usage telemetry for day-to-day impact metrics."
        )

    return bullets[:3]


def build_executive_summary(
    report: dict[str, Any],
    prior_report: dict[str, Any] | None,
    config: MetricsConfig,
) -> dict[str, Any]:
    targets = config.executive_targets
    checklist = (report.get("onboarding") or {}).get("checklist") or {}
    window_30d = ((report.get("team_benefit") or {}).get("window_30d") or {})

    return {
        "headline": _build_headline(report, checklist, window_30d, targets),
        "key_outcomes": _build_key_outcomes(report, targets),
        "narrative_bullets": _build_narrative_bullets(report, targets),
        "trends": _build_trends(report, prior_report),
        "data_confidence": _data_confidence(report),
        "users": report.get("users") or {},
        "reporting_period": "last 30 days",
        "repo_name": (report.get("repo") or {}).get("name", "unknown"),
    }


def render_executive_markdown(summary: dict[str, Any], generated_at: str) -> str:
    try:
        generated_human = datetime.fromisoformat(
            generated_at.replace("Z", "+00:00")
        ).strftime("%d %b %Y")
    except ValueError:
        generated_human = generated_at[:10]

    lines = [
        f"# Newbie impact summary — {summary.get('repo_name', 'unknown')}",
        "",
        f"Reporting period: {summary.get('reporting_period', 'last 30 days')} · "
        f"Generated {generated_human}",
        "",
        "## Headline",
        "",
        summary.get("headline", ""),
        "",
        "## Key outcomes",
        "",
    ]

    for outcome in summary.get("key_outcomes") or []:
        status = STATUS_LABELS.get(outcome.get("status", "unknown"), outcome.get("status", ""))
        lines.append(
            f"- {outcome.get('label')}: **{outcome.get('value')}** ({status})"
        )

    lines.extend(["", "## What this means", ""])
    for bullet in summary.get("narrative_bullets") or []:
        lines.append(f"- {bullet}")

    lines.extend(["", "## Trend (vs prior report)", ""])
    trends = summary.get("trends") or []
    if trends:
        for trend in trends:
            direction = trend.get("direction", "unknown")
            lines.append(f"- {trend.get('metric')}: **{direction}**")
    else:
        lines.append("- No prior report available for comparison.")

    users = summary.get("users") or {}
    roster = users.get("roster") or []
    if roster:
        lines.extend(["", "## Engineer adoption", ""])
        for entry in roster:
            w30 = entry.get("window_30d") or {}
            intents = w30.get("skill_intents") or {}
            intent_total = sum(intents.values())
            lines.append(
                f"- **{entry.get('display_name', entry.get('user_id'))}**: "
                f"{w30.get('query_runs', 0)} lookups, {intent_total} skill uses (30d)"
            )

    confidence = summary.get("data_confidence") or {}
    lines.extend(
        [
            "",
            f"## Data confidence: {confidence.get('level', 'Unknown')}",
            "",
            confidence.get("note", ""),
            "",
            "---",
            "",
            "Technical detail: see [onboarding-metrics.md](onboarding-metrics.md)",
            "",
        ]
    )
    return "\n".join(lines)
