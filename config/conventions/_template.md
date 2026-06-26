# <library> conventions

Indexed version: see `store/manifests/<library>.json` (`ref`, `commit`).

Populate this file after indexing. Ground every section in retrieved chunks:

```bash
python scripts/query.py --library <library> --prompt "module docstring Args public import style"
python scripts/query.py --library <library> --prompt "deprecated removed replacement do not use"
```

## API usage

- Import the public package surface shown in retrieval — not `_`-prefixed internal modules unless retrieval documents an exception.
- Match docstring / comment style from indexed sources (discover via query).

## Customer file layout

File naming, module structure, and test layout for customer deliverables live in `config/conventions/languages/<language>.md` — not in this library file. Resolve language from `config/workspace.yaml` or infer from `customer.root`.

Note: if `config/libraries.yaml` excludes `**/tests/**`, upstream test patterns are not indexed — ground test **behavior** from `repos/<library>/` source search only.

## Deprecated APIs — never emit

| Never use | Use instead |
|-----------|-------------|
| _(add rows after deprecation query)_ | |

If retrieval surfaces `@deprecate` / `deprecation_with_replacement` on a symbol, treat it as blocked for new code.
