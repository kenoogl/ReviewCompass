---
date: 2026-06-27
gate: stages/design.yaml#alignment
feature: workflow-management
phase: design
stage: alignment
reopen: R-0（next-json-kind-redesign / MWP-0）
decision: existing_sufficient
review_wave_evidence: .reviewcompass/specs/_cross_feature/reviews/2026-06-26-design-review-wave.md
---

# design alignment：MWP-0 kind 再設計（workflow-management）

## 対象

reopen R-0（`docs/reviews/reopen-classification-2026-06-26-wm-next-json-kind-redesign.md`）の設計フェーズ alignment 段。

requirements.md Req 2 受入 11・受入 12（MWP-0 で追加）と design.md §5.2〜§5.4（MWP-0 追記）の意図が欠落・弱体化・逸脱・未根拠追加なく引き継がれているかを確認する。

## requirements との整合

| 受入条件 | design での受け皿 | 判定 |
|---|---|---|
| Req 2 受入 11(1)：最上位必須フィールド5つ | §5.2 で明示 | 整合 |
| Req 2 受入 11(2)：`action_parameters` は run_maintenance 時の条件付き必須（6サブフィールド） | §5.2 条件付き必須フィールド節で明示 | 整合 |
| Req 2 受入 11(3)：`feature` は3種の値のみ | §5.2 フィールド型定義で明示 | 整合 |
| Req 2 受入 11(4)：進行中作業単位がない場合は `feature`/`phase`/`stage`/`active_gate` すべて null | §5.2 で明示 | 整合 |
| Req 2 受入 11(5)：後方互換フィールド `pending_gates` の整合規則 | §5.2 後方互換フィールドの整合規則節で明示 | 整合 |
| Req 2 受入 11(6)①：`commit_stop_point` 時 stage=null | §5.3 in_progress フィールド表に明記（review-wave 所見2 対処済み） | 整合 |
| Req 2 受入 11(6)②〜⑥：他 required_action 種別のフィールド制約 | §5.2 スキーマ設計上の機械表現は tasks・implementation フェーズで対応（先送り明示済み） | 先送り（既知・明示有り） |
| Req 2 受入 12：3値を commit-preflight に移動、next --json の kind を7値に限定 | §5.2 値域表（7値）・§5.4 commit-preflight 設計で明示 | 整合 |

## review-wave 対処内容の確認

| 所見 | 修正内容 | 確認 |
|---|---|---|
| C：「enum 修正で完結する」が受入12を弱める | §5.2 481行目：「値種の増減は受入12改訂が必要」を追記 | ✓ |
| D：`completion_conditions` 廃止の範囲が不明確 | §5.3 537行目：`action_parameters.completion_conditions` は別物・存続と注記 | ✓ |
| E：docs/notes の正本範囲が未明示 | §5.2 469行目：正本範囲は kind 値域のみと追記 | ✓ |

## tasks.md への追跡

design §5.2〜§5.4 の実装対応（JSON Schema 定義・commit-preflight 出力定義）は tasks フェーズで作業単位化される予定。MWP-0 tasks 段は tasks.review-wave が完了しており、alignment・approval が残っている。

## 先送り事項（tasks フェーズへ）

- 受入 11(6)②〜⑥の JSON Schema `if/then` 表現（スキーマ設計の機械検証）
- `reason`（next_action 内補足）と最上位 `reasons` 配列の責務差の明確化
- §5.3「廃止」と §Req12「廃止予定」の表現統一

## 判定

design.alignment：**通過**（先送り事項3件は tasks フェーズで対応予定として明示済み）
