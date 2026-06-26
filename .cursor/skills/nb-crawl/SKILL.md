---
name: nb-crawl
description: >-
  Index open-source libraries for Cursor-native search — clone, tree-sitter chunk,
  write manifests and chunk cache. Use when the user asks to index, refresh, or crawl a library.
disable-model-invocation: true
---

# nb-crawl

Index a configured library into the workspace for **Cursor codebase search** + MCP symbol validation. No vector DB or OpenAI key required.

## Project root

Run all commands from the workspace root that contains `config/libraries.yaml`.

## Prerequisites

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Index a library

```bash
python scripts/index.py --library <name>
```

Options:

- `--reset` — delete and recreate the chunk cache
- `--skip-crawl` — re-chunk an existing checkout

Indexing writes:

- `repos/<name>/` — library source (Cursor indexes this; gitignored locally)
- `store/manifests/<name>.json` — version metadata (**commit to git**)
- `store/manifests/<name>.symbols.json` — public symbol list for CI (**commit to git**)
- `store/chunks/<name>.jsonl` — structured chunk cache for query.py (optional to commit)

## Crawl only

```bash
python scripts/crawl.py --library <name>
```

## Export symbols only

```bash
python scripts/export_symbols.py --library <name>
```

## Verify setup

```bash
python scripts/doctor.py
```

Doctor checks manifests, symbols, source checkout, and chunk cache.

## Add a library

```bash
python scripts/add_library.py --name <name> --repo <url> --ref <tag-or-sha>
python scripts/index.py --library <name>
```

Fill in `config/conventions/<name>.md` after searching deprecations in `repos/<name>/`.

## Checklist

```
- [ ] python scripts/doctor.py passes
- [ ] python scripts/index.py --library <name> completes
- [ ] store/manifests/<name>.json exists
- [ ] store/manifests/<name>.symbols.json exists
- [ ] repos/<name>/ checkout present
- [ ] config/conventions/<name>.md populated
```
