"""Metrics event and report schema constants."""

from __future__ import annotations

REPORT_SCHEMA_VERSION = 2
USER_SNAPSHOT_SCHEMA_VERSION = 1

EVENT_SCRIPT_RUN = "script_run"
EVENT_SKILL_INTENT = "skill_intent"
EVENT_SESSION_END = "session_end"
EVENT_SESSION_START = "session_start"

TRACKED_SCRIPTS = frozenset(
    {
        "query.py",
        "doctor.py",
        "index.py",
        "verify_symbols.py",
        "check_manifests.py",
        "init_customer.py",
    }
)

SKILL_KEYWORDS: dict[str, str] = {
    "nb-generate": "nb-generate",
    "nb-validate": "nb-validate",
    "nb-test": "nb-test",
    "nb-crawl": "nb-crawl",
    "nb-report": "nb-report",
    "nb generate": "nb-generate",
    "nb validate": "nb-validate",
    "nb test": "nb-test",
    "nb crawl": "nb-crawl",
    "nb report": "nb-report",
}

MILESTONE_KEYS = (
    "scaffold_adopted",
    "first_library_configured",
    "first_index",
    "first_convention_doc",
    "first_customer_code",
    "first_doctor_pass",
    "first_query",
)
