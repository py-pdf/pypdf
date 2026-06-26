"""Fetch GitHub Actions workflow statistics for metrics reports."""

from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any


def _github_repo_slug() -> str | None:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    url = result.stdout.strip()
    if url.endswith(".git"):
        url = url[:-4]
    if "github.com" not in url:
        return None
    parts = url.split("github.com")[-1].strip(":/").split("/")
    if len(parts) >= 2:
        return f"{parts[0]}/{parts[1]}"
    return None


def _fetch_workflow_runs(
    repo: str,
    workflow_name: str,
    *,
    days: int,
    token: str | None,
) -> dict[str, Any] | None:
    if not token:
        return None

    since = datetime.now(timezone.utc) - timedelta(days=days)
    since_iso = since.isoformat().replace("+00:00", "Z")
    url = (
        f"https://api.github.com/repos/{repo}/actions/workflows"
        f"?per_page=100"
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            workflows_payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None

    workflow_id = None
    for workflow in workflows_payload.get("workflows", []):
        if workflow.get("name") == workflow_name or workflow.get("path", "").endswith("ci.yml"):
            workflow_id = workflow.get("id")
            break
    if workflow_id is None:
        return None

    runs_url = (
        f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/runs"
        f"?per_page=100&created=>={since_iso[:10]}"
    )
    try:
        req = urllib.request.Request(runs_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            runs_payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None

    runs = runs_payload.get("workflow_runs", [])
    if not runs:
        return {"workflow_runs": 0, "success_rate": None, "failures": 0}

    successes = sum(1 for run in runs if run.get("conclusion") == "success")
    failures = sum(1 for run in runs if run.get("conclusion") == "failure")
    total = len(runs)
    return {
        "workflow_runs": total,
        "success_rate": round(successes / total, 3) if total else None,
        "failures": failures,
    }


def fetch_ci_stats(workflow_name: str, *, days: int = 30) -> dict[str, Any] | None:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    repo = _github_repo_slug()
    if not repo:
        return None
    return _fetch_workflow_runs(repo, workflow_name, days=days, token=token)
