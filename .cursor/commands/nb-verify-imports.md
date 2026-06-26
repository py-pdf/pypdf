---
name: nb-verify-imports
description: Pre-PR symbol and import validation — MCP lookup plus verify_symbols for changed files.
---

# NB verify imports

Run the import guardrails a new engineer must clear before opening a PR. Deterministic checks first; explain failures in plain language.

## Workflow

1. **List configured libraries**
   ```bash
   python scripts/query.py --library <name> --prompt "list public imports" 2>/dev/null || true
   ```
   Or use **nb-symbols** MCP: `list_libraries`.

2. **MCP symbol validation** (when nb-symbols is enabled)
   - Call `verify_imports` with the library name and import list from changed files.
   - Call `lookup_symbol` for any symbol the engineer is unsure about.
   - Block private or missing symbols — cite the manifest, do not guess replacements.

3. **Python symbol check** (changed `.py` files under customer root)
   ```bash
   python scripts/verify_symbols.py --git-diff
   ```
   If no git diff context, run against explicit paths:
   ```bash
   python scripts/verify_symbols.py path/to/changed_file.py
   ```

4. **Manifest alignment** (DevOps spot-check)
   ```bash
   python scripts/check_manifests.py
   python scripts/doctor.py
   ```

5. **Report results**

   | Check | Pass/Fail | Notes |
   |-------|-----------|-------|
   | MCP verify_imports | | |
   | verify_symbols.py | | |
   | doctor.py | | |

   On failure: name the symbol, the library, and the fix (use public symbol from manifest or re-index).

## When to use

- Before opening a PR with library imports
- After nb-generate, as part of nb-validate
- When Nina (QA) or Marcus (DevOps) need evidence that onboarding did not increase under-tested PRs

## Hard stops

- Never approve imports absent from `store/manifests/<library>.symbols.json`.
- Never suggest deprecated symbols when conventions or retrieval mark them blocked.
