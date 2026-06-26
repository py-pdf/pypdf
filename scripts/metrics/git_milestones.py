"""Extract onboarding milestones from git history."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common import (
    CONFIG_DIR,
    CONFIG_PATH,
    CONVENTIONS_DIR,
    MANIFESTS_DIR,
    PROJECT_ROOT,
    load_libraries_config,
)
from metrics.config import MetricsConfig


@dataclass
class Milestone:
    date: str
    commit: str

    def to_dict(self) -> dict[str, str]:
        return {"date": self.date, "commit": self.commit}


def _run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _first_commit_for_path(path_glob: str) -> Milestone | None:
    output = _run_git(
        "log",
        "--diff-filter=A",
        "--format=%H|%aI",
        "--reverse",
        "--",
        path_glob,
    )
    if not output:
        return None
    first_line = output.splitlines()[0]
    commit, date = first_line.split("|", 1)
    return Milestone(date=date, commit=commit[:12])


def _first_commit_touching_paths(paths: list[str]) -> Milestone | None:
    earliest: Milestone | None = None
    for path in paths:
        milestone = _first_commit_for_path(path)
        if milestone and (earliest is None or milestone.date < earliest.date):
            earliest = milestone
    return earliest


def _first_manifest_index() -> Milestone | None:
    if not MANIFESTS_DIR.exists():
        return None
    manifests = sorted(
        path
        for path in MANIFESTS_DIR.glob("*.json")
        if not path.name.endswith(".symbols.json")
    )
    if not manifests:
        return None
    earliest: Milestone | None = None
    for manifest in manifests:
        milestone = _first_commit_for_path(str(manifest.relative_to(PROJECT_ROOT)))
        if milestone is None:
            continue
        if earliest is None or milestone.date < earliest.date:
            earliest = milestone
    return earliest


def _convention_has_substance(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    stripped = re.sub(r"\s+", " ", text).strip()
    if len(stripped) < 200:
        return False
    placeholder_markers = ("TODO", "TBD", "_template")
    lower = stripped.lower()
    return not any(marker.lower() in lower for marker in placeholder_markers)


def _first_convention_doc() -> Milestone | None:
    conventions_dir = CONVENTIONS_DIR
    if not conventions_dir.exists():
        return None
    earliest: Milestone | None = None
    for path in sorted(conventions_dir.glob("*.md")):
        if path.name in ("_template.md",):
            continue
        if not _convention_has_substance(path):
            continue
        milestone = _first_commit_for_path(str(path.relative_to(PROJECT_ROOT)))
        if milestone is None:
            continue
        if earliest is None or milestone.date < earliest.date:
            earliest = milestone
    return earliest


def _customer_roots(config: MetricsConfig) -> list[Path]:
    roots: list[Path] = []
    if config.customer_root and config.customer_root.exists():
        roots.append(config.customer_root)
    else:
        for candidate in ("../customer-app", "../customer_pypdf", "customer"):
            path = (PROJECT_ROOT / candidate).resolve()
            if path.exists() and path.is_dir():
                roots.append(path)
    return roots


def _first_customer_code(config: MetricsConfig) -> Milestone | None:
    roots = _customer_roots(config)
    earliest: Milestone | None = None
    for root in roots:
        try:
            rel = root.relative_to(PROJECT_ROOT)
            milestone = _first_commit_for_path(str(rel))
        except ValueError:
            continue
        if milestone and (earliest is None or milestone.date < earliest.date):
            earliest = milestone
    return earliest


def _first_library_configured() -> Milestone | None:
    milestone = _first_commit_for_path(str(CONFIG_PATH.relative_to(PROJECT_ROOT)))
    if milestone is None:
        return None
    libraries = load_libraries_config()
    if not libraries:
        return None
    return milestone


def _days_between(start: str, end: str) -> int | None:
    try:
        start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)
        return max(0, (end_dt - start_dt).days)
    except ValueError:
        return None


def extract_milestones(config: MetricsConfig) -> dict[str, Any]:
    milestones: dict[str, Milestone | None] = {
        "scaffold_adopted": _first_commit_touching_paths(
            [
                ".cursor/skills",
                "config/libraries.yaml",
            ]
        ),
        "first_library_configured": _first_library_configured(),
        "first_index": _first_manifest_index(),
        "first_convention_doc": _first_convention_doc(),
        "first_customer_code": _first_customer_code(config),
        "first_doctor_pass": None,
        "first_query": None,
    }

    serialized = {
        key: milestone.to_dict() if milestone else None for key, milestone in milestones.items()
    }

    anchor = serialized.get("scaffold_adopted") or serialized.get("first_library_configured")
    deltas: dict[str, int | None] = {}
    if anchor:
        anchor_date = anchor["date"]
        for target_key, delta_key in (
            ("first_index", "to_first_index"),
            ("first_customer_code", "to_first_customer_code"),
            ("first_doctor_pass", "to_first_doctor_pass"),
            ("first_query", "to_first_query"),
        ):
            target = serialized.get(target_key)
            if target:
                deltas[delta_key] = _days_between(anchor_date, target["date"])
            else:
                deltas[delta_key] = None

    return {"milestones": serialized, "deltas_days": deltas}


def build_checklist(config: MetricsConfig) -> dict[str, bool]:
    libraries = load_libraries_config()
    conventions_dir = CONVENTIONS_DIR
    ci_workflow = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
    metrics_workflow = PROJECT_ROOT / ".github" / "workflows" / "metrics-report.yml"
    workspace_config = CONFIG_DIR / "workspace.yaml"

    manifests_ok = bool(libraries) and all(
        (MANIFESTS_DIR / f"{lib.name}.json").exists()
        and (MANIFESTS_DIR / f"{lib.name}.symbols.json").exists()
        for lib in libraries
    )

    conventions_filled = bool(libraries) and all(
        _convention_has_substance(conventions_dir / f"{lib.name}.md") for lib in libraries
    )

    return {
        "libraries_configured": bool(libraries),
        "manifests_committed": manifests_ok,
        "conventions_filled": conventions_filled,
        "ci_configured": ci_workflow.exists(),
        "metrics_workflow_configured": metrics_workflow.exists(),
        "workspace_configured": workspace_config.exists(),
        "customer_root_resolved": config.customer_root is not None
        and config.customer_root.exists(),
    }


def repo_info(config: MetricsConfig) -> dict[str, str]:
    name = _run_git("rev-parse", "--show-toplevel")
    repo_name = Path(name).name if name else PROJECT_ROOT.name
    branch = _run_git("rev-parse", "--abbrev-ref", "HEAD") or config.default_branch
    return {"name": repo_name, "default_branch": config.default_branch, "current_branch": branch}


def first_customer_code_for_user(email: str, config: MetricsConfig) -> Milestone | None:
    """First commit under customer.root authored by the given git email."""
    earliest: Milestone | None = None
    for root in _customer_roots(config):
        try:
            rel = root.relative_to(PROJECT_ROOT)
            path = str(rel)
        except ValueError:
            continue
        output = _run_git(
            "log",
            f"--author={email}",
            "--diff-filter=ACMR",
            "--format=%H|%aI",
            "--reverse",
            "--",
            path,
        )
        if not output:
            continue
        first_line = output.splitlines()[0]
        commit, date = first_line.split("|", 1)
        milestone = Milestone(date=date, commit=commit[:12])
        if earliest is None or milestone.date < earliest.date:
            earliest = milestone
    return earliest
