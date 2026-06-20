prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.1-pro-preview

# Task
Review the target document for the requested phase and criteria.

# Phase
prompt_quality

# Criteria
---
criteria_id: proxy-decision-prompt-quality-review
phase: prompt-quality
review_target: proxy-decision-prompt-draft.md
---

# Proxy Decision Prompt Quality Review Criteria

Review the target prompt draft itself. Do not judge the C1-C7 clusters yet.

The question is:

Is the draft prompt suitable to give to a proxy_model for deciding C1-C7 cluster validity, final triage labels, and required design responses for the `workflow-management` design triad-review?

If user-provided review requirements exist, also judge whether the draft prompt preserves and operationalizes those requirements without unauthorized narrowing, broadening, replacement, or added authority.

## Required Quality Checks

Check both general LLM-as-Judge prompt quality and the workflow-specific proxy decision requirements.

### General API Review Prompt Quality

The prompt draft must:

1. Show that main identified the materials and judgment points before sending the prompt.
2. Include enough background and related context for the model to avoid guessing.
3. Ask a non-leading analysis question.
4. Define a scope that is neither too broad nor too narrow.
5. Provide or rely on a fixed, parser-friendly output contract when combined with the API review runner template.
6. Avoid credentials, personal data, or unrelated confidential material.
7. Keep prompt-review target, proxy judgment target, source materials, and out-of-scope operations distinct.

### User Review Requirements Fit

The prompt draft must:

1. Preserve the user instruction to use proxy_model for judgment.
2. Preserve the later user correction that the newly created prompt-review mechanism must be used before proxy_model judgment.
3. Map those requirements into the review task, required checks, out of scope, and finding policy.
4. Avoid narrowing the requested review so that any C1-C7 cluster is silently omitted.
5. Avoid broadening the requested review into direct edits, implementation, commit, push, `spec.json` updates, or gate completion.
6. Avoid replacing the requested proxy judgment with a generic design review.
7. Mark assumptions explicitly when the user requirement is ambiguous.

### Proxy Decision Requirements

The prompt draft must:

1. Ask proxy_model to decide cluster validity, final label, adopted / rejected findings, required design response, and downstream risk.
2. Allow proxy_model to confirm, weaken, strengthen, split, merge, or reject clusters instead of forcing a closed choice.
3. Include source finding IDs and enough source finding content for traceability.
4. Include model-result context and target identity for the v2 review-run.
5. Include upstream requirements context for Requirement 13 through 16.
6. Include current design context relevant to each cluster.
7. Keep proxy_model from authorizing human-only or irreversible operations.
8. Produce output that can be converted into proxy decision YAML without losing cluster / finding traceability.

### Vertical Intent Transfer Requirements

Because this is a design triad-review decision, the prompt draft must:

1. Limit target judgment to the current design phase artifact and the C1-C7 review clusters.
2. Use requirements material only for background and intent-transfer checking.
3. Include upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, and intended design transfer where relevant.
4. Prevent the model from judging downstream tasks or implementation correctness unless downstream invention would be forced by a design omission.

## Finding Policy

- Report `CRITICAL` if the draft prompt would authorize or imply authorization of commit, push, `spec.json` update, phase transition, gate completion, direct edits, or human-only approval.
- Report `CRITICAL` if the draft prompt would violate a user-stated prohibited action or authority limit.
- Report `ERROR` if the draft prompt omits, weakens, broadens, or replaces the user-stated proxy judgment requirement.
- Report `ERROR` if the draft prompt would likely cause proxy_model to judge the wrong target, rely only on main's labels, omit any C1-C7 cluster, miss required upstream-transfer obligations, or produce output unusable as proxy decision evidence.
- Report `WARN` if the draft prompt is usable but has avoidable ambiguity, framing bias, incomplete source-material presentation, weak target/source/out-of-scope separation, or incomplete mapping from user requirements to checks.
- Report `INFO` for minor wording or ergonomics improvements.
- Return `findings: []` only if the draft prompt is safe to use for the intended proxy_model judgment.

## Output Contract

Return YAML only with top-level key `findings`.

Each finding must include:

- `severity`: CRITICAL, ERROR, WARN, or INFO
- `target_location`: specific section in the prompt draft
- `description`: concise finding summary
- `rationale`: why this matters for proxy decision prompt quality

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
duration_seconds: 31.488
findings:
- severity: WARN
  target_location: '## Context / V2 model results table'
  description: Model identifiers in the v2 results table ('gpt-5.4', 'gemini-3.1-pro-preview')
    are non-standard or unverifiable names. If proxy_model cannot verify these as
    canonical model IDs, it may silently distrust or misattribute finding provenance.
  rationale: Source finding traceability depends on proxy_model being able to match
    finding IDs to roles. Implausible model names may cause proxy_model to flag uncertainty
    rather than proceeding, or to weight findings inconsistently. This is avoidable
    ambiguity without affecting correctness of the prompt structure.
- severity: WARN
  target_location: '## Source Findings By Cluster / C3 / Finding IDs'
  description: Finding 'claude-sonnet-4-6-adversarial-009' is listed as 'related'
    in C3 but appears nowhere else in the prompt. Its content ('non-blocking traceability
    point about linking record_human_decision to decision_scope') is summarized but
    its relationship to the adopted vs. rejected decision is left open. Proxy_model
    has no guidance on whether to treat 'related' as a candidate for adoption or as
    pre-rejected.
  rationale: The output contract requires explicit adopted_findings and rejected_findings
    lists. A 'related' finding with no disposition guidance could cause proxy_model
    to omit it from both lists, breaking finding traceability for C3.
- severity: WARN
  target_location: '## Source Findings By Cluster / C1 / Finding IDs'
  description: 'Finding ''claude-sonnet-4-6-adversarial-008'' is also listed as ''related''
    in C1 without a disposition hint. Same traceability gap as C3''s adversarial-009:
    proxy_model may omit it from adopted_findings and rejected_findings.'
  rationale: Consistent with the C3 issue above. The output contract provides no 'related'
    slot, so findings marked only as 'related' risk falling through without a recorded
    decision.
- severity: WARN
  target_location: '## Current Design Material'
  description: The section header states 'They are not a substitute for the target
    artifact' but the prompt never instructs proxy_model to read the actual target
    artifact path. The target path '.reviewcompass/specs/workflow-management/design.md'
    is named in the Review object section but no instruction tells proxy_model whether
    it has access to that file or must rely solely on the summaries provided.
  rationale: If proxy_model assumes it has file-system access it does not have, it
    may hallucinate design content. If it assumes it must only use the summaries,
    it may mark findings as unverifiable. The ambiguity could degrade decision quality
    for every cluster. An explicit statement ('rely on the summaries provided; the
    full artifact is not attached') or the actual attachment would remove this risk.
- severity: WARN
  target_location: '## Upstream Requirements Material / Requirement 15'
  description: Requirement 15 is presented with less detail than Requirements 13,
    14, and 16. It has no 'Required transfer' sub-fields that itemize what proxy_model
    should check against design. C6 (prompt length-bound check) depends primarily
    on Requirement 15, meaning proxy_model has thinner context for judging that cluster.
  rationale: The vertical intent transfer rules require upstream purpose, responsibility
    boundaries, and acceptance criteria to be present where relevant. The lighter
    treatment of Requirement 15 creates an asymmetry that could lead to a weaker or
    under-reasoned C6 decision.
- severity: INFO
  target_location: '## Output Contract / YAML template'
  description: The output contract YAML template uses inline pipe-separated alternatives
    (e.g., 'must-fix | should-fix | leave-as-is', 'true | false', 'valid | partially_valid
    | invalid') inside quoted strings. A parser consuming raw YAML will receive the
    literal pipe-delimited string rather than an enumerated value, requiring a secondary
    parsing step.
  rationale: The criteria require output usable as proxy decision YAML without loss
    of traceability. Pipe-delimited enum hints inside string values are a documentation
    convention, not a machine-readable enum constraint. Replacing them with YAML comments
    or an explicit enum note would make the contract more directly parser-friendly.
- severity: INFO
  target_location: '## Judgment Question / assessment point 2'
  description: 'The question asks whether a cluster ''can safely be deferred to tasks
    / implementation'' but the output contract field is named ''design_level: true
    | false''. The mapping is implicit. Adding a one-line gloss (e.g., ''design_level:
    true means the issue must be resolved at design phase; false means it can be deferred'')
    would prevent proxy_model from inverting the boolean.'
  rationale: 'Minor but avoidable inversion risk. Proxy_model must emit ''design_level:
    false'' to mean ''deferrable'', which is counterintuitive without an explicit
    note.'
- severity: INFO
  target_location: '## User Review Requirements / Requirement-to-prompt mapping'
  description: The mapping entry for the user correction ('先ほど作成したプロンプトレビューの仕組みはつかわないのか')
    explains that this draft is subject to prompt quality review before proxy_model
    use. This is correct procedurally but proxy_model, receiving this prompt, cannot
    act on that mapping entry. Including it as a judgment instruction rather than
    a traceability note could cause minor confusion.
  rationale: The entry is useful for audit traceability but serves no decision function
    for proxy_model. Labeling it explicitly as 'traceability note, not a judgment
    instruction' would prevent proxy_model from trying to apply it as a check.


# 前段所見 2：
role: primary
provider: openai-api
model: gpt-5.5
attempts: 1
duration_seconds: 35.891
findings:
- severity: ERROR
  target_location: Output Contract / authority_limits_confirmed
  description: The required authority-limit confirmation omits several prohibited
    authorities that the prompt itself identifies or imports from Requirement 14.
  rationale: The prompt requires explicit confirmation of authority limits, but the
    output schema only covers commit, push, spec_json_update, phase_transition, and
    direct_file_edit. It does not require explicit confirmation for gate completion,
    human-only approval substitution, reopen finalize, or approval-required irreversible
    operation execution. This weakens the proxy/human boundary that is central to
    the cluster triage.
- severity: WARN
  target_location: Output Contract / final_label and design_level
  description: The relationship between final_label and design_level is underdefined
    and can produce contradictory triage outputs.
  rationale: The schema defines design_level=true as meaning the issue must be resolved
    before triad-review can complete, which appears equivalent to must-fix, but final_label
    also allows should-fix without defining whether should-fix is blocking or deferrable.
    A proxy model could return should-fix with design_level=true or must-fix with
    design_level=false, leaving main without an unambiguous gate decision.
- severity: WARN
  target_location: Output Contract / cluster_decisions
  description: The schema does not include an explicit cluster adoption or rejection
    field even though the prompt asks the proxy to decide adopted clusters.
  rationale: Validity, final_label, adopted_findings, and rejected_findings provide
    partial information, but they do not directly state whether the cluster as a whole
    is adopted for design response. This can be ambiguous for partially_valid clusters
    or for clusters with mixed adopted and rejected source findings.


# 前段所見 3：
role: judgment
provider: gemini-api
model: gemini-3.1-pro-preview
attempts: 1
duration_seconds: 43.165
findings:
- severity: WARN
  target_location: Output Contract / YAML template
  description: 'Instructions for empty values (e.g., `or use [] if none`) are placed
    inside list item markers and string field placeholders. For example, `- <finding
    id, or use [] if none>` encourages the model to output a nested empty list (`-
    []`) rather than an empty parent array (`adopted_findings: []`). Similarly, using
    `[]` for an empty `reason` string creates a type mismatch.'
  rationale: The criteria require a fixed, parser-friendly output contract. Injecting
    `[]` into list elements or string fields will likely cause schema validation failures
    (e.g., List[List] instead of List[str], or List instead of str) in strict downstream
    YAML parsers, making the decision evidence unusable without manual correction.


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
- Produce one item in `decisions` per cluster.
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

Do not treat the proposed labels as binding. You may confirm, weaken, strengthen, or reject clusters if the evidence warrants it. If you think clusters should be split or merged, still return one decision item for each original cluster C1-C7 and describe the split/merge recommendation in `notes_for_main`.

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

Do not merely choose from main's proposed labels. You may confirm, weaken, strengthen, or reject each cluster if the evidence supports that decision.

If you think clusters should be split or merged, keep the output shape stable by returning one decision item for each original cluster C1-C7. Put the split/merge recommendation in `notes_for_main`.

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
- `cluster_adopted`: boolean. `true` means the cluster is adopted into design triad-review response; `false` means the cluster is rejected as a cluster even if individual findings are documented.
- `blocking`: boolean. `true` means design triad-review should not complete until the required design response is addressed; `false` means the issue may be tracked without blocking this gate.
- `design_level`: boolean. `true` means the issue belongs to design phase; `false` means it can safely be deferred to tasks / implementation without design-phase policy invention.

Consistency rules:

- `final_label: must-fix` must use `cluster_adopted: true`, `blocking: true`, and `design_level: true`.
- `final_label: should-fix` must use `cluster_adopted: true`, `blocking: false`, and may use `design_level: true` or `false` with rationale.
- `final_label: leave-as-is` must use `cluster_adopted: false`, `blocking: false`, and an empty `required_design_response`.

Set `proxy_model_id` to the actual model ID executing this proxy judgment. Do not copy the placeholder literally.

```yaml
proxy_model_id: <actual proxy model id>
decision_prompt_path: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-proxy-decision-prompt-quality-run/proxy-decision-prompt-draft.md
raw_response_path: proxy-decision-response.yaml
review_run_id: 2026-06-20-workflow-management-design-vertical-redo-review-run-v2
proxy_decision_scope: design_triad_review_cluster_triage
decisions:
  # Repeat this item shape for each original cluster C1 through C7.
  - cluster_id: <C1-C7>
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

