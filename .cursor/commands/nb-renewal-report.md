---
name: nb-renewal-report
description: Generate renewal-defense evidence for ADM — sync metrics, write reports, and summarize for leadership.
---

# NB renewal report

Produce the empirical evidence pack an ADM needs for renewal defense. Raw evidence and capture mechanisms — not an exec slide deck.

## Workflow

1. **Read the nb-report skill** and follow its workflow.

2. **Sync local telemetry** (current engineer):
   ```bash
   python scripts/sync_metrics.py --show-id
   python scripts/sync_metrics.py --write --push
   ```

3. **Regenerate team reports**:
   ```bash
   python scripts/report_metrics.py --write
   ```

4. **Read generated artifacts**:
   - `reports/executive-summary.md` — headline for leadership
   - `reports/onboarding-metrics.md` — eng/PM detail and per-user roster
   - `reports/onboarding-metrics.json` — automation fields

5. **Anchor on three renewal metrics** (pick and defend):

   | Metric | Newbie proxy | Where to cite |
   |--------|---------------|---------------|
   | Time-to-first-meaningful-PR | `onboarding.days_to_first_query`, `first_customer_code` milestones | Per-user roster, git milestones |
   | PR-rejection / rework rate | `symbol_checks.pass_rate`, CI `success_rate` | `team_benefit` window in JSON |
   | Weekly active / provisioned seats | `users.active_30d` vs `users.synced_count` | Executive summary |
   | Senior-engineer interrupt volume | Not auto-tracked — note as gap or capture via champion quotes | Coverage gaps section |
   | Design → deploy cycle time | `deltas_days.to_first_customer_code` | Onboarding milestones |

   State which three you chose and why they fit this account.

6. **Champion narrative**
   - Identify a primary champion candidate (technical believer + org leverage).
   - Pull 1–2 concrete before/after artifacts from the reports (query runs, days to first query, symbol pass rate).

7. **Output format for ADM**

   ```markdown
   ## Renewal defense snapshot

   **Headline:** (one sentence from executive-summary.md)

   **Three metrics:**
   1. ...
   2. ...
   3. ...

   **Champion:** (name/role + evidence)

   **Coverage gaps:** (what we cannot yet measure — action items)

   **Recommended next capture:** (sync cadence, CI token, cloud reindex)
   ```

## Rules

- Do not invent metrics — cite fields from generated reports or run scripts to refresh.
- Call out `coverage_gaps` honestly; treat them as action items, not failures.
- Avoid internal jargon (chunk counts, hook paths) in the ADM-facing summary.
