# Post-write Review Target

criteria_id: reopen-classification-review-v2
phase: post_write_verification
generated_at: 2026-06-26T13:00:00.000000+00:00

## 変更の概要

MWP-0（next --json の kind 値を 41 種類から 7 種類へ整理し、commit 関連 kind を commit-preflight へ移動する仕様変更）を、ReviewCompass 自身のワークフローに乗せて実施するため、reopen 手続きを開始した。

今回の変更内容は2点：

1. `docs/reviews/reopen-classification-2026-06-26-wm-next-json-kind-redesign.md`（新規作成）：reopen の手戻り種別（分類）を記録した根拠文書。
2. `.reviewcompass/specs/workflow-management/requirements.md`（追記）：受入基準（Requirement 4 受入 9）と Change Intent への記録を追記した。

## 審査してほしい判断ポイント

以下の4つの claim（判断対象）を、それぞれ独立して分析してほしい。

### claim-1：R-0 分類（requirements 起点）の妥当性

今回の変更は「R-0（requirements 起点。intent・feature-partitioning へは遡らない）」と分類した。

分類根拠ファイルには次のように書いてある：
- intent は変わらない（`next --json` の kind 整理は「次アクション通知の出力形式改善」であり新しい意図を導入しない）
- feature-partitioning は変わらない（対象は `workflow-management` の `next --json` 出力インターフェイスであり、機能分割・責務境界の再定義は不要）

**問い**：この R-0 分類は妥当か。intent や feature-partitioning を変えなくてよい理由は十分か。見落としや論理の飛躍はないか。

### claim-2：影響範囲が workflow-management のみである判断の妥当性

feature impact 判定では、`workflow-management` のみを `reopen_existing_feature` とし、他の feature（foundation / runtime / evaluation / analysis / self-improvement / conformance-evaluation）はすべて `no_reopen_existing_feature` と判定した。

根拠：他機能は `next --json` の kind 値を正本仕様として直接参照していない（共通語彙・共通スキーマに変更なし）。

**問い**：他機能の仕様・設計・要件が `next --json` の kind 値に依存している可能性を見落としていないか。特に foundation・runtime・conformance-evaluation は `next --json` の出力を処理したり検査したりする責務を持つ可能性があるが、その点は問題ないか。

### claim-3：受入基準の追記位置の適切性

今回の受入基準は「Requirement 4（不可逆操作の直前ゲート）の受入 9」として追記した。

追記内容は「`commit_candidate` / `commit_mixing_risk` / `commit_unit_stale` の3種類の判定を `next --json` の `kind` から除外し、`commit-preflight` サブコマンドの出力にのみ含める」というものである。

一方、requirements.md には以下の構造がある：
- Requirement 2：検査スクリプト（`next --json` の出力を定義する責務を持つ）
- Requirement 4：不可逆操作の直前ゲート（コミット操作のゲートを定義）

**問い**：この受入基準は Requirement 4 ではなく Requirement 2 に追記すべきではなかったか。`next --json` の出力インターフェイス定義は Requirement 2 の管轄ではないか。追記位置に問題があれば、どこが正しい追記先か。

### claim-4：Change Intent の記述と実際の変更の整合性

Change Intent（requirements.md 末尾の改訂記録）には次のように書いた：

> 「Requirement 4 受入 1 に `commit_candidate` / `commit_mixing_risk` / `commit_unit_stale` を `next --json` から除外し `commit-preflight` サブコマンドへ集約するという追記を行う。」

しかし実際に行った変更は：
- 「Requirement 4 受入 9」という新しい項目を**新設**した（既存の受入 1 への追記ではない）

**問い**：Change Intent の記述（「受入 1 に追記」）と実際の変更（「受入 9 の新設」）は矛盾しているか。矛盾している場合、どちらの記述が正しいか、またどのように修正すべきか。

## 対象ファイルの内容

### docs/reviews/reopen-classification-2026-06-26-wm-next-json-kind-redesign.md

```
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

手戻り種別：R-0（requirements 起点。intent・feature-partitioning へは遡らない）。

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

- workflow-management（R-0）：requirements に `next --json` kind 再設計・`commit-preflight` への移動・手引き改修の受入基準を追記または更新する。requirements は drafting 相当の本文修正後に triad-review / review-wave / alignment / approval を再実施する。
- design：7 種類の kind 定義・サブフィールド設計・廃止フィールド・`commit-preflight` 集約の設計を更新する。
- tasks：kind 変更に対応するテスト要件と実装作業を追記する。
- implementation：TDD で失敗テストを先に作成し、kind 整理を実装する。

impacted_downstream_phases：design／tasks／implementation。
```

### .reviewcompass/specs/workflow-management/requirements.md（関連部分の抜粋）

**Requirement 4（不可逆操作の直前ゲート）の受入基準から、今回追記した受入 9 と既存受入 1 を抜粋：**

```
### Requirement 4：不可逆操作の直前ゲート

受入基準：
1. 本機能は段フラグや `spec.json` など所定設定ファイルへの確定的書き込みを「不可逆操作」と定め、実行前に特定のチェックを通過させる。
（受入 2〜8 は省略）
9. 本機能は `commit_candidate`、`commit_mixing_risk`、`commit_unit_stale` の3種類の判定を `next --json` の `kind` から除外し、`commit-preflight` サブコマンドの出力にのみ含める。これらの判定は「作業の現在地カテゴリ」ではなく「コミット操作の前確認」であり、`next --json` の `kind` は作業の現在地のみを示す7種類（`completed` / `in_progress` / `blocking_in_progress` / `verification_pending` / `reopen_in_progress` / `feature_definition_required` / `unknown`）に限定する。設計の詳細は `docs/notes/2026-06-26-next-json-kind-redesign.md` を正本とする。（2026-06-26 reopen R-0 next-json-kind-redesign、根拠：`docs/reviews/reopen-classification-2026-06-26-wm-next-json-kind-redesign.md`）
```

**Change Intent（末尾の改訂記録）の 2026-06-26 追記：**

```
- 2026-06-26 の reopen R-0（next-json-kind-redesign）により、Requirement 2 受入 11 の `kind` 値域（design で確定と記載）の設計が確定したことを受けて、Requirement 4 受入 1 に `commit_candidate` / `commit_mixing_risk` / `commit_unit_stale` を `next --json` から除外し `commit-preflight` サブコマンドへ集約するという追記を行う。`next --json` の `kind` は7種類（`completed` / `in_progress` / `blocking_in_progress` / `verification_pending` / `reopen_in_progress` / `feature_definition_required` / `unknown`）に整理し、サブ情報はサブフィールドで返す設計とする。詳細は `docs/notes/2026-06-26-next-json-kind-redesign.md` を正本とする（根拠は `docs/reviews/reopen-classification-2026-06-26-wm-next-json-kind-redesign.md`）。本改訂は仕様確定後に TDD で実装する正順の手続きである。
```

**Requirement 2 の責務（参考）：**

Requirement 2 は「検査スクリプト」を定義しており、`next --json` の出力インターフェイス・`kind` 値の定義もこの Requirement の管轄である（受入 11：`next --json` の `kind` 値域は設計で確定と記載されている）。

