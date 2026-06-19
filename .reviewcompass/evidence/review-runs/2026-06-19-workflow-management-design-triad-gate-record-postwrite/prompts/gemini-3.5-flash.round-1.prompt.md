prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.5-flash

# Task
Review the target document for the requested phase and criteria.

# Phase
post_write_verification

# Criteria
# Post-write Review Target

criteria_id: workflow_management_design_triad_gate_record_post_write
phase: post_write_verification
generated_at: 2026-06-19T04:02:27.345810+00:00

## Change Summary

Recorded design triad-review gate completion after user-approved triage, C2/C3 design fixes, and no-finding post-write verification.

## Review Question

Verify that the reopen in-progress record and working progress note accurately mark only design triad-review complete, leave later design review-wave/alignment/approval and downstream gates pending, and cite the correct evidence without overclaiming commit, push, spec.json mutation, or later gate completion.

## Target Files

- stages/in-progress/reopen-procedure-2026-06-19.yaml sha256=9b1b2ec9cc2a0a32ade92fdedd9401d18202b8895df2e616d38c7cddcc8ca375
- docs/notes/working/2026-06-19-integrated-design-manual-workflow-progress.md sha256=18a0951829eb6187e61e2edd56e2e323eb1d6f47e283d1560a26b0a0db2458e7

## Scope

- Check whether the changed target files clearly state the intended contract.
- Check whether related instructions are mutually consistent across targets.
- Check whether the documented procedure is actionable before API review, triage, manifest, or commit steps continue.

## Out Of Scope

- Do not request unrelated refactors or style-only rewrites.
- Do not judge files that are not listed in Target Files.
- Do not treat missing implementation work as a document defect unless the target text claims it already exists.

## Finding Policy

- Report must-fix findings for contradictions, missing required gates, or instructions that would allow an unsafe workflow action.
- Report should-fix findings for ambiguity that could cause repeated manual judgment or unnecessary API review loops.
- Return findings: [] when the target files are internally consistent for this review question.

## Sensitive Information Check

- status: passed
- External API review must not proceed if this section reports potential secrets.


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
stages/in-progress/reopen-procedure-2026-06-19.yaml
docs/notes/working/2026-06-19-integrated-design-manual-workflow-progress.md

# Target document
## stages/in-progress/reopen-procedure-2026-06-19.yaml

process_id: reopen-procedure
feature: workflow-management
classification: R-0
started_at: '2026-06-19T00:00:00+09:00'
trigger: 統合設計メモ Requirement 13〜16 反映後の workflow state 実体差し戻し
classification_basis: docs/reviews/reopen-classification-2026-06-19-wm-integrated-design-requirements.md
completed_steps:
- R-0 判定確定・spec.json フラグ差し戻し完了（requirements.triad-review/review-wave/alignment/approval
  → false、design/tasks/implementation 全段 → false、recheck.upstream_change_pending →
  true、impacted_downstream_phases → design/tasks/implementation）
- intent/INTENT.md と requirements.md に統合設計メモを反映済み（commit 50c6cbda）
- requirements triad-review gate 完了（新規3者レビュー、proxy_model 判断、C1〜C7反映、post-write verification
  no findings）
- requirements review-wave gate 完了（全 feature impact check、workflow-management 以外 existing_sufficient、post-write
  verification no findings）
- requirements alignment gate 完了（intent / requirements / triad-review / review-wave
  / workflow_state 整合、post-write verification no findings）
- requirements approval gate 完了（利用者発言『承認』に基づく明示承認）
- design drafting 完了（Requirement 13〜16 を design.md へ展開し、operation contract、承認ゲート、side
  track stack、workflow-state snapshot、structured effective prompt、proxy_model triage
  decision 機械処理化、Phase 0〜6 を設計化）
- design triad-review gate 完了（3者レビュー、利用者承認 triage、C2/C3反映、post-write verification
  no findings）
next_step: 第3過程：design review-wave / impact check
step_number: 3
pending_gates:
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
completed_gates:
- stages/requirements.yaml#triad-review
- stages/requirements.yaml#review-wave
- stages/requirements.yaml#alignment
- stages/requirements.yaml#approval
- stages/design.yaml#triad-review
drafting_completed_gates:
- stages/requirements.yaml#drafting
- stages/design.yaml#drafting
current_blocker: null
side_track_records:
- completed_maintenance: stages/completed/maintenance-2026-06-19-post-write-review-target-preflight.yaml
  rationale: post-write API review の criteria / review-target 生成を機械化する局所改善を、本線
    design drafting 再開前の maintenance commit として記録した。reopen gate 状態は変更しない。
  evidence:
  - .reviewcompass/post-write-verification/post-write-2026-06-19-268.yaml
  - .reviewcompass/evidence/review-runs/2026-06-19-post-write-review-target-preflight-postwrite/review_summary.md
reopen_step_records:
- from_step: 1
  completed_step: R-0 判定確定・spec.json フラグ差し戻し完了（requirements.triad-review/review-wave/alignment/approval
    → false、design/tasks/implementation 全段 → false、recheck.upstream_change_pending
    → true、impacted_downstream_phases → design/tasks/implementation）
  rationale: 利用者承認済み（2026-06-19 Codex セッション、「承認」発言）。分類根拠：docs/reviews/reopen-classification-2026-06-19-wm-integrated-design-requirements.md
  evidence:
  - docs/reviews/reopen-classification-2026-06-19-wm-integrated-design-requirements.md
  - .reviewcompass/specs/workflow-management/spec.json
- from_step: 2
  completed_step: intent/INTENT.md と requirements.md に統合設計メモを反映済み（commit 50c6cbda）
  rationale: Requirement 13〜16、Change Intent、XDI-WM-005、および intent 追記は commit 50c6cbda
    で反映済み。次は正式 requirements triad-review から再実施する。
  evidence:
  - 50c6cbda
  - intent/INTENT.md
  - .reviewcompass/specs/workflow-management/requirements.md
- from_step: 3
  completed_step: requirements triad-review の proxy_model 判定結果を requirements と関連記録へ反映済み
  rationale: C1/C2 must-fix と C3〜C7 should-fix を requirements.md へ反映し、review-response.md
    に反映内容を記録した。C8/C9 は proxy_model 判定どおり leave-as-is とした。requirements triad-review
    gate 自体は post-write verification 後に完了記録する。
  evidence:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-integrated-design-review-run/review-response.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-integrated-design-review-run/proxy-decision-summary.md
- from_step: 3
  completed_step: requirements review-wave gate 完了（全 feature impact check、workflow-management
    以外 existing_sufficient）
  rationale: requirements review-wave / impact check を実施し、workflow-management 以外の
    feature は consumer / derivative として現行正本で受けられるため requirements 正本変更不要と判断した。post-write
    verification は gemini-3.5-flash no findings。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-review-wave.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-review-wave-summary.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-256.yaml
- from_step: 3
  completed_step: design drafting 完了（Requirement 13〜16 を design.md へ展開）
  rationale: requirements approval 済みの Requirement 13〜16 を workflow-management design.md
    へ展開し、operation contract 語彙、required_action 対応、承認ゲート、side track stack、workflow-state
    snapshot、structured effective prompt、proxy_model triage decision 機械処理化、Phase 0〜6
    の段階的実装順序を設計化した。次は design triad-review gate。
  evidence:
  - .reviewcompass/specs/workflow-management/design.md
  - docs/notes/working/2026-06-19-integrated-design-manual-workflow-progress.md
- from_step: 3
  completed_step: design triad-review gate 完了
  rationale: design triad-review を実施し、C1 leave-as-is、C2/C3 should-fix のトリアージ案を利用者発言「承認」に基づき確定した。
    C2/C3 は design.md の完成判定基準へ反映済み。post-write verification は gemini-3.5-flash no findings。
    次は design review-wave / impact check。
  evidence:
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-design-integrated-design-review-run/raw-review-triage-summary.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-design-integrated-design-review-run/triage.yaml
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-design-integrated-design-review-run/review-response.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-276.yaml
downstream_impact_decisions:
- gate: stages/requirements.yaml#triad-review
  feature_scope: workflow-management
  decision: proxy_approved
  rationale: 新規3者レビューを実施し、proxy_model 判断により C1/C2 must-fix、C3-C7 should-fix、C8/C9
    leave-as-is を確定した。C1-C7 は requirements.md と review-response.md に反映済みで、post-write
    verification は gemini-3.5-flash no findings。利用者の『次へ』指示に基づき gate 完了へ進める。
  evidence:
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-integrated-design-review-run/proxy-decision-summary.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-integrated-design-review-run/review-response.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-254.yaml
  - .reviewcompass/specs/workflow-management/requirements.md
- gate: stages/requirements.yaml#review-wave
  feature_scope: all_features
  decision: existing_sufficient
  rationale: requirements review-wave / impact check を実施し、workflow-management 以外の
    feature は consumer / derivative として現行正本で受けられるため requirements 正本変更不要と判断した。post-write
    verification は gemini-3.5-flash no findings。利用者の『進めて』指示に基づき gate 完了へ進める。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-review-wave.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-review-wave-summary.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-256.yaml
- gate: stages/requirements.yaml#alignment
  feature_scope: workflow-management
  decision: existing_sufficient
  rationale: requirements alignment を実施し、intent、requirements、triad-review 対処、review-wave
    判定、workflow_state / reopen 記録が整合していると確認した。requirements 内の追加修正は不要で、design/tasks/implementation
    への recheck は維持する。post-write verification は gemini-3.5-flash no findings。利用者の『次へ』指示に基づき
    gate 完了へ進める。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-reopen-alignment.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-258.yaml
- gate: stages/requirements.yaml#approval
  feature_scope: workflow-management
  decision: approved
  rationale: 利用者が 2026-06-19 Codex セッションで『承認』と明示し、requirements drafting、triad-review、review-wave、alignment
    が完了済みであるため、統合設計メモ反映の requirements phase を承認済みとして扱う。
  evidence:
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-approval.md
  - .reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-reopen-alignment.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-259.yaml
- gate: stages/design.yaml#triad-review
  feature_scope: workflow-management
  decision: approved
  rationale: design triad-review を実施し、利用者承認に基づき C1 は leave-as-is、C2/C3 は should-fix
    とした。C2/C3 は design.md へ反映済みで、post-write verification は gemini-3.5-flash no findings。
  evidence:
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-design-integrated-design-review-run/raw-review-triage-summary.md
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-design-integrated-design-review-run/triage.yaml
  - .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-design-integrated-design-review-run/review-response.md
  - .reviewcompass/post-write-verification/post-write-2026-06-19-276.yaml


## docs/notes/working/2026-06-19-integrated-design-manual-workflow-progress.md

---
date: 2026-06-19
record_type: working-note
status: active
topic: integrated-design-manual-workflow-progress
related:
  - docs/notes/2026-06-18-integrated-design-selection-execution-layers.md
  - docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md
  - docs/notes/working/2026-06-19-integrated-design-requirements-missing.md
  - docs/notes/working/2026-06-19-proxy-model-triage-cost-issues.md
  - intent/INTENT.md
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/spec.json
---

# 統合設計メモ反映・開発進捗（手動管理）

## 前提

- 現在はシステム自体の改変中である。
- 管理の大本は各 feature の `spec.json` である。`spec.json` の workflow_state を実体に合わせて手動管理し、この表はその判断材料と作業進捗の補助記録として使う。
- `next --json` が正しい現在位置を返す保証はないため、当面は `spec.json` とこの表を照合して手動管理する。
- 対象入力は次の3件である。
  - `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md`
  - `docs/notes/working/2026-06-18-mechanized-workflow-execution-design.md`
  - `docs/notes/working/2026-06-19-integrated-design-requirements-missing.md`

## 0. Intent Phase

- [x] Drafting
  - [x] `intent/INTENT.md` に裁定負荷を LLM の暗黙判断へ隠さない意図を追加
  - [x] 現在位置と次操作が機械的に一意である状態を追加
  - [x] workflow-management の責務として `next --json`、operation contract、承認ゲート、側道スタック、状態スナップショット、構造化有効プロンプトを位置づけ

- [x] Review / Verification
  - [x] requirements 反映と合わせて3者レビューで traceability を確認
  - [x] should-fix 候補を intent 側にも反映

- [x] Commit
  - [x] `50c6cbda Recover integrated design requirements`

## 1. Requirements Phase

注記：この節の完了済み項目は、requirements 文書への追記作業と初期 traceability 確認の実績である。workflow 上の requirements phase 全体（formal triad-review / review-wave / alignment / approval）を完了した事実はまだない。

- [x] Drafting
  - [x] Requirement 13: operation contract 語彙と `required_action` 対応
  - [x] Requirement 14: 承認ゲート、側道スタック、状態スナップショット
  - [x] Requirement 15: 構造化有効プロンプトと LLM judge 監査
  - [x] Requirement 16: Phase 0〜6 の段階的実装計画
  - [x] Change Intent / XDI-WM-005 を追加

- [x] Initial Traceability Review
  - [x] `implementation_review_independent_3way_codex_operator` で source note との対応を確認
  - [x] preliminary run は無効扱いとして削除
  - [x] should-fix 候補を抽出

- [x] Review Response
  - [x] 19 `required_action` 対応の完全性を補強
  - [x] 複合 operation の未確定事項を明示
  - [x] `record_human_decision` と対象操作の紐付け課題を明示
  - [x] LLM judge 監査観点を補強
  - [x] Phase 0 / Phase 1 / D-003 anchor を明確化

- [x] Post-write Verification
  - [x] `post_write_verification_google`
  - [x] no findings
  - [x] manifest 作成

- [x] Commit
  - [x] `50c6cbda Recover integrated design requirements`

- [x] Workflow State Reconciliation
  - [x] `.reviewcompass/specs/workflow-management/spec.json` と実体を照合
  - [x] `docs/reviews/reopen-classification-2026-06-19-wm-integrated-design-requirements.md` を作成
  - [x] `stages/in-progress/reopen-procedure-2026-06-19.yaml` を発行
  - [x] `spec.json` を requirements triad-review から再開する状態へ差し戻し

- [x] Formal Requirements Triad Review
  - [x] workflow 上の requirements triad-review を正式段として実施する判断
  - [x] `implementation_review_independent_3way_codex_operator` で新規3者レビューを実施
  - [x] 利用者提示ゲート用に raw 参照・同根クラスタ・三段階トリアージ案を記録
  - [x] proxy_model（gemini-3.1-pro-preview）判断を取得し、triage.yaml へ反映
  - [x] must-fix / should-fix / leave-as-is の最終ラベルを確定
  - [x] proxy_model 判定運用のコスト問題と機械処理化候補を working note に記録
  - [x] must-fix / should-fix を requirements と関連記録へ反映する
  - [x] 反映後の post-write verification を実施する
  - [x] requirements triad-review gate の完了を記録する

- [x] Review-wave / Impact Check
  - [x] workflow-management 以外の feature への波及有無を確認する
  - [x] `.reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-review-wave.md` に記録する
  - [x] requirements review-wave gate の完了を記録する

- [x] Alignment
  - [x] intent / requirements / 既存 workflow-management 仕様との整合を確認する
  - [x] `.reviewcompass/specs/_cross_feature/reviews/2026-06-19-requirements-integrated-design-reopen-alignment.md` に記録する
  - [x] requirements alignment gate の完了を記録する

- [x] Approval
  - [x] 利用者承認を記録する
  - [x] requirements approval gate 完了後の post-write verification を実施する

## 2. Design Phase

- [x] Drafting
  - [x] Requirement 13〜16 を `.reviewcompass/specs/workflow-management/design.md` へ展開する
  - [x] operation contract registry の設計を書く
  - [x] 複合 operation の表現方針を決める
  - [x] approval gate の記録構造を設計する
  - [x] Requirement 14 の side-track stack 契約を design に展開する
    - [x] frame schema
    - [x] push / pop 操作
    - [x] `return_to` の機械参照
    - [x] `staged_file_set` / `staged_file_digest`
    - [x] `max_depth` の Phase 3 WARN / Phase 5 block 方針
  - [x] workflow-state snapshot の生成方式と正本状態との関係を設計する
  - [x] structured effective prompt の生成方式を設計する
  - [x] proxy_model triage decision の機械処理化方針を設計する
    - [x] cluster-level decision から finding-level decision への展開
    - [x] finding ID coverage validation
    - [x] approval scope の機械的区別
    - [x] batch triage decision 適用
  - [x] Phase 0〜6 の実装順序を design 上に落とす

- [x] Triad Review
  - [x] design 3者レビューを実施する
  - [x] must-fix / should-fix / leave-as-is を整理する
  - [x] 必要な design 修正を反映する

- [ ] Review-wave / Impact Check
  - [ ] workflow-management 以外の feature への影響を確認する
  - [ ] runtime / foundation / evaluation / conformance-evaluation への波及有無を判定する

- [ ] Alignment
  - [ ] requirements Requirement 13〜16 と design の対応を確認する

- [ ] Approval
  - [ ] 利用者承認を得る

- [ ] Commit
  - [ ] design phase の成果を guarded commit する

## 3. Tasks Phase

- [ ] Drafting
  - [ ] design から tasks を作成する
  - [ ] Phase 0〜6 を実装タスクに分解する
  - [ ] TDD の失敗テスト単位を定義する
  - [ ] 既存 T-015 との関係を整理する
  - [ ] どの Phase を先に実装するか決める

- [ ] Triad Review
  - [ ] tasks 3者レビューを実施する
  - [ ] タスク粒度、順序、テスト可能性を確認する

- [ ] Review-wave / Impact Check
  - [ ] 他 feature の tasks へ波及する項目があるか確認する

- [ ] Alignment
  - [ ] requirements / design / tasks の追跡表を確認する

- [ ] Approval
  - [ ] 利用者承認を得る

- [ ] Commit
  - [ ] tasks phase の成果を guarded commit する

## 4. Implementation Phase

- [ ] Phase 1 Schema / Vocabulary
  - [ ] operation contract schema
  - [ ] `effect_kind` schema
  - [ ] `phase_boundary` schema
  - [ ] workflow-state snapshot schema
  - [ ] language task common I/O schema

- [ ] Phase 0 Selection Layer
  - [ ] D-003 19段階優先順位を実装する
  - [ ] `required_action` 唯一化を実装する
  - [ ] invariant 検査を実装する
  - [ ] `reopen-recompile` または同等の repair command を実装する

- [ ] Phase 2 Read-only Registry
  - [ ] `operation-list --json` または同等コマンドを実装する
  - [ ] operation contract を機械可読に返す

- [ ] Phase 3 Advisory Preflight
  - [ ] `operation-preflight <id> --json` または同等を実装する
  - [ ] pending conflict / side-track depth / commit mixing / prompt audit を WARN として検出する

- [ ] Phase 4 Structured Effective Prompt
  - [ ] structured effective prompt を生成する
  - [ ] 既存 `effective_prompt_path` との互換を維持する

- [ ] Phase 5 Mechanical Blocking
  - [ ] advisory WARN を block に昇格する
  - [ ] `serial_only`、承認欠落、side-track depth 超過、commit 混線を遮断する

- [ ] Phase 6 LLM Judge Audit
  - [ ] structured prompt と運用文書を入力に LLM judge 監査を実装する
  - [ ] gap を構造化出力で返す
  - [ ] 最終承認は自動化しない

- [ ] Proxy Decision Mechanization
  - [ ] proxy_model 判定用の canonical command path を文書化または機械化する
  - [ ] proxy raw output から `decisions-input.yaml` を生成する helper を実装する
  - [ ] cluster-to-finding mapping の coverage validation を実装する
  - [ ] `review_triage.py decide` の batch 適用または同等の一括処理を実装する
  - [ ] `review_triage_decide` approval と apply-fixes approval の scope mismatch を検出する

- [ ] Implementation Review
  - [ ] 実装 3者レビュー
  - [ ] post-write verification
  - [ ] 必要修正の反映

- [ ] Commit
  - [ ] 実装成果を guarded commit する

## 5. Current Immediate Step

- [x] `.reviewcompass/specs/workflow-management/spec.json` の workflow_state と実体を照合する
- [x] `TODO_NEXT_SESSION.md` にこの進捗表への参照を反映する
- [x] post-write verification を再実行する
- [x] TODO 更新と本 working note を guarded commit する
- [x] 統合設計メモ反映用の reopen 分類と workflow state 差し戻しを行う
- [x] requirements triad-review の扱いを決める
  - [x] 新規3者レビューを実施するか、既存 traceability review を正式段の証跡として採用するか判断する
  - [x] 新規3者レビューを正式段の証跡として採用し、proxy_model 判断まで完了する
- [x] requirements triad-review の must-fix / should-fix を反映する
  - [x] C1: 19 `required_action` と複合 operation の要件粒度
  - [x] C2: side-track stack と commit mixing 防止の不変条件
  - [x] C3: 承認ゲートと `record_human_decision`
  - [x] C4: structured effective prompt の第1層機械検査
  - [x] C5: cross-feature impact と review-wave への持ち上げ
  - [x] C6: D-003 / Phase 0 の canonical anchor
  - [x] C7: `spec.json.reopened` と現在 R-0 scope の意味づけ
- [x] proxy_model 判定運用の問題点と改善案を working note に記録する
- [x] proxy_model 判定運用の機械処理化を後続 design/tasks/implementation の対象として扱う
- [x] requirements 反映後の post-write verification を実施する
- [x] requirements triad-review gate の完了を記録する
- [x] requirements review-wave / impact check を実施する
- [x] requirements review-wave gate の完了を記録する
- [x] requirements alignment を実施する
- [x] requirements alignment gate の完了を記録する
- [x] requirements approval を利用者に確認し、承認された場合は gate 完了を記録する
- [x] requirements approval gate 完了後の post-write verification を実施する
- [x] design drafting に着手する

