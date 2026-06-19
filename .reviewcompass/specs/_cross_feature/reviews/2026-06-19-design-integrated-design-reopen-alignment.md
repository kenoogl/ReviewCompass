---
date: 2026-06-19
gate: stages/design.yaml#alignment
feature: workflow-management
reopen: R-0
reopen_topic: integrated-design-design
decision: existing_sufficient
---

# design alignment：統合設計メモ反映

reopen R-0（`docs/reviews/reopen-classification-2026-06-19-wm-integrated-design-requirements.md`）の第3過程、workflow-management design フェーズの alignment 段。

本段では、requirements Requirement 13〜16、workflow-management design、design triad-review 対処、design review-wave 判定、`spec.json` / reopen 進行中記録の整合を確認する。

## requirements Requirement 13〜16 との整合

| requirements | design での受け皿 | 整合判定 |
| --- | --- | --- |
| Requirement 13：operation contract 語彙と `required_action` 対応 | §Requirement 13 設計モデルで、schema 配置、operation contract schema、`required_action` と gate 種別の対応、preconditions / postconditions を設計化している。 | 整合 |
| Requirement 14：承認ゲート、側道スタック、状態スナップショット | §Requirement 14 設計モデルで、decision record、side-track stack frame、push / pop、`staged_file_set` / digest、workflow-state snapshot を設計化している。 | 整合 |
| Requirement 15：構造化有効プロンプトと監査 | §Requirement 15 設計モデルで、structured effective prompt schema、第1層機械検査、Phase 6 LLM judge audit を設計化している。 | 整合 |
| Requirement 16：段階的実装計画 Phase 0〜6 | §Requirement 16 設計モデルで、Phase 0〜6、D-003 anchor、Phase 1 schema 前提、review-wave scope、proxy_model triage decision 機械処理化を設計化している。 | 整合 |

Design traceability table には Requirements 13〜16 の受入項目が追跡されており、XDI-WM-005 でも選択層／実行層接続、operation contract、structured effective prompt、side-track stack、workflow-state snapshot、Phase 0〜6 が設計境界として記録されている。

## design triad-review 対処との整合

design triad-review では、C1 を `leave-as-is`、C2/C3 を `should-fix` と判断し、利用者発言「承認」に基づき確定した。

| cluster | final label | design 反映 | 整合判定 |
| --- | --- | --- | --- |
| C1: `classification: R-0` の意味 | leave-as-is | `classification: R-0` は requirements reopen の由来分類であり、現在 active design gate は `next_step`、`pending_gates`、`completed_gates` で別管理するため、本文修正なし。 | 整合 |
| C2: Completion Criteria が旧最小条件のまま | should-fix | Completion Criteria を Requirement 13〜16 の operation surface を含む形へ更新した。 | 整合 |
| C3: `tools/check-workflow-action.py` が3コマンドだけに見える | should-fix | Completion Criteria item 2 を workflow / reopen selector と gate entrypoint の表現へ更新し、item 10 を追加した。 | 整合 |

詳細は `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-design-integrated-design-review-run/review-response.md` に記録済みである。

## design review-wave 判定との整合

design review-wave では、workflow-management 以外の feature を consumer / derivative として impact review scope に含めたうえで、design 正本変更は不要と判定した。

- reopen scope: workflow-management のみ
- impact review scope: all features
- other features: `existing_sufficient`
- carry-forward unresolved: 0

この判定は Requirement 16 受入 12、および design §Requirement 16 設計モデルの review-wave scope と整合する。operation contract、structured effective prompt、workflow-state snapshot、proxy_model triage decision の機械処理化は他 feature が参照し得るが、正本設計変更の所有者は workflow-management である。

## workflow_state / reopen 記録との整合

`spec.json` の現在状態は次の通りである。

- requirements: drafting / triad-review / review-wave / alignment / approval は完了
- design: drafting / triad-review / review-wave / alignment / approval は `false`
- tasks / implementation: 全段 `false`
- `recheck.upstream_change_pending`: true
- `recheck.impacted_downstream_phases`: design, tasks, implementation
- `reopened`: 履歴フラグとして true を保持

`stages/in-progress/reopen-procedure-2026-06-19.yaml` は、design drafting / triad-review / review-wave の完了を進行中記録として保持している。design alignment 完了後も、利用者承認を要する design approval が残るため、`spec.json` の design flags はまだ変更しない。

この状態は、現在の active reopen scope と履歴フラグを同一視しない方針、および phase approval 前に `spec.json` を先行更新しない方針と整合する。

## 下流 recheck 状態との整合

design で追加・補強した内容は、tasks / implementation へ順に展開する必要がある。

- **tasks**: Phase 0〜6、operation contract schema、preflight、structured prompt、side-track stack、workflow-state snapshot、proxy_model triage decision 機械処理化を TDD 可能なタスクへ分解する必要がある。
- **implementation**: 既存挙動を壊さない順序で、schema / read-only registry / advisory preflight / structured prompt / mechanical blocking / LLM judge audit を実装する必要がある。

したがって、`recheck.impacted_downstream_phases` が design / tasks / implementation を保持していることは妥当である。design approval 完了後に、tasks 以降の gate へ進む。

## 判定

- **decision: existing_sufficient**
- requirements Requirement 13〜16、design、triad-review 対処、review-wave 判定、workflow_state / reopen 記録は整合している。
- design 内の追加修正は不要。
- tasks / implementation への連鎖再実施は `recheck.impacted_downstream_phases` と pending gates で追跡中であり、design alignment 時点では維持する。
