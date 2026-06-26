# Per-user metrics files

Each engineer who uses Newbie in Cursor gets **one file** in this directory:

```text
reports/users/<user_id>.json
```

`user_id` is a 12-character hash of `git config user.email` — no raw email is committed.

## Automatic sync

After `nb init`, a **pre-push git hook** refreshes your file and commits it whenever
you `git push` — no manual step required. Cursor project hooks must be enabled so
local usage is recorded.

Manual override:

```bash
python scripts/sync_metrics.py --show-id
python scripts/sync_metrics.py --write --push
```

## Manager aliases (optional)

Map hashed IDs to readable names in `config/metrics.yaml`:

```yaml
user_aliases:
  a1b2c3d4e5f6: "Alice"
```

## Privacy

- Raw hook events stay in `.newbie/metrics/events.jsonl` (gitignored)
- Only aggregated snapshots are committed here
- Each engineer commits **only their own file**
