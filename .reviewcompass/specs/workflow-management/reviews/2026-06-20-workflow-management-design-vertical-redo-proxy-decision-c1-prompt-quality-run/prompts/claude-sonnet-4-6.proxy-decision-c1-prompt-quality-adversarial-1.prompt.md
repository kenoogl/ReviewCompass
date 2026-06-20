prompt_id: anthropic_review
provider: anthropic-api
model_id: claude-sonnet-4-6

# Task
Review the target document for the requested phase and criteria.

# Phase
prompt_quality

# Criteria
---
criteria_id: proxy-decision-c1-prompt-quality-review
phase: prompt-quality
review_target: proxy-decision-c1-prompt.md
---

# Proxy Decision C1 Prompt Quality Review Criteria

Review the target prompt draft itself. Do not decide C1.

The question is:

Is the draft prompt suitable to give to a proxy_model for deciding only C1, the operation contract / registry / preflight authority boundary cluster, in the `workflow-management` design triad-review?

## Required Quality Checks

### User Review Requirements Fit

The prompt draft must:

1. Preserve the instruction to judge items individually.
2. Judge C1 only and exclude C2-C7.
3. Ask for cluster validity, final label, adopted / rejected findings, required design response, and downstream risk.
4. Avoid direct edits, implementation, commit, push, `spec.json` update, gate completion, or human-only approval.

### Judgment Granularity

The prompt draft must:

1. Contain one primary judgment question.
2. Avoid bundling multiple independent clusters or design-policy judgments.
3. Include only source findings and materials needed for C1.
4. Keep common background short enough that C1-specific evidence remains central.

### Source-Material Quality

The prompt draft must:

1. Clearly distinguish review target, source materials, source findings, and out-of-scope work.
2. Include enough Requirement 12 / 13 context to judge operation contract / registry / preflight authority.
3. Include the current design material relevant to C1 in model-readable form.
4. Include all C1 source finding IDs and enough finding content for traceability.
5. Avoid path-only source material listing as the only basis for judgment.

### Output And Triage Fit

The prompt draft must:

1. Return output compatible with `tools/api_providers/run_proxy_decision.py`: top-level `proxy_model_id` and `decisions` list.
2. Require every C1 source finding ID to be adopted or rejected.
3. Define allowed labels and consistency rules.
4. Confirm authority limits explicitly.
5. Avoid parser-hostile placeholders or ambiguous empty-list instructions.

## Finding Policy

- Report `CRITICAL` if the draft prompt would authorize or imply authorization of commit, push, `spec.json` update, phase transition, gate completion, direct edits, or human-only approval.
- Report `ERROR` if the draft prompt judges anything beyond C1, omits a C1 source finding, lacks required Requirement 12 / 13 context, or produces output unusable by `run_proxy_decision.py`.
- Report `WARN` if the draft prompt is usable but has avoidable ambiguity, framing bias, incomplete source-material presentation, or weak target/source/out-of-scope separation.
- Report `INFO` for minor wording or ergonomics improvements.
- Return `findings: []` only if the draft prompt is safe to use for the intended C1 proxy_model judgment.

## Output Contract

Return YAML only with top-level key `findings`.

Each finding must include:

- `severity`: CRITICAL, ERROR, WARN, or INFO
- `target_location`: specific section in the prompt draft
- `description`: concise finding summary
- `rationale`: why this matters for C1 proxy decision prompt quality

If there are no findings, return exactly:

findings: []


# Output contract
Return YAML only.
The top-level key must be exactly findings.
Do not use review: as a wrapper.
Do not use result:, metadata:, or summary: as wrappers.
Do not wrap the YAML in Markdown code fences.
Do not include ```yaml or any other fence marker.
Do not write explanatory prose before or after the YAML.

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
.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-proxy-decision-c1-prompt-quality-run/proxy-decision-c1-prompt.md

# Target document
---
prompt_id: workflow-management-design-v2-proxy-decision-c1
phase: design
gate: stages/design.yaml#triad-review
cluster_id: C1
status: draft_for_prompt_quality_review
---

# Proxy Model Judgment Prompt: C1

## Execution Metadata For This Run

This prompt is bound to the `proxy_model_openai_gpt_55` variant for this run.

- `proxy_model_id`: `gpt-5.5`
- `decision_prompt_path`: `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-proxy-decision-c1-prompt-quality-run/proxy-decision-c1-prompt.md`

## User Review Requirements

Use proxy_model to judge only C1 from the v2 design review. Do not judge C2-C7 in this prompt.

Review purpose:

- Decide whether C1 identifies a real design-level issue in the current `workflow-management` design triad-review.
- Decide C1's final triage label: `must-fix`, `should-fix`, or `leave-as-is`.
- Decide which C1 source findings are adopted or rejected.
- Decide what design response is required if C1 is adopted.

Review object:

- Cluster: C1 only.
- Review-run: `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/`
- Target artifact under review: `.reviewcompass/specs/workflow-management/design.md`
- Upstream source material: `.reviewcompass/specs/workflow-management/requirements.md`

Review focus:

- Operation contract / registry / preflight authority boundary.
- Whether the design leaves more than one source of truth for operation contract vocabulary, output contract, or preflight authority.
- Whether this is a design-level issue or can safely be deferred to tasks / implementation.

Out of scope:

- Do not judge C2-C7.
- Do not edit `design.md`.
- Do not update `spec.json`.
- Do not move the design gate or authorize phase completion.
- Do not authorize commit or push.
- Do not authorize human-only approvals or irreversible operations.

## Context

Current workflow state:

- Reopen procedure is in progress.
- Current gate: `stages/design.yaml#triad-review`.
- Requirements approval is complete.
- Design drafting is complete.
- The v2 design review corrected the earlier target-selection issue and reviewed `.reviewcompass/specs/workflow-management/design.md`.

V2 model result context:

- `gpt-5.4` returned 6 findings.
- `claude-sonnet-4-6` returned 9 findings.
- `gemini-3.1-pro-preview` returned no findings.

Use finding IDs for traceability. Do not reject a finding only because a model label is unfamiliar.

## Upstream Requirements Material

### Requirement 12 Context

Purpose:

- Treat operation registry / preflight as a unified read-only operation-start check.
- Prevent preflight from becoming an independent authority that can drift from workflow contracts.

Required transfer to design:

- Preflight reads operation definitions and state evidence before an operation starts.
- Preflight does not execute operations, update contracts, consume approvals, or mutate workflow state.
- `next --json` remains the action selector; registry / preflight must not invent a parallel source of action truth.

Forbidden drift:

- Do not let operations docs, scripts, or preflight implementation become the canonical source of operation vocabulary or output contract when a machine-readable contract / registry model is required.

### Requirement 13

Purpose:

- Connect the single `next --json` action selector to operation contracts.
- Make each `required_action` machine-readable through operation contract fields.
- Keep operation contract and registry / preflight boundaries single-source and machine-readable.

Required transfer to design:

- Define where operation contract source of truth lives.
- Define what the operation registry owns and what it may only reference.
- Define that registry / preflight read contracts but do not redefine contract fields.
- Detect drift or duplication between registry and contract fail-closed.

Forbidden drift:

- Do not leave both `stages/operation-registry.yaml` and `stages/operation-contracts.yaml` plausible as operation contract authorities.
- Do not allow registry schema or operations docs to redefine `effect_kind`, `approval_required`, `phase_boundary`, or equivalent contract fields.
- Do not leave tasks to decide whether registry field duplication is structurally forbidden or only rejected later by an integrity check.

## Current Design Material Relevant To C1

The following summaries are the available design material for this proxy judgment. Rely on this prompt's summaries and source finding content. Do not assume direct file-system access to `design.md` or `requirements.md`. If text not included here is necessary for a definitive answer, mark C1 as `partially_valid` and explain what is missing.

Current design statements summarized from `design.md`:

- The repository structure lists both `stages/operation-registry.yaml` and `stages/operation-contracts.yaml`.
- The architecture section names `stages/operation-registry.yaml` as operation registry / preflight binding for Requirements 12 and 13.
- The architecture section names `stages/operation-contracts.yaml` as operation contract source of truth for Requirement 13.
- Requirement 13 design states that `stages/operation-contracts.yaml` is the physical source of truth for operation contracts.
- Requirement 13 design states that `stages/operation-registry.yaml` references operation contract ID, contract digest, and schema version.
- Requirement 13 design states that the registry owns canonical invocation, workflow binding, required inputs, target identity, planned outputs, sequence mode, worktree / pending / artifact policy, and contract references.
- Requirement 13 design states that registry / preflight reads contracts and does not execute operations, update contracts, create workflow state, consume approvals, or mutate artifacts.
- Requirement 13 design includes fail-closed integrity conditions for contract / registry drift and duplicated contract fields.
- Reviewers identified earlier wording that can be read as placing operation contract schema in `stages/operation-registry.yaml`.
- Reviewers also identified wording that appears to assign precheck vocabulary and output contract authority to operations docs and script implementation rather than to operation contract / registry artifacts.

## Source Findings For C1

### Finding C1-F1

Finding ID:

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-001`

Severity:

- `ERROR`

Target location:

- Requirement 12 design model §1, architecture, Requirement 13 design model §3

Finding summary:

- The design is internally contradictory about operation registry / contract authority.
- One part says operation contract schema is placed in `stages/operation-registry.yaml`.
- Other parts say `stages/operation-contracts.yaml` is the contract source of truth and registry only references it.

Rationale:

- Requirements 12 and 13 need a single machine-readable source-of-truth boundary between operation contract and registry / preflight.
- If two files can both look canonical, downstream tasks must invent which file is authoritative.

### Finding C1-F2

Finding ID:

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-002`

Severity:

- `ERROR`

Target location:

- Architecture, Requirement 12 design model §1, lightweight check script model §1

Finding summary:

- The design assigns precheck vocabulary and output contract source of truth to operations docs and script implementation rather than registry / contract artifacts.

Rationale:

- Requirement 13 requires the operation contract / registry boundary to be the machine-readable source of truth.
- Requirement 12 warns against making preflight a separate authority.
- If docs or scripts own the vocabulary / output contract, design, registry, and code can drift.

### Finding C1-F3

Finding ID:

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-008`

Severity:

- `WARN`

Target location:

- Requirement 13 design model §5, registry / preflight read-only boundary

Finding summary:

- The design says duplicated contract fields in the registry fail closed, but does not explicitly state that registry schema structurally forbids `effect_kind`, `approval_required`, or `phase_boundary`.
- This can be read as a runtime guard rather than a schema-level prohibition.

Rationale:

- Requirement 13 requires a clear single machine-readable source-of-truth boundary.
- The distinction between schema-level prohibition and runtime rejection affects downstream task and implementation scope.

## Judgment Question

Judge whether C1 identifies a real design-level issue that should affect the current design triad-review before moving forward.

Do not merely confirm the main proposal. You may confirm, weaken, strengthen, or reject C1 if the evidence supports that decision.

Assess:

1. Whether C1 is valid.
2. Whether C1 is design-level or can safely be deferred to tasks / implementation.
3. Whether C1 should be `must-fix`, `should-fix`, or `leave-as-is`.
4. Which C1 source findings are adopted or rejected.
5. What design response is required, if any.
6. What downstream risk remains if C1 is not fixed.

Do not authorize commit, push, `spec.json` mutation, phase transition, gate completion, direct edits, human-only approval substitution, reopen finalize, or approval-required irreversible operation execution.

## Output Contract

Return YAML only.

Allowed values:

- `final_label`: `must-fix`, `should-fix`, or `leave-as-is`
- `validity`: `valid`, `partially_valid`, or `invalid`
- `cluster_adopted`: boolean
- `blocking`: boolean
- `design_level`: boolean

Consistency rules:

- Every C1 source finding ID listed above must appear exactly once in `adopted_findings` or `rejected_findings`.
- `final_label: must-fix` must use `cluster_adopted: true`, `blocking: true`, and `design_level: true`.
- `final_label: should-fix` must use `cluster_adopted: true`, `blocking: false`, and may use `design_level: true` or `false` with rationale.
- For `final_label: should-fix` with `design_level: false`, `required_design_response` may be an empty array if the response should be deferred to tasks / implementation.
- `final_label: leave-as-is` must use `cluster_adopted: false`, `blocking: false`, and an empty `required_design_response`.

Use the execution metadata given above for `proxy_model_id` and `decision_prompt_path`.

```yaml
proxy_model_id: gpt-5.5
decision_prompt_path: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-proxy-decision-c1-prompt-quality-run/proxy-decision-c1-prompt.md
raw_response_path: proxy-decision-c1-response.yaml
review_run_id: 2026-06-20-workflow-management-design-vertical-redo-review-run-v2
proxy_decision_scope: design_triad_review_cluster_triage
decisions:
  - cluster_id: C1
    final_label: <must-fix | should-fix | leave-as-is>
    validity: <valid | partially_valid | invalid>
    cluster_adopted: <true | false>
    blocking: <true | false>
    design_level: <true | false>
    adopted_findings:
      - <finding id>
    rejected_findings:
      - finding_id: <finding id>
        reason: <why this finding is rejected or not adopted>
    decision_rationale: <why this label and validity are correct>
    required_design_response:
      - <what design.md must clarify/change>
    downstream_risk_if_unfixed: <risk, or "none">
    notes_for_main:
      - <optional instruction for later human-facing triage / implementation planning>
authority_limits_confirmed:
  commit: not_authorized
  push: not_authorized
  spec_json_update: not_authorized
  gate_completion: not_authorized
  phase_transition: not_authorized
  direct_file_edit: not_authorized
  human_only_approval_substitution: not_authorized
  reopen_finalize: not_authorized
  approval_required_irreversible_operation: not_authorized
```

For empty arrays, use the parent key with an empty array value, for example:

```yaml
adopted_findings: []
rejected_findings: []
required_design_response: []
notes_for_main: []
```

Do not include Markdown fences in the actual response.

