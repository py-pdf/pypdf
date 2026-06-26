# Go conventions

Customer deliverable layout for Go projects. Library API rules live in `config/conventions/<library>.md`.

## File naming

- Source: `snake_case.go` or single-word names — match existing files under `customer.root`.
- One primary type or concern per file when the project already follows that pattern.

## Module / import style

- Use the module path from `go.mod`.
- Group imports: standard library, blank line, third-party — match `goimports` style already in the repo.

## Tests

- Files: `<topic>_test.go` in the same package as the code under test (or `_test` external package when the project uses that pattern).
- Framework: **go test** — `func TestXxx(t *testing.T)` with table-driven subtests where variants apply.
- Assertions: `testing` package, or `testify` only when already a project dependency.

## Infer when workspace.yaml is silent

Under `customer.root`: `go.mod`, dominant `.go` files.

Default test framework: **go test**.
