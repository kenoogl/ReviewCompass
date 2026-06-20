prompt_id: openai_review
provider: openai-api
model_id: gpt-5.5

# Task
Review the target document for the requested phase and criteria.

# Phase
proxy_model

# Criteria
proxy-decision-cluster-triage

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
なし

# Target path
.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-proxy-decision-prompt-quality-run/proxy-decision-prompt-draft.md

# Target document
---
prompt_id: workflow-management-design-v2-proxy-decision
phase: design
gate: stages/design.yaml#triad-review
intended_proxy_target:
  review_run: 2026-06-20-workflow-management-design-vertical-redo-review-run-v2
  clusters:
    - C1
    - C2
    - C3
    - C4
    - C5
    - C6
    - C7
status: draft_for_prompt_quality_review
---

# Proxy Model Judgment Prompt

## User Review Requirements

Preserve the user's instruction: use proxy_model to judge the v2 design review clusters before editing `design.md`, updating workflow state, committing, or pushing.

Review purpose:

- Decide whether each v2 review cluster should be adopted for the current `workflow-management` design triad-review.
- Decide the final triage label for each cluster: `must-fix`, `should-fix`, or `leave-as-is`.
- Decide the required design response for adopted clusters.

Review object:

- Review-run: `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/`
- Clusters: C1 through C7 from `raw-review-triage-summary.md`
- Target artifact under review: `.reviewcompass/specs/workflow-management/design.md`
- Upstream source material: `.reviewcompass/specs/workflow-management/requirements.md`

Review focus:

- Requirement 13 through 16 transfer from requirements to design.
- Whether the cited cluster is a real design-level issue or can safely be deferred to tasks / implementation.
- Whether the proposed label is too strong, too weak, or correct.
- Whether downstream tasks would need to invent policy if the design is left unchanged.

Scope boundaries:

- In scope: cluster validity, final triage label, adopted / rejected source findings, required design response, and downstream risk.
- Out of scope: editing `design.md`, updating `spec.json`, moving the design gate, authorizing phase completion, committing, pushing, or executing implementation.

Output requirements:

- Return YAML only.
- Produce one decision per cluster.
- Preserve finding IDs for traceability.
- Confirm authority limits explicitly.

Prohibited actions and authority limits:

- Do not authorize commit.
- Do not authorize push.
- Do not authorize `spec.json` update.
- Do not authorize phase transition or gate completion.
- Do not edit files.
- Do not treat proxy_model judgment as human-only approval.

Requirement-to-prompt mapping:

- User request "proxy_modelで判断" -> Proxy model decides cluster validity, final triage label, and required design response.
- User correction "先ほど作成したプロンプトレビューの仕組みはつかわないのか" -> Traceability note: this draft is subject to prompt quality review before proxy_model use. This is not a proxy judgment instruction.
- Workflow rule `SESSION_WORKFLOW_GUIDE.md#3.3-a-2` -> Proxy model may judge important findings, but irreversible operations remain human-only.
- Workflow rule `SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review` -> Judge requirements-to-design transfer without judging downstream implementation correctness.

## Context

The current mainline is a reopen procedure for `workflow-management`.

Current gate:

- `stages/design.yaml#triad-review`
- `next --json` reports `reopen_in_progress`
- Requirements approval is complete.
- Design drafting is complete.
- The old design review run is not sufficient because it used a wrapper as both criteria and target.
- The v2 design review run corrected that problem and used `design.md` as the actual target.

V2 model results:

| role | model | findings |
|---|---|---:|
| primary | `gpt-5.4` | 6 |
| adversarial | `claude-sonnet-4-6` | 9 |
| judgment | `gemini-3.1-pro-preview` | 0 |

Model IDs are labels recorded by the review-run artifacts. Use the finding IDs and role/source paths for traceability; do not reject a finding only because a model label is unfamiliar.

Main's proposed triage:

| cluster | proposed label |
|---|---|
| C1 | must-fix |
| C2 | must-fix |
| C3 | must-fix |
| C4 | must-fix |
| C5 | must-fix |
| C6 | should-fix |
| C7 | should-fix |

Do not treat the proposed labels as binding. You may confirm, weaken, strengthen, split, merge, or reject clusters if the evidence warrants it.

## Upstream Requirements Material

### Requirement 13

Purpose:

- Connect the single `next --json` action selector to operation contracts.
- Make all 19 `required_action` values machine-readable through operation contract fields.
- Avoid hidden representative values for branchy or compound actions.

Required transfer:

- Map all 19 `required_action` values to `effect_kind`, actor, `approval_required`, `phase_boundary`, `sequence`, branching, and referenced preconditions / postconditions.
- Include `run_maintenance`, `run_reopen_pending_gate`, and `run_workflow_stage` branch details.
- Keep operation contract and operation registry boundaries single-source and machine-readable.
- `record_human_decision` must not by itself satisfy an `approval_required=true` target operation.

Forbidden drift:

- Do not let tasks invent missing operation contract policy.
- Do not duplicate or redefine contract fields in the registry.
- Do not make preflight a separate authority from operation contract / registry.

### Requirement 14

Purpose:

- Make approval gates, side tracks, and workflow-state snapshots machine-readable.
- Distinguish proxy-allowed judgment from human-only approval.

Required transfer:

- Approval decisions bind target operation ID, target `required_action`, artifact or staged file set digest, actor, timestamp, and source.
- Human-only decisions include commit, push, `spec.json` update, phase approval, reopen finalize, and approval-required irreversible operation execution.
- Proxy model may judge findings or auxiliary triage, but cannot replace human-only approval.

Forbidden drift:

- Do not allow proxy_model to authorize phase approval or irreversible operations.
- Do not leave approval record binding weak enough that an approval record cannot be tied to its target operation.

### Requirement 15

Purpose:

- Treat effective prompts as structured language-task specifications.
- Separate language-task review from mechanical operation execution.

Responsibility boundary:

- Language tasks define what an LLM should judge or produce.
- Mechanical tasks, operation execution, blocking, and guard enforcement remain owned by operation contracts, preflight, runners, and guards.

Required transfer:

- Prompt checks must be machine-checkable where required, including decision-point-specific bounds when length bounds are part of the check.
- The design must define where first-layer prompt check configuration lives when a check depends on decision-point-specific policy.
- The design must define the failure verdict or handling path for a failed first-layer prompt check.
- The design must keep LLM judge audit output structured enough for downstream triage.

Forbidden drift:

- Do not leave prompt validation rules as repeated manual judgment when the requirement expects machine-checkable checks.
- Do not turn LLM judge audit into authorization for operation execution or human-only approval.

### Requirement 16

Purpose:

- Implement selection-layer and execution-layer mechanization in Phase 0 through Phase 6 without mixing concerns.
- Distinguish active reopen scope from historical `spec.json.reopened`.
- Mechanize proxy_model triage decision evidence and human-required predicate.

Required transfer:

- Phase 0 completion includes the D-003 six failure tests and mechanical workflow-state repair detection.
- `spec.json.reopened` is historical and must not be treated as active reopen scope.
- Proxy triage must use evidence completeness, cluster coverage, approval gate record, operation contract `approval_required`, review-wave impact evidence, and human-only decision boundary.
- Human-required evidence always outranks proxy approval.

Forbidden drift:

- Do not make active reopen scope an implicit inference from historical flags.
- Do not let proxy triage bypass human-required predicates.
- Do not define Phase 0 completion only by unstable section references.

## Current Design Material

The following summaries identify the design areas cited by the review findings. For this proxy judgment, rely on the summaries and source finding content provided in this prompt. Do not assume direct file-system access to `design.md` or `requirements.md`. If a conclusion would require text not included here, mark the relevant cluster as `partially_valid` and explain what material is missing.

### Operation Contract / Registry / Preflight

- The architecture lists both `stages/operation-registry.yaml` and `stages/operation-contracts.yaml`.
- Requirement 13 design states that `stages/operation-contracts.yaml` is the operation contract physical source of truth, while `stages/operation-registry.yaml` references operation contract ID, digest, and schema version.
- The design also contains earlier text that can be read as placing operation contract schema in `stages/operation-registry.yaml`.
- The design says registry / preflight reads contracts and does not execute, update, or consume approvals.
- The design says duplicated contract fields in the registry should fail closed, but reviewers questioned whether this is a schema-level prohibition or only a runtime integrity check.

### Required Action Mapping

- The design defines the 19 `required_action` vocabulary in `.reviewcompass/schema/required_action.schema.json`.
- The design includes a partial operation mapping and an explicit branch table for `run_reopen_pending_gate`.
- Reviewers say the mapping does not enumerate all 19 values individually with all required fields.
- The design says `run_maintenance` and `run_workflow_stage` are compound operations, but reviewers say concrete branches, internal steps, max side effects, and approval aggregation rules are missing.

### Approval Records and Proxy / Human Boundary

- The design defines an approval gate record with target operation, target `required_action`, artifact digest, staged file set digest, decision, actor, timestamp, source, and `decision_scope`.
- It says `decision_scope` has `human_only`, `proxy_allowed`, and `advisory_only`.
- It says `decided_by=proxy_model` with `decision_scope=human_only` does not count as approval.
- Reviewers say the design does not define how `decision_scope` is assigned per operation / `required_action`.
- Reviewers also found an older approval-stage example that still allows `proxy_model` for approval, while Requirement 14 requires phase approval to be human-only.

### Active Reopen Scope

- The design says `spec.json.reopened` may remain as historical record and must not be treated as current active reopen scope.
- The design says current scope, impact review scope, direct / indirect feature, and flag policy are distinguished in in-progress reopen record, classification record, `spec.json.recheck`, and review-wave / alignment evidence.
- Reviewers say the authoritative active reopen scope field, file, initialization, and clearing rules are not defined clearly enough.

### Phase 0 and D-003 Traceability

- The design defines Phase 0 as the D-003 selection layer: 19-step priority, `required_action` uniqueness, invariant checks, and reopen plan compiler / `reopen-recompile`.
- The design says Phase 0 stable anchor is `docs/notes/working/2026-06-16-next-json-unique-state-redesign.md`.
- The design says if section numbers change, the six D-003 failure tests should be copied to tasks or implementation acceptance units.
- Reviewers say Phase 0 completion either omits mechanical workflow-state repair detection or is not self-contained because the six tests are not enumerated in design.

### Prompt Length Bound

- The design lists first-layer structured prompt checks.
- Reviewers say the check for prompt length within decision-point-specific bounds lacks a source of truth, owner, and failure verdict.

### Drafting Status Versus Implemented Status

- The design says Requirement 13 through 16 operation contract, side track stack, structured effective prompt, workflow-state snapshot, and proxy_model triage decision mechanization remain future tasks / implementation.
- Reviewers say some wording elsewhere describes implementation-first contracts as already established or design-followed, blurring current design approval status.

## Source Findings By Cluster

### C1: operation contract / registry / preflight authority boundary is not settled

Main proposed label: `must-fix`

Finding IDs:

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-001`
- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-002`
- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-008`

Disposition requirement:

- Decide each listed finding as adopted or rejected. Do not omit `adversarial-008` merely because it was previously described as related.

Source finding summary:

- GPT says operation registry / contract authority is internally contradictory between `stages/operation-registry.yaml` and `stages/operation-contracts.yaml`.
- GPT says precheck vocabulary and output contract authority appear to belong to docs and script implementation rather than registry / contract artifacts.
- Claude says registry schema boundary is not explicit enough because duplicated contract fields may be interpreted as runtime rejection rather than schema-level prohibition.

### C2: 19 required_action mapping and compound operation details are incomplete

Main proposed label: `must-fix`

Finding IDs:

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-001`
- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-002`

Source finding summary:

- Claude says the design does not individually map all 19 `required_action` values to operation contract fields.
- Claude says `run_maintenance` and `run_workflow_stage` lack concrete branch conditions, internal steps, max effect, and approval aggregation rules.

### C3: approval record binding and proxy / human boundary remain under-specified or contradictory

Main proposed label: `must-fix`

Finding IDs:

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-003`
- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-004`
- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-003`
- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-004`
- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-009`

Disposition requirement:

- Decide each listed finding as adopted or rejected. Do not omit `adversarial-009` merely because it was previously described as related.

Source finding summary:

- GPT says approval records leave artifact digest and staged file set digest as optional alternatives without an operation-type rule requiring the correct binding.
- GPT says an older approval-stage example allows `proxy_model` for phase approval while Requirement 14 says phase approval is human-only.
- Claude says `decision_scope` assignment is not machine-checkable per operation / required_action.
- Claude says proxy triage predicates are not connected strongly enough to operation contract preconditions.
- Claude adds a non-blocking traceability point about linking `record_human_decision` to `decision_scope`.

### C4: active reopen scope has no clear authoritative state structure

Main proposed label: `must-fix`

Finding IDs:

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-005`

Source finding summary:

- Claude says the design correctly distinguishes historical `spec.json.reopened` from active scope, but does not define the active scope's authoritative field, file, initialization, clearing, or `next --json` read path.

### C5: Phase 0 completion criteria and D-003 traceability are not fully design-level

Main proposed label: `must-fix`

Finding IDs:

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-005`
- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-007`

Disposition requirement:

- Decide each listed finding as adopted or rejected. Do not omit `adversarial-007` merely because it was previously described as related.

Source finding summary:

- GPT says Phase 0 completion criteria omit mechanical workflow-state repair detection.
- Claude says the design references the six D-003 failure tests but does not enumerate them, leaving weak traceability to a working note.

### C6: structured prompt length-bound check lacks an implementable source of truth

Main proposed label: `should-fix`

Finding IDs:

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-006`

Source finding summary:

- Claude says prompt length bounds are required to be decision-point-specific, but the design does not say where they are stored, who sets them, or what verdict applies.

### C7: design overclaims or blurs current drafting status versus implemented status

Main proposed label: `should-fix`

Finding IDs:

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-006`

Source finding summary:

- GPT says some sections describe implementation-first contracts as already established or design-followed, while other sections say Requirement 13 through 16 work remains future tasks / implementation.

## Judgment Question

Judge whether each cluster identifies a real design-level issue that should affect the current design triad-review before moving forward.

Do not merely choose from main's proposed labels. You may confirm, weaken, strengthen, split, merge, or reject each cluster if the evidence supports that decision.

For each cluster, assess:

1. Whether the cluster is valid.
2. Whether it is design-level or can safely be deferred to tasks / implementation.
3. Whether main's proposed label is appropriate.
4. What design response is required, if any.
5. What downstream risk remains if it is not fixed.

Do not authorize commit, push, `spec.json` mutation, phase transition, gate completion, or direct edits.

## Output Contract

Return YAML only.

Allowed values:

- `final_label`: `must-fix`, `should-fix`, or `leave-as-is`
- `validity`: `valid`, `partially_valid`, or `invalid`
- `design_level`: boolean. `true` means the issue must be resolved at design phase before this triad-review can complete; `false` means it can safely be deferred to tasks / implementation without design-phase policy invention.

```yaml
review_run_id: 2026-06-20-workflow-management-design-vertical-redo-review-run-v2
proxy_decision_scope: design_triad_review_cluster_triage
cluster_decisions:
  - cluster_id: C1
    final_label: must-fix
    validity: valid
    design_level: true
    adopted_findings:
      - <finding id>
    rejected_findings:
      - finding_id: <finding id>
        reason: <why this finding is rejected or not adopted>
    decision_rationale: <why this label and validity are correct>
    required_design_response:
      - <what design.md must clarify/change, or empty list if none>
    downstream_risk_if_unfixed: <risk, or "none">
    notes_for_main:
      - <optional instruction for later human-facing triage / implementation planning>
authority_limits_confirmed:
  commit: not_authorized
  push: not_authorized
  spec_json_update: not_authorized
  phase_transition: not_authorized
  direct_file_edit: not_authorized
```

Do not include Markdown fences in the actual response.

