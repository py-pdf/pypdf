---
name: nb-validate
description: >-
  Review user-written customer code against an indexed library's constructs by
  querying the Newbie retrieval stack and comparing code to retrieved patterns.
  Use when the user wrote code themselves and wants it checked, validated,
  or reviewed for library standards, idioms, or API correctness.
disable-model-invocation: true
---

# NB Validate

Review user-written code against an indexed library's APIs and idioms. **Do not rewrite the code unless the user asks** — report findings and let them fix it.

Works for customer code in any language; library API checks are language-agnostic.

## Project root

Run all commands from the workspace root that contains `config/libraries.yaml`.

## Step 1 — Understand the user's code

Before querying, extract from the code they wrote:

1. **Language** — from file extension and `config/workspace.yaml` / `customer.root`; read `config/conventions/languages/<language>.md` for layout expectations
2. **Library** — infer from imports; confirm against `config/libraries.yaml`
3. **Intent** — what the code is trying to do in plain language
4. **APIs used** — classes, functions, modules, and patterns referenced

If the library is unclear, ask. Do not guess across multiple libraries.

Read `config/conventions/<library>.md` when present for import style and deprecated APIs.

## Step 2 — Retrieve reference patterns

Build a search from intent + APIs used:

1. **Cursor Codebase Search** over `repos/<library>/`
2. **nb-symbols MCP** — `search_library_code(library, "<intent and APIs>")`
3. **Optional CLI**:
   ```bash
   python scripts/query.py --library <name> --prompt "<intent and APIs used>"
   ```

## Step 3 — Compare and review

Check the user's code against retrieved patterns:

| Check | What to look for |
|-------|------------------|
| **API existence** | Every method/class/module used appears in retrieved patterns |
| **Import style** | Imports match library conventions (module paths, public vs internal) |
| **Object model** | Correct reader/writer/context-manager usage, construction, lifecycle |
| **Idioms** | Error handling, iteration, and composition match library examples |
| **Public API** | Prefer public symbols; flag reliance on `_`-prefixed internals |
| **Invented APIs** | Flag methods, kwargs, or modules not present in retrieved patterns |
| **Deprecated APIs** | Cross-check `config/conventions/<library>.md` deprecation tables |
| **Language layout** | File naming and module structure match `config/conventions/languages/<language>.md` |
| **Formatter / linter config** | Whether the customer repo's own linter (ruff/isort/eslint/etc.) passes on the file — separate from library API checks (see below) |

**Library import *paths* vs project formatter *rules* are different concerns:**

- *Library import paths* (this skill's grounding): which symbols/modules are imported, public vs internal — checked against retrieved chunks.
- *Project formatter rules* (the customer repo's config): import **grouping/ordering**, blank lines between sections, quote style, line length — defined by `pyproject.toml` `[tool.ruff]` / `[tool.isort]`, `.eslintrc`, etc. Retrieval does **not** cover these. Index excludes `**/tests/**` (see `config/libraries.yaml`), so canonical test import blocks are not retrievable — do not infer grouping from grepping the customer tree, which often mixes styles.

If the customer repo has a linter configured but you cannot confirm it was run on the code, raise a 🟡 suggestion: run it (e.g. `cd <customer.root> && ruff check <file>`) before merging, since CI will. When practical, run it yourself and report the result.

When retrieval is thin for a symbol the user uses, say so — do not assume the API exists.

## Step 4 — Report findings

Use this format:

```markdown
## Validation: `<library>`

**Language:** <resolved language>
**Intent:** <one-line summary of what the code does>

### Passes
- <what matches library patterns>

### Issues
- 🔴 **Critical** — <must fix: wrong API, invented method, broken pattern>
- 🟡 **Suggestion** — <idiom or style improvement backed by retrieved pattern>
- 🟢 **Note** — <optional: public API alternative, readability>

### Reference patterns used
- `<symbol>` (<kind>) — <why it was relevant>

### Gaps
- <APIs or behaviors not covered by retrieval; suggest re-index or narrower query>
```

Cite retrieved patterns when flagging an issue (symbol name, module, or brief excerpt).

## Rules

1. **Review only** — do not edit or regenerate the user's code unless they explicitly ask
2. Ground every API claim in retrieved chunks — no hallucinated library methods
3. Prefer public symbols from retrieval over internal helpers
4. If the code is correct but non-idiomatic, mark it as 🟡 with the preferred pattern
5. If validation cannot proceed (missing index, wrong library), say why and point to `nb-crawl`

## Example

User pastes code that merges PDFs; imports resolve to `pypdf`.

```bash
python scripts/query.py --library pypdf --prompt "merge PDFs PdfReader PdfWriter add_page"
```

Compare imports, reader/writer usage, and page loop against retrieved chunks. Cross-check `config/conventions/pypdf.md`.

## If query fails

```bash
python scripts/doctor.py
python scripts/index.py --library <name>
```

## Supported libraries

See `config/libraries.yaml`. Add new libraries with `python scripts/add_library.py`.
