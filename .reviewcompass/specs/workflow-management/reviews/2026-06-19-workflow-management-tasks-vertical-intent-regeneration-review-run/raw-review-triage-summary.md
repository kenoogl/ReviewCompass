# Raw Review Triage Summary

- run_id: `2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run`
- variant: `implementation_review_independent_3way_codex_operator`
- criteria: `workflow-management tasks vertical intent regeneration`
- gate: `stages/tasks.yaml#triad-review`
- baseline: `2026-06-19-workflow-management-tasks-granularity-regeneration-review-run.baseline-before-vertical-intent`

## Role Assignments

| role | path | provider | model | raw |
| --- | --- | --- | --- | --- |
| primary | api | openai-api | gpt-5.4 | `raw/gpt-5.4.round-1.txt` |
| adversarial | api | anthropic-api | claude-opus-4-8 | `raw/claude-opus-4-8.round-1.txt` |
| judgment | api | gemini-api | gemini-3.1-pro-preview | `raw/gemini-3.1-pro-preview.round-1.txt` |

## Model Summary

| model | parse_status | findings | severity |
| --- | --- | ---: | --- |
| gpt-5.4 | parsed | 9 | ERROR:4, WARN:3, INFO:2 |
| claude-opus-4-8 | parsed | 5 | WARN:2, INFO:3 |
| gemini-3.1-pro-preview | parsed | 0 | - |

Baseline model summary:

| model | findings | severity |
| --- | ---: | --- |
| gpt-5.4 | 3 | WARN:3 |
| claude-opus-4-8 | 9 | WARN:1, INFO:8 |
| gemini-3.1-pro-preview | 0 | - |

## Same-root Clusters

### C1: T-016 registry / contract boundary is still not vertically settled

Proposed label: `must-fix candidate`

Findings:

- `2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run-gpt-5.4-primary-001`
- `2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run-gpt-5.4-primary-002`
- `2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run-claude-opus-4-8-adversarial-001`

Plain explanation:

The regenerated T-016 improved the baseline C1 issue by adding a contract / registry reference rule and red tests. The vertical audit also exposed a sharper problem: the task may be adding a design decision that is not fully fixed upstream. Requirements allow operation contract mappings in the registry or an equivalent machine-readable definition, while design says the registry references operation contracts but does not fully settle the two-file source-of-truth / digest synchronization model. This is no longer just "needs detail"; it is a vertical intent question about whether tasks are allowed to introduce that split.

Effect vs baseline:

- Baseline C1 was a `should-fix` ambiguity.
- New C1 is stronger: possible unsupported addition from tasks beyond design.
- The audit made the defect more precise and more serious.

### C2: T-017 state persistence and mutation boundary improved, but still has gaps

Proposed label: `should-fix candidate`

Findings:

- `2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run-gpt-5.4-primary-003`
- `2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run-gpt-5.4-primary-004`
- `2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run-claude-opus-4-8-adversarial-004`

Plain explanation:

The regenerated T-017 now names read-only vs mutating operations, snapshot non-canonical status, stack push / pop / current, and additional red tests. That resolves part of baseline C2. The remaining gap is finer: snapshot / approval / stack storage and mutation boundaries are still not fully locked at completion-condition level, especially pop return failure, parent-child staged overlap, and repair / stop behavior.

Effect vs baseline:

- Baseline C2 was broad: "where is state stored and which commands mutate it?"
- New C2 is narrower: most pieces are present, but edge-case transitions still need precise tests.
- The audit shows partial improvement, not full resolution.

### C3: Proxy / human boundary surfaced as an upstream-design alignment issue

Proposed label: `must-fix candidate`

Findings:

- `2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run-claude-opus-4-8-adversarial-002`
- related: `2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run-gpt-5.4-primary-006`
- related: `2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run-gpt-5.4-primary-007`

Plain explanation:

The regenerated tasks tried to make the human-required predicate concrete. Claude says T-019 now inherits design intent well, but also flags that T-017's proxy delegation boundary may be imported from broader approval discipline rather than being clearly designed in Requirement 14. GPT still says T-019 needs clearer priority / conflict handling among triage item, approval gate record, operation contract, and review-wave impact evidence.

Effect vs baseline:

- Baseline C3 was "T-019 does not define the human-required predicate."
- New C3 shows a split: T-019 improved, but proxy / human boundary now exposes a vertical alignment question between Requirement 14, Requirement 16, and broader approval discipline.
- The audit did its job: it separated "task detail" from "upstream design authority."

### C4: T-018 remains mostly sound, with a broader machine-task leakage check suggested

Proposed label: `should-fix candidate`

Findings:

- `2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run-gpt-5.4-primary-005`

Plain explanation:

T-018 preserves the main Requirement 15 intent: structured effective prompt is a language task specification, not a machine execution script. GPT suggests expanding the red tests beyond commit / spec.json / phase mutation to include review-run artifact creation, approval consumption, and side-track mutation. This is a useful precision improvement, not a sign that the vertical intent failed.

Effect vs baseline:

- Baseline mostly treated T-018 as adequate.
- New audit adds a narrow should-fix test expansion.

### C5: New discipline wiring and task granularity are confirmed

Proposed label: `leave-as-is candidate`

Findings:

- `2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run-gpt-5.4-primary-008`
- `2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run-gpt-5.4-primary-009`
- `2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run-claude-opus-4-8-adversarial-003`
- `2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run-claude-opus-4-8-adversarial-004`
- `2026-06-19-workflow-management-tasks-vertical-intent-regeneration-review-run-claude-opus-4-8-adversarial-005`
- `gemini-3.1-pro-preview: no findings`

Plain explanation:

The new `vertical-intent-transfer-review` discipline is wired into `WORKFLOW_DISCIPLINE_MAP.yaml` for triad-review, review-wave, and alignment, and `next --json` now includes it as required discipline / required input. The regenerated tasks remain implementation-ready in the basic sense: they have target files, first failing tests, implementation order, completion conditions, verification commands, forbidden actions, and stop conditions.

Effect vs baseline:

- Baseline already had positive granularity findings.
- New audit confirms the discipline wiring and keeps the implementation-ready finding.

## Proposed Three-level Triage

| cluster | proposed triage | reason |
| --- | --- | --- |
| C1 | must-fix | Vertical audit found a possible unsupported task-level design addition around registry / contract source of truth. |
| C2 | should-fix | Baseline issue improved, but edge-case mutation / return behavior needs tighter red tests. |
| C3 | must-fix | Proxy / human boundary now appears to require upstream design alignment, not only task wording. |
| C4 | should-fix | Narrow red-test expansion for machine-task leakage in prompts. |
| C5 | leave-as-is | Discipline wiring and basic task granularity are confirmed. |

## Vertical Audit Effect

The new discipline did not merely re-score the same findings. It changed the kind of review:

1. It preserved the baseline granularity check.
2. It identified where tasks improved baseline findings.
3. It exposed unsupported additions from tasks into design space.
4. It separated task-level ambiguity from upstream design authority.

The most important effect is that C1 and C3 are no longer just "make tasks more detailed" issues. They are vertical integrity issues: either design must explicitly authorize the model, or tasks must be rewritten to stay within the existing design.

## Stop Point

This is the comparison gate. Do not edit design/tasks again, ask proxy_model, update `spec.json`, move the gate, or commit until the user decides how to handle the new C1/C3 vertical findings.
