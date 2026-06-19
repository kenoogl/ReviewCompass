---
date: 2026-06-19
gate: stages/tasks.yaml#alignment
feature: workflow-management
reopen: R-0
reopen_topic: integrated-design-tasks
decision: existing_sufficient
---

# tasks alignment：統合設計メモ反映

reopen R-0（`docs/reviews/reopen-classification-2026-06-19-wm-integrated-design-requirements.md`）の第3過程、workflow-management tasks フェーズの alignment 段。

本段では、requirements Requirement 13〜16、workflow-management design、workflow-management tasks、tasks triad-review 対処、tasks review-wave 判定、`spec.json` / reopen 進行中記録の整合を確認する。

## requirements Requirement 13〜16 との整合

| requirements | tasks での受け皿 | 整合判定 |
| --- | --- | --- |
| Requirement 13：operation contract 語彙と `required_action` 対応 | T-016 が operation contract 語彙、19 `required_action` 対応、precondition / postcondition / side effect / phase boundary、commit boundary 強制を担当する。 | 整合 |
| Requirement 14：承認ゲート、side track stack、workflow-state snapshot | T-017 が承認ゲート、proxy_model / human decision 境界、side track stack、staged file set / digest、workflow-state snapshot payload / drift 検査を担当する。 | 整合 |
| Requirement 15：構造化有効プロンプトと prompt audit | T-018 が language task I/O、structured effective prompt manifest、prompt audit、既存 `rounds.yaml` の `effective_prompt_path` / `effective_prompt_sha256` 互換を担当する。 | 整合 |
| Requirement 16：Phase 0〜6 と proxy_model triage decision 機械処理化 | T-019 が Phase 0〜6、proxy_model triage decision、consumer impact blocking、active reopen scope / impact review scope 分離を担当する。 | 整合 |

Tasks traceability table は Requirement 13〜16 の受入項目を T-016〜T-019 へ追跡しており、XDI-WM-005 でも operation contract、承認ゲート、side track stack、workflow-state snapshot、構造化有効プロンプト、prompt audit、Phase 0〜6、proxy_model triage decision、review-wave consumer impact を保持している。

## design との整合

| design 領域 | tasks での受け皿 | 整合判定 |
| --- | --- | --- |
| §Requirement 13 設計モデル | T-016 が schema / registry / `required_action` 対応 / precondition / postcondition を実装タスク化する。 | 整合 |
| §Requirement 14 設計モデル | T-017 が decision record、side-track stack frame、push / pop、workflow-state snapshot、digest drift 検出を実装タスク化する。 | 整合 |
| §Requirement 15 設計モデル | T-018 が structured prompt manifest と prompt audit を既存 T-004 の effective prompt 記録と接続する。 | 整合 |
| §Requirement 16 設計モデル | T-019 が Phase 0〜6 の開始条件・完了条件・禁止事項・回帰範囲と proxy_model decision traceability を実装タスク化する。 | 整合 |

Design approval 完了後に tasks drafting へ進み、Requirement 13〜16 の設計内容は T-016〜T-019 として展開済みである。tasks 内の追加修正は、design triad-review / review-wave の既存判定範囲を逸脱していない。

## tasks triad-review 対処との整合

tasks triad-review では、proxy_model が C1〜C3 を `must-fix`、C4 を `should-fix`、C5 を `leave-as-is` と判断した。C1〜C4 は tasks.md と review response へ反映済みである。

| cluster | final label | tasks 反映 | 整合判定 |
| --- | --- | --- | --- |
| C1: T-017 workflow-state snapshot coverage | must-fix | T-017 の完了条件・テスト要件に `spec.json.workflow_state`、`reopened`、`recheck`、in-progress sha、pending / drafting completed / completed gates、downstream impact decisions、operation contract digest、staged file set digest、worktree dirty path digest を明示した。 | 整合 |
| C2: T-018 prompt manifest compatibility | must-fix | T-018 の完了条件・テスト要件に、structured prompt manifest が既存 T-004 `effective_prompt_path` / `effective_prompt_sha256` を拡張すること、text-only 互換 WARN、mismatch / missing-field DEVIATION を明示した。 | 整合 |
| C3: T-019 consumer impact and scope distinction | must-fix | T-019 の完了条件・テスト要件に consumer impact 入力、carry-forward、downstream impact decisions、active reopen scope / impact review scope、`spec.json.reopened` 履歴フラグとの分離を明示した。 | 整合 |
| C4: Requirement 14〜16 traceability rows | should-fix | 追跡表に proxy_model / human 境界、staged file set / digest、prompt manifest 互換、consumer impact blocking、scope separation を直接見える形で反映した。 | 整合 |
| C5: positive state and responsibility-boundary findings | leave-as-is | 単独修正なし。タスク数、責務分離、`spec.json`、reopen in-progress state は既に整合している。 | 整合 |

詳細は `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-integrated-design-review-run/review-response.md` に記録済みである。

## tasks review-wave 判定との整合

tasks review-wave では、workflow-management 以外の feature を consumer / derivative として impact review scope に含めたうえで、tasks 正本変更は不要と判定した。

- reopen scope: workflow-management のみ
- impact review scope: all features
- other features: `existing_sufficient`
- carry-forward unresolved: 0
- workflow-management: tasks / implementation recheck pending

この判定は Requirement 16 受入 10〜12、および T-019 の consumer impact blocking / active reopen scope / impact review scope 分離と整合する。operation contract、workflow-state snapshot、structured effective prompt、approval / side-track 機構、proxy_model triage decision は他 feature が参照し得るが、tasks 正本の所有と再実施対象は workflow-management である。

## workflow_state / reopen 記録との整合

`spec.json` の現在状態は次の通りである。

- requirements: drafting / triad-review / review-wave / alignment / approval は完了
- design: drafting / triad-review / review-wave / alignment / approval は完了
- tasks: drafting / triad-review / review-wave は完了、alignment / approval は未完了
- implementation: 全段未完了
- `recheck.upstream_change_pending`: true
- `recheck.impacted_downstream_phases`: design, tasks, implementation
- `reopened`: 履歴フラグとして true を保持

`stages/in-progress/reopen-procedure-2026-06-19.yaml` は、tasks drafting / triad-review / review-wave の完了を進行中記録として保持し、次 gate を `stages/tasks.yaml#alignment` としている。

この状態は、現在の active reopen scope と履歴フラグを同一視しない方針、および phase approval 前に approval flag を先行更新しない方針と整合する。tasks alignment 完了後も、利用者承認を要する tasks approval が残るため、implementation へはまだ進まない。

## 下流 recheck 状態との整合

tasks で追加・補強した内容は、implementation へ順に展開する必要がある。

- **implementation**: T-016〜T-019 に従い、schema / operation contract registry / preflight / approval gate / side-track stack / workflow-state snapshot / structured prompt manifest / proxy_model decision traceability / consumer impact blocking を、Phase 0〜6 の順序で実装する必要がある。

したがって、`recheck.impacted_downstream_phases` が design / tasks / implementation を保持していることは妥当である。tasks approval 完了後に implementation gate へ進む。

## 判定

- **decision: existing_sufficient**
- requirements Requirement 13〜16、design、tasks、triad-review 対処、review-wave 判定、workflow_state / reopen 記録は整合している。
- tasks 内の追加修正は不要。
- implementation への連鎖再実施は `recheck.impacted_downstream_phases` と pending gates で追跡中であり、tasks alignment 時点では維持する。
