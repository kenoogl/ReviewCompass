---
feature: all_features
phase: all
stage: completed-summary
date: 2026-06-09
status: completed
record_type: completed-workflow-summary
---

# ReviewCompass Completed Workflow Summary

## Summary

2026-06-09 時点で、ReviewCompass の全 7 feature は intent、feature-partitioning、requirements、design、tasks、implementation の全段を完了している。

`tools/check-workflow-action.py next --json` は `kind: completed` を返し、理由は `すべての workflow_state が完了しています` である。本記録作成直前の `git status --short` は出力なしで、作業ツリーは clean だった。

この文書は、完了後に次の運用・リリース・追加改善を検討するための全体サマリである。作業順序の正本ではない。今後も作業開始時は `tools/check-workflow-action.py next --json` と各 feature の `spec.json` を正本として扱う。

## Completed Scope

対象 feature:

- `foundation`
- `runtime`
- `evaluation`
- `analysis`
- `workflow-management`
- `self-improvement`
- `conformance-evaluation`

対象 phase / stage:

| Phase | Completed stages |
| --- | --- |
| intent | drafting, review, approval |
| feature-partitioning | candidate-proposal, approval |
| requirements | drafting, triad-review, review-wave, alignment, approval |
| design | drafting, triad-review, review-wave, alignment, approval |
| tasks | drafting, triad-review, review-wave, alignment, approval |
| implementation | drafting, triad-review, review-wave, alignment, approval |

## Feature Outcomes

| Feature | Completed role |
| --- | --- |
| `foundation` | ReviewCompass の共通正本、規律、レビュー語彙、状態入力の基盤を定義した。 |
| `runtime` | レビュー実行、prompt rendering、API provider 呼び出し、raw 保存、実行記録の基盤を整備した。 |
| `evaluation` | レビュー結果の parsed findings、三段階トリアージ、承認、post-write verification manifest を扱う評価基盤を整備した。 |
| `analysis` | レビュー結果・判断結果を後続分析へ渡すための記録、要約、分析入力の扱いを整備した。 |
| `workflow-management` | `next --json`、reopen、upstream recheck、post-write verification、commit guard など、作業順序を機械判定する制御層を整備した。 |
| `self-improvement` | レビューで得た改善知見を carry-forward register へ抽象化し、次回以降の改善入力として扱えるようにした。 |
| `conformance-evaluation` | 仕様・実装・状態記録の整合性を検査し、既存システムへの後追い intent 追加時の差分候補抽出を追加した。 |

## Review And Gate Evidence

主要な完了証跡:

- `.reviewcompass/specs/*/spec.json`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-04-implementation-phase-summary.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-04-implementation-review-wave.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-04-implementation-alignment.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-requirements-alignment.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-design-alignment.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-tasks-alignment.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-09-existing-system-sdd-implementation-alignment.md`
- `.reviewcompass/specs/conformance-evaluation/conformance/2026-06-09-real-data-r2-post-hoc-intent-diff.md`
- `learning/workflow/carry-forward-register/reviewcompass-import.yaml`

ReviewCompass の完了判定は、会話上の記憶ではなく以下の機械状態へ固定されている。

- `tools/check-workflow-action.py next --json`
- feature ごとの `spec.json`
- review-run の raw / parsed / summary / triage / approval 記録
- post-write verification manifest
- commit approval guard
- carry-forward register

## Final Hardening

完了直前に行った主な堅牢化:

- 既存システムへ後追い intent を追加した場合も、reopen 分類から requirements / design / tasks / implementation の再確認連鎖へ進めるようにした。
- `workflow-management` に、後追い intent、上流正本変更、feature impact、downstream impact、drafting-before-review、commit 代行判定の機械ガードを反映した。
- `conformance-evaluation` に `post_hoc_intent_diff` を追加し、既存仕様・実装コードから後追い intent の差分候補を抽出できるようにした。
- `review_triage.py` を強化し、item-level の `decision_status: draft` が残る triage を未解決として扱うようにした。
- carry-forward register を正本化し、旧 ReviewCompass 固有の持ち越し台帳を一般化された `required_inputs.unresolved_cross_scope_items` として扱えるようにした。

## Current Operating Rule

通常ワークフロー上の未完了タスクはない。

次に作業する場合は、まず以下を確認する。

```bash
.venv/bin/python3 tools/check-workflow-action.py next --json
git status --short
git log --oneline -5
```

`next --json` が `post_write_verification`、`reopen_in_progress`、`resume_in_progress`、`unknown` のいずれかを返した場合は、通常作業へ進まない。`completed` が維持されている場合のみ、運用・リリース・追加改善などの新しい作業を別途定義する。

## Candidate Next Work

完了後の候補作業:

1. `post_hoc_intent_diff` の実データ試行結果を fixture または回帰確認へ採用するか判断する。
2. ReviewCompass の運用開始、リリース、配布、または導入手順を新しい計画として切る。
3. review-wave 改善メモに残した follow-up candidates を棚卸しし、次の改善候補を選ぶ。
4. 完了状態の外部向け説明を作る場合は、本サマリと implementation phase summary を根拠にして、研究報告・README・運用ガイドのどれへ展開するかを決める。

