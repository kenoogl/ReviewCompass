---
criteria_id: workflow-management-implementation-req14-approval-gate-transfer-review-criteria
phase: implementation
status: draft_for_prompt_quality_review
---

# workflow-management implementation req14-approval-gate-transfer API Review Criteria

## Review Task

Review the target for: Req 14 approval gate implementation upstream transfer.

Primary judgment question:

Does the target satisfy Req 14 approval gate implementation upstream transfer, while carrying upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, and intended transfer without any of the following?

- omission
- weakening
- contradiction
- unsupported addition
- drift

Limit findings to this judgment item.

## User Review Requirements

- Review purpose: workflow-management implementation triad-review
- Review object: Req 14 approval gate implementation artifacts
- Review focus:
  - approval/proxy human-only boundary
  - approval decision binding and digest checks
- Scope boundaries:
  - In scope:
    - approval gate schema, implementation, CLI integration, and focused tests
  - Out of scope:
    - side track stack behavior
    - workflow-state snapshot behavior
- Output requirements:
  - parser-compatible findings
- Prohibited actions:
  - commit
  - push
  - spec.json update
  - phase completion
- Requirement-to-prompt mapping:
  - Review purpose -> Review Task, Required Checks, and Vertical Intent Transfer Customization
  - Review focus -> Required Checks
  - Scope boundaries -> Review Target and Out Of Scope
  - Output requirements -> Finding Policy
  - Prohibited actions -> Out Of Scope and Finding Policy CRITICAL rules

## Generic API Review Core

- Keep criteria and target roles distinct.
- Treat the target files as the only review target.
- Treat source materials as background or intent-transfer evidence, not as targets.
- Do not use path-only source materials as model-readable evidence.
- Preserve user review requirements without narrowing, broadening, or replacement.
- Exclude credentials, personal identifiers, third-party non-sendable confidential material, and unrelated logs.
- Return parser-compatible findings only.

## Review Target

- `.reviewcompass/schema/approval_gate.schema.json`
- `tools/check-workflow-action.py`
- `tools/check_workflow_action/approval_gate.py`
- `tests/workflow-management/test_approval_gate.py`

At the actual review-run, pass every path listed here as --target. The API runner reads and injects those file contents into the model prompt; this section is the target manifest, not a substitute for target content.
If any one or more listed target path contents are absent from the injected prompt, report CRITICAL against Review Target and do not return findings: [].
If any listed target path is absent, stop the review after reporting the CRITICAL target-incompleteness finding; do not continue with partial target review.
For multi-target runs, treat a path as present only when the Target document contains a heading or label with the exact target path followed by non-empty file content. For the standard runner, the expected per-target heading form is `## <target path>`.
Treat a path as absent if the prompt does not contain an exact target-path section or label for that path, if a read error or placeholder is shown instead of file content, or if the injected section is empty.

Do not treat this criteria file, a wrapper, or an author-written summary as a substitute for the target.

## Source Materials

### workflow-management-req14-approval-gate-upstream-intent

Purpose: Requirement 14 / design / tasks intent for approval gates and human-only approval boundaries.

- source_paths:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/specs/workflow-management/tasks.md
- source_paths_note: source_paths are provenance only; use the structured summary fields below as the model-readable upstream intent material.
- source_material_injection_note: The structured summary, source excerpts, and cross-references in this section are model-readable upstream intent material. They must be present inline in the criteria prompt and must not be replaced by path-only references.
- source_language_note: Source excerpts may be in Japanese while structured summary fields may be in English. Treat both as model-readable upstream intent material; when translation or wording appears to conflict, prefer the source excerpts and report the discrepancy according to the conflict instructions.
- source_anchors:
  - .reviewcompass/specs/workflow-management/requirements.md sha256:e7621e6d56a3ef42085e2864a88366d670e55c304668dd21f48dde32411e13f3
  - .reviewcompass/specs/workflow-management/design.md sha256:ac6bd42e57b507a615af3ed6a40f3c031f56fe75f27e7f1fcc12ddcb4dc46558
  - .reviewcompass/specs/workflow-management/tasks.md sha256:053858cf4abf94bd7b54bf8a45a8ca9504afef39ea8be48bd282193f95e84098
- source_cross_references:
  - requirements.md lines 238-255: Requirement 14 purpose and acceptance criteria 1-3, 11, 12 define approval gates, record_human_decision separation, non-approved decision blocking, digest/actor/source binding, proxy/human boundary, and read/write operation separation.
  - design.md lines 1788-1833: Req 14 design model defines approval gate record fields, non-approved decision blocking, decision_scope derivation, binding_kind/digest requirements, human-only override set, and proxy_model limits.
  - design.md lines 2225-2236: Requirement trace table maps Req 14 acceptance criteria to the Req 14 design model.
  - tasks.md lines 127-128: Implementation tasks require proxy_model gating and explicitly state proxy_model is limited to implementation policy judgment, not commit, push, spec.json update, or phase transition.
- source_anchor_instruction: source_anchors are provenance. Do not attempt to verify hashes during this review. If injected source excerpts or target code visibly contradict the structured summary or cross-reference descriptions above, report the discrepancy as WARN or ERROR according to impact.
- source_label_instruction: If a source excerpt is visibly inconsistent with its file label, line range, or anchor description, report WARN against Source Materials; report ERROR if the mismatch changes required approval-gate behavior.
- source_conflict_instruction: If source excerpts and the structured summary visibly conflict, treat the source excerpts as higher-priority evidence for this review. If the conflict cannot be resolved from provided material, report WARN against Source Materials; report ERROR if the conflict changes required approval-gate behavior.

Source excerpts (model-readable upstream source text):

- requirements.md lines 240-246:
  - "保守担当者が、不可逆操作の承認、予期しない側道作業、現在状態の可視化を、LLM の暗黙解釈ではなく機械可読な状態として扱えるようにする。"
  - "本機能は承認ゲートを、`wait_for_human_decision` と `record_human_decision` のペア、およびその後の `next --json` による分岐として扱う。`record_human_decision` が完了した事実は、対象操作が承認された事実と同一視しない。"
  - "承認、拒否、保留、修正要求の各判断は、対象 operation ID、対象 `required_action`、対象 artifact または staged file set digest、判断者、判断時刻、出典を持つ。"
- requirements.md lines 254-255:
  - "commit、push、spec.json 更新、phase approval、reopen finalize、approval_required な不可逆操作の実行許可は human-only decision として扱い、proxy_model decision だけで通過させてはならない。"
  - "状態を書き換える push / pop / consume / invalidate / save 系操作と、状態を読む current / snapshot / inspect 系操作を同一 operation として曖昧化してはならない。"
- design.md lines 1803-1807:
  - "`approved` 以外の判断は対象不可逆操作へ進めない。"
  - "`decision_scope` は最低限 `human_only`、`proxy_allowed`、`advisory_only` の 3 値とする。"
  - "`binding_kind=none` は `wait_for_human_decision`、`collect_required_decisions`、`completed` のような read-only / wait-only operation に限る。"
- design.md lines 1820-1833:
  - "`decided_by=proxy_model` かつ `decision_scope=human_only` の record は承認として扱わず、`next --json` は対象不可逆操作へ進めない。"
  - "human-only decision の初期集合は commit、push、`spec.json` 更新、phase approval、reopen finalize、`approval_required=true` の不可逆 operation 実行許可とする。"
  - "proxy_model は finding triage、同根 cluster の採否案、補助的な整合判断を代行できる。ただし proxy_model decision は human-only decision の承認主体を置換しない。"
- design.md lines 2225-2236:
  - "Requirement 14：承認ゲート、側道スタック、状態スナップショット" maps acceptance criteria 1-3 and 11-12 to the Req 14 design model, including `decision_scope` / `binding_kind` / digest binding and proxy / human decision boundaries.
- tasks.md lines 127-128:
  - "`explicit_human_approval_recorded` 述語は `actor=proxy_model` の場合 `reviewcompass.yaml#human_proxy.proxy_allowed` を参照して代行可否を機械判定する。"
  - "proxy_model 代行は実装方針判断に限定し、コミット・プッシュ・spec.json 更新・フェーズ移行には使わない。"

Structured Summary (model-readable upstream intent):

- purpose: Treat irreversible-operation approval as machine-readable state, not as implicit LLM conversation context.
- responsibility_boundaries:
  - Approval gate records distinguish approved, rejected, deferred, and changes_requested decisions and bind them to the target operation, required_action, artifact or staged file set digest, actor, time, and source.
  - record_human_decision records a decision but does not itself authorize the target operation; next --json decides whether to proceed, stay blocked, redraft, or repair.
  - proxy_model may support triage or advisory judgments, but commit, push, spec.json update, phase approval, reopen finalize, and approval_required irreversible operations remain human-only.
- acceptance_criteria:
  - Approval gate schema and implementation enforce decision_scope, binding_kind, digest binding, source metadata, and non-approved decision blocking.
  - proxy_model decisions cannot satisfy human_only decisions and cannot replace human approval.
  - Focused tests cover approved, rejected, deferred, changes_requested, stale digest, wrong actor/source, and proxy/human boundary behavior.
- forbidden_actions:
  - Do not treat record_human_decision completion as target-operation approval.
  - Do not let proxy_model pass a human_only approval boundary.
  - Do not use binding_kind none for approval-required irreversible operations.
- unresolved_or_design_deferred_items:
  - No approval-gate-specific deferred items are currently recorded for this review. Any later claimed deferred item must not weaken the human-only approval boundary in the current implementation.
- unresolved_items_review_rule: If the target claims resolved behavior for an unresolved item without implementation evidence, report WARN or ERROR according to impact.
- intended_target_phase_transfer:
  - Implementation should expose approval gate validation and tests covering human/proxy boundaries, digest binding, and non-approved decision blocking.


## Vertical Intent Transfer Customization

Phase chain:

- requirements.md -> design.md -> tasks.md -> implementation

The upstream artifacts in this phase chain are represented by the model-readable structured summary, source excerpts, and cross-references in Source Materials above. Use those upstream materials only for background and transfer checking. Limit target judgment to the current phase artifact.

## Required Checks

1. Check the target against the single judgment item: Req 14 approval gate implementation upstream transfer.
2. Check that the target satisfies preserved user review requirements.
3. Check that source materials are used only for background or required intent transfer.
4. Check that no finding depends on unstated assumptions or path-only source material.
5. Respect review-run authority limits: do not approve, authorize, delegate, or imply approval of commit, push, spec.json update, phase completion, gate completion, or human-only approval. This is a reviewer behavior constraint, not a target finding.
6. Actively inspect whether the target code omits, weakens, contradicts, or bypasses required approval-gate behavior. Mentions of workflow-operation names are not sufficient evidence by themselves; schema field presence alone is not sufficient evidence of enforcement. Base findings on behavior, such as allowing or risking proxy_model decisions, non-approved decisions, stale digests, missing bindings, or wrong actor/source records to satisfy a human-only boundary. If a target file is present but contains only stub, placeholder, or non-enforcing content for required approval-gate behavior, treat that as missing or weakened behavior according to impact.
7. Check each preserved review focus item:
  - approval/proxy human-only boundary
  - approval decision binding and digest checks

## Out Of Scope

- side track stack behavior
- workflow-state snapshot behavior
- The reviewing model must not approve, authorize, delegate, or imply approval of commit, push, spec.json update, phase completion, gate completion, or human-only approval.
- These limits constrain this review run and the reviewing model; target code may still be reviewed when it omits, weakens, contradicts, or bypasses required approval-gate behavior.
- Do not judge downstream correctness unless a target omission would force downstream invention.

## Finding Policy

- Use CRITICAL for target behavior that bypasses human-only approval or irreversible-operation boundaries.
- Use CRITICAL if a listed target path is absent from the injected prompt, because the review target is incomplete.
- Use ERROR for missing required behavior, weakened user requirements, or unsupported target behavior.
- Treat stub, placeholder, or non-enforcing target content as missing or weakened behavior according to impact.
- Use WARN for meaningful ambiguity, weak traceability, or coverage gaps.
- Use INFO only for minor non-blocking improvements.
- Traceable evidence means a target file plus the narrowest available anchor for every checked claim, such as a line number, function name, schema field, JSON Pointer path, CLI option, fixture, or test case.
- For JSON schema targets, prefer schema field names or JSON Pointer paths over line numbers when they are the narrowest anchor.
- If required behavior is absent and no implementing anchor exists, state that no implementing code, schema field, fixture, or test case was found for the required behavior.
- For each finding, identify the target file and the narrowest available location such as line number, function, schema field, or test case.
- Return findings: [] if and only if every required check passes with traceable evidence and no deviation from the preserved review requirements or upstream intent.
