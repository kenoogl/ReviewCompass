---
criteria_id: workflow-management-requirements-reopen-protocol-review-criteria
phase: requirements
gate: stages/requirements.yaml#triad-review
intended_review_target:
  - .reviewcompass/specs/workflow-management/requirements.md
source_materials:
  note: "Front matter records provenance only. Model-readable source material is embedded in the body. The actual review-run must not depend on the preanalysis audit bundle at .reviewcompass/specs/workflow-management/reviews/2026-07-01-workflow-management-requirements-reopen-protocol-review-run/preanalysis-audit-bundle.md; that bundle was an audit input, not an authority source."
  embedded:
    - reopen-protocol-mechanization-plan
    - current-reopen-state
    - current-spec-state
    - reopen-procedure-guidance
    - vertical-intent-transfer-guidance
    - api-review-protocol-guidance
    - behavior-path-source-summary
user_review_requirements:
  provided_by: workflow
status: draft_for_prompt_quality_review
---

# workflow-management requirements reopen-protocol Review Criteria

## Review Task

Review `.reviewcompass/specs/workflow-management/requirements.md` for `stages/requirements.yaml#triad-review`.

The review question is:

Does `requirements.md` carry the upstream reopen-protocol intent into requirements-stage policy without omission, weakening, contradiction, unsupported addition, or drift?

Report a finding when the target requirements text creates a requirements-level omission, weakening, contradiction, unsupported addition, ambiguity, or traceability gap for this review question. Do not report findings against source materials, downstream artifacts, or implementation code unless their contents reveal such a target requirements defect.

## Why This Review Exists

This review-run is required because the active reopen edits `workflow-management` requirements. A requirements edit must pass requirements triad-review before review-wave, alignment, approval, downstream phase gates, proxy_model decisions, `spec.json` updates, phase transitions, commit, or push can be treated as complete.

The prior process failure being guarded against is: a reopen that changed `requirements.md` proceeded without rerunning requirements triad-review and review-wave, while design/tasks/implementation impact was handled as late supplemental metadata instead of as normal reopen-chain work.

## User And Workflow Review Requirements

Review purpose:

- Requirements triad-review for reopen protocol mechanization.
- Vertical transfer check from user/workflow decisions, reopen classification, planning notes, and governance documents into `requirements.md`.

Review object:

- `.reviewcompass/specs/workflow-management/requirements.md`.

Review focus:

- Edited phase full-gate re-execution.
- Downstream phase impact decisions with evidence even when downstream documents do not change.
- Fail-closed detection at `next --json`, `reopen-finalize`, and commit preflight.
- Superseding reopen record policy for already-pushed incomplete reopen records.
- proxy_model and human-only authority boundaries.
- Requirements-stage target/source/out-of-scope separation.

Scope boundaries:

- In scope: whether the target requirements text carries the reopen protocol requirements and authority limits needed by later design/tasks/implementation work.
- Out of scope: judging design.md, tasks.md, implementation code, or current runner correctness as final correctness targets.
- Source-only: runner, guard, preflight, and tests may be used to understand behavior-path claims, but implementation defects are not target findings at this gate unless they reveal a requirements omission or contradiction.

Output requirements:

- Parser-compatible findings.
- Include `findings: []` only when the target requirements text is traceable, sufficiently scoped, and internally consistent for the stated review question.

Prohibited actions and authority limits:

- Do not authorize commit, push, `spec.json` update, phase transition, gate completion, proxy_model decision, or human approval delegation.
- Do not treat this review-run, prompt-quality-run, or a proxy_model answer as approval to mutate workflow state.

Requirement-to-prompt mapping:

- Edited phase full-gate requirement -> Review Task, Source Materials, Required Checks 1.
- Downstream impact decision evidence -> Review Task, Source Materials, Required Checks 2.
- Fail-closed behavior paths -> Review Task, behavior-path source summary, Required Checks 3.
- Superseding reopen record policy -> Source Materials, Required Checks 4.
- proxy_model boundary -> Source Materials, Required Checks 5, Out Of Scope.
- Requirements-stage scope -> Scope boundaries, Required Checks 6.

## Review Target

The review target is only:

- `.reviewcompass/specs/workflow-management/requirements.md`

At the actual review-run, pass this path as the review target. Do not treat this criteria file, a wrapper, source summaries, design/tasks/implementation documents, or author-written preanalysis as a substitute for the target document.

Target sections expected to be relevant. These are target locations, not source material; the actual review-run must receive the full `requirements.md` file as target content.

- Requirement 3 acceptance criterion 5 -> Required Check 1, edited phase full-gate rerun.
- Requirement 5 acceptance criterion 7 -> Required Checks 1, 2, and 4, reopen state and superseding record policy.
- Requirement 16 acceptance criteria 11-14 -> Required Checks 2, 3, 5, and 6, downstream impact evidence, fail-closed surfaces, authority boundaries, and state separation.
- Related in-target context: Requirement 2 acceptance criteria 9/13 and Requirement 9 acceptance criteria 3/5 -> Required Checks 3, 5, and 6, guard authority and state-transition boundaries.

## Source Materials

Use these source materials only for background and intent-transfer checking. Do not judge these source materials as review targets unless the requirements document omits, weakens, or contradicts their required transfer.

### reopen-protocol-mechanization-plan

Source path:

- `.reviewcompass/backlog/plans/plan-2026-07-01-reopen-protocol-mechanization-review.yaml`

Purpose:

- Correct a process failure where a requirements-changing reopen did not rerun requirements triad-review/review-wave and downstream impact was deferred until finalize/commit repair.

Responsibility boundaries:

- A phase whose canonical artifact is substantively edited must be marked as an edited phase.
- Edited phases require full review gates, not only alignment/approval.
- Downstream impact must be recorded as normal reopen-chain work, not late metadata.
- Completed records already pushed should not be rewritten silently; use a superseding reopen record with a reason.

Acceptance criteria / required transfer:

- RPMR-I1: reopen state keeps the substantively edited phases as `edited_phases` or an equivalent machine-readable field.
- RPMR-I2: each phase in `edited_phases` requires triad-review, review-wave, alignment, and approval; drafting completion is checked where drafting is required.
- RPMR-I3: upstream phase edits require downstream phase impact coverage through `impacted_downstream_phases` and `downstream_impact_decisions`.
- RPMR-I4: downstream no-change decisions still need gate, feature scope, decision, rationale, and evidence.
- RPMR-I5: `next --json` detects missing edited phase gates or downstream decisions before normal completion.
- RPMR-I6: `reopen-finalize` recomputes required gates and decisions before creating a completed record.
- RPMR-I7: commit preflight is a final guard, not the first expected detection point.
- RPMR-Q3: already-pushed incomplete completed reopen records should be handled by a superseding reopen record with replacement rationale, not by silent history rewriting.

Forbidden or high-risk drift:

- Treating downstream impact as optional supplemental metadata.
- Letting completed reopen records be generated before required gates or decisions are present.
- Relying on commit preflight as the first normal detector.

Completeness note for this source summary:

- It covers the plan's stated current_problem items about missed requirements triad-review/review-wave, late downstream impact handling, completed record generation before required gate checks, and weak edited-phase/downstream distinction.
- It includes all plan design questions RPMR-Q1 through RPMR-Q4 as the responsibility and acceptance items above.
- It includes fail-closed invariants RPMR-I1 through RPMR-I7, including RPMR-Q3's superseding-record repair concern.
- It intentionally excludes the plan's red-test implementation evidence from the actual requirements review target; implementation evidence is represented only through the behavior-path source summary below.

### current-reopen-state

Source path:

- `stages/in-progress/reopen-procedure-2026-07-01.yaml`

Structured summary:

- classification: `R-0`
- edited_phases: `requirements`
- impacted_downstream_phases: `design`, `tasks`, `implementation`
- full_reopen_downstream_phases: `design`, `tasks`, `implementation`
- downstream_impact_decisions: empty at this moment
- drafting_completed_gates: `stages/requirements.yaml#drafting`
- active gate: `stages/requirements.yaml#triad-review`
- pending gates: requirements/design/tasks/implementation triad-review, review-wave, alignment, approval

Intended target-phase transfer:

- The requirements document should support this kind of active state: requirements was edited, downstream phases remain in scope, and the review cannot be considered complete before required gates and downstream decisions are recorded.

### current-spec-state

Source path:

- `.reviewcompass/specs/workflow-management/spec.json`

Structured summary:

- requirements drafting is true.
- requirements triad-review, review-wave, alignment, and approval are false.
- design/tasks/implementation drafting, triad-review, review-wave, alignment, and approval are false.
- `recheck.upstream_change_pending` is true.
- `recheck.impacted_downstream_phases` includes design, tasks, and implementation.

Intended target-phase transfer:

- Requirements must distinguish active reopen scope from historical reopen flags, and must not imply that downstream gates can stay complete after upstream requirements changed.

### reopen-procedure-guidance

Source path:

- `.reviewcompass/guidance/REOPEN_PROCEDURE.md`

Structured summary:

- A phase whose canonical artifact is substantively changed re-enters triad-review, review-wave, alignment, and approval.
- Downstream impact is assessed for requirements, design, tasks, and implementation, not only for intent changes.
- Even when downstream changes are unnecessary, the decision needs gate, feature scope, decision, rationale, and evidence.
- Reopen progress should fail closed when required gates or impact evidence are missing.

### vertical-intent-transfer-guidance

Source path:

- `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`

Structured summary:

- Requirements review checks upstream decision materials against `requirements.md`.
- For requirements review, downstream documents are source context at most, not correctness targets.
- Source materials must not be path-only.
- The prompt must separate purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved/deferred items, and intended target-phase transfer.

### api-review-protocol-guidance

Source paths:

- `.reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md`
- `.reviewcompass/guidance/discipline_llm_as_judge_prompting.md`
- `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2`

Structured summary:

- Main preanalysis is a hypothesis and source-selection aid, not an answer key.
- Preanalysis sufficiency audit must check material selection, judgment item split, and source coverage before real review-run.
- Prompt quality review must use adversarial review, main revision, and judgment approval; actual review-run starts only when judgment has no findings.
- After actual review-run, raw/parsed/rounds/model-summary/triage artifacts and user-visible triage must be presented before proxy_model, implementation edits, `spec.json` updates, or phase movement.
- proxy_model may judge important finding triage, but cannot authorize commit, push, `spec.json` update, phase transition, or human-only approval.

Governing excerpts needed for authority boundaries:

- `SESSION_WORKFLOW_GUIDE.md#3.3-a-2`: "API review-run が完了したら、proxy_model 判断依頼、実装修正、spec.json 更新、フェーズ移行のいずれにも進む前に、メインセッション LLM は次を利用者へ提示して停止する。この提示ゲートを完了する前に proxy_model を呼び出してはいけない。"
- `SESSION_WORKFLOW_GUIDE.md#3.3-a-2`: the user-visible gate must include variant, role path/provider/model, raw summary, same-root clusters, three-level triage, must-fix explanation/proposals, and proxy_model scope that excludes commit, push, `spec.json` update, and phase transition.
- `SESSION_WORKFLOW_GUIDE.md#3.3-a-2`: "variant が未確定、または role 割当が曖昧な場合は review-run を開始しない。"
- `SESSION_WORKFLOW_GUIDE.md#3.3-a-2`: "proxy_model は重要件の採用案・判断理由・最終ラベルを決定する。実装は担当しない"
- `SESSION_WORKFLOW_GUIDE.md#3.3-a-2`: "コミット・プッシュ・spec.json 更新・フェーズ移行は人間の明示承認を要求する。proxy_model はこれらの不可逆操作を代行しない"
- `API_REVIEW_PROMPT_QUALITY.md#8`: standard order is main preanalysis, preanalysis sufficiency audit, API review criteria draft, prompt quality review, actual review-run, raw/parsed/model summary/triage, and optional proxy_model decision.
- `API_REVIEW_PROMPT_QUALITY.md#8`: "監査結果の `required_prompt_changes` を反映してから、通常の `templates/review/api_review_prompt_quality_criteria_template.md` による prompt quality review へ進む。"

### behavior-path-source-summary

Source paths:

- `tools/check-workflow-action.py`
- `tests/tools/test_check_workflow_action.py`

Structured summary:

- `_required_downstream_impact_phases_for_edited_phases` derives downstream phases dynamically from edited phases.
- `_gate_chain_for_edited_phases_and_downstream` expands edited phases and downstream full reopen phases to required full gates.
- `_reopen_downstream_impact_action` returns `record_reopen_downstream_impact_decision` when downstream decisions are missing.
- `validate_reopen_completion_impact_decisions` and `_validate_reopen_finalize_downstream_impact_decisions` reject incomplete completed/finalize records.
- Focused tests cover initializing edited phase downstream scope, design edit dynamic downstream scope, false scope dynamic downstream phase, and finalize rejection when impacted downstream decisions are missing.

Use this behavior-path material only to assess whether the requirements text makes behavior-path claims sufficiently explicit. Do not judge code correctness as the target of this requirements review.

## Required Checks

1. Check whether `requirements.md` requires every edited phase to rerun triad-review, review-wave, alignment, and approval, and whether the text avoids implying that alignment/approval alone is enough.
2. Check whether `requirements.md` requires downstream impact decisions for affected downstream phases, including no-change decisions with gate, feature scope, decision, rationale, and evidence.
3. Check whether `requirements.md` requires missing gates or decisions to be detected by `next --json` and `reopen-finalize`, with commit preflight as a final guard rather than the first normal detector.
4. Check whether `requirements.md` requires incomplete completed reopen records to be handled as superseding reopen records with replacement reasons, rather than silent history rewriting.
5. Check whether `requirements.md` preserves proxy_model and human-only authority boundaries: proxy_model may support important-issue judgment, but must not authorize commit, push, `spec.json` mutation, phase transition, or human-only approval.
6. Check whether the requirements text keeps current active reopen scope, downstream impact review scope, historical reopen flags, consumer/derivative feature impact, and future downstream correctness review distinct enough for later phases.
7. Use the behavior-path source summary only to evaluate whether `requirements.md` makes sufficient behavior-path policy claims. Do not report runner or test code correctness as the target finding at this requirements gate. Do report a target requirements finding if the requirements text contradicts behavior-path evidence, omits a required behavior-path policy, or would force later phases to invent the policy.

## Out Of Scope

- Do not judge whether design.md, tasks.md, or implementation code is correct.
- Do not judge whether current runner implementation fully satisfies the requirements.
- Do not approve or authorize commit, push, `spec.json` mutation, phase transition, gate completion, proxy_model use, or human approval delegation.
- Do not treat source material defects as target findings unless they create a requirements transfer defect.
- Do not use main preanalysis as an answer key.
- Do not audit this criteria file, the preanalysis, or the prompt split in the actual requirements review-run.

## Finding Policy

- Report `CRITICAL` if the target requirements would authorize or imply authorization of commit, push, `spec.json` mutation, phase transition, gate completion, proxy_model substitution for human-only judgment, or human approval delegation.
- Report `ERROR` if the target omits, weakens, broadens, or replaces a workflow review requirement in a way that changes the review outcome.
- Report `ERROR` if edited phase full-gate requirements, downstream impact decision evidence, fail-closed detection points, superseding reopen record policy, or proxy_model authority boundaries are missing, contradicted, or ambiguous enough to require downstream invention.
- Report `WARN` for ambiguity likely to force repeated manual judgment, weak traceability, unclear state boundaries, or overclaiming completion.
- Report `INFO` only for non-blocking traceability improvements.
- Return `findings: []` only when the target is traceable, internally consistent, correctly scoped, and sufficiently grounded for downstream phases.
