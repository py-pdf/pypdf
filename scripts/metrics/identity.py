"""Per-user identity for Newbie metrics (hashed git email).

Identity resolves in this order so cloud agents and CI attribute work to the
triggering engineer rather than a bot identity:

1. ``NB_USER_ID``   — explicit pre-hashed id (set by the cloud agent / CI).
2. ``NB_USER_EMAIL``— raw email to hash (e.g. the PR author).
3. ``git config user.email`` — the local desktop default.

In a Cloud Agent the git identity is the cloud bot, so callers should pass the
triggering engineer via ``NB_USER_EMAIL`` (or a resolved ``NB_USER_ID``).
"""

from __future__ import annotations

import hashlib
import os
import subprocess

from common import PROJECT_ROOT
from metrics.config import MetricsConfig

# Bot identities that should never be treated as a real engineer. When git
# reports one of these and no NB_USER_* override is set, attribute to a stable
# "cloud-bot" bucket instead of polluting a person's onboarding metrics.
_BOT_EMAIL_MARKERS = (
    "[bot]",
    "github-actions",
    "noreply@github.com",
    "cursor-agent",
    "cursor[bot]",
)


def git_user_email() -> str:
    override = os.environ.get("NB_USER_EMAIL")
    if override and override.strip():
        return override.strip().lower()

    result = subprocess.run(
        ["git", "config", "user.email"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    email = result.stdout.strip().lower() if result.returncode == 0 else ""
    return email or "unknown@local"


def is_bot_email(email: str) -> bool:
    lowered = email.lower()
    return any(marker in lowered for marker in _BOT_EMAIL_MARKERS)


def user_id_from_email(email: str) -> str:
    normalized = email.strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]


def current_user_id() -> str:
    explicit = os.environ.get("NB_USER_ID")
    if explicit and explicit.strip():
        return explicit.strip()

    email = git_user_email()
    # No human override and git identity is a cloud/CI bot: bucket separately so
    # automated runs do not get attributed to a real engineer.
    if not os.environ.get("NB_USER_EMAIL") and is_bot_email(email):
        return "cloud-bot"
    return user_id_from_email(email)


def email_domain(email: str) -> str:
    if "@" not in email:
        return "unknown"
    return email.split("@", 1)[1]


def resolve_display_name(user_id: str, config: MetricsConfig) -> str:
    alias = config.user_aliases.get(user_id)
    if alias:
        return alias
    return user_id
