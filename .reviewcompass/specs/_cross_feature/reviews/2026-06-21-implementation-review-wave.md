---
date: 2026-06-21
gate: stages/implementation.yaml#review-wave
feature: all_features
phase: implementation
stage: review-wave
reopen: R-0（requirement-13-16-vertical-redo）
decision: existing_sufficient
carry_forward_unresolved: 0
summary_evidence: .reviewcompass/specs/_cross_feature/reviews/2026-06-21-implementation-review-wave-summary.md
gate_completion_authorized: false
---

# implementation review-wave：Requirement 13〜16 縦方向やり直し

## 対象

workflow-management implementation triad-review 後の横断 review-wave。

今回の implementation 対応は、Requirement 13〜16 / T-016〜T-019 の実装と、Req15 / Req16 API レビュー結果の同根クラスタ整理、triage 反映、修正、修正追跡証跡化である。主な実装対象は次の通り。

- Req15: structured effective prompt、prompt audit、source/precondition/postcondition/prompt length の fail-closed 検査、effective prompt sha traceability
- Req16: proxy triage decision、human-required predicate、approval scope、implementation phase evidence、review-wave consumer impact、operation-list read-only 出力
- review-run traceability: Req15 / Req16 の `must-fix-clusters.*`、`proxy-decision-summary.md`、`autonomous-ledger.yaml`、`review-traceability-report.md`

## 機械サマリ

`tools/check-workflow-action.py review-wave-summary --out .reviewcompass/specs/_cross_feature/reviews/2026-06-21-implementation-review-wave-summary.md` を実行した。

- status: ok
- carry-forward 未消化: 0
- feature_order: foundation, runtime, evaluation, analysis, workflow-management, self-improvement, conformance-evaluation
- workflow-management: implementation.review-wave / alignment / approval が未完了
- 未充足依存: self-improvement←workflow-management, conformance-evaluation←workflow-management

未充足依存は、workflow-management の implementation 後段 gate がまだ完了していないために発生している一時状態である。本 review-wave では、workflow-management 以外の feature の implementation 正本を再オープンする必要は確認されなかった。

## 持ち越し所見

正本：`learning/workflow/carry-forward-register/reviewcompass-import.yaml`。

未消化の carry-forward は 0 件であり、本 review-wave で新たに消化すべき横断所見はない。

## 上流意図伝達の確認

本 review-wave は、Requirement 13〜16 の目的・責務境界・受入条件・禁止事項が implementation 対応後も弱体化していないかを確認する。

- Requirement 13 の「`next --json` が返す地点に応じて、そこで行う機械処理と規律を確定する」意図は、operation contract、effective prompt、prompt audit の実装に維持されている。
- Requirement 14 の「承認・side track・状態可視化を機械可読に扱う」意図は、approval scope、commit boundary、workflow-state snapshot、review-run traceability の実装に維持されている。
- Requirement 15 の「API レビュー用プロンプトを品質監査可能にする」意図は、必須構造、source artifact、precondition、postcondition、prompt length の fail-closed 検査に維持されている。
- Requirement 16 の「proxy_model と human-required 条件を混同せず、実行層へ機械的に接続する」意図は、proxy triage decision schema/check、human-required predicate、review-wave consumer impact の実装に維持されている。

横断判断では、他 feature に新たな implementation 正本変更を追加しない。これは上流意図の弱体化ではなく、今回の変更が workflow-management の中央ワークフロー機構を所有境界としているためである。

## 機能横断の影響判定

今回の implementation 変更の直接所有者は workflow-management である。他 feature は、workflow-management が提供する操作契約、承認ゲート、effective prompt、proxy decision、review-run traceability を consumer / derivative として利用する。

本 review-wave では、次の切り分けを正本として扱う。

- **reopen scope**：`workflow-management` のみ。implementation 正本と関連ツールを実質変更したため、同 feature の implementation 後段 gate を再実施する。
- **impact review scope**：全 feature。foundation / runtime / evaluation / analysis / self-improvement / conformance-evaluation は consumer / derivative として確認する。
- **flag 方針**：他 feature については implementation 正本変更を要求しないため、既存 workflow flag を維持する。影響確認結果は本 review-wave に記録する。

| feature | 判定 | 根拠 |
| --- | --- | --- |
| foundation | existing_sufficient | foundation は共有語彙・配置規約を所有するが、今回の変更は workflow-management の手続き実行、承認、prompt audit、proxy decision の実装である。foundation implementation 正本変更は不要である。 |
| runtime | existing_sufficient | runtime は実行状態や証跡生成側の provider であり、今回の変更は workflow-management がそれらを読む際の検査・記録・承認境界を強める。runtime implementation の run status や evidence writer 実装変更を要求しない。 |
| evaluation | existing_sufficient | evaluation は review-run と post-write verification の成果物を供給する側である。今回の変更は、それらを structured effective prompt や proxy decision として扱う workflow-management 側の検査であり、evaluation implementation の分類・比較・出力契約を変更しない。 |
| analysis | existing_sufficient | analysis は workflow-management の手続き履歴・状態を読む consumer である。workflow-state snapshot と traceability report は workflow-management 側で整備されるため、analysis implementation の取り込み契約変更は不要である。 |
| workflow-management | reopen_existing_feature | 本 reopen の所有機能。Requirement 13〜16 の implementation、triad-review 修正、review-wave、alignment、approval の対象である。 |
| self-improvement | existing_sufficient | self-improvement は改善提案や規律変更の提案側であり、実体の workflow 操作と承認境界は workflow-management 手続きへ委ねる。今回の実装で self-improvement implementation 正本変更は不要である。 |
| conformance-evaluation | existing_sufficient | conformance-evaluation は gap を workflow-management の reopen 手続きへ引き渡す consumer / upstream source である。active reopen scope、impact review scope、proxy/human 境界は workflow-management 側で扱うため、conformance-evaluation implementation 正本変更は不要である。 |

## 判定

- **decision: existing_sufficient**
- workflow-management 以外の feature について、implementation 正本変更は不要。
- consumer / derivative としての影響は、現行正本で受けられる。
- 未充足依存は workflow-management の implementation review-wave / alignment / approval が残っていることによる一時状態である。

## 証跡

- `.reviewcompass/specs/workflow-management/spec.json`
- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/tasks.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req15-review-run/review-traceability-report.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req16-review-run/review-traceability-report.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-run/user-visible-triage-gate.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-21-implementation-review-wave-summary.md`

## 停止点

本記録は implementation review-wave の軽量横断確認結果である。gate 完了、phase transition、commit、push、`spec.json` 更新、alignment、approval はまだ行わない。
