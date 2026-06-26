---
date: 2026-06-26
classifier: claude_session
classification: R-0（workflow-management）
trigger_source: 2026-06-26 セッションで `next --json` の kind 値が 41 種類あり「作業状態」「手続き内部ステップ」「コミット操作確認」が混在していることを確認。設計文書 `docs/notes/2026-06-26-next-json-kind-redesign.md` で 7 種類への整理設計が確定。利用者指示により reopen 正式手続きへ進む。
feature: workflow-management
finding: next-json-kind-redesign
---

## 分類根拠

`next --json` が返す `kind` 値を 41 種類から 7 種類へ整理する。現状の `kind` には「作業の現在地」「手続き内部のサブステップ追跡」「コミット操作の前確認」が同一フィールドに混在しており、機械的な次アクション決定が困難になっている。整理後は `kind` が「作業の現在地カテゴリ」のみを示し、サブ情報はサブフィールドで返す設計とする。

手戻り種別：**R-0（requirements 起点。intent・feature-partitioning へは遡らない）**。

- intent（意図）：workflow-management の意図は「段集合 YAML による静的検査、所定手続きの階層構造、不可逆操作の直前ゲート、修復手続きの機械強制を担う」ことである。`next --json` の kind 整理は既存の「次アクション通知」の出力形式改善であり、新しい意図を導入しない。意図文書の改訂は不要。
- feature-partitioning（機能分割）：対象は `workflow-management` の `next --json` 出力インターフェイスであり、機能分割・責務境界の再定義は不要。

## 事実

- 設計文書：`docs/notes/2026-06-26-next-json-kind-redesign.md` に新旧対照表・詳細フィールド設計・廃止フィールド一覧が確定済み。
- 現状の kind 種類：41 種類。うち `maintenance_in_progress` と `blocking_unit_in_progress` は意味が同一だが別 kind として実装されており、reopen のサブステップ 13 種類が `kind` に詰め込まれている。
- 変更後の kind：7 種類（`completed` / `in_progress` / `blocking_in_progress` / `verification_pending` / `reopen_in_progress` / `feature_definition_required` / `unknown`）。
- commit 関連の kind 移動：`commit_candidate` / `commit_mixing_risk` / `commit_unit_stale` の 3 種類を `next --json` から除外し `commit-preflight` サブコマンドへ集約する。
- 手引き改修：`WORKFLOW_NAVIGATION.md` の `next_drafting_gate` 廃止に伴う記述改修が必要。

## feature impact 判定

| feature | decision | impact_basis | rationale |
| --- | --- | --- | --- |
| workflow-management | reopen_existing_feature | contract_ownership | `next --json` の出力インターフェイスと `commit-preflight` の判定ロジックを所有する。kind 整理・commit 関連 kind 移動・手引き改修の requirements / design / tasks / implementation を所有するため。 |
| foundation | no_reopen_existing_feature | no_implementation_impact | 共通語彙・共通スキーマに変更なし。 |
| runtime | no_reopen_existing_feature | no_implementation_impact | session 記録や hook 実行契約に変更なし。 |
| evaluation | no_reopen_existing_feature | no_implementation_impact | レビュー評価契約に変更なし。 |
| analysis | no_reopen_existing_feature | no_implementation_impact | 分析・可視化・報告機能に変更なし。 |
| self-improvement | no_reopen_existing_feature | no_implementation_impact | 自己改善提案や規律本文に変更なし。 |
| conformance-evaluation | no_reopen_existing_feature | no_implementation_impact | 実装照合・逸脱検出に変更なし。 |

新 feature 判定：no_new_feature。

## 再実施対象

- **workflow-management（R-0）**：requirements に `next --json` kind 再設計・`commit-preflight` への移動・手引き改修の受入基準を追記または更新する。requirements は drafting 相当の本文修正後に triad-review / review-wave / alignment / approval を再実施する。
- **design**：7 種類の kind 定義・サブフィールド設計・廃止フィールド・`commit-preflight` 集約の設計を更新する。
- **tasks**：kind 変更に対応するテスト要件と実装作業を追記する。
- **implementation**：TDD で失敗テストを先に作成し、kind 整理を実装する。

impacted_downstream_phases：design／tasks／implementation。

## 停止点

reopen-start により in-progress ファイルを発行し、spec.json のフラグ差し戻し（workflow-management：requirements 以降の alignment・approval を false、recheck＝upstream_change_pending を true・impacted_downstream_phases に design／tasks／implementation を設定）を行ったうえで、第1過程停止点として差し戻し内容の利用者承認を待つ。
