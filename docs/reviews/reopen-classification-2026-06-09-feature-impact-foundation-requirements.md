---
date: 2026-06-09
classifier: codex_main_session
classification: N-0
trigger_source: feature-partitioning 成果物の補正。3役レビューにより、intent 追記に対する feature impact 判定を「全 feature 一律 reopen」から direct impact / indirect check に分け直した。
feature: foundation
finding: feature-partitioning-updated-after-foundation-requirements
---

## 分類根拠

2026-06-09 に、`.reviewcompass/specs/_cross_feature/reviews/2026-06-09-feature-impact-reopen-review-run/review_summary.md` の3役レビュー結果を受けて、feature-partitioning 成果物を補正した。

補正後の判定では、実装上の所有を軸に、`foundation`、`runtime`、`evaluation`、`conformance-evaluation` を direct impact、`analysis`、`workflow-management`、`self-improvement` を indirect check とする。intent 文書内の挿入箇所は、intent の性質上、feature 所属判定の主根拠にしない。新 feature は作成しない。

`tools/check-workflow-action.py next --json` は、feature-partitioning 成果物が `foundation` requirements 成果物より新しいため、`foundation` requirements に対して `reopen_classification_required` を返した。`tools/check-workflow-action.py` の `_reopen_trigger_for_upstream_phase` は、上流 phase が `feature-partitioning` の場合に既定候補 `N-0` を返す。

したがって、本件は `N-0` として reopen-start する。

## 事実

- `stages/feature-partitioning/2026-05-24-proposal.md` を補正し、intent 更新後の再確認を direct impact / indirect check に分けた。
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-intent-feature-reopen-decision.md` を同じ判定に補正した。
- `stages/completed/reopen-procedure-2026-06-08-intent-review-collection-mapping.yaml` の `feature_impact_decisions` を同じ判定に補正した。
- 機械判定は、次処理として `foundation` requirements の reopen 分類と reopen-start を要求している。

## 再実施対象

`N-0` の trigger_map に従い、次を対象にする。

- `stages/intent.yaml#review`
- `stages/intent.yaml#approval`
- `stages/feature-partitioning.yaml#candidate-proposal`
- `stages/feature-partitioning.yaml#approval`

下流の requirements 以降については、reopen 開始後の第2過程以降で direct impact / indirect check の区分に従って確認する。

## 停止点

reopen-start により in-progress ファイルを発行した後、フラグ差し戻しと再実施範囲の処理へ進む前に、機械判定の次処理を再確認する。
