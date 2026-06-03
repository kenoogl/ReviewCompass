# Post-write verification recheck target: proxy review and parallel implementation workflow

## Scope

This recheck covers the fixes applied after `postwrite-proxy-review-parallel-workflow-2026-06-04-r1`.

The original update canonicalized:

- main session LLM review-run triage,
- proxy_model decision delegation,
- parallel implementation via sub-implementation LLMs,
- separated thread + separated worktree policy,
- subthread output classification,
- proxy approval machine checks in `tools/api_providers/review_triage.py`.

## r1 summary

The first independent 3-way post-write verification returned 13 findings:

- claude-sonnet-4-6: 6 findings, WARN 3 / INFO 3
- gpt-5.4: 4 findings, WARN 3 / INFO 1
- gemini-3.1-pro-preview: 3 findings, WARN 2 / INFO 1

No `must-fix` was identified. The triage classified 11 items as `should-fix` and 2 as `leave-as-is`.

## r1 should-fix clusters and applied fixes

### 1. Important-finding threshold

Problem:
The previous text did not define exactly when a finding becomes important enough to require proxy_model or human judgment.

Fix:
`SESSION_WORKFLOW_GUIDE.md` now defines `重要件の判定閾値`:

- `must-fix`, `ERROR`, and `CRITICAL` are always important.
- `should-fix` is also important when it affects upstream specs, data contracts, machine guards, evidence retention, workflow authority boundaries, or same-root findings from multiple models.
- Ambiguous cases are treated as important.

### 2. Proxy input evidence

Problem:
The previous guard required proxy raw response existence, but not the prompt, candidate options, or original review raw evidence.

Fix:
The canonical docs and `review_triage.py` now require:

- `decision_prompt_path`
- `source_raw_paths`
- `candidate_options`
- `raw_response_path`

The guard checks that prompt/raw paths exist, raw response is non-empty, and candidate options are present.

### 3. Work-noise promotion

Problem:
Failed patch attempts and intermediate logs could be wrongly discarded as `work_noise` even when they explain a blocker or rejected approach.

Fix:
The canonical docs now say judgment-relevant failed attempts, failed patches, and intermediate logs are promoted from `work_noise` to `decision_basis` and summarized or retained.

### 4. Parallelization boundary

Problem:
The previous boundary focused on same files and examples, leaving generated artifacts, shared helper APIs, and transitive contracts ambiguous.

Fix:
The canonical docs now make generated artifacts, shared helpers, transitive contracts, same manifests, and same traceability outputs serial boundaries.

### 5. Same-repo exception

Problem:
The prior wording allowed same-repo parallel work for "very small" checks, which was vague.

Fix:
Same-repo parallel implementation is now prohibited by default. The exception is limited to read-only investigation or checks that leave no diff.

### 6. Incidental changes

Problem:
The main LLM could bundle opportunistic refactors or adjacent changes into an approved fix.

Fix:
The canonical docs now prohibit unapproved incidental refactors, adjacent behavior changes, and out-of-scope cleanup. Such cases stop as new judgment questions.

### 7. Human approval boundary

Problem:
The irreversible-operation list did not explicitly include deleting canon, removing guards, lowering important thresholds, deleting approval evidence, or shrinking verification scope.

Fix:
The canonical docs now treat these operations as requiring explicit human approval.

## r1 leave-as-is decisions

The following were retained as future-scope / out-of-current-scope:

- Full machine enforcement that a proxy_model cannot be wired to an apply step. The current scope relies on role separation, approval record shape, and separated implementation authority.
- Cryptographic or signed provenance for `proxy_model_id`. Future work may add API log IDs or signatures, but the current lightweight guard checks structured evidence presence and consistency.

## Files changed by the fix

- `docs/operations/SESSION_WORKFLOW_GUIDE.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/tasks.md`
- `docs/notes/2026-06-04-proxy-review-parallel-implementation-plan.md`
- `tools/api_providers/review_triage.py`
- `tools/api_providers/tests/test_review_triage.py`
- `tests/tools/test_session_record_contract.py`

## Verification commands

```text
.venv/bin/python3 -m pytest tests/tools/test_session_record_contract.py -q
8 passed

.venv/bin/python3 -m pytest tools/api_providers/tests/test_review_triage.py -q
16 passed

.venv/bin/python3 -m pytest tools/api_providers/tests -q
113 passed
```

## Recheck request

Please review whether the r1 findings were adequately addressed and whether any substantive issue remains.

Focus especially on:

1. Whether the important-finding threshold is now clear enough.
2. Whether proxy_model decision records are auditable enough for the lightweight workflow layer.
3. Whether `work_noise` versus `decision_basis` is now safe.
4. Whether the parallelization boundary is now clear enough.
5. Whether the human-only boundary for irreversible process weakening is explicit enough.

Return structured YAML if possible. If strict YAML is difficult, return raw findings with stable IDs, severity, target location, description, rationale, and recommendation.
