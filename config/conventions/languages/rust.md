# Rust conventions

Customer deliverable layout for Rust projects. Library API rules live in `config/conventions/<library>.md`.

## File naming

- Source: `snake_case.rs` — match existing files under `customer.root`.
- One primary type or concern per file when the project already follows that pattern.
- Binary crates: `main.rs` in `src/bin/<name>.rs` or `src/main.rs` per existing layout.

## Module / import style

- Use the crate name from `Cargo.toml` for in-crate paths.
- Group `use` statements: std, external crates, then `crate::` / `super::` — match `rustfmt` style already in the repo.
- Prefer public API paths shown in retrieved library chunks; avoid `_`-prefixed or `#[doc(hidden)]` internals unless retrieval documents an exception.

## Tests

- Unit tests: `#[cfg(test)] mod tests { ... }` in the same file, or `tests/<topic>.rs` for integration tests — match the customer project's existing pattern.
- Files: `tests/<topic>.rs` for integration tests; inline `mod tests` for unit tests.
- Framework: **cargo test** — `#[test]` functions; prefer `#[test]` with table-style loops or parameterized helpers when variants apply.
- Assertions: `assert!`, `assert_eq!`, `assert_matches!`; use `Result` and `?` in tests when the project already does.

## Infer when workspace.yaml is silent

Under `customer.root`: `Cargo.toml`, dominant `.rs` files under `src/`.

Default test framework: **cargo test**.
