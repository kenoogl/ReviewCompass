# Raw review triage summary

## 1. Review Run

- run_id: `2026-06-16-workflow-management-implementation-operation-registry-preflight-review-run`
- variant: `implementation_review_independent_3way_codex_operator`
- phase: `implementation`
- target: `review-target.md`
- target_manifest: `target-manifest.yaml`

## 2. Role Assignments

| role | path | provider | model |
| --- | --- | --- | --- |
| primary | api | openai-api | gpt-5.4 |
| adversarial | api | anthropic-api | claude-opus-4-8 |
| judgment | api | gemini-api | gemini-3.1-pro-preview |

## 3. Raw / Parse Summary

| model | parse_status | findings | severity |
| --- | --- | ---: | --- |
| gpt-5.4 | parsed | 4 | WARN:3, INFO:1 |
| claude-opus-4-8 | parsed | 8 | ERROR:3, WARN:3, INFO:2 |
| gemini-3.1-pro-preview | parsed | 3 | ERROR:1, WARN:1, INFO:1 |

Raw paths:

- `raw/gpt-5.4.round-1.txt`
- `raw/claude-opus-4-8.round-1.txt`
- `raw/gemini-3.1-pro-preview.round-1.txt`

## 4. Same-root Clusters

### C1: Known invocation is a second parser source of truth

Source findings:

- `gpt-5.4-primary-001`
- `claude-opus-4-8-adversarial-001`
- `gemini-3.1-pro-preview-judgment-001`

Plain explanation:

The implementation prevents some command mistakes by keeping `KNOWN_INVOCATIONS`, but this duplicates the real CLI parser. If the real parser changes and this table is not updated, the preflight can start giving wrong guidance.

Candidate labels:

- Recommended: `must-fix`
- Alternative: `should-fix` if this is explicitly accepted as a short-lived phase-1 limitation with a follow-up task.

Recommended handling:

Add a synchronization or drift-detection mechanism. A minimal first step is an automated test or exported command registry check that compares registered options with the parser source for the commands in scope. A fuller fix is to make the command registry derive from parser-exported metadata.

### C2: Family-required checks are declared but not executed per check

Source findings:

- `gpt-5.4-primary-002`
- `claude-opus-4-8-adversarial-002`
- `claude-opus-4-8-adversarial-003`
- `claude-opus-4-8-adversarial-006`

Plain explanation:

The registry lists many required checks, but `operation-preflight` currently executes only a small subset. The response also returns several generic fields as empty defaults. This makes the implementation look more complete than it is.

Candidate labels:

- Recommended: `must-fix`
- Alternative: split into `must-fix` for false-coverage risk and `should-fix` for additional family-specific breadth.

Recommended handling:

Fail closed when a required check is declared but no executor exists. The preflight response should report each required check as `ok`, `failed`, or `not_implemented`. For this feature, `not_implemented` should make the verdict `DEVIATION` unless the registry explicitly marks the operation as design-only or placeholder.

### C3: Deployment/export boundary only rejects absolute paths

Source findings:

- `gpt-5.4-primary-003`
- `claude-opus-4-8-adversarial-004`
- `gemini-3.1-pro-preview-judgment-002`

Plain explanation:

The current deployment boundary check rejects absolute paths, but a relative path like `../outside.zip` can still escape the intended output area. This means the check avoids probing external paths but does not fully prevent boundary mistakes.

Candidate labels:

- Recommended: `must-fix`
- Alternative: `should-fix` if deployment/export is explicitly out of phase-1 runtime scope.

Recommended handling:

Normalize planned output paths against a declared root and reject paths that escape the root. Keep the check read-only: it should inspect path strings and resolved path relationships without creating directories or files.

### C4: Exit-code and JSON-mode contract needs tightening

Source findings:

- `claude-opus-4-8-adversarial-005`
- `gemini-3.1-pro-preview-judgment-003`

Plain explanation:

The command returns non-zero for `WARN` and `DEVIATION`, even in JSON mode. That may be fine, but callers need an explicit contract. Also, unexpected verdict strings should not silently collapse into `DEVIATION`.

Candidate labels:

- Recommended: `should-fix`
- Alternative: `must-fix` if CI integration is in immediate scope.

Recommended handling:

Validate verdicts explicitly before mapping exit codes. Document or encode that JSON consumers must treat exit codes 1 and 2 as structured preflight outcomes, not command crashes.

### C5: LLM/provider/model independence is implemented positively

Source findings:

- `gpt-5.4-primary-004`
- `claude-opus-4-8-adversarial-007`

Plain explanation:

The registry validator rejects LLM/provider/model fields, and a test covers this. This supports the requirement that operation preflight not depend on the LLM being used.

Candidate labels:

- Recommended: `leave-as-is`

Recommended handling:

Keep as-is. If the registry expands, preserve the same rule and test coverage.

### C6: Existing CLI regression evidence is positive

Source findings:

- `claude-opus-4-8-adversarial-008`

Plain explanation:

The change is additive and the existing workflow CLI tests passed, so there is no immediate evidence of existing CLI regression.

Candidate labels:

- Recommended: `leave-as-is`

Recommended handling:

Keep as-is. Re-run the broader workflow test suite after any fixes to C1-C4.

## 5. Three-level Triage Draft

Recommended `must-fix`:

- C1: Known invocation is a second parser source of truth.
- C2: Family-required checks are declared but not executed per check.
- C3: Deployment/export boundary only rejects absolute paths.

Recommended `should-fix`:

- C4: Exit-code and JSON-mode contract needs tightening.

Recommended `leave-as-is`:

- C5: LLM/provider/model independence is implemented positively.
- C6: Existing CLI regression evidence is positive.

## 6. Stop Condition

Per `SESSION_WORKFLOW_GUIDE` review-run proxy gate, do not ask proxy_model, edit implementation, update `spec.json`, or advance the implementation gate until the user or approved proxy process decides the labels and handling for the clusters above.
