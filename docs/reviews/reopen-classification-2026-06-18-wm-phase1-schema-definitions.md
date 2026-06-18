---
date: 2026-06-18
classifier: claude_main_session
classification: R-0（workflow-management）
trigger_source: セッション 77e272a2 の設計判断。設計メモ `docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` §7 item 2 で確定した「Phase 0 の TDD 開始前に必要な最小 Phase 1 作業」として、`required_action` 語彙スキーマと `next --json` 応答スキーマの定義を新要件として追加する。
feature: workflow-management
finding: phase1-schema-definitions
---

## 分類根拠

`next --json` が返す `required_action` フィールドの19語彙と、応答全体のスキーマを `.reviewcompass/schema/` 配下に正式定義する。これらは Phase 0（D-003 選択層の TDD 実装）の前提条件であり、テストが参照する契約として機械可読なスキーマファイルが必要である。

手戻り種別：**R-0（requirements 起点。intent・feature-partitioning へは遡らない）**。

- intent（意図）：`workflow-management` の意図は「段集合 YAML による静的検査、所定手続きの階層構造、修復手続きの機械強制」。スキーマ定義は `next --json` の action selector 契約（Requirement 2）のインフラであり、既存意図の範囲内。新しい意図を導入しない。意図文書の改訂は不要。
- feature-partitioning（機能分割）：`required_action` 語彙と `next --json` 応答スキーマは `workflow-management` が所有する検査スクリプトの契約であり、同 feature の責務境界内で受けられる。`foundation` が所有するのはレビュー実行系スキーマ（所見・スコア等）であり、ワークフロー管理系スキーマとは別物。再分割は不要。

### R-0 と R-1 の分岐点

「スキーマファイルという新しい成果物を意図文書に明記するか」が分岐点。`.reviewcompass/schema/` 配下のスキーマは `next --json` 契約の実装補助物であり、意図文書に明記する性格のものではない。既存「軽量版検査スクリプトの提供」（Requirement 2）の機械可読化として **R-0** を採用する。

## 事実

- 根拠設計書：`docs/notes/2026-06-18-integrated-design-selection-execution-layers.md` §7 item 2（Phase 0/1 分割方針）
- 根拠設計書：`docs/notes/working/2026-06-16-next-json-unique-state-redesign.md` §4.2（`required_action` 19語彙の列挙）および §4.1（`next --json` 応答の目標 JSON 契約）
- 既存 Requirement 2 受入9（2026-06-17 maintenance で追加）は「`next_action.required_action` は常に1つ」を要求しているが、語彙の正式スキーマファイルへの定義は要件として明記されていない
- Phase 0 TDD を始めるには、テストが `EXPECTED_REQUIRED_ACTIONS` として参照する語彙セットが機械可読なスキーマとして確定している必要がある（テストファイル `tests/tools/test_phase1_schema_definitions.py` は失敗状態のまま、スキーマファイル作成を待っている）

追加する要件（Requirement 2 の受入基準に追記）：
1. 本検査スクリプトは `required_action` の19語彙（D-003 §6 の19段階優先順位に対応）を `.reviewcompass/schema/required_action.schema.json` として JSON Schema 形式で定義する。語彙の追加・変更は本スキーマファイルの修正で完結し、コード側の enum リストはこのファイルを参照する。
2. 本検査スクリプトは `next --json` の目標応答スキーマ（`verdict`・`exit_code`・`next_action`・`reasons` の最上位構造と、`next_action` 内の `kind`・`required_action`・`feature`・`phase`・`stage`・`active_gate` の型・null 許容性）を `.reviewcompass/schema/next_action_response.schema.json` として JSON Schema 形式で定義する。

## feature impact 判定

| feature | decision | impact_basis | rationale |
| --- | --- | --- | --- |
| workflow-management | reopen_existing_feature | contract_ownership | `next --json` の action selector 契約（Requirement 2）を所有。新要件（スキーマファイル定義）の要件・設計・実装を所有するため。 |
| foundation | no_reopen_existing_feature | no_implementation_impact | 共通スキーマはレビュー実行系であり、ワークフロー管理系スキーマに変更なし。 |
| runtime | no_reopen_existing_feature | no_implementation_impact | レビュー実行パイプラインに変更なし。 |
| evaluation | no_reopen_existing_feature | no_implementation_impact | 評価契約に変更なし。 |
| analysis | no_reopen_existing_feature | no_implementation_impact | 横断分析に変更なし。 |
| self-improvement | no_reopen_existing_feature | no_implementation_impact | 規律提案契約に変更なし。 |
| conformance-evaluation | no_reopen_existing_feature | no_implementation_impact | 実装推定・照合に変更なし。 |

新 feature 判定：no_new_feature（workflow-management の責務境界で受けられるため）。

## 再実施対象

- **workflow-management（R-0）**：requirements の `alignment`〜`approval`（新受入基準の追記）、および実装変更を行う implementation（TDD：失敗テスト → スキーマファイル作成 → 全テスト通過）。
- impacted_downstream_phases：design／tasks／implementation。

## 停止点

reopen-start により in-progress ファイルを発行し、spec.json のフラグ差し戻し（workflow-management：requirements の alignment・approval を false、recheck＝upstream_change_pending を true・impacted_downstream_phases に design／tasks／implementation を設定）を行ったうえで、第 1 過程停止点として差し戻し内容の利用者承認を待つ。この時点ではコミットしない。
