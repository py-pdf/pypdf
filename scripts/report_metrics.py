#!/usr/bin/env python3
"""Aggregate Newbie onboarding and team-benefit metrics into committed reports."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import PROJECT_ROOT, REPORTS_DIR  # noqa: E402
from metrics.aggregate import build_report, render_markdown  # noqa: E402
from metrics.config import load_metrics_config  # noqa: E402
from metrics.executive import build_executive_summary, render_executive_markdown  # noqa: E402

JSON_PATH = REPORTS_DIR / "onboarding-metrics.json"
MD_PATH = REPORTS_DIR / "onboarding-metrics.md"
EXECUTIVE_PATH = REPORTS_DIR / "executive-summary.md"


def _load_prior_report() -> dict | None:
    if not JSON_PATH.exists():
        return None
    try:
        return json.loads(JSON_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Newbie onboarding metrics reports.")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write reports/onboarding-metrics.json, .md, and executive-summary.md",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print report JSON to stdout",
    )
    args = parser.parse_args()

    config = load_metrics_config()
    prior_report = _load_prior_report()
    report = build_report(config)
    executive = build_executive_summary(report, prior_report, config)
    report["executive_summary"] = executive

    if args.write:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        JSON_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        MD_PATH.write_text(render_markdown(report), encoding="utf-8")
        EXECUTIVE_PATH.write_text(
            render_executive_markdown(executive, report.get("generated_at", "")),
            encoding="utf-8",
        )
        print(f"Wrote {JSON_PATH.relative_to(PROJECT_ROOT)}")
        print(f"Wrote {MD_PATH.relative_to(PROJECT_ROOT)}")
        print(f"Wrote {EXECUTIVE_PATH.relative_to(PROJECT_ROOT)}")

    if args.json or not args.write:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
