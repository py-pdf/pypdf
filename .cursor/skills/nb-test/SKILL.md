---
name: nb-test
description: >-
  Analyze user code for test gaps, weak assertions, and deprecated APIs by
  querying the Newbie retrieval stack for library usage and edge-case patterns,
  then emit paste-ready tests, a worked example (input + expected output +
  sample run), and a plain-language test plan. Use when the user asks for
  tests, coverage, edge cases, missing tests, weak tests, or a test plan
  for indexed-library code.
disable-model-invocation: true
---

# NB Test

Given a file or function the user points at, analyze test coverage gaps and produce grounded test output plus a QA/PM-friendly summary — in the **customer project's language and test framework**.

## Project root

Run all commands from the workspace root that contains `config/libraries.yaml`.

## Step 0 — Resolve language and test framework

1. Read `config/workspace.yaml` — use `customer.language` and `customer.test_framework` when set.
2. If unset, infer from files under `customer.root` (see `config/conventions/languages/<language>.md`).
3. Read `config/conventions/languages/<language>.md` for test file naming, directory, and framework structure.

Do not default to pytest unless the customer project is Python.

## Step 1 — Understand the target code

Before querying, extract from the file or function the user indicated:

1. **Language** — from file extension and workspace config
2. **Library** — infer from imports; confirm against `config/libraries.yaml`
3. **Intent** — what the code does in plain language
4. **APIs used** — classes, functions, modules, kwargs, and control flow
5. **Branches** — conditionals, loops, early returns, exception paths, empty-input cases
6. **Existing tests** — if the user pointed at a test file or nearby tests, note weak assertions there too

If the library is unclear, ask. Do not guess across multiple libraries.

Read `config/conventions/<library>.md` for deprecated APIs. Read `config/conventions/languages/<language>.md` for test file layout before emitting tests.

## Step 2 — Check index scope for tests

Read `config/libraries.yaml` for the library's `exclude` globs. If `**/tests/**` is excluded (common default), upstream test-suite code is **not** in `repos/<library>/` scope — say so explicitly. Do not claim to have retrieved upstream test patterns when they were never indexed.

## Step 3 — Retrieve library patterns

Run targeted queries the same way **nb-generate** and **nb-validate** do. Build prompts from intent + APIs + behaviors to exercise.

**Similar usage and edge cases** (primary grounding for what to assert):

```bash
python scripts/query.py --library <name> --prompt "<intent, APIs, edge cases, error paths>"
```

Use `--top-k 10` for non-trivial code. Add `--json` when you need structured metadata (`is_public`, `symbol`, `kind`).

**Deprecation markers** (required when the target code or proposed tests touch library APIs):

```bash
python scripts/query.py --library <name> --prompt "deprecated removed replacement do not use"
```

Also read `store/manifests/<library>.json` for indexed version (`ref`, `commit`) and cross-check `config/conventions/<library>.md` deprecated-API tables.

**Optional — upstream test patterns** (only when tests are included in index globs):

```bash
python scripts/query.py --library <name> --prompt "test assert parametrize fixture <APIs and scenarios>"
```

If this returns no test-like chunks (expected when `**/tests/**` is excluded), state that clearly. Ground test **behavior and assertions** only in retrieved non-test source patterns (docstrings, examples, error messages, parameter validation). Do not invent library-specific test helpers or assertion idioms from general knowledge.

## Step 4 — Analyze coverage and assertion quality

| Check | What to look for |
|-------|------------------|
| **Untested branches** | Each `if`/`elif`/`else`, loop exit, guard clause, and `raise`/throw without a corresponding scenario |
| **Edge cases** | Empty inputs, single-item inputs, boundary values, malformed data, missing files, wrong types — only when retrieval or the target code implies they matter |
| **Weak assertions** | Truthiness-only checks, bare `not None`, equality with no message, no check on exceptions or side effects |
| **Deprecated APIs** | Symbols flagged in retrieval (`@deprecate`, `deprecation_with_replacement`) or in conventions files — flag if the target code tests against them |
| **Public API** | Prefer testing through public symbols shown in retrieval; flag reliance on `_`-prefixed internals |

When retrieval is thin for a behavior you need to test, list it under **Gaps** — do not fill with invented APIs or generic library patterns.

## Step 5 — Emit three outputs

Always produce **all three** sections below. Do not mark the task complete until each is present.

### A. Paste-ready test block

Follow test layout from `config/conventions/languages/<language>.md` (file path, naming, framework structure).

Rules for generated tests:

1. Use **only** library APIs and idioms shown in retrieved chunks
2. Match **import style** from retrieval and library conventions
3. Prefer **specific assertions** grounded in retrieved behavior (expected values, exception types/messages, property shapes)
4. Never test against deprecated APIs — use replacements from retrieval or conventions
5. If you cannot ground a test case in retrieval, omit it and list it under **Gaps** instead of guessing
6. **Conform imports/format to the customer's linter, not retrieval.** The index excludes `**/tests/**`, so canonical test import blocks are not retrievable — do not copy grouping by eye from sibling tests. Follow the customer's `pyproject.toml` `[tool.ruff]` / `[tool.isort]` rules (see `config/conventions/languages/<language>.md` → Linting & formatting). When you run the block in `customer.root`, also run the linter (e.g. `ruff check --fix`) so the paste-ready block is `I001`-clean.

Use the appropriate fenced code block language tag (`python`, `typescript`, `go`, etc.) and structure for the resolved test framework (pytest, vitest/jest, go test, etc.).

Place the block where the engineer can paste it into the customer project's test tree under `customer.root`.

### B. Worked example — input and output

Show **at least one** representative test case as a concrete before/after so the reader can see what "passing" looks like. Use real or minimal fixture data — not placeholders like `...` or `TODO`.

Include:

1. **Input** — the exact arguments, fixture files, or setup state the test uses (inline values, `@pytest.mark.parametrize` rows, table-driven cases, etc.)
2. **Expected output** — what a passing run asserts or returns (return value, raised exception type/message, file bytes, side effect)
3. **Run command** — how to execute that test in the customer project (e.g. `pytest tests/test_merge_pdfs.py::test_empty_input -v`)
4. **Sample terminal output** — a short fenced block showing successful run output (pass line, assertion detail, or `--tb=short` on failure when demonstrating an edge case)

When you can run the test block in the customer project without destructive side effects, **run it** and paste actual output. When you cannot run (missing fixtures, uncommitted code, wrong environment), construct the example from retrieved behavior and label it **Expected output (not run)**.

Keep examples scoped to one happy path and one meaningful edge or error path when both are grounded in retrieval.

### C. Test plan summary

Plain language for QA or PM — **3–5 bullets**:

```markdown
## Test plan summary

- **Covered:** <scenarios the test block exercises>
- **Not covered:** <branches or edge cases with no grounded test yet>
- **Risky:** <behaviors that depend on thin retrieval or complex I/O>
- **Weak assertions flagged:** <existing or proposed asserts that need strengthening>
- **Deprecated APIs flagged:** <symbols to stop testing against, with replacement if known from retrieval>
```

Adjust bullets to what applies; keep total to 3–5 items.

## Full report template

```markdown
## Test analysis: `<library>` — `<file or function>`

**Language:** <resolved language>
**Test framework:** <resolved framework>
**Intent:** <one-line summary>
**Index:** <ref @ commit from manifest>
**Upstream tests in index:** yes | no (see `config/libraries.yaml` exclude globs)

### Coverage gaps
- <branch or edge case> — <why it matters>

### Weak assertions
- <location or proposed test> — <what is weak and preferred check>

### Deprecated APIs
- <symbol> — <replacement from retrieval or conventions, or "blocked">

### Reference patterns used
- `<symbol>` (<kind>) — <why it grounded a test or gap>

### Gaps
- <behavior not covered by retrieval; suggest narrower query or re-index via nb-crawl>

---

## Test block

<paste-ready code in customer language/framework>

---

## Worked example

**Input:** <concrete args, fixtures, or setup>

**Expected output:** <assertions, return values, exceptions>

```bash
<run command>
```

```
<sample passing terminal output, or "Expected output (not run)" with realistic pytest/vitest/go test lines>
```

---

## Test plan summary

<3–5 bullets>
```

## Rules

1. **Vector-grounded only** — library API claims and test scenarios must come from retrieved chunks or conventions deprecation tables; no hallucinated methods
2. **No fake upstream tests** — if tests are excluded from the index, do not imply you read the library's test suite
3. **No generic filler** — when retrieval is empty for a scenario, report the gap; do not paste boilerplate truthiness-only tests
4. **Language conventions for layout** — file paths, naming, and test structure come from `config/conventions/languages/<language>.md`; behavior comes from retrieval
5. **Show tests working** — every report includes at least one worked example with concrete input, expected output, run command, and sample terminal output (actual run preferred)
6. **Do not edit user code** unless they explicitly ask — default is analysis + paste-ready tests
7. If multiple skills apply (e.g. user also wants API correctness), run **nb-test** for tests; use **nb-validate** separately for code review

## Example

User: "Write tests for `merge_pdfs` in `merge_pdfs.py`" — library resolves to `pypdf`, language resolves to `python`.

```bash
python scripts/query.py --library pypdf --prompt "merge PDFs PdfReader PdfWriter add_page empty file error"
python scripts/query.py --library pypdf --prompt "deprecated removed replacement do not use PdfFileReader"
```

Analyze branches in `merge_pdfs`, note that upstream tests are not indexed, ground assertions in retrieved merge/page patterns, emit `tests/test_merge_pdfs.py` block plus test plan summary. Read `config/conventions/pypdf.md` for deprecations; read `config/conventions/languages/python.md` for layout.

**Worked example** (illustrative shape — ground values in retrieval):

**Input:** two minimal single-page PDF fixtures (`tests/fixtures/a.pdf`, `tests/fixtures/b.pdf`); call `merge_pdfs([a, b])`.

**Expected output:** return value is bytes; merged PDF has `len(PdfReader(BytesIO(result)).pages) == 2`.

```bash
pytest tests/test_merge_pdfs.py::test_merge_two_pdfs -v
```

```
tests/test_merge_pdfs.py::test_merge_two_pdfs PASSED                     [100%]

============================== 1 passed in 0.04s ==============================
```

If fixtures are not present yet, show the same structure with **Expected output (not run)** and note which fixture files the test block expects.

## If query fails

```bash
python scripts/doctor.py
python scripts/index.py --library <name>
```

## Supported libraries

See `config/libraries.yaml`. Add new libraries with `python scripts/add_library.py`.
