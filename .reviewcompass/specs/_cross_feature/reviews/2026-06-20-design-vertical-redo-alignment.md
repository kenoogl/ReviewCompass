---
date: 2026-06-20
gate: stages/design.yaml#alignment
feature: workflow-management
phase: design
stage: alignment
reopen: R-0（requirement-13-16-vertical-redo）
decision: existing_sufficient
review_wave_evidence: .reviewcompass/specs/_cross_feature/reviews/2026-06-20-design-vertical-redo-review-wave.md
target_manifest: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/post-fix-target-manifest.yaml
---

# design alignment：Requirement 13〜16 縦方向やり直し

## 対象

reopen R-0（`docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md`）の第3過程、workflow-management design フェーズの alignment 段。

本段では、requirements Requirement 13〜16、workflow-management design、design triad-review v2 post-fix、design review-wave、tasks T-016〜T-019 への追跡が同じ意図で接続しているかを確認する。

## requirements Requirement 13〜16 との整合

| requirements | design での受け皿 | 整合判定 |
| --- | --- | --- |
| Requirement 13：operation contract 語彙と `required_action` 対応 | §Requirement 13 設計モデルで、operation contract / registry / preflight の正本境界、19 `required_action` 対応、preconditions / postconditions、branch / internal step / approval aggregation を設計化している。 | 整合 |
| Requirement 14：承認ゲート、側道スタック、状態スナップショット | §Requirement 14 設計モデルで、approval gate record、decision_scope、binding_kind、digest 束縛、proxy / human 境界、side track stack、workflow-state snapshot を設計化している。 | 整合 |
| Requirement 15：構造化有効プロンプトと監査 | §Requirement 15 設計モデルで、language task I/O、structured effective prompt、prompt audit、review-run 記録、長さ基準の正本と失敗 verdict を設計化している。 | 整合 |
| Requirement 16：段階的実装計画 Phase 0〜6 | §Requirement 16 設計モデルで、Phase 0〜6、D-003 traceability、active reopen scope / impact review scope、proxy_model triage decision、human-required predicate を設計化している。 | 整合 |

Design traceability table は Requirement 13〜16 の受入項目を §Req 13〜§Req 16 へ接続しており、XDI-WM-005 でも operation contract、structured effective prompt、side-track stack、workflow-state snapshot、Phase 0〜6 を設計入力として保持している。

## triad-review post-fix との整合

design triad-review v2 では 15 件を triage finalization 済みにした。

- `must-fix`: 13 件
- `should-fix`: 2 件
- post-fix coverage: 15 / 15
- integrated post-fix review: 実施済み
- integrated post-fix recheck: 実施済み

統合 post-fix review で見つかった追加不整合（`approval_required` boolean と approval contract prose の混在、branch step `source_ref` 欠落）は design.md の Req 13 周辺で修正済みである。`post-fix-target-manifest.yaml` は現在 SHA を記録し、元の `target-manifest.yaml` は初回 triad-review 入力証跡として保持している。

## review-wave との整合

design review-wave は軽量確認として実施し、他 feature の design 正本変更は不要と判定した。

- decision: `existing_sufficient`
- carry-forward unresolved: 0
- reopen scope: workflow-management のみ
- impact review scope: all features
- flag policy: 他 feature の workflow flag は false に戻さない

この判定は Requirement 16 の consumer / derivative impact 確認、active reopen scope と impact review scope の分離、および design §Requirement 16 の downstream impact evidence と整合する。

## tasks への追跡

tasks.md は Requirement 13〜16 を T-016〜T-019 へ分解している。

| design / requirements 意図 | tasks での受け皿 | 整合判定 |
| --- | --- | --- |
| operation contract 語彙、19 `required_action`、registry / contract 境界 | T-016 | 整合 |
| approval gate、proxy / human 境界、side track stack、snapshot | T-017 | 整合 |
| structured effective prompt、prompt audit、review-run prompt manifest | T-018 | 整合 |
| Phase 0〜6、proxy_model triage decision、review-wave consumer impact blocking | T-019 | 整合 |

tasks の詳細化は後続 gate で再確認する必要があるが、design alignment 時点では requirements → design → tasks の追跡は成立している。

## workflow_state / reopen 記録との整合

現在の状態は次の通りである。

- requirements: drafting / triad-review / review-wave / alignment / approval は完了
- design: drafting / triad-review / review-wave / alignment は完了、approval は未完了
- tasks / implementation: 未完了
- `recheck.upstream_change_pending`: true
- `recheck.impacted_downstream_phases`: design, tasks, implementation
- `spec.json.reopened`: 履歴フラグとして true を保持

design alignment 完了後も、利用者承認を要する design approval が残るため、reopen は完了しない。tasks / implementation への連鎖再実施も残る。

## 判定

- **decision: existing_sufficient**
- requirements Requirement 13〜16、design、triad-review post-fix、review-wave、tasks 追跡、workflow_state / reopen 記録は整合している。
- design 内の追加修正は不要。
- 次は `stages/design.yaml#approval` の人間承認ゲートである。

## 証跡

- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/tasks.md`
- `.reviewcompass/specs/workflow-management/spec.json`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/triage.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-design-vertical-redo-review-run-v2/post-fix-target-manifest.yaml`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-20-design-vertical-redo-review-wave.md`
