---
date: 2026-07-01
gate: stages/requirements.yaml#alignment
feature: workflow-management
phase: requirements
stage: alignment
reopen: R-0（reopen protocol mechanization review）
decision: existing_sufficient
review_wave_evidence: .reviewcompass/specs/_cross_feature/reviews/2026-07-01-requirements-reopen-protocol-review-wave.md
---

# requirements alignment：reopen protocol mechanization review

## 対象

reopen R-0（`.reviewcompass/backlog/plans/plan-2026-07-01-reopen-protocol-mechanization-review.yaml`）の第3過程、workflow-management requirements フェーズの alignment 段。

本段では、reopen 分類、requirements 正本、triad-review 対処、review-wave 判定、`spec.json` / reopen 進行中記録の整合を確認する。

## reopen 分類との整合

今回の reopen は、requirements を実質編集し、design / tasks / implementation へ波及する機械処理契約を正本化する R-0 である。

| reopen 意図 | requirements での受け皿 | 整合判定 |
| --- | --- | --- |
| edited phase の full review gate を要求する | Requirement 5 に edited phase / downstream impact fail-closed 契約を追加 | 整合 |
| downstream impact decision の不足を fail-closed にする | Requirement 5 で `no_impact` / `existing_sufficient` でも 5-field decision を要求 | 整合 |
| superseding reopen でも必要 gate chain を維持する | Requirement 5 で superseding reopen record の full gate chain 要求を明示 | 整合 |
| workflow state と reopen record を真実源にする | `spec.json` と `stages/in-progress/reopen-procedure-2026-07-01.yaml` で pending / completed gates を保持 | 整合 |

## triad-review 対処との整合

requirements triad-review では、実 review-run と利用者可視 triage を経て、次を反映済みである。

| cluster | label | requirements 反映 | 整合判定 |
| --- | --- | --- | --- |
| C1 fail-closed detection layering | must-fix | normal completion / reopen-finalize / commit preflight の検出層を明確化 | 整合 |
| C2 superseding reopen full-gate chain | must-fix | superseding reopen record にも edited phase の full gate chain を要求 | 整合 |
| C3 downstream no-change decision evidence | must-fix | no-change decision でも構造化 5-field evidence を要求 | 整合 |
| C4 feature-scope traceability | should-fix | Requirement 16 AC11-12 との active reopen / impact review / consumer-derivative scope 境界へ接続 | 整合 |

反映済み requirements は、triad-review の must-fix / should-fix 対処方針と矛盾しない。

## review-wave 判定との整合

requirements review-wave では、workflow-management 以外の feature について requirements 正本変更は不要と判定した。

- decision: `existing_sufficient`
- carry-forward unresolved: 0
- reopen scope: workflow-management のみ
- downstream recheck: design / tasks / implementation

この判定は Requirement 5 と Requirement 16 の scope 境界と整合する。すなわち、今回の変更は workflow-management の reopen 機械処理契約であり、他 feature は consumer / derivative として参照し得るが、requirements 正本を再オープンする必要はない。

## workflow_state / reopen 記録との整合

`spec.json` の現在状態は次の通りである。

- requirements: drafting / triad-review / review-wave は完了、alignment / approval は未完了
- design / tasks / implementation: drafting から未完了
- `recheck.upstream_change_pending`: true
- `recheck.impacted_downstream_phases`: design, tasks, implementation
- `reopened`: 履歴フラグとして true を保持

`stages/in-progress/reopen-procedure-2026-07-01.yaml` は、requirements triad-review と review-wave を `completed_gates` に記録し、次 gate を `stages/requirements.yaml#alignment` としている。review-wave 停止点 commit は `commit_stop_point_records` に記録済みである。

この状態は、workflow_state を状態判定の真実源とし、active reopen scope と履歴フラグを同一視しない方針と整合している。

## 下流 recheck 状態との整合

requirements で追加・補強した reopen 契約は、design / tasks / implementation へ順に展開する必要がある。

- design: edited phase / downstream impact decision / superseding reopen / fail-closed 検出層を設計へ反映する必要がある。
- tasks: 上記契約を TDD 可能な作業単位へ分解する必要がある。
- implementation: `next --json`、`reopen-finalize`、commit preflight の機械処理として実装・検証する必要がある。

したがって、`recheck.impacted_downstream_phases` が design / tasks / implementation を保持していることは妥当である。

## 判定

- decision: existing_sufficient
- reopen 分類、requirements、triad-review 対処、review-wave 判定、workflow_state / reopen 記録は整合している。
- requirements 内の追加修正は不要。
- design / tasks / implementation への連鎖再実施は `recheck.impacted_downstream_phases` と pending gates で追跡中であり、requirements alignment 時点では維持する。
- 次は `stages/requirements.yaml#approval` の人間承認ゲートである。

## 証跡

- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/spec.json`
- `stages/in-progress/reopen-procedure-2026-07-01.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-07-01-workflow-management-requirements-reopen-protocol-review-run/review_summary.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-07-01-workflow-management-requirements-reopen-protocol-review-run/triage.yaml`
- `.reviewcompass/specs/_cross_feature/reviews/2026-07-01-requirements-reopen-protocol-review-wave.md`
- `.reviewcompass/specs/_cross_feature/reviews/review-wave-summary.json`
