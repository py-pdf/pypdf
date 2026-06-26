---
name: nb-init
description: Set up Newbie in this repo — thin local or cloud footprint. You run the steps; the engineer does not paste shell commands.
---

# NB init

Set up Newbie in the **current Cursor workspace**. **You (the agent) run every step** via the Shell tool. **Do not** dump a bash checklist on the engineer — execute init, index, and git yourself unless they explicitly ask for commands.

## Choose a mode

| Mode | When | What you run |
|------|------|----------------|
| **Thin (default)** | Desktop-only; plugin serves rules/skills/MCP from `~/.cursor/plugins/` | `nb init` |
| **Cloud** | Cloud Agents, PR metrics CI, or repo must be self-contained | `nb init --cloud` |

If the user mentions Cloud Agents, PR report automation, or a committed footprint → **cloud**.

## Step 1 — Resolve `nb_cli.py` (you only)

Do **not** ask the engineer to find paths. Resolve in order:

1. `scripts/nb_cli.py` in the workspace (after a prior cloud init)
2. `${HOME}/.cursor/plugins/local/newbie/scripts/nb_cli.py`
3. Any path the user gave for a local plugin install

If missing, stop and ask **only** for the Newbie plugin install path — never run a home-directory search.

## Step 2 — Run init (you)

```bash
python3 "<NB_CLI>" init              # thin
python3 "<NB_CLI>" init --cloud      # cloud / Cloud Agents
```

**Cloud materialize must never wipe library config.** The CLI preserves existing `config/libraries.yaml`, `.newbie/libraries.yaml`, or the last git version automatically.

After cloud init, if libraries are configured, the CLI may reindex automatically. If not, continue to Step 3.

## Step 3 — Index libraries (you)

If `config/libraries.yaml` lists libraries (or `.newbie/libraries.yaml` in thin mode):

1. Read and follow **nb-crawl** — **you** run index/reindex, not the user.
2. After cloud init, prefer:
   ```bash
   python3 "<NB_CLI>" index --library <name>    # thin (plugin runtime)
   # or, after cloud materialize:
   python scripts/reindex_all.py                 # from repo root, venv if present
   ```
3. Run doctor; fix failures before declaring done.

If `libraries.yaml` is empty, ask which library to index **once**, then use **nb-crawl** to add and index it.

## Step 4 — Python deps (you, only when indexing)

Create `.venv` and install deps **only if** indexing or MCP needs it and `.venv` is missing:

```bash
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements-mcp.txt
```

(Cloud repos use `requirements-mcp.txt` at root; thin mode uses the plugin bundle path relative to `NB_CLI`.)

## Step 5 — Git (you, when footprint changed)

After **cloud** init or new manifests, **you** stage and commit — do not tell the engineer to run `git add ...`:

- Cloud footprint: `scripts/`, `.cursor/`, `.githooks/`, `config/`, `.github/`, `requirements*.txt`, `store/manifests/*.json`
- Never commit: `.newbie/metrics/`, `repos/`, `store/chunks/`, `.venv/`

Ask before pushing to `origin` unless the user already asked you to push.

## What the engineer does after setup (nothing technical)

1. Keep **Cursor project hooks** enabled.
2. Work normally — **metrics commit on every `git push`** (pre-push hook from init).
3. Open PRs — **metrics-report-pr.yml** (cloud) posts team reports on the PR.

No `sync_metrics` or `report_metrics` commands for day-to-day use.

## Thin vs cloud (reminder)

- **Thin:** `.newbie/` holds local index state; plugin assets stay in `~/.cursor/plugins/`.
- **Cloud:** full footprint in the repo for Cloud Agent VMs; `.cursor/environment.json` rebuilds venv + index on each cloud run.

See `docs/cloud-agents.md` for dashboard MCP/secrets (ops-only — you handle if the user asks).

## Subcommands (for you, not the user)

| Command | Purpose |
|---------|---------|
| `init` | Thin workspace + pre-push metrics hook |
| `init --cloud` | Materialize repo footprint + hooks + optional reindex |
| `install-hooks` | Re-install pre-push hook |
| `index` / `doctor` / `add-library` | Indexing (prefer **nb-crawl** skill) |

## Rules

1. **Never** give the engineer a multi-step terminal script for setup — **run it yourself**.
2. **Never** seed an empty `libraries.yaml` over an existing or recoverable config.
3. After init, **always** offer to index (nb-crawl) if libraries are configured.
4. Match **customer-workspace** for where application code lives — not Newbie infra folders.
