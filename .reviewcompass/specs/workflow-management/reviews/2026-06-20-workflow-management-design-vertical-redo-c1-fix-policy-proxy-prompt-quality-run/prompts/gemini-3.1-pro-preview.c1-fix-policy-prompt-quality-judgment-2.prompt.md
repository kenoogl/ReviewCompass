prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.1-pro-preview

# Task
Review the target document for the requested phase and criteria.

# Phase
prompt_quality

# Criteria
---
criteria_id: proxy-decision-c1-fix-policy-prompt-quality-review
phase: prompt-quality
review_target: proxy-decision-c1-fix-policy-prompt.md
---

# C1 Fix Policy Proxy Prompt Quality Review Criteria

Review the target prompt draft itself. Do not judge the eventual `design.md` fix yet.

Question:

Is the draft prompt suitable for asking `proxy_model` to judge the C1 fix policy, given the prior C1 `must-fix / blocking` decision and the current workflow constraints?

## Required Checks

The prompt draft must:

1. Preserve the user request to use proxy mode for C1 response policy instead of main-session unilateral approval.
2. Keep the judgment limited to C1 fix policy, not C2-C7.
3. Include enough prior C1 decision material and relevant design excerpts for the proxy model to judge without guessing.
4. Ask a non-leading question that permits confirming, modifying, rejecting, or replacing the main session's Policy A.
5. Avoid forcing a closed A/B/C choice.
6. Distinguish prior proxy decision, current design material, main-session proposed policy, judgment question, and out-of-scope operations.
7. Avoid authorizing direct file edits, `spec.json` updates, gate completion, phase transition, commit, push, human-only approval substitution, reopen finalization, or irreversible operations.
8. Use a parser-friendly YAML output contract.
9. Avoid credentials, tokens, passwords, nonces, personal identifiers, third-party confidential material, and unrelated full logs.
10. Keep the source material to the minimum needed for this single judgment.

## Finding Policy

- Report `CRITICAL` if the prompt authorizes or implies authorization of irreversible operations, gate completion, human-only approvals, or direct edits.
- Report `ERROR` if the prompt asks the wrong question, combines independent judgments, omits material needed to judge C1 fix policy, or forces a closed choice.
- Report `WARN` if the prompt is usable but has avoidable ambiguity, weak source/target separation, output contract weakness, or mildly leading wording.
- Report `INFO` for minor wording or ergonomics issues.
- Return `findings: []` only if the prompt is safe to use for the intended proxy_model judgment.

## Output Contract

Return YAML only with top-level key `findings`.

If there are no findings, return exactly:

```yaml
findings: []
```

Each finding must include:

```yaml
severity: CRITICAL | ERROR | WARN | INFO
target_location: string
description: string
rationale: string
```


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
duration_seconds: 21.951
findings:
- severity: WARN
  target_location: '## Main Session''s Proposed Response Policy / Alternative Policy
    B and C'
  description: The prompt names Alternative Policy B and Alternative Policy C as labeled
    options, which creates mild leading-choice framing even though the judgment question
    explicitly says 'Do not simply choose from A/B/C.' The labeled enumeration anchors
    the proxy model's answer space to three named options, making it slightly harder
    to propose a genuinely independent policy.
  rationale: Criteria 4 and 5 require a non-leading question that permits confirming,
    modifying, rejecting, or replacing Policy A without forcing a closed choice. Naming
    and describing B and C as distinct alternatives alongside A biases the model toward
    selecting among the three rather than reasoning from first principles. The judgment
    question partially mitigates this but the structural framing in the policy section
    still nudges toward A/B/C enumeration.
- severity: WARN
  target_location: '## Output Contract / selected_policy field'
  description: 'The YAML output contract enumerates a closed set of pipe-delimited
    values for `selected_policy`: `policy_a | policy_a_with_modifications | broader_rewrite_required
    | defer_to_tasks | other`. Including `other` partially opens the field, but the
    enumeration still anchors the model''s vocabulary. A free-string field or a separate
    `selected_policy_description` field would better match the open-ended judgment
    question.'
  rationale: Criteria 5 and 8 require the output contract to support an open answer
    while remaining parser-friendly. The enumeration with `other` is usable but creates
    mild tension with the non-closed-choice requirement in criterion 5, because `other`
    is syntactically awkward and under-specified relative to what a genuinely different
    policy would look like.
- severity: WARN
  target_location: '## Output Contract / rejected_policies block'
  description: 'The `rejected_policies` block pre-names exactly three keys: `policy_a`,
    `broader_rewrite`, and `defer_to_tasks`. This structurally presupposes that the
    proxy model will reject at least some of those policies and implicitly requires
    it to comment on all three, even if the proxy model''s conclusion is that Policy
    A is fully sufficient and neither B nor C is worth discussing.'
  rationale: A parser-friendly contract should not force the proxy model to populate
    fields that may not apply to its conclusion. If the proxy model selects `policy_a`
    as fully sufficient, the `rejected_policies.policy_a` key is contradictory. This
    creates output ambiguity and may force the model to write placeholder text.
- severity: INFO
  target_location: '## Current Design Material Relevant To C1 / Design Summary: Requirement
    12 Boundaries'
  description: This section is labelled 'Design Summary' rather than 'Design Excerpt',
    making it unclear whether it is verbatim source text or a paraphrase synthesised
    by the main session. If it is a paraphrase, the proxy model cannot verify it against
    the actual design.md wording.
  rationale: Criterion 3 requires enough prior material for the proxy model to judge
    without guessing. A paraphrase summary reduces verifiability. Labelling it explicitly
    as 'main-session summary (not verbatim)' or replacing it with a verbatim excerpt
    would improve transparency without materially increasing prompt length.
- severity: INFO
  target_location: '## Execution Metadata For This Run / proxy_model_id'
  description: 'The metadata names `gpt-5.5` as the target proxy model. The output
    contract YAML also hard-codes `proxy_model_id: gpt-5.5`. If the actual model variant
    differs at execution time, the hard-coded value creates a mismatch in the output
    artifact without any prompt-level instruction to override it.'
  rationale: Minor ergonomics issue. The prompt could instruct the proxy model to
    confirm or correct the model identifier rather than simply echoing a hard-coded
    string, reducing the risk of a stale identifier propagating into the response
    artifact.


# 前段所見 2：
role: judgment
provider: gemini-api
model: gemini-3.1-pro-preview
attempts: 1
duration_seconds: 22.68
findings:
- severity: INFO
  target_location: '## Output Contract'
  description: 'The output contract code block still hard-codes `proxy_model_id: gpt-5.5`
    despite the new instructions in the metadata section telling the model to report
    the actual executing model ID.'
  rationale: Language models heavily anchor on literal values provided in YAML code
    blocks. Changing `gpt-5.5` to a type declaration like `string` or a descriptive
    placeholder (e.g., `<actual_model_id>`) in the example block would better ensure
    the model follows the instruction to dynamically report its actual ID.


# Target path
.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-c1-fix-policy-proxy-prompt-quality-run/proxy-decision-c1-fix-policy-prompt.md

# Target document
---
prompt_id: workflow-management-design-v2-proxy-decision-c1-fix-policy
phase: design
gate: stages/design.yaml#triad-review
cluster_id: C1
status: draft_for_prompt_quality_review
---

# Proxy Model Judgment Prompt: C1 Fix Policy

## Execution Metadata For This Run

This prompt is intended for the `proxy_model_openai_gpt_55` variant.

- `proxy_model_id`: expected `gpt-5.5`; if the actual executing model ID differs, report the actual model ID in the output.
- `decision_prompt_path`: `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-c1-fix-policy-proxy-prompt-quality-run/proxy-decision-c1-fix-policy-prompt.md`

## User Review Requirements

Use proxy_model to judge the design response policy for C1 only.

The user requested proxy mode instead of human approval for the C1 response policy. The purpose is to avoid the main session LLM unilaterally deciding how to respond to a blocking C1 design finding.

Review purpose:

- Decide how the main session should respond to C1's `must-fix / blocking` proxy_model decision.
- Decide whether the proposed local design fix policy is sufficient, insufficient, too broad, or should be replaced.
- Specify the required design.md response boundaries before the main session edits `design.md`.

Review object:

- Cluster: C1 only.
- Prior proxy decision: C1 was judged `must-fix`, `valid`, `blocking`, and `design_level`.
- Target artifact to be edited later, if authorized by the workflow: `.reviewcompass/specs/workflow-management/design.md`
- This prompt asks for a response policy, not for direct file edits.

Out of scope:

- Do not judge C2-C7.
- Do not edit `design.md`.
- Do not update `spec.json`.
- Do not move the design gate or authorize phase completion.
- Do not authorize commit or push.
- Do not authorize human-only approvals or irreversible operations.
- Do not decide tasks or implementation correctness except where a design omission would force downstream invention.

## Current State

Workflow state:

- Reopen procedure is in progress.
- Current gate: `stages/design.yaml#triad-review`.
- Requirements approval is complete.
- Design drafting is complete.
- C1 proxy_model judgment is complete and parsed.
- C1 is blocking; design triad-review cannot be completed until the design-level response is settled and applied through the proper workflow.

## Prior Proxy Decision For C1

Prior proxy_model: `gpt-5.5`

Prior decision summary:

- `cluster_id`: C1
- `final_label`: `must-fix`
- `validity`: `valid`
- `cluster_adopted`: true
- `blocking`: true
- `design_level`: true

Adopted source findings:

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-001`
- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-002`
- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-008`

Prior rationale:

- Requirements 12 and 13 require a single machine-readable operation contract authority and a clear read-only registry / preflight boundary.
- Current design contains correct statements that `stages/operation-contracts.yaml` is the physical source of truth and that registry references it.
- Current design also contains wording that can be read as placing contract schema authority in `stages/operation-registry.yaml`.
- Current design contains wording that can be read as assigning precheck vocabulary or output contract authority to operation docs or scripts.
- This ambiguity is not safe to defer because downstream tasks would have to decide which artifact owns operation vocabulary, output contract fields, and preflight authority.
- Requirement 13 specifically requires the design to decide whether duplicated contract fields are structurally forbidden rather than leaving that decision to implementation-only integrity checks.

Prior required design response:

- Clarify unambiguously that `stages/operation-contracts.yaml` is the sole physical source of truth for operation contract vocabulary and contract fields, including fields such as `effect_kind`, `approval_required`, `phase_boundary`, `required_action` mappings, and equivalent output/effect contract fields.
- Clarify that `stages/operation-registry.yaml` owns only registry-specific metadata and references to operation contracts, such as contract ID, contract digest, schema version, invocation binding, workflow binding, target identity, required inputs, planned outputs as references or projections where applicable, sequence mode, and worktree/pending/artifact policy.
- Remove or rewrite wording that says or implies that operation contract schema lives in `stages/operation-registry.yaml`.
- Remove or rewrite wording that says or implies that operations documentation, check scripts, or preflight implementation define the canonical precheck vocabulary, `required_action` vocabulary, output contract, effect kind, approval requirement, phase boundary, or equivalent contract semantics.
- State that registry and preflight read operation contracts and state evidence only; they do not redefine contract fields, update contracts, execute operations, consume approvals, create workflow state, or mutate artifacts.
- State at the design level that registry schema structurally forbids duplicated contract-authority fields such as `effect_kind`, `approval_required`, and `phase_boundary`, and that any attempted duplication or digest/schema mismatch fails closed.
- Preserve `next --json` as the single action selector and specify that registry/preflight may validate and bind to that selector but must not invent a parallel source of action truth.

## Current Design Material Relevant To C1

The following excerpts and structured summaries are the material available for this response-policy judgment.

### Design Excerpt: Requirement 12 Opening

```text
Requirement 12 は、作業開始前に「正本コマンド・入力・成果物・順序・衝突・停止条件」を同じ形式で確認するための operation contract 層である。本節は read-only preflight を先に確定し、runner による実行代行は後段へ分離する。
```

### Design Excerpt: Requirement 12 Section 1

```text
### 1. operation contract schema（Req 12 受入 1）

**配置先**：`stages/operation-registry.yaml`。workflow-management が所有し、他 feature は参照のみ行う。

各 operation は最低限、次のフィールドを持つ。
```

The listed fields include:

- `operation_id`
- `kind`
- `operation_family`
- `canonical_invocation`
- `workflow_binding`
- `required_inputs`
- `target_identity`
- `planned_outputs`
- `sequence_mode`
- `worktree_policy`
- `pending_conflict_policy`
- `artifact_policy`
- `family_required_checks`
- `vocabulary_refs`

### Main-Session Summary: Requirement 12 Boundaries

This is a main-session paraphrase, not a verbatim excerpt. Use it as orientation only.

Requirement 12 appears to state:

- preflight is read-only.
- preflight does not create or update review-run directory, manifest, approval record, session record, commit, or deployment/export output.
- preflight includes `next --json` active state dimensions in `state_refs.next_action`.
- Requirement 12 does not own `next --json`; it uses the selector result for operation preflight.
- preflight must not independently select pending gates or maintenance actions.

### Design Excerpt: Requirement 13 Opening

```text
Requirement 13 は、`next --json` の選択層が返す唯一 action を、実行層の operation contract へ接続する。Requirement 12 の operation registry / preflight は「操作開始前の read-only 確認」を担い、本節の operation contract は「操作の副作用・承認要否・順序・前提・事後条件」を定義する。
```

### Design Excerpt: Requirement 13 Section 3

```text
19語彙の正本は `.reviewcompass/schema/required_action.schema.json` である。operation contract の物理正本は `stages/operation-contracts.yaml` とし、`stages/operation-registry.yaml` は operation registry / preflight binding の正本として各 `required_action` から `operation_contract` ID と contract digest / schema_version を参照する。

`stages/operation-contracts.yaml` は、最低限 `required_action`、`effect_kind`、`approval_required`、`phase_boundary`、`sequence`、実行主体、分岐条件、preconditions / postconditions、side effects、承認要否の集約規則を持つ。`stages/operation-registry.yaml` は canonical invocation、workflow binding、required inputs、target identity、planned outputs、worktree / pending / artifact policy と contract 参照を持ち、contract field を再定義しない。registry / preflight は contract を読み取って確認するだけで、contract 更新、operation 実行、approval consume を行わない。
```

### Design Excerpt: Requirement 13 Integrity Conditions

```text
registry / contract の整合検査は次を fail-closed にする。

- registry が参照する contract ID が存在しない
- registry が保持する contract digest または schema_version が contract 正本と一致しない
- registry が `effect_kind`、`approval_required`、`phase_boundary`、preconditions / postconditions、side effects を複製して二重正本化している
- contract が required_action schema に存在しない語彙を参照している
- required_action schema の語彙が contract に接続されていない
```

### Design Excerpt: Requirement 13 Section 5

```text
operation preflight は `stages/operation-registry.yaml` を入口にし、参照先 `stages/operation-contracts.yaml` の preconditions / postconditions / side effects / approval_required を読み取る。preflight の責務は「開始前に確認すること」であり、contract 正本、workflow state、approval record、side track stack、snapshot、review-run artifact を作成・更新しない。

read-only advisory 段階では、contract 参照欠落、digest drift、確認不能 precondition、正本 field 重複を `WARN` 以上にする。runner-enabled operation では同じ状態を `DEVIATION` とし、operation 実行を開始しない。
```

### Design Excerpt: XDI-WM-004

```text
- operation registry は `stages/operation-registry.yaml` を正本とし、operation id、kind、canonical invocation、workflow binding、required inputs、target identity、planned outputs、sequence mode、worktree / pending / artifact policy を定義する。
- preflight は read-only を Phase 1 とし、review-run directory、manifest、approval record、session record、commit、deployment / export output を作成しない。
```

### Design Excerpt: XDI-WM-005

```text
- `required_action` 19語彙は operation contract に接続し、`effect_kind`、承認要否、phase boundary、sequence、preconditions / postconditions を機械可読に持つ。
- 複合 operation は単一代表値へ丸めず、branch / internal step / max effect / approval aggregation を registry 上で表す。
- structured effective prompt は LLM の言語タスク仕様であり、機械タスクは operation contract / preflight / runner / guard の責務とする。
- Phase 0〜6 は選択層、schema、read-only registry、advisory preflight、structured prompt、mechanical blocking、LLM judge audit の順に分け、TDD 実装時に混在させない。
```

## Main Session's Proposed Response Direction

The main session proposes a local design fix direction. Treat it as a proposal to evaluate, not as a preferred answer you must select.

### Proposed Local Fix Direction

Apply a local textual / structural design correction to `design.md`:

1. State that `stages/operation-contracts.yaml` is the sole physical source of truth for operation contract vocabulary and contract fields.
2. State that `stages/operation-registry.yaml` owns only registry-specific metadata and contract references.
3. State that registry schema structurally forbids duplicated contract-authority fields such as `effect_kind`, `approval_required`, and `phase_boundary`.
4. State that preflight is read-only and reads operation contracts plus state evidence only.
5. State that `next --json` remains the single action selector and registry / preflight only validate and bind to it.
6. Rewrite the Requirement 12 section title / placement wording so it no longer says or implies that operation contract schema lives in `stages/operation-registry.yaml`.
7. Rewrite XDI-WM-004 / XDI-WM-005 wording as needed so that registry / contract ownership is not ambiguous.

Other possible response directions include:

- A broader rewrite that fully separates Requirement 12 into registry/preflight ownership and Requirement 13 into contract ownership.
- A narrower correction limited to the contradictory placement wording.
- Deferring some details to tasks / implementation if, and only if, the design-level source-of-truth boundary is already sufficient.
- Another response policy that better fits the evidence.

The main session has not been authorized to edit `design.md`. This prompt asks proxy_model to independently decide the response policy first.

## Judgment Question

Judge the appropriate response policy for C1 before `design.md` is edited.

Do not simply choose from named options. You may confirm the local fix direction, require modifications, require a broader rewrite, allow a narrower correction, reject deferral, allow limited deferral, or propose another response policy if the evidence supports it.

Assess:

1. Whether the proposed local fix direction is sufficient to satisfy the prior C1 required design response.
2. Whether the proposed local fix direction is too narrow and a broader rewrite is necessary.
3. Whether any part of the proposed local fix direction is too broad, creates new drift, or improperly moves decisions into the wrong artifact.
4. Whether deferring to tasks / implementation would be acceptable.
5. The minimum required design changes the main session must make before C1 can be considered addressed.
6. Any wording or scope pitfalls the main session should avoid when editing.

Do not authorize commit, push, `spec.json` mutation, phase transition, gate completion, direct edits, human-only approval substitution, reopen finalize, or approval-required irreversible operation execution.

## Output Contract

Return YAML only.

Required structure:

```yaml
proxy_model_id: string
decision_prompt_path: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-c1-fix-policy-proxy-prompt-quality-run/proxy-decision-c1-fix-policy-prompt.md
raw_response_path: proxy-decision-c1-fix-policy-response.yaml
review_run_id: 2026-06-20-workflow-management-design-vertical-redo-review-run-v2
cluster_id: C1
decision_scope: c1_fix_policy
selected_policy: string
selected_policy_category: local_fix_sufficient | local_fix_with_modifications | broader_rewrite_required | narrower_fix_sufficient | limited_deferral_allowed | deferral_rejected | other
local_fix_direction_sufficient: true | false
blocking_until_design_edit: true | false
decision_rationale: string
required_design_changes:
  - string
wording_or_scope_pitfalls:
  - string
non_selected_or_risky_directions:
  - direction: string
    reason: string
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

