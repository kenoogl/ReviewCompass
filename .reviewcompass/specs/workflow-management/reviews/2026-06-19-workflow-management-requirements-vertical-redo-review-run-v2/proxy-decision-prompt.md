# Proxy Model Triage Decision Prompt

You are the proxy_model for a ReviewCompass requirements triad-review.

Your task is to independently judge the four findings from a corrected vertical intent-transfer review. Do not simply accept the draft triage proposal. Analyze whether each finding identifies:

- a blocking requirements problem that must be fixed before requirements triad-review can complete,
- a non-blocking requirements clarification that should be fixed before downstream design/tasks replay,
- or an observation that should be left unchanged.

You may disagree with the draft proposal. If the available labels are not a perfect fit, choose the closest workflow label and explain the mismatch in the rationale.

## Review Context

Review run: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2`

The review target is `.reviewcompass/specs/workflow-management/requirements.md`, specifically Requirement 13 through Requirement 16 and directly related Change Intent / traceability text.

Downstream `design.md` and `tasks.md` correctness are out of scope. Implementation code, commit, push, spec mutation, phase approval, and reopen movement are out of scope.

## Upstream Intent Summary

The upstream purpose is to reduce dependence on LLM memory and implicit interpretation. `next --json` remains the selector that decides the single current action. Execution must be governed by machine-readable operation contracts, preflight checks, approval gates, side-track state, workflow-state snapshots, and structured language-task prompts.

For this reopen, Requirement 13-16 must restore upstream intent that was previously under-transferred into requirements. The prior result only added minimal Phase 1 schema points, while the upstream materials intended operation contract vocabulary, approval gates, side-track stack, workflow-state snapshot, structured effective prompts, and Phase 0-6 ordering to be requirements-visible.

Important upstream boundaries:

- `next --json` decides the current `required_action`; operation contracts do not replace it.
- operation contracts define execution details such as `effect_kind`, `approval_required`, sequence, preconditions, postconditions, pending conflicts, and fail-closed behavior.
- registry / preflight are read-only consumers or confirmations of the contract; they must not become independent sources of truth or consume approvals.
- `record_human_decision` records a decision but does not itself authorize an approval-required operation.
- proxy_model may triage findings, but cannot replace human-only decisions such as commit, push, spec updates, phase approval, reopen finalize, or approval-required irreversible operations.
- workflow-state snapshots are visualization / audit support, not canonical state.
- LLMs perform language tasks; mechanical checks, guards, preflight, and approval enforcement must not be left to implicit LLM judgment.

Important upstream acceptance intent:

- all 19 `required_action` terms must map to operation contract information, including `effect_kind`, execution actor, and `approval_required`;
- `approval_required` is independent from `effect_kind`;
- approval-required actions include at least `commit_stop_point`, `apply_approved_reopen_plan`, `run_reopen_start`, `advance_reopen_after_commit_stop_point`, `advance_reopen_after_approval_stop_point`, `finalize_reopen`, and `repair_workflow_state`;
- complex operations may vary by internal step or stage kind, but LLMs must not infer them ad hoc;
- side-track depth excess, scope drift, and commit mixing are warning-only in Phase 3 and mechanically blocked in Phase 5;
- structured effective prompts describe language tasks, while mechanical checks belong to contracts, preflight, runners, and guards;
- LLM judge audit is auxiliary and cannot automate final approval;
- phase order is Phase 1 schema, Phase 0 selector implementation, then Phase 2 read-only registry, Phase 3 warning preflight, Phase 4 structured prompts, Phase 5 blocking guards, and Phase 6 optional LLM judge audit.

Important unresolved / design-deferred items:

- representation of complex operations may be maximum side-effect representative, list-valued `effect_kind`, or internal-step decomposition;
- exact data structure tying `record_human_decision` to an approval target is design-deferred;
- human-required predicate priority and conflict resolution for proxy_model applicability are design-deferred.

Requirements should not force final design for these deferred details, but should preserve enough constraints that design cannot silently choose an unsafe option.

## Current Findings

### F1

finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2-claude-opus-4-8-adversarial-001`

Original severity: ERROR

Target: Requirement 13 AC5

Finding summary: AC5 says approval-required operations need an explicit human decision record. Requirement 13 AC6 and Requirement 14 AC1 / AC3 state that `record_human_decision` completion is not approval, but AC5 itself does not locally cross-reference that boundary. The reviewer says this may allow a design-stage misread that `record_human_decision` existence alone satisfies approval.

Draft triage proposal: `should-fix`, because surrounding requirements already state the boundary, but a local cross-reference would reduce drift.

### F2

finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2-claude-opus-4-8-adversarial-002`

Original severity: WARN

Target: Requirement 14 AC11

Finding summary: AC11 says proxy_model cannot replace human-only decisions, but does not cross-reference Requirement 16 AC13 / AC14 where proxy applicability predicates and priority are defined. The reviewer says the safety boundary is distributed and easier to misread downstream.

Draft triage proposal: `should-fix`.

### F3

finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2-claude-opus-4-8-adversarial-003`

Original severity: WARN

Target: Requirement 13 AC8 / AC9 and Requirement 16 AC2 / AC4

Finding summary: AC8 defines minimum constraints for complex operations, while AC9 lists representation options. The reviewer says AC9 does not explicitly state that AC8's minimum constraints must survive whichever representation design chooses, so a representative-value design might silently lose branch conditions, maximum side effect, or approval aggregation rules.

Draft triage proposal: `should-fix`.

### F4

finding_id: `2026-06-19-workflow-management-requirements-vertical-redo-review-run-v2-claude-opus-4-8-adversarial-004`

Original severity: INFO

Target: Requirement 16 AC1 / AC3

Finding summary: This is a confirmation that Phase 1 -> Phase 0 dependency and Phase 0 completion criteria are transferred correctly. No omission was identified.

Draft triage proposal: `leave-as-is`.

## Decision Labels

Use these workflow labels:

- `must-fix`: the finding identifies a blocking requirements omission, weakening, unsupported addition, or responsibility-boundary drift that must be fixed before requirements triad-review can complete.
- `should-fix`: the finding identifies a non-blocking clarification or traceability improvement that should be fixed before downstream design/tasks replay.
- `leave-as-is`: the finding is already covered well enough, asks for design-level detail, is only a confirmation, or should not change the requirements.

## Required Output

Return only YAML with this exact top-level shape:

```yaml
proxy_model_id: gpt-5.5
decision_prompt_path: proxy-decision-prompt.md
raw_response_path: proxy-decision-response.yaml
decisions:
  - finding_id: <exact finding id>
    final_label: must-fix | should-fix | leave-as-is
    rationale: <specific reason>
    rejected_options:
      must-fix: <why not selected>
      should-fix: <why not selected>
      leave-as-is: <why not selected>
```

For every finding, include all three `rejected_options` keys except the selected label may say `selected`.

Do not include prose outside YAML.

YAML formatting rule: write every `rationale` value and every `rejected_options` value as a block scalar (`|-`). Do not put colons inside plain unquoted scalar values.

## Sensitive Information Check

No API keys, access tokens, passwords, personal contact information, or non-public third-party confidential data are intentionally included in this prompt.
