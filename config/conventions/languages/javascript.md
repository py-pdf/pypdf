# JavaScript conventions

Customer deliverable layout for JavaScript (non-TypeScript) projects. Library API rules live in `config/conventions/<library>.md`.

For TypeScript projects, use `config/conventions/languages/typescript.md` instead.

## File naming

- Source: `camelCase.js` or `kebab-case.js` — match existing files under `customer.root`.
- React components: `PascalCase.jsx` when the project already uses that pattern.
- ES modules: prefer `.js` with `"type": "module"` in `package.json` when the project already uses ESM.

## Module / import style

- Prefer `import` / `export` when the project uses ESM; use `require` / `module.exports` only when the customer project is CommonJS throughout.
- Match import paths and barrel exports already used in the customer project.

## Tests

- Directory: `tests/`, `__tests__/`, or co-located `*.test.js` — match the customer project's existing layout.
- Files: `<topic>.test.js` or `<topic>.spec.js`.
- Framework: **vitest**, **jest**, or **node:test** — infer from `package.json` devDependencies/scripts; default to **vitest** when unclear.
- Structure: `describe` / `it` (or `test`) blocks with explicit assertions; use `expect(...).to...` matchers.

## Infer when workspace.yaml is silent

Under `customer.root`: `package.json` with dominant `.js`/`.jsx`/`.mjs` sources and **no** `tsconfig.json` or `"typescript"` dependency.

Default test framework: **vitest** (override via `customer.test_framework: jest` or `node:test` in `workspace.yaml`).
