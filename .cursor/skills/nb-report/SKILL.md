---
name: nb-report
description: >-
  Generate Newbie onboarding and team-benefit metrics: sync per-user Cursor usage,
  build team reports, and produce executive summaries. Use when the user asks for
  onboarding metrics, usage reporting, executive summary, per-engineer stats,
  sync metrics, or mentions nb-report.
disable-model-invocation: true
---

# NB Report

Measure onboarding speed and ongoing team benefit from the Newbie workspace. Produces committed reports under `reports/` and per-engineer files under `reports/users/`.

## Project root

Run all commands from the workspace root that contains `config/libraries.yaml`.

## Prerequisites

1. **Cursor project hooks** enabled (`.cursor/hooks.json` ships with the scaffold).
2. **`git user.email`** set to the engineer's work email (used for hashed `user_id`).
3. Optional: copy and edit metrics config:

```bash
cp config/metrics.yaml.example config/metrics.yaml
```

## Workflow overview

| Step | Who | Command |
|------|-----|---------|
| 1. Sync personal usage | Each engineer | `python scripts/sync_metrics.py --write --push` |
| 2. Regenerate team reports | Any lead / CI | `python scripts/report_metrics.py --write` |

Hooks log activity to `.nb/metrics/events.jsonl` (gitignored). Sync commits **only** `reports/users/<user_id>.json`. Team reports aggregate all synced user files.

## Step 1 — Per-user sync (each engineer)

Show hashed identity (for optional aliases in `config/metrics.yaml`):

```bash
python scripts/sync_metrics.py --show-id
```

Sync local hook events to the repo:

```bash
python scripts/sync_metrics.py --write --push
```

Re-run after significant Cursor usage or weekly. Engineers who never sync do **not** appear in team rosters — coverage gaps call this out.

Optional display names (manager-maintained, in `config/metrics.yaml`):

```yaml
user_aliases:
  a1b2c3d4e5f6: "Alice"
```

## Step 2 — Team report generation

```bash
python scripts/report_metrics.py --write
```

Preview JSON without writing:

```bash
python scripts/report_metrics.py --json
```

Writes:

| File | Audience |
|------|----------|
| `reports/executive-summary.md` | C-level — headline, outcomes, trends, engineer adoption |
| `reports/onboarding-metrics.md` | Eng / PM — milestones, checklist, per-user roster table |
| `reports/onboarding-metrics.json` | Automation — `schema_version: 2`, includes `users` and `executive_summary` |

Weekly refresh: GitHub Actions workflow **Metrics report** (`.github/workflows/metrics-report.yml`).

## Step 3 — Present findings (match audience)

Read the generated files; do not dump raw JSON unless the user asks.

### C-level / stakeholders

Start with `reports/executive-summary.md`. Summarize:

- Headline verdict
- Active engineers (30d) vs synced count
- Time to first indexed library (repo-wide)
- Data confidence level and what it means

Avoid: chunk counts, internal field names, git SHAs, hook file paths.

### PM / eng leads

Use `reports/onboarding-metrics.md` plus the **Per-user roster (30d)** table. Highlight:

- Checklist completion
- Coverage gaps (missing syncs, CI stats)
- Per-engineer query runs and days to first query

### Engineer (self)

Run sync, then point them at their row in the roster or `reports/users/<user_id>.json`.

## Report interpretation

| Metric | Meaning |
|--------|---------|
| `users.synced_count` | Engineers who ran `sync_metrics.py --push` |
| `users.active_30d` | Synced engineers with query/skill/session activity in last 30 days |
| `deltas_days.to_first_index` | Repo-wide days from scaffold adoption to first library index |
| `onboarding.days_to_first_query` (per user) | Days from repo scaffold adoption to that engineer's first successful `query.py` |
| `team_benefit.window_30d.query_runs` | Sum of grounded API lookups across synced users |
| `coverage_gaps` | Known blind spots — treat as action items, not errors |

Full glossary: [reports/README.md](../../../reports/README.md).

## Troubleshooting

| Symptom | Action |
|---------|--------|
| Zero query runs / empty roster | Confirm hooks enabled; run `sync_metrics.py --write --push` |
| User not in team report | That engineer has not pushed their user file |
| CI stats `n/a` in CI workflow | Expected without `GITHUB_TOKEN`; available in scheduled workflow |
| Wrong name in roster | Add `user_aliases` in `config/metrics.yaml` after `--show-id` |

```bash
python scripts/doctor.py   # unrelated to metrics but confirms index health
```

## Rules

1. **Do not commit** `.nb/metrics/events.jsonl` — only synced user files and team reports belong in git.
2. **Do not invent metrics** — cite fields from generated reports or run the scripts to refresh.
3. **Per-user sync before team rollup** — team totals come from `reports/users/*.json`, not one laptop's local events alone.
4. **Privacy** — committed files use hashed `user_id` only; no raw emails in reports.
5. When the user asks to commit reports, sync user file first (if they are an individual contributor), then run `report_metrics.py --write`.

## Example prompts

- "Use nb-report to sync my metrics and regenerate the executive summary"
- "How many engineers are active on Newbie this month?"
- "Show me the onboarding metrics report for leadership"

## Related docs

- [docs/customer-onboarding.md](../../../docs/customer-onboarding.md) — Measuring onboarding section
- [reports/users/README.md](../../../reports/users/README.md) — one file per engineer
