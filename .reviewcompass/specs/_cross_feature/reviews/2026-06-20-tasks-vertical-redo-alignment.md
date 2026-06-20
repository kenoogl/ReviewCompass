---
date: 2026-06-20
gate: stages/tasks.yaml#alignment
feature: workflow-management
phase: tasks
stage: alignment
reopen: R-0（requirement-13-16-vertical-redo）
decision: existing_sufficient
review_wave_evidence: .reviewcompass/specs/_cross_feature/reviews/2026-06-20-tasks-vertical-redo-review-wave.md
target_manifest: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-tasks-vertical-redo-review-run-v3/post-fix-target-manifest.yaml
---

# tasks alignment：Requirement 13〜16 縦方向やり直し

reopen R-0（`docs/reviews/reopen-classification-2026-06-19-wm-requirement-13-16-vertical-redo.md`）の第3過程、workflow-management tasks フェーズの alignment 段。

本段では、requirements Requirement 13〜16、workflow-management design、workflow-management tasks、tasks triad-review v3 post-fix、tasks review-wave 判定、`spec.json` / reopen 進行中記録の整合を確認する。

## requirements Requirement 13〜16 との整合

| requirements | tasks での受け皿 | 整合判定 |
| --- | --- | --- |
| Requirement 13：operation contract 語彙と `required_action` 対応 | T-016 が operation contract 語彙・schema、`required_action` 対応、registry / contract 正本境界、branch / internal step、approval aggregation、precondition / postcondition / side effect / phase boundary、commit boundary 強制を担当する。 | 整合 |
| Requirement 14：承認ゲート、side track stack、workflow-state snapshot | T-017 が approval gate record、`decision_scope`、`binding_kind`、proxy_model / human decision 境界、side track stack、workflow-state snapshot、staged file set / digest、`source_next_action_sha256`、drift 検査を担当する。 | 整合 |
| Requirement 15：構造化有効プロンプトと prompt audit | T-018 が language task I/O、structured effective prompt manifest、`prompt_length` bounds、`next_action_compatible`、prompt audit、Phase 6 judge audit を担当する。 | 整合 |
| Requirement 16：Phase 0〜6 と proxy_model triage decision 機械処理化 | T-019 が Phase 0〜6、read-only `operation-list --json`、proxy_model triage decision、human-required predicate、active reopen scope / impact review scope 分離、consumer impact blocking を担当する。 | 整合 |

Tasks traceability table は Requirement 13〜16 の受入条件を T-016〜T-019 へ追跡している。特に XDI-WM-005 は、operation contract、承認ゲート、side track stack、workflow-state snapshot、構造化有効プロンプト、prompt audit、Phase 0〜6、proxy_model triage decision、review-wave consumer impact を tasks 層で保持している。

## design との整合

| design 領域 | tasks での受け皿 | 整合判定 |
| --- | --- | --- |
| §Requirement 13 設計モデル | T-016 が `stages/operation-contracts.yaml`、operation contract schema、registry / preflight binding、branchy operation contract、approval aggregation、commit boundary を実装タスク化する。 | 整合 |
| §Requirement 14 設計モデル | T-017 が approval gate record、`decision_scope`、`binding_kind`、side-track stack frame、push / pop、workflow-state snapshot、digest drift 検出を実装タスク化する。 | 整合 |
| §Requirement 15 設計モデル | T-018 が language task I/O、structured prompt manifest、prompt audit、既存 `rounds.yaml` の `effective_prompt_path` / `effective_prompt_sha256` 互換、Phase 6 judge audit を実装タスク化する。 | 整合 |
| §Requirement 16 設計モデル | T-019 が Phase 0〜6 の開始条件・完了条件・禁止事項・成果物・回帰範囲、proxy_model decision traceability、human-required predicate、scope 分離を実装タスク化する。 | 整合 |

Design approval 完了後に tasks drafting へ進み、Requirement 13〜16 の設計内容は T-016〜T-019 として展開済みである。tasks 内の追加修正は、design triad-review / review-wave / alignment の既存判定範囲を逸脱していない。

## tasks triad-review v3 post-fix との整合

tasks triad-review v3 では 25 件を decided とし、final label は must-fix 10 件、should-fix 12 件、leave-as-is 3 件であった。review response 後、C1〜C6 は `tasks.md` に反映し、C7 は leave-as-is として記録した。`assert-apply-fixes-ready` は true、post-fix coverage は 25/25 である。

| cluster | final handling | tasks 反映 | 整合判定 |
| --- | --- | --- | --- |
| C1: T-016 branchy operation contract / approval aggregation | reflected | T-016 に `branching.branches[]`、`sequence.internal_steps`、branch `max_effect_kind`、`approval_aggregation`、`human_only_override_applies`、`approval_contract_ref`、`phase_boundary` coverage を明示した。 | 整合 |
| C2: T-017 approval gate record / decision binding | reflected | T-017 に approval gate record field set、`decision_scope` 導出、`binding_kind` 値域、digest 要件、target binding fail-closed を明示した。 | 整合 |
| C3: T-017 workflow-state snapshot contract | reflected | T-017 に `.reviewcompass/runtime/workflow-state-snapshot.yaml`、`source_next_action_sha256`、required top-level sections、`current_work` fields を明示した。 | 整合 |
| C4: T-018 prompt length / next-action compatibility | reflected | T-018 に `WORKFLOW_DISCIPLINE_MAP.yaml` 由来の `prompt_length` bounds、`failure_verdict`、`next_action_compatible`、`on_completion` compatibility checks を明示した。 | 整合 |
| C5: T-018 language task vocabulary / Phase 6 judge audit | reflected | T-018 に design vocabulary の `document_kind` / `input` / `output_format` / `constraints` と、Phase 6 judge audit の structured gap output を追加した。 | 整合 |
| C6: T-019 Phase 2 operation-list / proxy triage safeguards | reflected | T-019 に read-only `operation-list --json`、active reopen scope / impact review scope 分離、review/apply scope mismatch checks、fixed human-required predicate order を明示した。 | 整合 |
| C7: inaccurate or already-covered residual claims | leave-as-is | excerpt range claim は不正確、workflow-state claim は既に正しく、実質 traceability issues は C5/C6 で処理済みとして追加修正なし。 | 整合 |

## tasks review-wave 判定との整合

tasks review-wave は `existing_sufficient` と判定した。carry-forward 未消化は 0 件であり、workflow-management 以外の feature について tasks 正本変更は不要とされた。

| feature | review-wave 判定 | alignment 判断 |
| --- | --- | --- |
| foundation | existing_sufficient | 共有語彙・配置規約の正本変更は不要。T-016〜T-019 は workflow-management 所有の操作契約・承認ゲート・prompt audit・triage decision 処理である。 |
| runtime | existing_sufficient | 実行状態や証跡生成は consumer / provider 関係として現行 tasks で受けられる。workflow-management 側の読み取り・検査・記録方法を変えるだけで足りる。 |
| evaluation | existing_sufficient | review-run / post-write verification 成果物の供給契約は変更しない。workflow-management が structured prompt manifest と proxy_model decision として束ねる。 |
| analysis | existing_sufficient | workflow-state snapshot は workflow-management が出力するため、analysis tasks の正本変更は不要。 |
| workflow-management | reopen_existing_feature | 本 reopen の所有機能。Requirement 13〜16 の T-016〜T-019 展開、triad-review v3 post-fix、review-wave / alignment / approval、implementation 再実施対象である。 |
| self-improvement | existing_sufficient | 改善提案側の正本変更は不要。proxy_model / human decision 境界や approval gate 実装は workflow-management 側で足りる。 |
| conformance-evaluation | existing_sufficient | gap handoff 後の active reopen scope / impact review scope 分離、consumer impact blocking は workflow-management 側で処理するため、conformance-evaluation tasks 変更は不要。 |

この判定は Requirement 16 受入 10〜14、および T-019 の consumer impact blocking / active reopen scope / impact review scope 分離と整合する。operation contract、workflow-state snapshot、structured effective prompt、approval / side-track 機構、proxy_model triage decision は他 feature が参照し得るが、tasks 正本の所有と再実施対象は workflow-management である。

## workflow_state / reopen 記録との整合

`spec.json` の現在状態は次の通りである。

- requirements: drafting / triad-review / review-wave / alignment / approval は完了
- design: drafting / triad-review / review-wave / alignment / approval は完了
- tasks: drafting / triad-review / review-wave は完了、alignment / approval は未完了
- implementation: 全段未完了
- `recheck.upstream_change_pending`: true
- `recheck.impacted_downstream_phases`: tasks, implementation

`stages/in-progress/reopen-procedure-2026-06-19.yaml` は、tasks drafting / triad-review / review-wave の完了を進行中記録として保持し、次 gate を `stages/tasks.yaml#alignment` としている。pending gate は `stages/tasks.yaml#alignment` と `stages/tasks.yaml#approval` であり、alignment 完了後も利用者承認を要する tasks approval が残る。

この状態は、`spec.json.workflow_state` を truth source として扱う規律と整合する。summary や会話上の理解ではなく、`spec.json` と reopen in-progress file の現在値に基づき、approval flag を先行更新しない。

## 下流 recheck 状態との整合

tasks で追加・補強した T-016〜T-019 は、implementation へ順に展開する必要がある。

- implementation: schema / operation contract registry / preflight / approval gate / side-track stack / workflow-state snapshot / structured prompt manifest / proxy_model decision traceability / consumer impact blocking を Phase 0〜6 の順序で実装する必要がある。

したがって、`recheck.impacted_downstream_phases` が tasks / implementation を保持していることは妥当である。tasks approval 完了後に implementation gate へ進む。

## 判定

- **decision: existing_sufficient**
- requirements Requirement 13〜16、design、tasks、tasks triad-review v3 post-fix、tasks review-wave 判定、workflow_state / reopen 記録は整合している。
- tasks 内の追加修正は不要。
- implementation への連鎖再実施は `recheck.impacted_downstream_phases` と pending gates で追跡中であり、tasks alignment 時点では維持する。

## 証跡

- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/tasks.md`
- `.reviewcompass/specs/workflow-management/spec.json`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-tasks-vertical-redo-review-run-v3/review_summary.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-tasks-vertical-redo-review-run-v3/triage.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-tasks-vertical-redo-review-run-v3/post-fix-coverage-inventory.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-tasks-vertical-redo-review-run-v3/integrated-post-fix-recheck.md`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-tasks-vertical-redo-review-run-v3/post-fix-target-manifest.yaml`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-20-tasks-vertical-redo-review-wave.md`
- `.reviewcompass/specs/_cross_feature/reviews/2026-06-20-tasks-vertical-redo-review-wave-summary.md`
- `stages/in-progress/reopen-procedure-2026-06-19.yaml`

## 停止点

本記録は tasks alignment の整合確認結果である。gate 完了、phase transition、commit、push、`spec.json` 更新、reopen finalization はまだ行わない。
