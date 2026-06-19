---
date: 2026-06-19
gate: stages/implementation.yaml#alignment
feature: workflow-management
reopen: R-0
reopen_topic: integrated-design-implementation
decision: existing_sufficient
---

# implementation alignment：統合設計メモ反映

reopen R-0（`docs/reviews/reopen-classification-2026-06-19-wm-integrated-design-requirements.md`）の第3過程、workflow-management implementation フェーズの alignment 段。

本段では、requirements Requirement 13〜16、workflow-management design、workflow-management tasks、implementation drafting、implementation triad-review 対処、implementation review-wave 判定、`spec.json` / reopen 進行中記録の整合を確認する。

## requirements Requirement 13〜16 との整合

| requirements | implementation drafting での受け皿 | 整合判定 |
| --- | --- | --- |
| Requirement 13：operation contract 語彙と `required_action` 対応 | T-016 が operation contract、`required_action` 対応、preconditions / postconditions / side_effects / workflow_state_effect、commit boundary の実装対象と赤テストを整理する。 | 整合 |
| Requirement 14：承認ゲート、side track stack、workflow-state snapshot | T-017 が approval gate、side track stack、workflow-state snapshot、staged file set digest、human-only decision / proxy_model decision 境界の実装対象と赤テストを整理する。 | 整合 |
| Requirement 15：構造化有効プロンプトと prompt audit | T-018 が structured effective prompt manifest、prompt audit、review-run recording、text-only 互換 WARN、manifest 不一致 DEVIATION の実装対象と赤テストを整理する。 | 整合 |
| Requirement 16：Phase 0〜6 と proxy_model triage decision 機械処理化 | T-019 が Phase 0〜6、proxy_model triage decision、review-wave consumer impact blocking、active reopen scope / impact review scope 分離の実装対象と赤テストを整理する。 | 整合 |

## design / tasks との整合

| 上流 | implementation drafting での受け皿 | 整合判定 |
| --- | --- | --- |
| design §Requirement 13 設計モデル | `.reviewcompass/schema/effect_kind.schema.json`、`phase_boundary`、`operation_contract`、operation contract registry / module / tests を T-016 実装対象として整理した。 | 整合 |
| design §Requirement 14 設計モデル | approval gate、side track stack、workflow-state snapshot の schema / module / CLI / tests を T-017 実装対象として整理した。 | 整合 |
| design §Requirement 15 設計モデル | language task I/O、effective prompt manifest、prompt audit、review-run recording 互換を T-018 実装対象として整理した。 | 整合 |
| design §Requirement 16 設計モデル | implementation phase plan、proxy triage decision schema / checker、review-wave consumer impact tests を T-019 実装対象として整理した。 | 整合 |
| tasks T-016〜T-019 | implementation drafting は T-016〜T-019 の所有ファイル候補、TDD 境界、依存順、停止条件を実装前の整理として展開した。 | 整合 |

implementation drafting は実装完了主張ではなく、実装前の整理である。`implementation-drafting.md` は、drafting 完了が triad-review 開始準備の記録であり、implementation triad-review 完了ではないことを明記している。

## implementation triad-review 対処との整合

implementation triad-review では、adversarial 役を利用者指示により `anthropic-api / claude-sonnet-4-6` に変更して実施した。proxy_model は C1/C2 を `must-fix`、C3〜C6 を `should-fix`、C7 を `leave-as-is` と判断した。

| cluster | final label | implementation drafting 反映 | 整合判定 |
| --- | --- | --- | --- |
| C1: drafting 完了表現 | must-fix | drafting 完了は triad-review 開始準備であり、review-wave / alignment / approval / commit / push 完了ではないと明記した。 | 整合 |
| C2: T-017 staged file digest と proxy/human 境界 | must-fix | `staged file set digest`、`human-only decision`、`proxy_model decision` 境界の赤テストを追加した。 | 整合 |
| C3: T-016 operation contract と commit boundary | should-fix | `preconditions`、`postconditions`、`side_effects`、`workflow_state_effect`、commit boundary の赤テストを追加した。 | 整合 |
| C4: T-018 review-run recording / migration boundary | should-fix | `text-only 互換 WARN`、`manifest 不一致 DEVIATION`、両欠落 DEVIATION、review-run recording の赤テストを追加した。 | 整合 |
| C5: T-019 phase / review-wave blocking | should-fix | Phase 0〜6 の entry / exit、forbidden operations、`review-wave consumer impact blocking` の赤テストを追加した。 | 整合 |
| C6: 検証欄の実行済み / 予定混在 | should-fix | 実行済み検証と、実装時に追加する予定の検証を分けて記録した。 | 整合 |
| C7: 進捗説明規律と workflow 記録 | leave-as-is | 修正不要。進捗説明規律は会話・報告規律であり、workflow_state の正本を置き換えない。 | 整合 |

詳細は `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/review-response.md` に記録済みである。

## implementation review-wave 判定との整合

implementation review-wave では、workflow-management 以外の feature を consumer / derivative として impact review scope に含めたうえで、implementation 正本変更は不要と判定した。

- reopen scope: workflow-management のみ
- impact review scope: all features
- other features: `existing_sufficient`
- carry-forward unresolved: 0
- workflow-management: implementation alignment / approval が残る

この判定は Requirement 16 受入 10〜12、および T-019 の consumer impact blocking / active reopen scope / impact review scope 分離と整合する。operation contract、workflow-state snapshot、structured effective prompt、approval / side-track 機構、proxy_model triage decision は他 feature が参照し得るが、implementation drafting と後続実装の所有は workflow-management である。

## workflow_state / reopen 記録との整合

`spec.json` の現在状態は次の通りである。

- requirements: drafting / triad-review / review-wave / alignment / approval は完了
- design: drafting / triad-review / review-wave / alignment / approval は完了
- tasks: drafting / triad-review / review-wave / alignment / approval は完了
- implementation: drafting / triad-review / review-wave は完了、alignment / approval は未完了
- `recheck.upstream_change_pending`: true
- `recheck.impacted_downstream_phases`: tasks, implementation
- `reopened`: 履歴フラグとして true を保持

`stages/in-progress/reopen-procedure-2026-06-19.yaml` は、implementation drafting / triad-review / review-wave の完了を進行中記録として保持し、次 gate を `stages/implementation.yaml#alignment` としている。

この状態は、現在の active reopen scope と履歴フラグを同一視しない方針、および phase approval 前に approval flag を先行更新しない方針と整合する。implementation alignment 完了後も、利用者または proxy_model の承認を要する implementation approval が残る。

## 判定

- **decision: existing_sufficient**
- requirements Requirement 13〜16、design、tasks、implementation drafting、triad-review 対処、review-wave 判定、workflow_state / reopen 記録は整合している。
- implementation drafting 内の追加修正は不要。
- implementation approval は未完了であり、次 gate として維持する。
