---
date: 2026-06-30
gate: stages/implementation.yaml#review-wave
feature: all_features
phase: implementation
stage: review-wave
reopen: R-0（MWP-0 next-json-kind-redesign）
decision: existing_sufficient
carry_forward_unresolved: 0
summary_evidence: .reviewcompass/specs/_cross_feature/reviews/2026-06-30-implementation-mwp0-review-wave-summary.md
gate_completion_authorized: false
---

# implementation review-wave：MWP-0 next-json-kind-redesign

## 対象

workflow-management implementation triad-review 後の横断 review-wave。

今回の implementation 対応は MWP-0（next-json-kind-redesign）であり、主な対象は次の通り。

- `next --json` の `kind` を作業現在地の 7 値に限定する。
- `commit_candidate` / `commit_mixing_risk` / `commit_unit_stale` を `commit-preflight` に分離する。
- `required_action` ごとの if/then 制約を `next_action_response.schema.json` に補完する。
- `next_action.reason` と最上位 `reasons` の責務差を schema と design に明示する。
- A/B/C 個別実装レビューと事前分析監査 run を triage 済みにする。

## 機械サマリ

`tools/check-workflow-action.py review-wave-summary --out .reviewcompass/specs/_cross_feature/reviews/2026-06-30-implementation-mwp0-review-wave-summary.md` を実行した。

- status: ok
- carry-forward 未消化: 0
- feature_order: foundation, runtime, evaluation, analysis, workflow-management, self-improvement, conformance-evaluation
- workflow-management: implementation.review-wave / alignment / approval が未完了
- 未充足依存: self-improvement←workflow-management, conformance-evaluation←workflow-management

未充足依存は、workflow-management の implementation 後段 gate がまだ完了していないために発生している一時状態である。本 review-wave では、workflow-management 以外の feature の implementation 正本を再オープンする必要は確認されなかった。

なお、summary の triage unresolved / human_required 件数には、過去の設計・タスク・Req14 系 review-run に残る未裁定項目が含まれる。MWP-0 の A/B/C 個別レビュー run と事前分析監査 run は triage 済みであり、本 review-wave の判断対象として新規修正を要求するものではない。

## 持ち越し所見

正本：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`。

未消化の carry-forward は 0 件であり、本 review-wave で新たに消化すべき横断所見はない。

## 上流意図伝達の確認

本 review-wave は、Requirement 2 受入 11(6) と受入 12、および T-020 の目的・責務境界・受入条件・禁止事項が implementation 対応後も弱体化していないかを確認する。

- 受入 12 の「`next --json` は作業現在地のみを示し、コミット前確認は `commit-preflight` に分離する」意図は、kind 値分離の実装と B 観点レビュー修正に維持されている。
- 受入 11(6) の「required_action ごとの条件付きフィールド制約を機械検証できる構造で表現する」意図は、A 観点レビュー修正で if/then 制約として補完されている。
- T-020 先送り事項(b) の「`next_action.reason` と最上位 `reasons` の責務差を明確化する」意図は、C 観点レビュー修正で schema と design に反映されている。
- 事前分析監査で指摘された prompt 分割不足や材料不足は、A/B/C の個別レビュー run に分割して実施したことで吸収済みである。

横断判断では、他 feature に新たな implementation 正本変更を追加しない。これは上流意図の弱体化ではなく、今回の変更が workflow-management のワークフロー出力契約と commit 操作前確認の所有境界に閉じているためである。

## 機能横断の影響判定

今回の implementation 変更の直接所有者は workflow-management である。他 feature は workflow-management が提供する workflow state / operation preflight / review-run traceability を consumer として参照し得るが、今回の MWP-0 は `next --json` と `commit-preflight` の責務分離を workflow-management 内で明確化する変更であり、他 feature の implementation 正本変更を要求しない。

| feature | 判定 | 根拠 |
| --- | --- | --- |
| foundation | existing_sufficient | foundation は共有語彙・配置規約を所有するが、今回の変更は workflow-management の操作出力契約であり、foundation implementation 正本変更は不要である。 |
| runtime | existing_sufficient | runtime は実行証跡や状態の供給側であり、`next --json` / `commit-preflight` の責務分離による runtime implementation 変更は不要である。 |
| evaluation | existing_sufficient | evaluation は review-run / verification 成果物を供給する側であり、今回の kind 分離や schema if/then 補完は workflow-management 側の解釈契約に閉じる。 |
| analysis | existing_sufficient | analysis は workflow-management の状態を読む consumer だが、commit 前確認の 3 値を `commit-preflight` に分離する変更は analysis implementation 正本変更を要求しない。 |
| workflow-management | reopen_existing_feature | 本 MWP-0 の所有機能。implementation review-wave、alignment、approval の対象である。 |
| self-improvement | existing_sufficient | self-improvement は規律改善側の consumer であり、今回の出力責務分離は workflow-management 側の契約明確化として受けられる。 |
| conformance-evaluation | existing_sufficient | conformance-evaluation は gap を workflow-management 手続きへ接続する consumer であり、今回の MWP-0 による implementation 正本変更は不要である。 |

## 判定

- **decision: existing_sufficient**
- workflow-management 以外の feature について、implementation 正本変更は不要。
- consumer としての影響は、現行正本で受けられる。
- 未消化 carry-forward は 0 件。
- 未充足依存は workflow-management の implementation review-wave / alignment / approval が残っていることによる一時状態である。

## 証跡

- `.reviewcompass/specs/workflow-management/spec.json`
- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/tasks.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-ifthen-review-run/`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-kind-sep-review-run/`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-reason-review-run/`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-27-workflow-management-implementation-mwp0-preanalysis-audit-run/`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-30-implementation-mwp0-review-wave-summary.md`

## 完了後の停止点

本記録に基づき、`workflow-management` の `implementation.review-wave` を完了済みとして記録する。commit、push、alignment、approval はまだ行わない。次は implementation alignment に進む。
