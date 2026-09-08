# pypdf

pure-python PDF library; only-optional dependencies (cryptography, Pillow); Python 3.9+.

## Setup

```bash
pip install -r requirements/dev.txt
pip install -r requirements/ci.txt   # use ci-3.11.txt on Python >= 3.11
pre-commit install
git submodule update --init          # only for `samples`-marked tests
```

## Commands

Test: `pytest`
Lint: `ruff check .`
Types: `mypy .`
Format: `pre-commit run --all-files`
Single test: `pytest tests/test_writer.py::test_writer_exception_non_binary`


## Project layout

pypdf/              Library source
pypdf/_page.py      Contains PageObject, a core class representing a single page in a PDF document.
pypdf/_writer.py      Contains PdfWriter, a core class for creating and modifying PDF documents.
pypdf/_reader.py      Contains PdfReader, a core class for reading and extracting information from PDF documents.
tests/              `pytest` suite
resources/          Small curated test PDFs
sample-files/       Git submodule for large/edge-case PDFs.
docs/               Sphinx docs; `docs/dev/` targets contributors.
requirements/       Dependencies for development and optional features


## Development Workflow

1. Branch off from latest `main`
2. Branch format: type/short-description (e.g., enh/user-auth).
3. Make changes
4. Run mypy and pytest
5. Use pre-commit when committing
6. Commit format: `PREFIX: Description`

Prefixes for commit messages:

`SEC`   Security fix (e.g. infinite loop, resource exhaustion).
`BUG`   User-facing bug fix. Put `Closes #123` in the body.
`ENH`   New feature.
`DEP`   Deprecating or removing a feature.
`PI`    Performance / smaller output files.
`ROB`   Handling broken PDFs better.
`DOC`   Docs only.
`TST`   Tests only.
`DEV`   Tooling / CI / pre-commit.
`MAINT` Refactoring and misc.
`STY`   Small style/consistency, better error messages.

Pick the single best match, top-down.

Within the commit message, add the following as the last line:

Co-authored-by: {{Agent Name, Model Name and version}} <{{email@agent-company.com}}>


## Boundaries

- Breaking changes MUST follow the deprecation process (-> docs/dev/deprecations.md)
- Never modify `CHANGELOG.md` or `requirements`.
- Keep PRs small and single-purpose: typos, style, a feature, and a bug fix are
  separate PRs. A feature PR must include its tests and docs.
- Never run "git push".

## When stuck
- ask a clarifying question, propose a short plan, or open a draft PR with notes
- do not push large speculative changes without confirmation
