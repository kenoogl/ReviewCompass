# Req15 / Req16 implementation review integrated triage summary

## Run status

- Req15 review_run_dir: `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req15-review-run`
- Req16 review_run_dir: `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req16-review-run`
- variant: `implementation_review_independent_3way_codex_operator`
- primary: `gpt-5.4`
- adversarial: `claude-sonnet-4-6`
- judgment: `gemini-3.1-pro-preview`

## Model result summary

Req15:

- `gpt-5.4`: parse failed, raw response contains readable candidate findings but is not counted as parsed triage evidence.
- `claude-sonnet-4-6`: parsed, 9 findings (`ERROR`: 4, `WARN`: 4, `INFO`: 1)
- `gemini-3.1-pro-preview`: parsed, 1 finding (`ERROR`: 1)

Req16:

- `gpt-5.4`: parsed, 8 findings (`ERROR`: 4, `WARN`: 4)
- `claude-sonnet-4-6`: parsed, 10 findings (`ERROR`: 4, `WARN`: 5, `INFO`: 1)
- `gemini-3.1-pro-preview`: parsed, 1 finding (`ERROR`: 1)

## Same-root clusters

### R15-A: prompt audit does not implement the required fail-closed checks

Proposed label: `must-fix`

Sources:

- Req15 `claude-sonnet-4-6` adversarial-001 / 002 / 003
- Req15 `gemini-3.1-pro-preview` judgment-001
- Req15 `gpt-5.4` primary raw, unparsed corroborating signal

Summary:

`audit_manifest` only checks `language_task` and `on_completion`. It does not reject the required missing structure, broken source refs, unknown action kind, review target manifest mismatch, unverified preconditions, impossible postconditions, or prompt length correspondence cases. The test suite also does not cover most of these required rejection cases.

Why this matters:

Req15 exists to prevent path-only, weakly structured, or machine-task-mixed prompts from entering API review. Without these checks, the effective prompt mechanism can appear structured while still letting the exact failure modes from this reopen pass.

### R15-B: prompt length boundary semantics are not actually verified

Proposed label: `must-fix`

Sources:

- Req15 `claude-sonnet-4-6` adversarial-004
- Req15 `gpt-5.4` primary raw, unparsed corroborating signal

Summary:

The prompt length test uses a fixture where `failure_verdict` is missing while `min_chars > max_chars`. The schema rejection can therefore be caused by the missing required field, not by the inverted bounds. The schema also does not itself express `min_chars <= max_chars`.

Why this matters:

The review criteria explicitly required source/digest/prompt-length structures to be auditable. A misleading passing test would leave a real length-boundary gap hidden.

### R15-C: machine-task leakage diagnostics are incomplete, but one reviewer concern is not confirmed

Proposed label: `should-fix`

Sources:

- Req15 `claude-sonnet-4-6` adversarial-005 / 006 / 007

Summary:

The audit stops after the first machine-task leakage in `language_task.constraints`, so multiple violations are not all reported. The reviewer also suspected `spec.json を更新` was missing from `DIRECT_FOLLOWUP_TERMS`, but the current implementation does include that term. The confirmed issue is therefore weaker: diagnostic completeness and test intent clarity, not a proven bypass for `spec.json を更新`.

Why this matters:

This affects triage quality and regression clarity, but it is less central than R15-A because direct followup detection for the named term is already present.

### R15-D: digest format and manifest build-time validation are inconsistent

Proposed label: `should-fix`

Sources:

- Req15 `claude-sonnet-4-6` adversarial-008 / 009
- Req15 `gpt-5.4` primary raw, unparsed corroborating signal

Summary:

Manifest source artifacts use `sha256:<hex>`, while review-run rounds store bare hex for `effective_prompt_sha256`. The builder also returns a manifest dict without validating it against the manifest schema.

Why this matters:

The current behavior may be compatible, but later audit/comparison code must understand the two digest forms. It is a traceability hardening issue rather than a proven current blocker.

### R16-A: proxy decision checks do not apply human-required predicates before accepting proxy output

Proposed label: `must-fix`

Sources:

- Req16 `gpt-5.4` primary-001
- Req16 `claude-sonnet-4-6` adversarial-001 / 002 / 004

Summary:

`check_decision` validates field presence, coverage, and approval scope, but does not call `evaluate_human_required`. `evaluate_human_required` also does not check required evidence completeness or conflicts such as missing raw response, parsed finding paths, or source triage evidence.

Why this matters:

Req16's core safety point is that proxy decisions cannot override human-required evidence. If the CLI entry point can return OK without evaluating those predicates, the proxy mode boundary is not enforced where users will actually run it.

### R16-B: proxy decision schema does not require enough evidence, coverage, and mapping structure

Proposed label: `must-fix`

Sources:

- Req16 `gpt-5.4` primary-003 / 007
- Req16 `claude-sonnet-4-6` adversarial-007

Summary:

The schema does not require explicit evidence completeness, finding-to-operation mapping, approval gate references, operation contract references, review-wave impact evidence, or missing/conflicting evidence markers. `approval_scope` arrays can also be empty.

Why this matters:

Even if runtime checks improve, a structurally incomplete proxy decision record can still be accepted as data unless the schema carries the evidence obligations.

### R16-C: approval scope semantics need a narrower rule than simple set equality

Proposed label: `human-required`

Sources:

- Req16 `gpt-5.4` primary-002
- Req16 `claude-sonnet-4-6` adversarial-003

Summary:

The current rule requires `review_triage_decide` and `apply_fixes` finding sets to be equal. The reviewers disagree on the risk framing: equality blocks obvious mismatches, but it may also collapse two different approval semantics into a single set comparison and fail to represent operation-scope differences.

Why this matters:

This is close to the earlier user concern that `review_triage_decide` approval and apply-fixes approval are distinct. Before changing behavior, the intended operation model should be confirmed: whether equality is required, insufficient, or only one precondition among several.

### R16-D: implementation phase checks do not enforce required snapshot evidence or commit boundary details

Proposed label: `must-fix`

Sources:

- Req16 `gpt-5.4` primary-004 / 005
- Req16 `gemini-3.1-pro-preview` judgment-001

Summary:

`check_phase_plan` verifies feature, phase order, entry/exit criteria, and forbidden operations. It does not validate required tests, snapshot evidence freshness, or meaningful commit-boundary evidence. The schema also allows extra/duplicate phase structure too broadly.

Why this matters:

Req16 is meant to keep implementation work phase-separated and machine-checkable. If stale or missing evidence is not checked, the phase plan can report OK while the proof of phase completion is weak.

### R16-E: review-wave consumer impact states are under-modeled

Proposed label: `should-fix`

Sources:

- Req16 `gpt-5.4` primary-008
- Req16 `claude-sonnet-4-6` adversarial-005 / 006

Summary:

The implementation blocks unresolved consumer impact when required supporting records are absent, but it does not model the full intended state set: no downstream impact, carried-forward impact, unresolved blocking impact, and resolved impact with evidence.

Why this matters:

The current blocker covers the most obvious unsafe case. The missing state distinction can still create false positives/false negatives later, especially when review-wave outputs become richer.

### R16-F: operation-list and positive-path CLI coverage are weak

Proposed label: `should-fix`

Sources:

- Req16 `gpt-5.4` primary-006
- Req16 `claude-sonnet-4-6` adversarial-008 / 009

Summary:

`operation-list` exposes read-only registry information, but pending conflicts are placeholder-like and read-only behavior is not proven by `check_phase_plan`. The proxy-triage-decision CLI has a negative incomplete-record test, but lacks a positive complete-record test.

Why this matters:

This is important hardening for operational confidence, but it is secondary to the direct proxy boundary failures in R16-A/B/D.

### R16-G: active reopen scope structure validation is a minor robustness issue

Proposed label: `leave-as-is`

Sources:

- Req16 `claude-sonnet-4-6` adversarial-010

Summary:

`resolve_active_reopen_scope` rejects missing scope and does not treat `spec.json.reopened` as active state. The remaining concern is stricter validation when `reopen_record` is a dict but has a malformed non-list scope.

Why this matters:

The central requirement is already met for this review target. This can be revisited if malformed active reopen records become an observed input path.

## Proposed handling

- Treat R15-A, R15-B, R16-A, R16-B, and R16-D as `must-fix`.
- Treat R15-C, R15-D, R16-E, and R16-F as `should-fix`.
- Treat R16-C as `human-required` before implementation because it changes the approval-scope model rather than just filling a missing check.
- Treat R16-G as `leave-as-is`.

## Stop point

This is the user-visible triage gate. Do not ask proxy_model, edit implementation, update spec.json, advance the phase, or apply final labels to `triage.yaml` until the triage decisions are approved by the user or proxy_model under an approved proxy-mode request.
