prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.1-pro-preview

# Task
Review the target document for the requested phase and criteria.

# Phase
prompt-quality

# Criteria
---
criteria_id: api-review-prompt-quality-review
phase: prompt-quality
review_target: <api-review-criteria-draft.md>
---

# API Review Prompt Quality Review Criteria

Review the target prompt draft itself. Do not review the eventual feature artifact yet.

The question is:

Is the draft prompt suitable to use as the `--criteria-file` for the intended API-mediated review, given that the actual `--target` will be the target artifact named in the draft?

If user-provided review requirements exist, also judge whether the draft prompt preserves and operationalizes those requirements without unauthorized narrowing, broadening, replacement, or added authority.

## Required Quality Checks

Check both general LLM-as-Judge prompt quality and any workflow / phase-specific review requirements.

### General API Review Prompt Quality

The prompt draft must:

1. Show that main identified the materials and judgment points before sending the prompt.
2. Include enough background and related context for the model to avoid guessing.
3. Ask a non-leading analysis question.
4. Define a scope that is neither too broad nor too narrow.
5. Provide or rely on a fixed, parser-friendly output contract when combined with the API review runner template.
6. Avoid credentials, personal data, or unrelated confidential material.
7. Keep `--criteria-file` and `--target` roles distinct.
8. Ensure the target manifest will contain the actual artifact under review.

### User Review Requirements Fit

When the review was requested by a user or by a workflow-specific gate, the prompt draft must:

1. Preserve the requested review purpose, review object, focus, scope boundaries, source materials, output requirements, and prohibited actions.
2. Map those requirements into the review task, required checks, out of scope, and finding policy.
3. Avoid narrowing the requested review so that important user-stated concerns disappear.
4. Avoid broadening the requested review into unrelated judgments or downstream phase decisions.
5. Avoid replacing the requested review question with a more convenient or generic question.
6. Mark assumptions explicitly when the user requirement is ambiguous.
7. Keep workflow-required checks distinguishable from user-requested checks when both apply.
8. Prevent commit, push, phase completion, human approval delegation, or unapproved specification changes unless those actions are explicitly in scope and allowed by the governing workflow.

### Judgment Granularity

The prompt draft must:

1. Contain one primary judgment question.
2. Avoid bundling multiple independent cluster, finding, acceptance, or design-policy judgments into one prompt.
3. Split multiple independent judgments into separate prompt files unless they are inseparable parts of the same decision.
4. Include only the source findings, upstream materials, target summaries, and output fields needed for the specific judgment item.
5. Keep common background short enough that it does not obscure the item-specific evidence.
6. Require separate prompt-quality review evidence for each item-specific prompt when the review is split.

### Source-Material Quality

The prompt draft must:

1. Clearly distinguish review target, source materials, and out-of-scope material.
2. Avoid path-only source material listing.
3. Include required source material as excerpt or structured summary in a model-readable form.
4. Mark front matter paths as provenance when they are not model-readable content.
5. Include unresolved or deferred items when they affect the target review.

### External API Material Policy

The prompt draft may include ReviewCompass repository specifications, designs, tasks, review findings, structured summaries, and evidence paths when they are necessary for API review or proxy_model judgment and the user has approved that API/proxy execution.

The prompt draft must:

1. Exclude API keys, tokens, passwords, nonces, and other secrets.
2. Exclude personal identifiers such as email addresses and phone numbers unless explicitly required and approved.
3. Exclude third-party confidential material that is not allowed to be sent externally.
4. Avoid unnecessary full logs or unrelated files.
5. Use the minimum review-relevant excerpts or structured summaries needed for the judgment item.
6. Not treat ordinary repository-internal specs, designs, review findings, or evidence paths as automatically prohibited solely because they are unpublished.

### Vertical Intent Transfer Requirements

When the review is a phase review under `SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`, the prompt draft must:

1. Limit target judgment to the current phase artifact.
2. Use upstream artifacts only for background and intent-transfer checking.
3. Include upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, and intended target-phase transfer.
4. Prevent the model from judging downstream tasks or implementation correctness unless downstream invention would be forced by a target omission.

### Output And Triage Fit

The prompt draft must:

1. Use severity labels compatible with the API parser: `CRITICAL`, `ERROR`, `WARN`, `INFO`.
2. Give enough target-location guidance for findings to be triaged.
3. Define when `findings: []` is acceptable.
4. Avoid wording that suppresses findings about critical boundaries while merely trying to prohibit the model from authorizing operations.

## Finding Policy

- Report `CRITICAL` if the draft prompt would authorize or imply authorization of irreversible operations, gate completion, or human-only approvals.
- Report `CRITICAL` if the draft prompt would violate a user-stated prohibited action or authority limit.
- Report `ERROR` if the draft prompt omits, weakens, broadens, or replaces a user-stated review requirement in a way that changes what will be reviewed.
- Report `ERROR` if the draft prompt combines multiple independent judgments so that the model is likely to miss item-specific evidence, conflate labels, or produce unusable decisions.
- Report `ERROR` if the draft prompt would likely cause models to review the wrong target, rely on summaries instead of the real target, miss required upstream-transfer obligations, leak secrets or prohibited third-party confidential material, or produce unusable output.
- Report `WARN` if the draft prompt is usable but has avoidable ambiguity, framing bias, incomplete source-material presentation, weak target/source/out-of-scope separation, incomplete mapping from user requirements to checks, or mildly oversized common background.
- Report `INFO` for minor wording or ergonomics improvements.
- Return `findings: []` only if the draft prompt is safe to use for the intended API review.

## Output Contract

Return YAML only with top-level key `findings`.

Each finding must include:

- `severity`: CRITICAL, ERROR, WARN, or INFO
- `target_location`: specific section in the prompt draft
- `description`: concise finding summary
- `rationale`: why this matters for API review quality

If there are no findings, return exactly:

findings: []


# Output contract
Return YAML only.
The top-level key must be exactly findings.
Do not add wrapper keys such as review, result, metadata, or summary.
Do not wrap the YAML in Markdown code fences.
Do not write prose before or after the YAML.

Each finding must include these keys:
- severity
- target_location
- description
- rationale

Use only these severity values:
- CRITICAL
- ERROR
- WARN
- INFO

If there are no findings, return exactly:

findings: []

Valid shape example:

findings:
  - severity: WARN
    target_location: "path or section"
    description: "Plain finding summary"
    rationale: "Why this matters"

# Prior findings
# 前段所見 1：
role: adversarial
provider: anthropic-api
model: claude-sonnet-4-6
attempts: 1
duration_seconds: 26.415
findings:
- severity: WARN
  target_location: Output Contract section (final YAML block)
  description: The draft wraps the output contract YAML examples in Markdown code
    fences (```yaml ... ```), which conflicts with the required parser-friendly plain-YAML
    output contract.
  rationale: The API review runner template expects plain YAML output with no fence
    markers. Showing fenced examples in the criteria file may cause the reviewing
    model to mirror that format in its response, producing output the parser cannot
    consume. The examples should be shown as plain indented YAML or clearly labeled
    as display-only illustrations.
- severity: WARN
  target_location: Source Materials / Implementation Commit Summary
  description: The commit summary is prose-only and does not include any structured
    excerpts, file-level diffs, or schema content from the actual implementation artifacts.
    The reviewing model will have no model-readable content for the implementation
    target until the run manifest is assembled.
  rationale: Per source-material quality requirements, path-only or summary-only listings
    are insufficient when the model needs to judge implementation correctness. If
    the run manifest does not separately inject the full target files, the model will
    be forced to guess at implementation details from the prose summary alone. The
    criteria draft should note explicitly that the run manifest must include verbatim
    file content, or include representative excerpts here for at least the boundary-critical
    modules (approval_gate.py, proxy_triage_decisions.py, prompt_audit.py).
- severity: WARN
  target_location: Required Checks / Check 6 (TDD coverage)
  description: Check 6 asks the reviewer to judge TDD coverage sufficiency but does
    not specify what 'enough for the risk level' means in measurable or observable
    terms, leaving the threshold ambiguous.
  rationale: An underspecified coverage criterion can cause the reviewing model to
    either suppress WARN findings about genuine gaps (too lenient) or flag every test
    file regardless of actual risk (too broad). Adding at least a qualitative anchor—e.g.,
    'fail-closed paths must have at least one explicit negative test per boundary
    condition listed in the requirements summary'—would make the check actionable
    and consistent across models.
- severity: WARN
  target_location: Review Target file list
  description: The file list includes tools/api_providers/run_role.py and tools/api_providers/run_review.py
    without explaining their connection to Requirement 14–16 or Requirement 13 touchpoints.
  rationale: Including files without scoping rationale risks prompting the model to
    review them broadly rather than only for the specific boundary properties in scope
    (e.g., whether they respect the approval/proxy boundary). A brief parenthetical
    tying each out-of-main-scope file to the relevant requirement check would prevent
    the review drifting into unrelated judgments about those files.
- severity: WARN
  target_location: Source Materials / Requirements Intent Summary — Requirement 13
    paragraph
  description: The Requirement 13 summary lists eight contract properties (authority,
    required_action mapping, effect kind, approval requirement, phase boundary, sequence,
    commit boundary, registry/contract separation) but does not state which of those
    are relevant only at touchpoints versus universally applicable, making it unclear
    how much weight the reviewer should assign Requirement 13 findings relative to
    Requirement 14–16 findings.
  rationale: Ambiguity about Requirement 13 scope could lead the model either to over-report
    Requirement 13 issues as ERROR when they are peripheral, or to under-report them
    as INFO when a real contract violation exists. Clarifying 'check only where T-016/T-019
    modules call into or read operation contract state' would bound the judgment appropriately.
- severity: INFO
  target_location: Front matter — review_target field
  description: review_target is set to a prose description ('workflow-management implementation
    artifacts from commits 5d3a5b6d..10cf6922') rather than a path or manifest reference.
  rationale: For provenance traceability it is preferable for review_target to reference
    the intended_actual_run_dir or a canonical manifest path so the criteria file
    and run directory are unambiguously linked. The current prose value is human-readable
    but not machine-resolvable.
- severity: INFO
  target_location: Finding Policy / CRITICAL definition
  description: The CRITICAL definition partially overlaps with the Out Of Scope list
    (both mention phase completion and push), creating mild redundancy. This is cosmetic
    but may cause the model to conflate the two sections.
  rationale: 'Minor clarity improvement: the Finding Policy could reference ''see
    Out Of Scope'' rather than restating the same operations, reducing the chance
    of interpretive drift between the two sections.'


# Target path
.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-prompt-quality-run/api-review-criteria-draft.md

# Target document
---
criteria_id: workflow-management-implementation-triad-review-2026-06-20-draft
phase: implementation.triad-review
review_target: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-run/review-target-manifest.md
intended_actual_run_dir: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-run
intended_variant: implementation_review_independent_3way_codex_operator
---

# Workflow-Management Implementation Triad Review Criteria Draft

## Review Task

Review the current `workflow-management` implementation drafting output for Requirement 14 through Requirement 16, with supporting checks for Requirement 13 where the implementation touches operation contracts.

Primary judgment question:

Do the implementation artifacts produced in commits `5d3a5b6d..10cf6922` correctly implement the approved `requirements.md`, `design.md`, and `tasks.md` intent for workflow-management implementation drafting, without omitting, weakening, or adding unsupported behavior across the requirements → design → tasks → implementation chain?

## Why This Review Exists

`workflow-management` has just moved `implementation.drafting` from `false` to `true`. Before marking `implementation.triad-review` complete, API-mediated triad-review must check the implementation itself and the upstream intent transfer:

- requirements define what must be protected or mechanized.
- design defines the implementation model and boundaries.
- tasks define the TDD work units and completion criteria.
- implementation artifacts must satisfy those without broadening authority into phase completion, commit, push, approval, or human-only decisions.

## User Review Requirements

This review is required by the workflow gate for `workflow-management / implementation / triad-review`.

Required user/workflow requirements:

1. Review purpose: defect detection and gate readiness for implementation triad-review.
2. Review object: implementation artifacts produced by the current implementation drafting sequence, not the earlier design or tasks documents themselves.
3. Review focus: upstream intent transfer, state defense, approval/proxy boundary, prompt audit boundary, operation contract/registry boundary, phase plan and proxy triage decision checks, read-only versus mutating operation separation, tests and verification sufficiency.
4. Scope boundaries: include Requirement 14, Requirement 15, Requirement 16 implementation and any Requirement 13 touchpoints needed to judge contract connection. Do not re-review unrelated dirty worktree files, unrelated prompt-quality side-track documents, or previously completed design/tasks review findings except as upstream context.
5. Source materials: structured summaries of requirements, design, tasks, and implementation commits are included below. The actual run target will contain the implementation files, not this criteria draft.
6. Output requirements: return parser-compatible YAML findings with severity, target_location, description, rationale.
7. Prohibited actions: do not authorize commits, pushes, phase completion, spec.json updates, human approval delegation, or implementation edits. Review findings are advisory until separately triaged and approved.

## Review Target

The actual implementation review-run must use the current implementation artifacts as `--target`. The run must pass the listed files themselves as target files so the model receives verbatim implementation content through the review runner, not only this summary or path list.

Target files and scope rationale:

- `.reviewcompass/schema/approval_gate.schema.json`
- `.reviewcompass/schema/side_track_stack.schema.json`
- `.reviewcompass/schema/workflow_state_snapshot.schema.json`
- `.reviewcompass/schema/language_task_io.schema.json`
- `.reviewcompass/schema/effective_prompt_manifest.schema.json`
- `.reviewcompass/schema/implementation_phase.schema.json`
- `.reviewcompass/schema/proxy_triage_decision.schema.json`
- `stages/workflow-management-implementation-phases.yaml`
- `tools/check-workflow-action.py`
- `tools/check_workflow_action/approval_gate.py`
- `tools/check_workflow_action/side_track_stack.py`
- `tools/check_workflow_action/workflow_state_snapshot.py`
- `tools/check_workflow_action/effective_prompt_builder.py`
- `tools/check_workflow_action/prompt_audit.py`
- `tools/check_workflow_action/implementation_phases.py`
- `tools/check_workflow_action/operation_list.py`
- `tools/check_workflow_action/proxy_triage_decisions.py`
- `tools/api_providers/run_role.py` (only for Requirement 15 review-run rounds recording of `prompt_manifest_path` / `prompt_manifest_sha256`, and compatibility with existing `effective_prompt_path` / `effective_prompt_sha256`)
- `tools/api_providers/run_review.py` (only for Requirement 15 propagation of prompt manifest metadata into multi-role review-run artifact recording)
- `tests/workflow-management/test_approval_gate.py`
- `tests/workflow-management/test_side_track_stack.py`
- `tests/workflow-management/test_workflow_state_snapshot.py`
- `tests/workflow-management/test_language_task_io_schema.py`
- `tests/workflow-management/test_effective_prompt_manifest.py`
- `tests/workflow-management/test_prompt_audit.py`
- `tests/workflow-management/test_prompt_manifest_rounds_recording.py`
- `tests/workflow-management/test_implementation_phase_plan.py`
- `tests/workflow-management/test_operation_list_read_only.py`
- `tests/workflow-management/test_proxy_triage_decision_machine.py`
- `tests/workflow-management/test_review_wave_consumer_impact.py`
- `tests/workflow-management/test_implementation_phase_cli.py`

The reviewer may use commit IDs and verification results as orientation, but must judge the target files' current verbatim content.

## Source Materials

### Requirements Intent Summary

Requirement 14 requires approval gates, side-track stack, and workflow-state snapshot support. The implementation must distinguish proxy and human decision scopes, track consumed decisions, prevent proxy decisions from satisfying human-only gates, keep side-track work bounded by allowed files and nesting depth, and detect drift in workflow state, staged file sets, pending gates, completed gates, operation contracts, and post-write manifest state.

Requirement 15 requires structured effective prompts and prompt audit. The implementation must define language task I/O and effective prompt manifest structure, record source artifacts and digests, preserve text prompt fields while adding prompt manifest metadata to review-run rounds, detect machine execution steps left in language tasks, reject direct state mutation or completion-routing instructions, and ensure `on_completion` remains compatible with next action / operation contracts. It must not turn prompt audit into commit, phase, or approval authorization.

Requirement 16 requires a staged implementation plan from Phase 0 to Phase 6. It must support read-only operation listing without changing `next --json`, define schema for implementation phases and proxy triage decisions, distinguish `spec.json.reopened` history from active reopen scope, block proxy application when human-required evidence exists, prioritize human-only decisions / unresolved approval gates / `approval_required=true` operations / unresolved review-wave impact over proxy labels, and judge proxy triage decisions by evidence completeness and target coverage rather than provider or model name.

Requirement 13 is relevant only where the target implementation reads, exposes, or depends on operation contract state. For this review, check Requirement 13 touchpoints in `operation_list.py`, `implementation_phases.py`, `proxy_triage_decisions.py`, `check-workflow-action.py`, and related tests. Do not conduct a general re-review of the entire operation contract design unless the target implementation creates a contract-boundary defect.

At those touchpoints, the implementation must preserve operation contract authority, required_action mapping, effect kind, approval requirement, phase boundary, sequence, commit boundary, registry/contract separation, and read-only preflight boundaries.

### Design Intent Summary

The design model separates read-only checks from mutating operations. Approval gate records bind decisions to operation IDs, required actions, artifacts, staged file set digests, source digests, and consumed state. Side-track stack exists to preserve mainline return conditions and prevent unbounded nested work. Workflow-state snapshot is a structured read-only evidence packet used to detect state drift.

Structured prompt design separates what the model judges from what tools execute. `language_task` describes document judgment inputs and output format; it must not contain git operations, review-run artifact creation, approval consumption, side-track mutation, operation execution, or direct spec/state mutation. `on_completion` can route to the next workflow expectation but cannot itself authorize state mutation.

The Requirement 16 design model says Phase 0 through Phase 6 must be tracked as implementation planning/control artifacts. `operation-list --json` is read-only and must not change `next --json`. Proxy triage decisions must preserve raw response, prompt, candidate decisions, selected decision, reasoning summary, and final application target. Human-required predicate order is fixed: coverage/evidence, finding-to-operation mapping, operation contract, approval gate record, review-wave impact, priority resolution.

### Tasks Intent Summary

T-017 requires tests and implementation for approval gate schema/module, side-track stack schema/module, workflow-state snapshot schema/module, and CLI exposure for snapshot and side-track current state.

T-018 requires tests and implementation for language task I/O schema, effective prompt manifest schema, prompt audit, manifest builder, prompt audit CLI, and review-run rounds recording of prompt manifest path/sha256 without removing existing effective prompt fields.

T-019 requires tests and implementation for implementation phase schema/plan, proxy triage decision schema/checker, operation-list read-only CLI, implementation-phase-check CLI, proxy-triage-decision-check CLI, active reopen scope versus `spec.json.reopened`, review-wave consumer impact blocking, and human-required predicate priority.

The TDD process requires red tests first, failed test confirmation, red-test commit, implementation without changing those tests, passing verification, and implementation commit.

### Implementation Commit Summary

The implementation drafting sequence includes:

- `d14335f9` / `5d3a5b6d`: approval gate, side-track stack, workflow-state snapshot red tests and initial implementation.
- `b550346e` / `7bf5f6d3`: additional defense-gap red tests and fixes for none-binding, target operation match, digest mismatch, side-track push constraints, and snapshot drift.
- `0757e832` / `dbe5aa1f`: structured prompt audit red tests and implementation, including manifest schemas, prompt audit CLI, builder, and review-run rounds metadata.
- `a06250de` / `61c87e5a`: implementation phase / proxy triage red tests and implementation, including schemas, phase plan, operation-list, proxy triage decision checks, review-wave consumer impact checks, and CLI.
- `10cf6922`: `spec.json` state update marking `workflow-management.implementation.drafting=true` after verification.

Verification performed before this triad-review:

- `tests/workflow-management` passed: 55 tests.
- T-019 targeted tests passed: 13 tests.
- Related operation contract tests passed: 12 tests.
- `implementation-phase-check --feature workflow-management --json` returned OK.
- `operation-list --json` returned OK.
- `next --json` now returns `workflow-management / implementation / triad-review`.

## Required Checks

Reviewers must check:

1. Upstream intent transfer: requirements → design → tasks → implementation is preserved for Requirement 14, Requirement 15, Requirement 16, and relevant Requirement 13 touchpoints.
2. Scope discipline: implementation artifacts do not add authority to approve, commit, push, complete phases, mutate spec.json, or satisfy human-only decisions outside explicit workflow gates.
3. Approval/proxy boundary: approval gate and proxy triage logic fail closed when human-only, unresolved approval, approval-required operation, digest mismatch, or review-wave unresolved evidence appears.
4. Read-only boundary: `workflow-snapshot`, `side-track-stack current`, `prompt-audit`, `operation-list`, `implementation-phase-check`, and proxy decision checks are read-only except where a separate mutating operation is explicitly intended.
5. Evidence completeness: prompt manifests, rounds metadata, proxy decision schema, phase plan, and snapshots record enough path/digest/status evidence to support later audit.
6. TDD coverage: fail-closed boundary conditions listed in the requirements summary must have explicit negative tests. At minimum, check for negative tests covering human-only / approval-required proxy blocking, unresolved review-wave impact, coverage mismatch, approval scope mismatch, direct state mutation prompt instructions, machine execution instructions in language_task, digest or operation-target mismatch, side-track scope limits, and snapshot drift.
7. Compatibility: existing text-only effective prompt fields remain compatible while structured prompt manifest fields are added.
8. Drift risk: implementation does not conflict with operation contract/registry authority or with `next --json` state selection.

## Out Of Scope

Do not judge:

- Whether design.md or tasks.md should be rewritten; those were earlier phase artifacts and are source materials here.
- Whether unrelated dirty worktree files should be committed.
- Whether to approve `implementation.triad-review`, `review-wave`, `alignment`, or `approval`.
- Whether to run proxy_model decisions or apply fixes.
- Whether to push to a remote.

## Finding Policy

Return `findings: []` only if no actionable issue is found in the implementation target.

Use:

- `CRITICAL` for issues that would let the workflow bypass human-only approval, commit/push/phase gates, or apply proxy decisions over human-required evidence. These operations are listed in Out Of Scope because the review must not authorize them; a target defect that would bypass them remains in scope as a finding.
- `ERROR` for implementation defects that violate Requirement 14, 15, 16, or required Requirement 13 boundaries, or for missing fail-closed behavior in state/proxy/prompt controls.
- `WARN` for test coverage gaps, ambiguous behavior, weak evidence recording, compatibility risk, or narrow cases likely to matter but not immediately unsafe.
- `INFO` for minor maintainability, naming, or ergonomics observations.

Each finding must include:

- `severity`
- `target_location`
- `description`
- `rationale`

Return YAML only, without Markdown fences:

findings:
  - severity: ERROR
    target_location: path:line-or-section
    description: concise finding summary
    rationale: why this matters

If there are no findings, return exactly:

findings: []

