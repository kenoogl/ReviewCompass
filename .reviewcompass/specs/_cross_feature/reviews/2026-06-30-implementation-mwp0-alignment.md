---
date: 2026-06-30
gate: stages/implementation.yaml#alignment
feature: all_features
phase: implementation
stage: alignment
reopen: R-0（MWP-0 next-json-kind-redesign）
decision: existing_sufficient
review_wave_evidence: .reviewcompass/specs/_cross_feature/reviews/2026-06-30-implementation-mwp0-review-wave.md
gate_completion_authorized: false
---

# implementation alignment：MWP-0 next-json-kind-redesign

## 対象

workflow-management implementation review-wave 後の alignment 段。

本段では、Requirement 2 受入 11(6) / 受入 12、design、tasks T-020、implementation 修正、A/B/C 個別レビュー証跡、事前分析監査の扱い、review-wave 判定、`spec.json` の workflow_state が整合しているかを確認する。

## requirements / design / tasks との整合

| 上流 | implementation での受け皿 | 整合判定 |
| --- | --- | --- |
| Requirement 2 受入 12：`next --json` の kind を作業現在地 7 値に限定し、commit 前確認 3 値を `commit-preflight` に分離する | `tools/check-workflow-action.py` の `commit-preflight` 外部公開 kind と `commit_preflight_response.schema.json`、T-020 kind 分離テストで受ける。B 観点レビュー修正により 3 値以外の外部公開を除外済み。 | 整合 |
| Requirement 2 受入 11(6)：`required_action` ごとの条件付きフィールド制約 | `next_action_response.schema.json` の if/then 制約と `SchemaIfThenConstraintTests` で受ける。A 観点レビュー修正により ①②③⑤の不足を補完済み。 | 整合 |
| design §5.2 / §5.3：kind 値域、if/then 制約、reason フィールド | schema と design の対応として受ける。C 観点レビュー修正により `next_action.reason` と最上位 `reasons` の責務差を明示済み。 | 整合 |
| tasks T-020：先送り事項(a)(b)(c) と完了条件 | kind 分離、if/then 制約、reason/reasons 明確化を TDD とレビュー対処で実装へ接続済み。 | 整合 |

## implementation triad-review 対処との整合

MWP-0 の実装レビューは A/B/C の個別 run に分割して実施し、各 run は triage 済みである。

| review run | 主な所見 | 実装結果 | 整合判定 |
| --- | --- | --- | --- |
| A: if/then 制約 | `commit_stop_point` の `blocked_by.type`、`run_reopen_pending_gate` / `run_reopen_drafting` の phase / stage 制約不足 | 失敗テスト追加後、`next_action_response.schema.json` の if/then 制約を補完。コミット `80943687` / `b978abd4`。 | 整合 |
| B: kind 値分離 | `commit-preflight` が 3 値以外を外部公開し得る | 外部レスポンスでは 3 値のみを公開し、内部状態値を外部 kind から除外。コミット `c8ead8fb`。 | 整合 |
| C: reason / reasons 責務差 | `next_action.reason` と最上位 `reasons` の責務差が schema / design 上不明確 | schema コメントと design §5.2 / §5.3 に責務差を明示。コミット `e3e5b55a` / `0da4f15a`。 | 整合 |

A/B/C のレビュー run は `triage_status: decided`、各 model は `triage_status: triaged`、`human_required_count: 0` である。

## 事前分析監査との整合

事前分析監査 run は、A/B/C 個別レビューへ分割する前のレビュー設計品質監査である。監査所見は後続の個別レビューと修正で吸収済みとして全件 `leave-as-is` に決定し、`triage_status: decided`、各 model `triage_status: triaged`、`human_required_count: 0` で閉じた。コミット `4d8b4197` により証跡化済みである。

この扱いは、未完了のレビュー設計を正本実装判断として混ぜず、後続の正式レビュー run を正とするため、implementation alignment の整合を損なわない。

## implementation review-wave 判定との整合

implementation review-wave では、未消化 carry-forward が 0 件であることを確認し、workflow-management 以外の feature について implementation 正本変更は不要と判定した。

- reopen scope: workflow-management のみ
- impact review scope: all features
- other features: `existing_sufficient`
- carry-forward unresolved: 0
- workflow-management: implementation approval が残る

この判定は、MWP-0 が workflow-management の `next --json` / `commit-preflight` 出力責務と schema 契約の明確化に閉じることと整合する。他 feature は現行正本で consumer として受けられる。

## workflow_state との整合

`spec.json` の現在状態は次の通りである。

- requirements: drafting / triad-review / review-wave / alignment / approval は完了
- design: drafting / triad-review / review-wave / alignment / approval は完了
- tasks: drafting / triad-review / review-wave / alignment / approval は完了
- implementation: drafting / triad-review / review-wave は完了、alignment / approval は未完了
- `recheck.upstream_change_pending`: false
- `recheck.impacted_downstream_phases`: []
- `reopened`: 履歴フラグとして true を保持

本 alignment 記録は、implementation.review-wave 完了後の整合確認に対応する。

## 判定

- **decision: existing_sufficient**
- Requirement 2 受入 11(6) / 受入 12、design、tasks T-020、implementation 修正、A/B/C 個別レビュー証跡、事前分析監査の扱い、review-wave 判定、workflow_state は整合している。
- workflow-management 以外の feature について、implementation 正本変更は不要。
- implementation approval は未完了であり、次 gate として維持する。

## 証跡

- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/tasks.md`
- `.reviewcompass/specs/workflow-management/spec.json`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-ifthen-review-run/`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-kind-sep-review-run/`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-reason-review-run/`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-preanalysis-audit-run/`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-30-implementation-mwp0-review-wave.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-30-implementation-mwp0-review-wave-summary.md`

## 完了後の停止点

本記録に基づき、`workflow-management` の `implementation.alignment` を完了済みとして記録する。commit、push、approval はまだ行わない。次は implementation approval に進む。
