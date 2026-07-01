prompt_id: anthropic_review
provider: anthropic-api
model_id: claude-sonnet-4-6

# Task
Review the target document for the requested phase and criteria.

# Phase
prompt-quality

# Criteria
---
criteria_id: main-preanalysis-sufficiency-audit
phase: prompt-quality
review_target: <preanalysis-audit-bundle.md>
status: template
---

# Main Preanalysis Sufficiency Audit Criteria

Review the target bundle before the actual API review-run.

The target bundle must contain:

- the user or workflow review requirement
- the source materials needed for the judgment item
- the main session LLM preanalysis
- the proposed API review criteria or prompt

The review question is:

Can the proposed API review prompt derive the needed review judgment from the provided source materials, without relying on the main preanalysis as an answer key, and does the main preanalysis reveal any missing viewpoints, unsupported claims, or framing bias that must be corrected before the real review-run?

## Required Method

Perform the audit in this order:

1. Independently reconstruct the judgment item from the source materials and user or workflow requirement.
2. Compare that reconstruction with the main preanalysis.
3. Judge whether the proposed API review prompt gives enough source material, scope, question, and output instructions for the actual reviewer.
4. Identify required prompt changes before any real review-run.

Treat the main preanalysis as a hypothesis and source-discovery aid. Do not treat it as ground truth.

## Required Checks

### Independent Reconstruction

From the source materials alone, identify:

- the judgment item ID
- the exact review question
- the target artifact or section
- the source materials that are necessary
- the material that is out of scope
- the rationale connecting the source materials to the review question

If multiple independent judgment items are present, report that the proposed review prompt must be split.

### Main Preanalysis Assessment

Compare the main preanalysis against the independent reconstruction.

Check for:

- supported parts that are well grounded in the sources
- missing perspectives or missing source materials
- unsupported, overconfident, or overstated parts
- framing bias, including treating a draft answer as established fact
- source coverage gaps caused by path-only references, summaries without source basis, or omitted upstream context

### Prompt Sufficiency

Judge whether the proposed API review prompt:

- includes enough model-readable source material
- asks one non-leading primary question
- keeps target, source materials, and out-of-scope material distinct
- preserves user or workflow requirements without narrowing, broadening, or replacing them
- defines the expected output clearly enough for the runner
- prevents the reviewer from authorizing commit, push, phase completion, human approval delegation, or unapproved specification changes

## Finding Policy

- Report `CRITICAL` if the prompt would authorize or imply authorization of irreversible operations, human-only approval, phase completion, or unapproved repository changes.
- Report `ERROR` if the prompt cannot support the requested review because source materials are missing, path-only, wrong, or treated as target material.
- Report `ERROR` if multiple independent judgments are bundled into one prompt.
- Report `ERROR` if the prompt depends on the main preanalysis as the answer instead of requiring source-based independent judgment.
- Report `ERROR` if user or workflow review requirements are omitted, narrowed, broadened, or replaced.
- Report `WARN` for usable prompts with avoidable ambiguity, incomplete source mapping, weak target/source separation, or bias risk.
- Report `INFO` for minor clarity or ergonomics improvements.

## Output Contract

Return YAML only. Do not wrap it in Markdown fences.

The response must include these top-level keys:

- `verdict`
- `independent_reconstruction`
- `preanalysis_assessment`
- `prompt_sufficiency`
- `required_prompt_changes`
- `findings`

Use one of these `verdict` values:

- `sufficient`
- `sufficient_with_revisions`
- `insufficient`

Use this shape:

verdict: sufficient_with_revisions
independent_reconstruction:
  judgment_items:
    - item_id: "<stable-id>"
      question: "<source-derived review question>"
      target_files:
        - "<path or section>"
      source_materials:
        - "<path, section, or embedded source label>"
      out_of_scope:
        - "<material or action not judged>"
      rationale: "<why this is the right judgment item>"
preanalysis_assessment:
  supported_parts:
    - "<grounded part>"
  missing_perspectives:
    - "<missing viewpoint or source>"
  unsupported_or_overconfident_parts:
    - "<claim that needs source support or softening>"
  bias_risks:
    - "<framing or anchoring risk>"
prompt_sufficiency:
  information: "sufficient | revisions_needed | insufficient"
  question: "sufficient | revisions_needed | insufficient"
  scope: "sufficient | revisions_needed | insufficient"
  sensitivity_check: "sufficient | revisions_needed | insufficient"
  notes:
    - "<short note>"
required_prompt_changes:
  - "<required change before actual review-run>"
findings:
  - severity: WARN
    target_location: "<section in proposed prompt or bundle>"
    description: "<concise finding>"
    rationale: "<why this matters>"

If there are no defects, return `verdict: sufficient`, complete the assessment keys with empty lists where appropriate, and return:

findings: []


# Output contract
Return YAML only.
The response must include the top-level key findings.
Additional top-level keys are allowed only when the criteria explicitly defines them.
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

If there are no findings and the criteria does not define additional top-level keys, return exactly:

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
.reviewcompass/specs/workflow-management/reviews/2026-07-01-workflow-management-design-review-run/preanalysis-audit-bundle.md

# Target document
---
bundle_id: workflow-management-design-reopen-protocol-preanalysis-audit
phase: prompt-quality
target_proposed_review_criteria: not_created_yet_by_protocol
main_preanalysis: .reviewcompass/specs/workflow-management/reviews/2026-07-01-workflow-management-design-review-run/main-preanalysis.md
source_materials: embedded
status: draft_for_preanalysis_sufficiency_audit
---

# Preanalysis Audit Bundle: workflow-management design reopen-protocol

This bundle is the target for `main-preanalysis-sufficiency-audit`.

The reviewer must not judge `design.md` itself yet. The reviewer must judge whether the main preanalysis provides enough source material, scope control, judgment-item separation, and authority boundaries for a later design triad-review.

The formal API review criteria has not been drafted yet because the active protocol state is `preanalysis_sufficiency_audit_required`. Treat the section "Proposed Criteria Seed" as the proposed future prompt shape to audit, not as an approved criteria file.

## User And Workflow Review Requirement

- Review purpose: `workflow-management` design triad-review preparation during an active reopen.
- Review object: main preanalysis and proposed future criteria seed for checking whether reopen protocol mechanization requirements were correctly transferred into `design.md`.
- Review focus:
  - requirements-to-design vertical transfer
  - edited phase full-gate chain
  - downstream impact decision evidence
  - fail-closed detection order at `next --json`, `reopen-finalize`, and commit preflight
  - superseding reopen record policy
  - design-stage target/source/out-of-scope separation
- Scope boundary:
  - In scope: whether the main preanalysis and proposed future criteria seed are sufficient to support a later design review.
  - Out of scope: actual correctness of tasks.md, implementation code, runner behavior, `spec.json` update, phase transition, commit, push, proxy_model decision, or gate completion.
- Required method:
  - Use the embedded source materials to reconstruct the judgment item independently.
  - Treat main preanalysis as a hypothesis and source-discovery aid, not as an answer key.
  - Identify required changes before criteria draft and before any real review-run.

## Review Target Manifest

The later actual review-run target is only:

- `.reviewcompass/specs/workflow-management/design.md`

Expected relevant target locations:

- `design.md` §reopen 機械強制モデル §5.
- `design.md` §session 跨ぎ状態管理モデル §1.
- `design.md` §Req 12 設計モデル §11.
- `design.md` §Req 16 設計モデル §2.
- `design.md` 変更履歴の 2026-07-01 entry.

These target locations are not source material. The actual review-run must pass the full target file as target content.

## Source Materials

This section embeds the source content needed for the audit. Path references are
provenance only; they are not evidence by themselves.

### Exact Upstream Requirement Excerpts

#### Requirement 5 acceptance 7

Source: `.reviewcompass/specs/workflow-management/requirements.md`

> 本機能は reopen state に、正本本文を実質編集する phase を `edited_phases` として、下流確認対象を `impacted_downstream_phases` として機械可読に保持する。`edited_phases` に含まれる phase は、`triad-review`、`review-wave`、`alignment`、`approval` の全 gate を再実施対象にしなければならない。上流 phase を編集した場合、下流 phase ごとの影響判断は `downstream_impact_decisions` に、少なくとも対象 gate、feature scope、判断、理由、証跡を持つ record として記録する。下流 phase を変更しない `no_impact` または `existing_sufficient` 判断も省略扱いせず、同じ 5 項目を持つ record として記録しなければならない。`next --json` は edited phase の必須 gate または downstream impact decision の不足を通常完了より前に検出し、`reopen-finalize` は completed reopen 記録を生成する前に必須 gate と downstream impact decision を再計算して不足を拒否する。commit preflight は最後の保険であり、通常経路の最初の検出点として扱ってはならない。既存の completed reopen に手続き不備がある場合は、履歴を改変せず superseding reopen record として置き換え理由を残す。この superseding reopen record も、対象となる edited phase について `triad-review`、`review-wave`、`alignment`、`approval` の全 gate を満たさなければならない。downstream impact decision の feature scope は Requirement 16 受入 11〜12 の active reopen scope / impact review scope / consumer・derivative feature scope の区別と整合しなければならない。

#### Requirement 12 acceptance 13-14

Source: `.reviewcompass/specs/workflow-management/requirements.md`

> 本機能は、Requirement 2 が所有する `next --json` の reopen 出力契約を拡張し、operation registry / preflight が `next` 状態を一意に参照できるようにする。`next` が `reopen_in_progress` を返す場合、現在の本線、次に実行すべき `required_action`、phase、stage、reopen scope、impact review scope、direct features、indirect features、flag policy、`next_pending_gate`、`next_drafting_gate`、`pending_gates`、`completed_gates`、superseded gate の有無、参照した state files を機械可読に返し、どの feature の workflow flag を false に戻し、どの feature の flag を維持するかを一意に判定できるようにする。これらの値は `feature_impact_decisions`、`spec.json`、`pending_gates`、`drafting_completed_gates`、`downstream_impact_decisions` と整合していなければならない。reopen scope と impact review scope が欠落、矛盾、または `feature_impact_decisions` / `spec.json` / `pending_gates` と整合しない場合、`next` は通常進行を許す `OK` として扱わず、`WARN` または `DEVIATION` と理由を返して停止させる。
>
> Requirement 12 の preflight は `next --json` の出力を複製せず、Requirement 2 の selector 結果を参照する。preflight が扱う `state_refs.next_action` では、`required_action`、`active_gate`、`blocked_by`、`action_parameters`、`state_refs` を用いて唯一 action と補助情報を分離し、古い in-progress record、複数 frame、pending gate、maintenance action を LLM が解釈で選ぶ経路を作らない。

#### Requirement 14 acceptance 11

Source: `.reviewcompass/specs/workflow-management/requirements.md`

> 承認ゲートは proxy_model が代行できる判断と、人間だけが承認できる判断を機械可読に区別する。少なくとも commit、push、spec.json 更新、phase approval、reopen finalize、approval_required な不可逆操作の実行許可は human-only decision として扱い、proxy_model decision だけで通過させてはならない。proxy_model は所見 triage や補助判断を代行できるが、human-only decision の承認主体を置換しない。proxy_model の適用可否と human-required predicate の優先順位は Requirement 16 受入 13〜14 と整合させる。

#### Requirement 16 acceptance 11-12

Source: `.reviewcompass/specs/workflow-management/requirements.md`

> 本改訂の active reopen scope は `workflow-management` の requirements から design / tasks / implementation への連鎖再実施である。active scope の正本は `stages/in-progress/reopen-procedure-*.yaml` の `active_reopen_scope` と `active_impact_review_scope` である。`spec.json.reopened` は過去に上流を reopen した履歴フラグとして保持され得るため、現在の active reopen scope と同一視しない。
>
> `active_reopen_scope` は正本を再オープンして workflow_state flag を false に戻した feature / phase / gate 範囲を持つ。`active_impact_review_scope` は、正本変更の有無を確認する consumer / derivative feature / phase / gate 範囲を持つが、当該 feature の workflow_state flag を自動で false に戻す根拠ではない。`next --json` は reopen 中にこの in-progress record を必ず読み、scope が欠落・不整合・stale の場合は `repair_workflow_state` を返す。

### Design Target Excerpts

These excerpts are the later actual review target, not source material. They are
included here so the preanalysis auditor can check whether the proposed criteria
points to concrete target locations.

#### `design.md` reopen mechanical enforcement model, section 5

> 本機能が管理する再オープン手続きの全体構成を、現在の 5 段ワークフロー（drafting → triad-review → review-wave → alignment → approval）に合わせて 4 つの過程で定義する。
>
> `edited_phases` に含まれる phase は、正本本文を実質編集した phase として扱う。対象 phase は trigger_map の最小 gate だけでは足りず、`triad-review`、`review-wave`、`alignment`、`approval` の full gate chain を必須にする。
>
> `impacted_downstream_phases` に含まれる phase は、正本本文を変更しない場合でも影響判断の対象である。下流 phase ごとの `no_impact`、`existing_sufficient`、`affected_update_required`、`approved` などの判断は省略不可で、`downstream_impact_decisions` に `gate`、`feature_scope`、`decision`、`rationale`、`evidence` を最低限持つ record として残す。
>
> 検出順は、通常経路では `next --json` が最初に不足を見つける。`reopen-finalize` は完了直前の再計算ガードとして、`commit-preflight` は最後の保険として同じ不足を遮断する。

#### `design.md` session-spanning state model, section 1

> `active_reopen_scope` と `active_impact_review_scope` は active scope の正本である。`spec.json.reopened` は過去に reopen した履歴フラグであり、active scope の正本ではない。`next --json` は reopen 中に `stages/in-progress/reopen-procedure-*.yaml` を読み、これら 2 フィールドから `next_action.reopen_scope` と `next_action.impact_review_scope` を生成する。

#### `design.md` Requirement 12 design model, section 11

> `reopen_scope` は正本を再オープンして flag を false に戻す feature、`impact_review_scope` は正本変更要否だけを確認し flag を維持する feature である。active scope の正本は `stages/in-progress/reopen-procedure-*.yaml` の `active_reopen_scope` と `active_impact_review_scope` であり、`next --json` はこれらを `next_action.reopen_scope` と `next_action.impact_review_scope` へ写す。

#### `design.md` Requirement 16 design model, section 2

> `active_reopen_scope` は正本を再オープンして workflow_state flag を false に戻した feature / phase / gate 範囲を持つ。`active_impact_review_scope` は、正本変更の有無を確認する consumer / derivative feature / phase / gate 範囲を持つが、当該 feature の workflow_state flag を自動で false に戻す根拠ではない。

### Structured Source Summary

```yaml
source_materials:
  - key: requirements-contract
    purpose: Upstream canonical contract that design must implement.
    source_path: .reviewcompass/specs/workflow-management/requirements.md
    structured_summary:
      - Requirement 5 acceptance 7 requires reopen state to retain edited_phases and impacted_downstream_phases.
      - edited_phases require triad-review, review-wave, alignment, and approval.
      - downstream no-change decisions still need gate, feature_scope, decision, rationale, and evidence.
      - next --json must detect missing gates or downstream decisions before normal completion.
      - reopen-finalize must recompute required gates and decisions before creating completed reopen records.
      - commit preflight is a final guard, not the first normal detector.
      - pushed incomplete completed reopen records must be handled by superseding reopen records, not history rewriting.
      - Requirement 12 requires next --json reopen output to expose active gate, required action, reopen scope, impact review scope, pending gates, completed gates, and state references without the LLM reselecting from context.
      - Requirement 14 acceptance 11 keeps proxy_model out of commit, push, spec.json update, phase approval, reopen finalize, and other human-only authorization.
      - Requirement 16 distinguishes active reopen scope from active impact review scope and consumer / derivative feature scope.
  - key: reopen-protocol-mechanization-plan
    purpose: Upstream planning and workflow decision material for why this reopen exists.
    source_path: .reviewcompass/backlog/plans/plan-2026-07-01-reopen-protocol-mechanization-review.yaml
    problem:
      - A previous requirements-changing reopen did not rerun requirements triad-review and review-wave.
      - Downstream design/tasks/implementation impact was handled as late supplemental metadata.
      - Missing downstream decisions were detected too late, around finalize or commit.
    invariants:
      - id: RPMR-I1
        statement: edited_phases must be machine-readable.
      - id: RPMR-I2
        statement: edited phases require triad-review, review-wave, alignment, and approval.
      - id: RPMR-I3
        statement: upstream phase edits require impacted_downstream_phases and downstream_impact_decisions.
      - id: RPMR-I4
        statement: downstream no-change decisions still need gate, feature_scope, decision, rationale, and evidence.
      - id: RPMR-I5
        statement: next --json must return reopen missing work instead of normal completion when gates or decisions are missing.
      - id: RPMR-I6
        statement: reopen-finalize must recompute required gates and decisions before completed record creation.
      - id: RPMR-I7
        statement: commit preflight is a final guard, not the first normal detector.
    historical_policy_question:
      - id: RPMR-Q3
        statement: Push済みで手続き不備のある completed reopen は履歴改変ではなく superseding reopen record として扱う。
    superseded_by_requirements:
      - Requirement 5 acceptance 7 now makes the superseding reopen record policy normative for this review.
      - Treat RPMR-Q3 as historical planning context, not as an unresolved policy question for the later design review.
  - key: current-reopen-state
    purpose: Active reopen state for the design gate.
    source_path: stages/in-progress/reopen-procedure-2026-07-01.yaml
    structured_state:
      classification: R-0
      edited_phases:
        - requirements
      impacted_downstream_phases:
        - design
        - tasks
        - implementation
      completed_requirement_gates:
        - stages/requirements.yaml#triad-review
        - stages/requirements.yaml#review-wave
        - stages/requirements.yaml#alignment
        - stages/requirements.yaml#approval
      drafting_completed_gates:
        - stages/requirements.yaml#drafting
        - stages/design.yaml#drafting
      active_gate: stages/design.yaml#triad-review
      pending_gates:
        - stages/design.yaml#triad-review
        - stages/design.yaml#review-wave
        - stages/design.yaml#alignment
        - stages/design.yaml#approval
        - stages/tasks.yaml#triad-review
        - stages/tasks.yaml#review-wave
        - stages/tasks.yaml#alignment
        - stages/tasks.yaml#approval
        - stages/implementation.yaml#triad-review
        - stages/implementation.yaml#review-wave
        - stages/implementation.yaml#alignment
        - stages/implementation.yaml#approval
  - key: current-spec-state
    purpose: Current machine workflow state.
    source_path: .reviewcompass/specs/workflow-management/spec.json
    structured_state:
      requirements:
        drafting: true
        triad-review: true
        review-wave: true
        alignment: true
        approval: true
      design_tasks_implementation:
        drafting_through_approval: false
      recheck:
        upstream_change_pending: true
        impacted_downstream_phases:
          - design
          - tasks
          - implementation
  - key: reopen-procedure-guidance
    purpose: Governing reopen procedure.
    source_path: .reviewcompass/guidance/REOPEN_PROCEDURE.md
    structured_summary:
      - A phase with substantive canonical artifact changes must rerun triad-review, review-wave, alignment, and approval.
      - Downstream impact decisions are required for requirements/design/tasks/implementation edits, not only intent edits.
      - No-change downstream decisions still need gate, feature scope, decision, rationale, and evidence.
      - Missing required gates or decisions must fail closed.
  - key: vertical-intent-transfer-guidance
    purpose: Governing review-scope rule for design triad-review.
    source_path: .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review
    structured_summary:
      - Design review checks requirements.md against design.md.
      - tasks.md and implementation may be source context but are not correctness targets for design review.
      - Source materials must not be path-only.
      - Required prompt material includes purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, and intended target-phase transfer.
  - key: api-review-protocol-guidance
    purpose: Governing TRIAD review / API review-run sequence.
    source_paths:
      - .reviewcompass/guidance/API_REVIEW_PROMPT_QUALITY.md
      - .reviewcompass/guidance/discipline_llm_as_judge_prompting.md
      - .reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2
    structured_summary:
      - main preanalysis precedes review-run and is not ground truth.
      - preanalysis sufficiency audit must verify material selection, split, judgment items, and source selection.
      - prompt quality review requires adversarial review, main revision, and judgment approval before actual review-run.
      - actual review-run must save raw, parsed, rounds, model summary, triage, and target manifest artifacts.
      - user-visible triage is a required stop before proxy_model, implementation edits, spec.json update, or phase movement.
      - proxy_model cannot authorize commit, push, spec.json update, phase transition, or human-only approval.
  - key: behavior-path-source-summary
    purpose: Behavior-path source material for fail-closed claims.
    source_paths:
      - tools/check-workflow-action.py
      - tests/tools/test_check_workflow_action.py
    structured_summary:
      - This code/test material is supporting behavior-path context only.
      - The normative source for what design.md must say is requirements.md, REOPEN_PROCEDURE.md, and workflow guidance.
      - The later design review must not treat unapproved implementation behavior as the standard.
      - helper functions derive downstream phases from edited phases.
      - helper functions expand edited phases and downstream reopen phases to full gates.
      - next --json reports missing drafting or missing downstream impact decisions before normal gate completion.
      - reopen-finalize rejects completed records when downstream decisions are missing.
      - commit preflight remains a final irreversible-operation guard.
      - focused tests cover edited phase downstream scope, dynamic downstream phase, finalize rejection, and drafting-before-review prevention.
```

## Main Preanalysis Under Audit

- Path: `.reviewcompass/specs/workflow-management/reviews/2026-07-01-workflow-management-design-review-run/main-preanalysis.md`
- Embedded content: the relevant main preanalysis follows. The auditor must treat it as a hypothesis, not as ground truth.

```markdown
# Main Preanalysis: workflow-management design reopen protocol review

対象 gate: `stages/design.yaml#triad-review`
位置づけ: 実 review-run 前の main preanalysis。これは reviewer への正解ではなく、source selection と判断項目の仮説である。

今回の triad-review は、`workflow-management` の `design.md` を対象に、requirements Requirement 5 受入 7 で確定した reopen protocol mechanization 契約が、設計層へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているかを確認する。

最低限の問いは次である。

- `requirements.md` の edited phase / downstream impact / fail-closed / superseding reopen 契約が、`design.md` の reopen 機械強制モデルへ設計として落ちているか。
- `design.md` の審査対象は design 本文であり、tasks / implementation の correctness はこの gate の対象外である。
- behavior-path claim を含むため、文書だけでなく `next --json`、`reopen-finalize`、commit preflight、関連 runner / tests を source material 候補に含める。
- review-run、proxy_model、`spec.json` 更新、phase/gate 完了、commit、push はこの preanalysis の範囲外であり、ここでは実行しない。

Claim 1: requirements-to-design vertical transfer
- Target: `design.md` §reopen 機械強制モデル §5、変更履歴。
- Source: `requirements.md` Requirement 5 受入 7、plan invariants、REOPEN_PROCEDURE。
- Out of scope: tasks.md / implementation code の正しさ。

Claim 2: edited phase full gate chain
- Target: `design.md` §reopen 機械強制モデル §5。
- Source: Requirement 5 受入 7、current reopen state、plan invariants RPMR-I1/I2。
- Out of scope: 現在の implementation が完全に full gate chain を検査しているかの判定。

Claim 3: downstream impact decision evidence
- Target: `design.md` §reopen 機械強制モデル §5、§session 跨ぎ状態管理モデル §1、§Req 12 設計モデル §11、§Req 16 設計モデル §2。
- Source: Requirement 5 受入 7、Requirement 16 受入 11〜12、REOPEN_PROCEDURE。
- Out of scope: design/tasks/implementation の downstream 正本文そのものの十分性。

Claim 4: fail-closed surface order
- Target: `design.md` §reopen 機械強制モデル §5、§Req 12 設計モデル §11。
- Source: Requirement 5 受入 7、behavior-path source summary、focused tests。
- Out of scope: 個々の関数のコードレビュー。

Claim 5: superseding reopen policy
- Target: `design.md` §reopen 機械強制モデル §5、変更履歴。
- Source: Requirement 5 受入 7、plan RPMR-Q3 as superseded historical context、current reopen trigger。
- Out of scope: 過去 completed reopen record の内容修正。

Claim 6: review target boundary
- Target: `design.md` と review prompt requirement。
- Source: SESSION_WORKFLOW_GUIDE vertical intent transfer、next required inputs、requirements.md。
- Out of scope: tasks.md / implementation の正しさ。

Open: prompt を 1 本にするか、behavior-path claim を分割するかは preanalysis sufficiency audit と prompt quality review で確認する。
```

## Proposed Criteria Seed

The later criteria draft should ask one primary non-leading question:

> Does `design.md` carry Requirement 5 acceptance 7 and related active-scope/proxy-boundary contracts into the design layer without omission, weakening, unsupported addition, target/source confusion, or authorization of out-of-scope operations?

The required content checks should cover:

1. Requirements-to-design transfer of purpose, responsibility boundary, acceptance criteria, and forbidden actions.
2. Whether edited phase full gate chain is designed as mandatory.
3. Whether downstream no-impact / existing-sufficient decisions require gate, feature_scope, decision, rationale, and evidence.
4. Whether fail-closed detection order assigns normal detection to `next --json`, completion guard to `reopen-finalize`, and final irreversible guard to commit preflight.
5. Whether pushed incomplete completed reopen records are handled as superseding reopen records without history rewriting.
6. Whether active reopen scope / active impact review scope / consumer-derivative feature scope are kept distinct where the design relies on these terms.
7. Whether proxy_model is explicitly kept out of commit, push, `spec.json` update, phase approval, reopen finalize, and human-only authorization.

Meta/process checks for the later criteria draft:

1. The review target is `design.md`; tasks / implementation correctness are out of scope.
2. Target, source materials, and out-of-scope material are separated.
3. The criteria contains the output contract expected by `run_review.py`.

The criteria must prohibit the reviewer from authorizing commit, push, phase completion, human approval delegation, proxy_model decision, implementation edits, or unapproved specification changes.

The later review-run output contract should require YAML with at least:

- `verdict`
- `reviewed_target`
- `source_materials_used`
- `findings`
- `out_of_scope_not_judged`

## Expected Audit Output Use

If the audit returns required changes, main must revise the preanalysis and/or source bundle before criteria draft.

If the audit returns `verdict: sufficient` or `sufficient_with_revisions` with no blocking findings, main may proceed to criteria draft, carrying any required prompt changes forward.

