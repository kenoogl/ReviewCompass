---
date: 2026-06-21
gate: stages/implementation.yaml#alignment
feature: all_features
phase: implementation
stage: alignment
reopen: R-0（requirement-13-16-vertical-redo）
decision: existing_sufficient
review_wave_evidence: .reviewcompass/specs/_cross_feature/reviews/2026-06-21-implementation-review-wave.md
gate_completion_authorized: false
---

# implementation alignment：Requirement 13〜16 縦方向やり直し

## 対象

workflow-management implementation review-wave 後の alignment 段。

本段では、Requirement 13〜16、design、tasks、implementation 修正、triad-review 証跡、review-wave 判定、`spec.json` の workflow_state が整合しているかを確認する。

## requirements Requirement 13〜16 との整合

| requirements | implementation での受け皿 | 整合判定 |
| --- | --- | --- |
| Requirement 13：operation contract 語彙と `required_action` 対応 | operation contract / operation registry / preflight / commit boundary / side effects / workflow_state_effect の実装と、`next --json` の地点に応じた operation 接続で受ける。 | 整合 |
| Requirement 14：承認ゲート、side track stack、workflow-state snapshot | approval scope、human-only / proxy-allowed 境界、commit approval digest、workflow-state snapshot、side track stack の検査で受ける。 | 整合 |
| Requirement 15：構造化有効プロンプトと監査 | structured effective prompt、prompt audit、source artifact、precondition、postcondition、prompt length、effective prompt sha traceability の fail-closed 検査で受ける。 | 整合 |
| Requirement 16：段階的実装計画 Phase 0〜6 | implementation phase plan、snapshot evidence、commit boundary、proxy triage decision schema/check、human-required predicate、review-wave consumer impact で受ける。 | 整合 |

## design / tasks との整合

| 上流 | implementation での受け皿 | 整合判定 |
| --- | --- | --- |
| design §Requirement 13 設計モデル | operation contract 語彙、registry / contract 境界、read-only preflight、drift / 重複検出を実装対象として維持した。 | 整合 |
| design §Requirement 14 設計モデル | approval gate record、decision_scope、binding_kind、side track stack、workflow-state snapshot の境界を実装対象として維持した。 | 整合 |
| design §Requirement 15 設計モデル | effective prompt manifest、language_task、prompt audit、LLM judge audit の構造化方針を実装対象として維持した。 | 整合 |
| design §Requirement 16 設計モデル | Phase 0〜6、active reopen scope と impact review scope の分離、proxy decision と human-required predicate の優先順位を実装対象として維持した。 | 整合 |
| tasks T-016〜T-019 | T-016 は operation contract、T-017 は approval / side track / snapshot、T-018 は effective prompt / prompt audit、T-019 は Phase 0〜6 / proxy triage decision として実装へ接続された。 | 整合 |

## implementation triad-review 対処との整合

Req15 / Req16 の API review-run では、同根クラスタを整理し、利用者承認後に triage と実装修正を反映した。

| review run | 主な所見 | 実装結果 | 整合判定 |
| --- | --- | --- | --- |
| Req15 | prompt audit の fail-closed 不足、prompt length 境界、machine-task leakage 診断、sha traceability | prompt audit の必須構造 / source / precondition / postcondition / length 検査、複数診断、effective prompt sha / builder schema validation を追加した。 | 整合 |
| Req16 | proxy decision の human-required 不足、schema evidence 不足、approval scope、phase evidence、review-wave impact、operation-list | proxy triage decision schema/check、approval scope、implementation phase evidence、review-wave consumer impact、operation-list pending conflict status を追加した。 | 整合 |

修正追跡は次に保存済みである。

- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req15-review-run/review-traceability-report.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req16-review-run/review-traceability-report.md`

## implementation review-wave 判定との整合

implementation review-wave では、未消化 carry-forward が 0 件であることを確認し、workflow-management 以外の feature について implementation 正本変更は不要と判定した。

- reopen scope: workflow-management のみ
- impact review scope: all features
- other features: `existing_sufficient`
- carry-forward unresolved: 0
- workflow-management: implementation approval が残る

この判定は、Requirement 16 の active reopen scope / impact review scope 分離、proxy / human 境界、review-wave consumer impact の扱いと整合する。他 feature は workflow-management の中央ワークフロー機構を consumer / derivative として参照でき、implementation 正本変更を要求しない。

## workflow_state との整合

`spec.json` の現在状態は次の通りである。

- requirements: drafting / triad-review / review-wave / alignment / approval は完了
- design: drafting / triad-review / review-wave / alignment / approval は完了
- tasks: drafting / triad-review / review-wave / alignment / approval は完了
- implementation: drafting / triad-review / review-wave は完了、alignment / approval は未完了
- `recheck.upstream_change_pending`: false
- `recheck.impacted_downstream_phases`: []
- `reopened`: 履歴フラグとして true を保持

`next --json` は現在、`all_features / implementation / alignment` を返している。本 alignment 記録は、その地点に対応する整合確認である。

## 判定

- **decision: existing_sufficient**
- Requirement 13〜16、design、tasks、implementation 修正、triad-review 証跡、review-wave 判定、workflow_state は整合している。
- workflow-management 以外の feature について、implementation 正本変更は不要。
- implementation approval は未完了であり、次 gate として維持する。

## 証跡

- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/tasks.md`
- `.reviewcompass/specs/workflow-management/spec.json`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req15-review-run/review-traceability-report.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req16-review-run/review-traceability-report.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-21-implementation-review-wave.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-21-implementation-review-wave-summary.md`

## 停止点

本記録は implementation alignment の整合確認結果である。gate 完了、commit、push、`spec.json` 更新、approval はまだ行わない。
