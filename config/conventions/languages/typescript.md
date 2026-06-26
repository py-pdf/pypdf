# TypeScript conventions

Customer deliverable layout for TypeScript (or TS-first) projects. Library API rules live in `config/conventions/<library>.md`.

## File naming

- Source: `camelCase.ts` or `kebab-case.ts` — match existing files under `customer.root`.
- React components: `PascalCase.tsx` when the project already uses that pattern.

## Module / import style

- Prefer `import { ... } from '...'` or default imports as shown in retrieved library chunks.
- Match `paths` / barrel exports already used in the customer project.

## Tests

- Directory: `tests/`, `__tests__/`, or co-located `*.test.ts` — match the customer project's existing layout.
- Files: `<topic>.test.ts` or `<topic>.spec.ts`.
- Framework: **vitest** or **jest** — infer from `package.json` devDependencies; default to **vitest** when unclear.
- Structure: `describe` / `it` (or `test`) blocks with explicit assertions; use `expect(...).to...` matchers.

## Infer when workspace.yaml is silent

Under `customer.root`: `tsconfig.json`, or `package.json` with `"typescript"` dependency and `.ts`/`.tsx` sources.

Default test framework: **vitest** (override via `customer.test_framework: jest` in `workspace.yaml`).
