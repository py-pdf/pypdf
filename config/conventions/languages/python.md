# Python conventions

Customer deliverable layout for Python projects. Library API rules live in `config/conventions/<library>.md`.

## File naming

- Scripts and modules: `snake_case.py`.
- Packages: directory with `__init__.py` when the project already uses packages.

## Module / import style

- Prefer the public package surface shown in library retrieval — not `_`-prefixed internal modules unless retrieval documents an exception.
- Match import style (absolute vs relative) from indexed library chunks and `config/conventions/<library>.md`.
- **Do not copy import grouping by eye from sibling files** — the customer tree may mix styles. Let the customer's formatter decide grouping (see below).

## Linting & formatting (run before declaring done)

Library retrieval grounds API usage, **not** the customer repo's formatter rules. Conform every new/changed `.py` file to the customer's own tooling, or CI lint will fail on correct APIs (the classic case: ruff `I001` import-order).

1. Read the customer's lint/format config under `customer.root` before finalizing: `pyproject.toml` `[tool.ruff]` / `[tool.ruff.lint]` / `[tool.isort]`, or `.ruff.toml`, `ruff.toml`, `setup.cfg`, `tox.ini`.
2. Pay attention to import-grouping config, which determines blank lines between import sections:
   - `[tool.isort] known_third_party` / `known_first_party` move packages between sections. Each section is separated by exactly one blank line; within a section there is none.
   - Example: with `known_third_party = ["pytest"]`, `import pytest` is its own third-party block (blank line after it), while `pypdf` **and** `tests` are both first-party and share one block (**no** blank line between them).
3. Run the customer linter/formatter on the files you wrote, from `customer.root`:

```bash
cd <customer.root> && ruff check --fix <files> && ruff format <files>
```

   (Use the project's configured tools — `ruff`, `isort`, `black`, `flake8` — per its config; don't assume ruff if the repo uses something else.)
4. Fix any remaining errors manually and re-run until clean. Don't declare the task done while the linter reports errors on files you touched.

## Tests

- Directory: root-level `tests/` unless the customer project uses another layout.
- Files: `tests/test_<topic>.py` with a module docstring.
- Framework: **pytest** — plain `def test_*` functions; prefer `@pytest.mark.parametrize` for variants.
- Shared fixtures: `tests/conftest.py` when reused across tests.
- **Test imports:** when the customer repo allows relative imports (e.g. ruff `TID252` ignored), prefer `from . import RESOURCE_ROOT, SAMPLE_ROOT` for the test package's own helpers. isort treats `.` as a separate **local** section (its own blank line), so this avoids the absolute-vs-relative trap where `from tests import ...` is first-party and must **not** have a leading blank line. Match the dominant style of the customer's `tests/` tree, and always confirm with the linter (step above) rather than by eye.

## Infer when workspace.yaml is silent

Under `customer.root`, any of: `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements.txt`, `Pipfile`, dominant `.py` files.

Default test framework: **pytest**.
