---
date: 2026-06-19
gate: stages/requirements.yaml#alignment
feature: workflow-management
reopen: R-0
reopen_topic: integrated-design-requirements
decision: existing_sufficient
---

# requirements alignment：統合設計メモ反映

reopen R-0（`docs/reviews/reopen-classification-2026-06-19-wm-integrated-design-requirements.md`）の第3過程、workflow-management requirements フェーズの alignment 段。

本段では、intent、requirements、triad-review 対処、review-wave 判定、`spec.json` / reopen 進行中記録の整合を確認する。

## intent との整合

`intent/INTENT.md` は、裁定負荷を LLM の暗黙判断に隠さず、機械タスク、LLM の言語タスク、人間判断を分離する意図を持つ。特に次を workflow-management の上位意図としている。

- `next --json` を現在実行してよい唯一 action selector とする。
- operation contract が action の前提条件、副作用、事後条件を定義する。
- 承認待ち、側道、post-write verification、reopen、commit stop point を機械可読な状態として扱う。
- LLM が手順を暗黙に裁定せず、状態スナップショットや構造化有効プロンプトで現在位置を読めるようにする。

Requirement 13〜16 は、上記の意図を requirements 層へ展開している。

| intent の要素 | requirements での受け皿 | 整合判定 |
| --- | --- | --- |
| `next --json` の唯一 action selector | Requirement 13 の `required_action` と operation contract 対応、Requirement 16 の Phase 0 | 整合 |
| 機械タスク / 言語タスク / 人間判断の分離 | Requirement 13 の `effect_kind` / `approval_required`、Requirement 15 の構造化有効プロンプト | 整合 |
| 承認待ちを機械可読状態として扱う | Requirement 13 / 14 の `record_human_decision`、承認 / 拒否 / 保留 / 修正要求の記録 | 整合 |
| 側道と復帰先を会話文脈に依存させない | Requirement 14 の side-track stack、`return_to`、`staged_file_set` / `staged_file_digest` | 整合 |
| 状態スナップショットは正本を置き換えない | Requirement 14 の workflow-state snapshot と正本参照規則 | 整合 |
| 後続フェーズで再推論しない | Requirement 16 の Phase 0〜6、reopen scope / impact review scope の区別 | 整合 |

## Requirements 13〜16 と既存 requirements の整合

| 要件 | 関係 | 整合判定 |
| --- | --- | --- |
| Requirement 2（検査スクリプト / `next --json`） | Requirement 13 と 16 は、既存の `next --json` 契約を operation contract / Phase 0 実装計画へ接続する。 | 整合 |
| Requirement 3（起草者と判定者の分離） | proxy_model triage decision は判断代行であり、commit / push / spec.json approve / phase movement を代行しない。 | 整合 |
| Requirement 4（不可逆操作の直前ゲート） | Requirement 13 / 14 は、承認記録と対象 operation を結びつけ、不可逆操作の直前ゲートを補強する。 | 整合 |
| Requirement 5（reopen 手続き） | Requirement 16 は reopen scope / impact review scope を区別し、現在の in-progress reopen record と整合する。 | 整合 |
| Requirement 6（session 跨ぎ状態管理） | Requirement 14 の side-track stack と workflow-state snapshot は session 跨ぎ状態管理を補強する。 | 整合 |
| Requirement 7（多層防御） | Requirement 15 の第1層機械検査と Phase 6 LLM judge audit は、多層防御の位置付けを保ったまま具体化する。 | 整合 |
| Requirement 8（機能依存マップ） | Requirement 16 の review-wave / impact review scope は feature_order と全 feature scope を前提にしている。 | 整合 |
| Requirement 12（operation registry / preflight） | Requirement 13〜16 は Requirement 12 の operation contract / preflight を、選択層・実行層・prompt 層・段階実装へ広げる。 | 整合 |

## triad-review 対処との整合

requirements triad-review では、C1/C2 を `must-fix`、C3〜C7 を `should-fix`、C8/C9 を `leave-as-is` と判断した。

| cluster | final label | requirements 反映 | 整合判定 |
| --- | --- | --- | --- |
| C1: 19 `required_action` と複合 operation | must-fix | Requirement 13 に19語彙対応表の最小項目、複合操作の分岐条件・最大副作用を追加 | 整合 |
| C2: side-track stack / commit mixing | must-fix | Requirement 14 に staged file set / digest の採取時点、照合条件、不一致時の扱いを追加 | 整合 |
| C3: 承認ゲート / `record_human_decision` | should-fix | Requirement 13 / 14 に承認対象との非同一視、判断種別、対象 operation identity を追加 | 整合 |
| C4: structured effective prompt | should-fix | Requirement 15 に output_format / postconditions / preconditions_checked / on_completion の検査を追加 | 整合 |
| C5: cross-feature impact | should-fix | Requirement 16 に review-wave での consumer / derivative impact check を追加 | 整合 |
| C6: D-003 canonical anchor | should-fix | Requirement 16 で現在の stable anchor を維持し、移動時の明示を要求 | 整合 |
| C7: `spec.json.reopened` と R-0 scope | should-fix | Requirement 16 に履歴フラグと現在 active reopen scope の区別を追加 | 整合 |
| C8 / C9 | leave-as-is | 単独修正なし | 整合 |

詳細は `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-requirements-integrated-design-review-run/review-response.md` に記録済みである。

## review-wave 判定との整合

requirements review-wave では、workflow-management 以外の feature を consumer / derivative として impact review scope に含めたうえで、requirements 正本変更は不要と判定した。

- reopen scope: workflow-management のみ
- impact review scope: all features
- other features: `existing_sufficient`
- carry-forward unresolved: 0

この判定は Requirement 16 受入 12 と整合する。すなわち、operation contract、構造化有効プロンプト、状態スナップショット、proxy_model triage decision の機械処理化は他 feature が参照し得るが、requirements 正本の所有と再実施対象は workflow-management である。

## workflow_state / reopen 記録との整合

`spec.json` の現在状態は次の通りである。

- requirements: drafting / triad-review / review-wave は完了、alignment / approval は未完了
- design / tasks / implementation: 全段未完了
- `recheck.upstream_change_pending`: true
- `recheck.impacted_downstream_phases`: design, tasks, implementation
- `reopened`: 履歴フラグとして true を保持

`stages/in-progress/reopen-procedure-2026-06-19.yaml` は、requirements triad-review と review-wave を `completed_gates` に記録し、次 gate を `stages/requirements.yaml#alignment` としている。

この状態は Requirement 16 受入 11 の「現在の active reopen scope と履歴フラグを同一視しない」方針と整合する。`reopened` は履歴として保持し、現在の再実施範囲は in-progress reopen record、`spec.json.recheck`、`pending_gates` / `completed_gates`、downstream impact decisions で管理する。

## 下流 recheck 状態との整合

requirements で追加・補強した内容は、design / tasks / implementation へ順に展開する必要がある。

- **design**: operation contract registry、複合 operation 表現、approval gate record、side-track stack、workflow-state snapshot、structured effective prompt、proxy decision mechanization、Phase 0〜6 の設計が必要。
- **tasks**: Phase 0〜6 と proxy decision mechanization を TDD 可能なタスクへ分解する必要がある。
- **implementation**: 既存挙動を壊さない順序で、schema / read-only registry / preflight / structured prompt / blocking / LLM judge audit を実装する必要がある。

したがって、`recheck.impacted_downstream_phases` が design / tasks / implementation を保持していることは妥当である。

## 判定

- **decision: existing_sufficient**
- intent、requirements、triad-review 対処、review-wave 判定、workflow_state / reopen 記録は整合している。
- requirements 内の追加修正は不要。
- design / tasks / implementation への連鎖再実施は `recheck.impacted_downstream_phases` と pending gates で追跡中であり、requirements alignment 時点では維持する。
