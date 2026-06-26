---
name: nb-onboard
description: Guided new-hire onboarding flow — doctor, query, generate, validate, and test for an indexed library.
---

# NB onboard

Run the full Newbie onboarding workflow for a new engineer contributing to an indexed library. Shift ownership to the engineer — explain each step briefly as you go.

## Inputs

Ask if missing:

- **Library name** — must exist in `config/libraries.yaml`
- **Task intent** — what they need to build (e.g. "merge two PDFs with pypdf")
- **Audience** — engineer (default), or PM/QA summary at the end

## Workflow

1. **Health check**
   ```bash
   python scripts/doctor.py
   ```
   If doctor fails, stop and list fixes before continuing.

2. **Retrieve grounded patterns**
   ```bash
   python scripts/query.py --library <name> --prompt "<intent>"
   ```
   Use only APIs shown in retrieved output.

3. **Generate customer code**
   - Read and follow the **nb-generate** skill.
   - Place deliverables in the repo's existing layout (discover it — don't assume `scripts/`); see the **customer-workspace** rule.
   - Infer language from the repo; `config/workspace.yaml` is an optional override.

4. **Validate**
   - Read and follow the **nb-validate** skill.
   - Compare final code against retrieved chunks; fix critical issues before continuing.

5. **Test plan (when in scope)**
   - Read and follow the **nb-test** skill.
   - Emit structured test cases and coverage gaps.

6. **Symbol check before PR**
   - If **nb-symbols** MCP is enabled, call `verify_imports` for new imports.
   - For Python customer code, run:
     ```bash
     python scripts/verify_symbols.py --git-diff
     ```

7. **Close with next steps**
   - Summarize what was built and where files live.
   - Metrics sync automatically on every `git push` (pre-push hook from `nb init`). Manual override: `python scripts/sync_metrics.py --write --push`
   - Point them to the **newbie-onboarding** agent for their next task.

## Hard stops

- Do not invent library APIs not in retrieval or symbol manifests.
- Do not skip query.py before generating library-specific code.
- Do not place customer deliverables in the Newbie workspace root.
