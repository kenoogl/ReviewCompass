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

- [ ] Drafting
  - [ ] Requirement 13〜16 を `.reviewcompass/specs/workflow-management/design.md` へ展開する
  - [ ] operation contract registry の設計を書く
  - [ ] 複合 operation の表現方針を決める
  - [ ] approval gate の記録構造を設計する
  - [ ] Requirement 14 の side-track stack 契約を design に展開する
    - [ ] frame schema
    - [ ] push / pop 操作
    - [ ] `return_to` の機械参照
    - [ ] `staged_file_set` / `staged_file_digest`
    - [ ] `max_depth` の Phase 3 WARN / Phase 5 block 方針
  - [ ] workflow-state snapshot の生成方式と正本状態との関係を設計する
  - [ ] structured effective prompt の生成方式を設計する
  - [ ] proxy_model triage decision の機械処理化方針を設計する
    - [ ] cluster-level decision から finding-level decision への展開
    - [ ] finding ID coverage validation
    - [ ] approval scope の機械的区別
    - [ ] batch triage decision 適用
  - [ ] Phase 0〜6 の実装順序を design 上に落とす

- [ ] Triad Review
  - [ ] design 3者レビューを実施する
  - [ ] must-fix / should-fix / leave-as-is を整理する
  - [ ] 必要な design 修正を反映する

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
- [ ] design drafting に着手する
