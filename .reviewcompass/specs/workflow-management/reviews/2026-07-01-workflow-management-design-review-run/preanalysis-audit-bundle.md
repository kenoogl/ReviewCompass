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
  - `next --json` reopen output contract and operation preflight boundary
  - proxy_model / human-only authorization boundary
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
- `design.md` §review-run 後の proxy_model 判断代行モデル.
- `design.md` §Req 14 設計モデル §1〜3.

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

#### Requirement 16 acceptance 13-14

Source: `.reviewcompass/specs/workflow-management/requirements.md`

> proxy_model triage decision の適用可否は、provider / model 名ではなく、機械可読な evidence completeness、対象 finding / cluster coverage、approval gate record、operation contract の `approval_required`、review-wave impact evidence、human-only decision 境界に基づいて判定する。human-required を示す証跡が 1 つでも存在する場合、または必要な判定元が欠落・競合する場合、proxy_model decision だけで通過させてはならない。
>
> human-required predicate の優先順位と競合解決は design で確定する。最低限、human-only decision 境界、未解決 approval gate、`approval_required: true` の対象 operation、未解決 review-wave impact evidence は proxy_model 適用より優先される。triage 上の leave-as-is や proxy approved は、これらの human-required 証跡を打ち消さない。

### Exact Planning Excerpts

#### reopen protocol mechanization plan

Source: `.reviewcompass/backlog/plans/plan-2026-07-01-reopen-protocol-mechanization-review.yaml`

> 直近の backlog routing reopen では `requirements.md` を変更したが、requirements の triad-review と review-wave を通さずに alignment と approval へ進んだ。
>
> design/tasks/implementation への下流影響は認識されたが、通常の第3過程の連鎖としてではなく、finalize/commit 修復時の補足判断として追加された。
>
> 既存の機械検査は、下流影響判断の不足を `reopen-finalize` が completed 記録を生成した後、commit 時にようやく検出した。
>
> 規律としては、正本本文を実質修正した phase は triad-review、review-wave、alignment、approval を再実施する必要がある。しかし、reopen state が「どの phase を実質編集したか」を機械的な必須入力として保持していないため、pending_gates が alignment/approval だけでも早期に止めにくい。
>
> requirements 変更後の design/tasks/implementation 影響判断は必須だが、`reopen-start` や `next --json` が「下流 phase ごとの判断予定」を一貫して要求していない。そのため、不足が `reopen-finalize` や commit preflight まで遅れて見つかりうる。
>
> downstream が「変更不要」または「既存成果物で十分」と判断された場合も、gate、feature_scope、decision、rationale、evidence を持つ判断証跡が必須である。これが不足している状態を `next --json` 段階で次作業として返す機械処理が不足している。
>
> RPMR-I1: reopen state は、実質編集した phase を `edited_phases` または同等の正本フィールドで機械可読に保持する。
>
> RPMR-I2: `edited_phases` に含まれる各 phase は、required gates として `triad-review`、`review-wave`、`alignment`、`approval` をすべて要求する。
>
> RPMR-I3: 上流 phase が編集された場合、下流 phase ごとの影響判断予定を `impacted_downstream_phases` と `downstream_impact_decisions` で覆う。
>
> RPMR-I4: 下流 phase を実際に修正しない場合でも、`existing_sufficient` または `no_impact` の downstream impact decision を gate 単位で記録する。
>
> RPMR-I5: `next --json` は、edited phase の required gates または downstream impact decision が不足している場合、completed や通常作業を返さず、reopen の不足作業を返す。
>
> RPMR-I6: `reopen-finalize` は、pending_gates が空であっても、edited phase と downstream phase から必須 gate / 必須 decision を再計算し、不足があれば completed 記録を生成しない。
>
> RPMR-I7: commit preflight は最後の保険として同じ不足を検出する。ただし初検出地点を commit に置かず、`next --json` と `reopen-finalize` で先に fail-closed させる。
>
> RPMR-Q3: push 済みだが手続き上 incomplete な reopen は、workflow-state の修復、新しい reopen、superseding reopen record のどれとして表現するべきか。

### Exact Workflow Guidance Excerpts

#### REOPEN_PROCEDURE 第3過程

Source: `.reviewcompass/guidance/REOPEN_PROCEDURE.md`

> `pending_gates` は review 系 gate（triad-review／review-wave／alignment／approval）の処理順を表す。phase の正本本文を更新する必要があり、先頭 gate が triad-review の場合、triad-review の前に drafting を実施する。drafting 完了後は `drafting_completed_gates` に `stages/<phase>.yaml#drafting` を記録し、その後に triad-review へ進む
>
> 正本本文（`.reviewcompass/specs/<feature>/<phase>.md`）を実質修正した phase は、triad-review → review-wave → alignment → approval の順に再実施する。これは requirements／design／tasks／implementation のいずれでも同じ
>
> 上流変更に対する下流影響判定を `downstream_impact_decisions` に記録する。これは intent に限らず、feature-partitioning／requirements／design／tasks／implementation のいずれを変更した場合も共通で必須とする
>
> 「既存で受けられる」「修正不要」と判断する場合も、判定対象 gate、feature 範囲、判断、理由、証跡を記録する。修正不要は reopen を省略する理由ではなく、reopen 後の影響判定結果としてのみ扱う
>
> approval は人間の承認（actor=human）。proxy_model は review-run 後の重要件判断だけを代行でき、approval 段の代行主体にはしない

#### REOPEN_PROCEDURE 第4過程

Source: `.reviewcompass/guidance/REOPEN_PROCEDURE.md`

> `reopen-finalize` で recheck をクリアする（`upstream_change_pending=false`、`impacted_downstream_phases=[]`）、第4過程完了履歴を追加する、進行中状態ファイルを `stages/completed/` へ移動する、の 3 点を一括で行う。`reopened.<上流>` は `true` のまま残す（履歴）。
>
> 第4過程の完了 commit では、`stages/completed/reopen-procedure-*.yaml` に `feature_impact_decisions`、`new_feature_decision`、`impacted_downstream_phases` と、`pending_gates` の各 gate を覆う `downstream_impact_decisions` が必要である。
>
> 完了 commit に正本本文の変更が含まれる phase は、`pending_gates` に triad-review／review-wave／alignment／approval をすべて含め、drafting を実施した phase は `drafting_completed_gates` または `completed_gates` に `stages/<phase>.yaml#drafting` を含める。

#### SESSION_WORKFLOW_GUIDE vertical intent transfer

Source: `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#vertical-intent-transfer-review`

> 各 phase の triad-review／review-wave／alignment では、対象 phase の成果物だけでなく、上流成果物または上流判断材料からの意図伝達を必須検査項目とする。review prompt は、少なくとも「上流の目的・責務境界・受入条件・禁止事項が、対象成果物へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているか」を問わなければならない。
>
> **design review**：`requirements.md → design.md` を確認し、要件の目的・境界・受入条件が設計へ欠落なく落ちているかを検査する
>
> review prompt は、review target / source materials / out of scope を明示する。審査対象は現在 phase の成果物に限定し、source materials は背景・意図伝達確認のための参照資料として扱う。下流 phase の成果物が source materials に含まれる場合でも、その correctness を現在 phase の review で判定してはならない。

#### SESSION_WORKFLOW_GUIDE §3.3(a-2) proxy_model gate

Source: `.reviewcompass/guidance/SESSION_WORKFLOW_GUIDE.md#3.3-a-2`

> API review-run が完了したら、proxy_model 判断依頼、実装修正、spec.json 更新、フェーズ移行のいずれにも進む前に、メインセッション LLM は次を利用者へ提示して停止する。この提示ゲートを完了する前に proxy_model を呼び出してはいけない。
>
> proxy_model に判断させる場合の対象 finding／cluster、判断範囲、不可逆操作（commit／push／spec.json 更新／フェーズ移行）を含まないこと
>
> コミット・プッシュ・spec.json 更新・フェーズ移行は人間の明示承認を要求する。proxy_model はこれらの不可逆操作を代行しない

### Design Target Excerpts

These excerpts are the later actual review target, not source material. They are
included here so the preanalysis auditor can check whether the proposed criteria
points to concrete target locations.

Do not use this section as evidence that `design.md` is correct. Excerpt presence
only proves that the proposed criteria points to concrete target locations. The
later reviewer must inspect the full target file independently.

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

#### `design.md` lightweight checker model, sections 4-5

> 共通フィールドは `kind`、`required_action`、`active_gate`、`feature`、`phase`、`stage`、`blocked_by`、`action_parameters`、`state_refs` とする。active workflow unit があるのは、通常 workflow の `<feature, phase, stage>` または reopen 第3過程の drafting / review gate だけである。この場合だけ `active_gate`、`feature`、`phase`、`stage` を非 null にする。
>
> selector の優先順位は、workflow state / reopen plan の破損、post-write verification pending、human decision、maintenance / side track top frame、reopen commit stop point、reopen 第1・第2過程、reopen 第3過程 drafting、reopen 第3過程 gate、reopen 第4過程、通常 workflow、completed の順に固定する。

#### `design.md` Requirement 16 design model, section 2

> `active_reopen_scope` は正本を再オープンして workflow_state flag を false に戻した feature / phase / gate 範囲を持つ。`active_impact_review_scope` は、正本変更の有無を確認する consumer / derivative feature / phase / gate 範囲を持つが、当該 feature の workflow_state flag を自動で false に戻す根拠ではない。

#### `design.md` proxy_model delegation model

> review-run 後の重要件判断は、approval 段の承認ではなく、triad-review 段内の修正方針決定に限って proxy_model が代行できる。
>
> 利用者：コミット、プッシュ、spec.json 更新、フェーズ移行、規律変更、大方針変更を承認する
>
> proxy approval は human-only approval、commit、push、`spec.json` 更新、phase / gate completion、reopen finalize を許可しない。

#### `design.md` Requirement 14 design model, human-only predicate

> human-only decision の初期集合は次とする。
>
> - commit
> - push
> - `spec.json` 更新
> - phase approval
> - reopen finalize
> - `approval_required=true` の不可逆 operation 実行許可
>
> proxy_model は finding triage、同根 cluster の採否案、補助的な整合判断を代行できる。ただし proxy_model decision は human-only decision の承認主体を置換しない。

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
      - Requirement 16 acceptance 13-14 makes proxy applicability depend on evidence completeness, finding/cluster coverage, approval gate record, operation contract approval_required, review-wave impact evidence, and human-only boundaries rather than provider/model names.
  - key: reopen-protocol-mechanization-plan
    purpose: Upstream planning and workflow decision material for why this reopen exists.
    source_path: .reviewcompass/backlog/plans/plan-2026-07-01-reopen-protocol-mechanization-review.yaml
    embedded_excerpt: "Exact Planning Excerpts / reopen protocol mechanization plan"
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
      - These paths are provenance hints, not required readable evidence for the later review-run unless excerpts are explicitly embedded in the criteria.
      - If code/test excerpts are not embedded, no finding may depend on current implementation behavior or on reviewer access to these paths.
      - helper functions derive downstream phases from edited phases.
      - helper functions expand edited phases and downstream reopen phases to full gates.
      - Criteria may refer to the existence of runner/test source paths only to ensure behavior-path claims are not purely document-only.
      - Criteria must not embed current tool/test behavior as normative requirements.
```

## Main Preanalysis Under Audit

- Path: `.reviewcompass/specs/workflow-management/reviews/2026-07-01-workflow-management-design-review-run/main-preanalysis.md`
- Embedded content: the relevant main preanalysis follows. The auditor must treat it as a hypothesis, not as ground truth.

```markdown
# Main Preanalysis: workflow-management design reopen protocol review

対象 gate: `stages/design.yaml#triad-review`
位置づけ: 実 review-run 前の main preanalysis。これは reviewer への正解ではなく、source selection と判断項目の仮説である。

全 claim 共通の欠落扱い: named target section が存在しない、名称変更で対応箇所を特定できない、または必要な設計責務が別節にも見つからない場合は、vacuous pass とせず finding 候補として扱う。

今回の triad-review は、`workflow-management` の `design.md` を対象に、requirements Requirement 5 受入 7 で確定した reopen protocol mechanization 契約が、設計層へ欠落・弱体化・逸脱・未根拠追加なく引き継がれているかを確認する。

最低限の問いは次である。

- `requirements.md` の edited phase / downstream impact / fail-closed / superseding reopen 契約が、`design.md` の reopen 機械強制モデルへ設計として落ちているか。
- `requirements.md` の `next --json` reopen output / operation preflight 境界、proxy_model / human-only authorization 境界が、`design.md` の該当設計節へ落ちているか。
- `design.md` の審査対象は design 本文であり、tasks / implementation の correctness はこの gate の対象外である。
- behavior-path claim は、文書だけでなく `next --json`、`reopen-finalize`、commit preflight、関連 runner / tests を補助文脈に含める。ただし現在実装の correctness は審査対象ではなく、規範は requirements.md / REOPEN_PROCEDURE.md / workflow guidance である。
- review-run、proxy_model、`spec.json` 更新、phase/gate 完了、commit、push はこの preanalysis の範囲外であり、ここでは実行しない。

Claim 1: requirements-to-design vertical transfer
- Target: `design.md` §reopen 機械強制モデル §5。
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
- Source: Requirement 5 受入 7、REOPEN_PROCEDURE 第3〜4過程。
- Supporting context only: behavior-path source summary。code/test path は provenance hint であり、criteria に excerpt を埋め込まない限り、現在実装の挙動を規範 source として扱わない。
- Out of scope: 個々の関数のコードレビュー、現在実装が requirements を満たすかの correctness 判定。

Claim 5: superseding reopen policy
- Target: `design.md` §reopen 機械強制モデル §5。
- Source: Requirement 5 受入 7、plan RPMR-Q3 as superseded historical context、current reopen trigger。
- Out of scope: 過去 completed reopen record の内容修正。

Claim 6: review target boundary
- Target: `design.md` と review prompt requirement。
- Source: SESSION_WORKFLOW_GUIDE vertical intent transfer、requirements.md。
- Out of scope: tasks.md / implementation の正しさ。

Claim 7: next --json reopen output and preflight boundary
- Target: `design.md` §Req 12 設計モデル §11、§軽量版検査スクリプトモデル §4〜5、§session 跨ぎ状態管理モデル §1。
- Source: Requirement 12 受入 13〜14、Requirement 5 受入 7、Requirement 16 受入 11〜12。
- Out of scope: `next --json` 実装コードの correctness 判定。
- Finding condition: output field list が欠落する、scope / gate / state refs の一意性が曖昧、reopen scope / impact review scope が欠落・矛盾・stale な場合に `OK` ではなく `WARN` または `DEVIATION` で停止する条件が欠落する、または preflight が `next --json` を複製・再選択できるように読める。

Claim 8: proxy_model and human-only authorization boundary
- Target: `design.md` §review-run 後の proxy_model 判断代行モデル、§Req 14 設計モデル §1〜3。該当箇所が存在しない場合は、欠落を finding 候補として扱う。
- Source: Requirement 14 受入 11、Requirement 16 受入 13〜14、SESSION_WORKFLOW_GUIDE §3.3(a-2)。
- Out of scope: proxy_model 実装コードの correctness、個別 finding の採否。
- Finding condition: proxy_model が human-only operation を許可できるように読める、human-required predicate の優先順位や競合解決が欠落する、または human-only override / approval gate record / operation contract との関係が設計から欠落する。

Proposed split decision: 実 review-run は 1 prompt とする案が妥当である。ただし behavior-path claim は補助文脈に限定し、実装 correctness を審査対象にしないことを criteria に明記する。preanalysis sufficiency audit の確認を経て criteria draft に反映する。
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
8. Whether Requirement 12 acceptance 13-14 is carried into design. The criteria must quote the exact field list: 「現在の本線、次に実行すべき `required_action`、phase、stage、reopen scope、impact review scope、direct features、indirect features、flag policy、`next_pending_gate`、`next_drafting_gate`、`pending_gates`、`completed_gates`、superseded gate の有無、参照した state files」 and must check the rule that operation preflight references `next --json` rather than reselecting state.
9. Whether Requirement 12 acceptance 13 failure behavior is carried into design: when reopen_scope or impact_review_scope is missing, contradictory, or inconsistent with feature_impact_decisions / spec.json / pending_gates, `next --json` must not return `OK` and must stop with `WARN` or `DEVIATION` plus reasons.
10. Whether Requirement 16 acceptance 13-14 priority ordering is carried into design: human-only decision boundary, unresolved approval gate, `approval_required: true` operation, and unresolved review-wave impact evidence take priority over proxy applicability, and triage leave-as-is or proxy approved cannot cancel human-required evidence. Finding condition: flag a finding if design.md omits this priority order, weakens any priority source, permits proxy applicability to override human-required evidence, or fails to state the conflict-resolution rule.

Missing-section handling:

- If a named target section is absent, renamed, or structurally reorganized, the reviewer must search the full target file for equivalent design responsibility.
- If the responsibility cannot be located, the reviewer must treat the absence as a potential finding.
- The reviewer must not treat a missing section as a pass only because the named anchor is absent.

Target excerpt handling:

- Design target excerpts in preparation bundles are anchors only.
- Excerpt presence is not evidence of correct requirements transfer.
- The reviewer must judge the full target file independently.
- The reviewer must not use excerpt inclusion as confirmation that the design already satisfies the source contract.

Preanalysis handling:

- The preanalysis claim list is hypothesis context only.
- It is not an exhaustive checklist, answer key, or coverage proof.
- The reviewer must derive findings independently from embedded source materials and the full target document.

Meta/process checks for the later criteria draft:

1. The review target is `design.md`; tasks / implementation correctness are out of scope.
2. Target, source materials, and out-of-scope material are separated.
3. Design target excerpts are target-location anchors only. The later reviewer must judge the target independently and must not treat excerpt existence as confirmation of correct transfer.
4. The reviewer must derive findings independently from embedded source materials and the full target document. The preanalysis claim list is hypothesis context only and must not be treated as a checklist, answer key, or coverage proof.
5. Behavior-path tool/test material is supporting context only; the reviewer must not judge current implementation correctness or treat unapproved code behavior as normative source. If code/test excerpts are not embedded in the criteria, the reviewer must not require access to those paths and must not base findings on current implementation behavior.
6. The criteria should quote the exact Requirement 12 terms `direct features` and `indirect features` and allow semantically equivalent design terminology only when the equivalence is explicit.
7. The criteria contains the output contract expected by `run_review.py`.

PROHIBITED ACTIONS:

- commit
- push
- `spec.json` update
- phase approval
- gate completion
- phase completion
- reopen finalize
- proxy_model decision authorization
- human approval delegation
- implementation edits
- unapproved specification changes

The later review-run output contract should require YAML with at least:

- `verdict`
- `reviewed_target`
- `source_materials_used`
- `findings`
- `out_of_scope_not_judged`

Each `findings` item should contain:

- `severity`: one of `CRITICAL`, `ERROR`, `WARN`, `INFO`
- `target_location`
- `description`
- `rationale`
- `source_materials`

## Expected Audit Output Use

If the audit returns required changes, main must revise the preanalysis and/or source bundle before criteria draft.

If the audit returns `verdict: sufficient` or `sufficient_with_revisions` with no blocking findings, main may proceed to criteria draft, carrying any required prompt changes forward.
