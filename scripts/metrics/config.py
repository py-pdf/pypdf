"""Load metrics configuration with sensible defaults."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from common import CONFIG_DIR, PROJECT_ROOT

METRICS_CONFIG_PATH = CONFIG_DIR / "metrics.yaml"
METRICS_EXAMPLE_PATH = CONFIG_DIR / "metrics.yaml.example"
WORKSPACE_CONFIG_PATH = CONFIG_DIR / "workspace.yaml"


@dataclass
class ExecutiveTargets:
    days_to_first_index: int = 7
    symbol_pass_rate_30d: float = 0.90
    ci_success_rate_30d: float = 0.95


@dataclass
class MetricsConfig:
    redact_prompts: bool = True
    log_command_args: str = "minimal"
    event_retention_days: int = 365
    customer_root: Path | None = None
    default_branch: str = "main"
    ci_workflow_name: str = "CI"
    executive_targets: ExecutiveTargets = field(default_factory=ExecutiveTargets)
    user_aliases: dict[str, str] = field(default_factory=dict)


def _load_executive_targets(data: dict[str, Any]) -> ExecutiveTargets:
    executive = data.get("executive") or {}
    targets = executive.get("targets") or {}
    return ExecutiveTargets(
        days_to_first_index=int(targets.get("days_to_first_index", 7)),
        symbol_pass_rate_30d=float(targets.get("symbol_pass_rate_30d", 0.90)),
        ci_success_rate_30d=float(targets.get("ci_success_rate_30d", 0.95)),
    )


def _resolve_customer_root(raw: str | None) -> Path | None:
    if not raw:
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = (PROJECT_ROOT / path).resolve()
    return path


def load_metrics_config() -> MetricsConfig:
    data: dict[str, Any] = {}
    config_path = METRICS_CONFIG_PATH if METRICS_CONFIG_PATH.exists() else None
    if config_path:
        with config_path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

    customer_root = _resolve_customer_root(data.get("customer_root"))
    if customer_root is None and WORKSPACE_CONFIG_PATH.exists():
        with WORKSPACE_CONFIG_PATH.open(encoding="utf-8") as handle:
            workspace = yaml.safe_load(handle) or {}
        customer_root = _resolve_customer_root((workspace.get("customer") or {}).get("root"))

    # Single-repo install: customer code lives in this repo. workspace.yaml is an
    # optional override for the legacy multi-root layout, so default to repo root.
    if customer_root is None:
        customer_root = PROJECT_ROOT

    return MetricsConfig(
        redact_prompts=bool(data.get("redact_prompts", True)),
        log_command_args=str(data.get("log_command_args", "minimal")),
        event_retention_days=int(data.get("event_retention_days", 365)),
        customer_root=customer_root,
        default_branch=str(data.get("default_branch", "main")),
        ci_workflow_name=str(data.get("ci_workflow_name", "CI")),
        executive_targets=_load_executive_targets(data),
        user_aliases={str(k): str(v) for k, v in (data.get("user_aliases") or {}).items()},
    )
