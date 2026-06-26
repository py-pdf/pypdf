---
name: nb-generate
description: >-
  Generate customer code in the project's language that matches an indexed
  library's constructs using Cursor codebase search, MCP, and retrieved patterns.
  Use when the user wants library-style code or mentions Newbie generation or retrieval.
disable-model-invocation: true
---

# NB Generate

Retrieve library patterns using **Cursor-native search**, then generate code that matches the library's APIs and idioms in the **customer project's language**.

## Project root

Run all commands from the workspace root that contains `config/libraries.yaml`.

## Step 0 — Resolve the library

1. Infer the target library from the user's request or imports.
2. Confirm it exists in `config/libraries.yaml`.
3. Confirm `store/manifests/<library>.json` exists (indexed).
4. If `config/conventions/<library>.md` exists, read it before generating.

If the library is unclear, ask. Do not default to a specific library.

## Step 0b — Resolve the language

1. Infer the language from the repo by default. `config/workspace.yaml` is optional — use `customer.language` only as an override when set.
2. Read `config/conventions/languages/<language>.md` for file naming, module/import style, and test layout.
3. If language is still unclear, match existing files in the repo or ask.

## Step 1 — Retrieve patterns (Cursor-native)

Use **all** of these, in order:

1. **Cursor Codebase Search** scoped to `repos/<library>/` for the user's intent and API names.
2. **nb-symbols MCP** — call `search_library_code(library, query)` and `lookup_symbol` for symbols you plan to use.
3. **Optional CLI helper** (for metrics/hooks):
   ```bash
   python scripts/query.py --library <name> --prompt "<user request>"
   ```

Read matching source files directly with the Read tool when search surfaces a path.

## Step 2 — Generate code

Use retrieved source as grounding context:

1. Use **only** APIs shown in retrieved source — do not invent methods or modules
2. Match **import style**, object model, and error-handling patterns from the library
3. Prefer **public** symbols from `store/manifests/<library>.symbols.json`
4. If retrieval is thin, say what is missing and suggest re-indexing or a narrower search
5. Apply rules from `config/conventions/<library>.md` and `config/conventions/languages/<language>.md`
6. Place deliverables in the repo's existing layout (discover it — don't assume `scripts/`), not in Newbie infrastructure folders. See the **customer-workspace** rule.

## Step 3 — Lint & format to the customer's config

Before declaring code done, run the customer's linter/formatter on files you touched (see `config/conventions/languages/<language>.md`).

## Example

User: "Merge two PDFs using pypdf"

1. Codebase search: `repos/pypdf/` for `PdfReader`, `PdfWriter`, merge
2. MCP: `search_library_code("pypdf", "merge two PDFs PdfReader PdfWriter")`
3. Read `config/conventions/pypdf.md` for import and deprecation rules
4. Discover where the repo keeps entrypoints/modules and generate there
5. Lint with customer ruff/eslint config

## If retrieval fails

```bash
python scripts/doctor.py
python scripts/index.py --library <name>
```

## Supported libraries

See `config/libraries.yaml`. Add new libraries with `python scripts/add_library.py`.
