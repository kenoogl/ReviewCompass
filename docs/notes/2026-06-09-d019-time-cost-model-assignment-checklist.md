---
date: 2026-06-09
candidate_id: D-019
title: time cost model assignment checklist
status: ready
source: docs/notes/2026-06-05-future-development-candidates.md
last_updated: 2026-06-09
---

# D-019 Time Cost Model Assignment Checklist

## 0. 位置づけ

このチェックリストは、D-019 `時間・コスト・モデル割当の記録` を進めるための作業台帳である。

D-019 の目的は、review-run の elapsed time、token usage、API cost、retry count、role assignment、finding contribution を、同じ粒度で分析に取り込める schema として固定することである。

## 1. 作業前確認

- [x] D-019 本文を確認した。
- [x] `rounds.yaml` に `role` / `provider` / `model_id` / `attempts` / `duration_seconds` / `invocation_path` が既にあることを確認した。
- [x] token usage と API cost は既存 run では常に保存されていないため、欠落を `missing` として記録できる必要を確認した。
- [x] D-008 dogfooding event ledger へ `model_assignment_cost` event type を接続する方針を確認した。

## 2. Schema Contract

`model-assignment-cost.schema.json` は次の root field を持つ。

| Field | Required | Purpose |
| --- | --- | --- |
| `event_type` | yes | `model_assignment_cost` 固定。 |
| `run_id` | yes | review-run の安定 ID。 |
| `schema_version` | yes | schema version。 |
| `source_ref` | yes | `rounds.yaml` などの relative path 証跡参照。 |
| `role_assignments` | yes | role ごとの provider / model / 実行指標。 |
| `summary` | yes | run 全体の時間・retry・cost/token completeness。 |

role assignment item の最小 field:

| Field | Required | Purpose |
| --- | --- | --- |
| `role` | yes | primary / adversarial / judgment などの役割。 |
| `provider` | yes | 呼び出し provider。 |
| `model_id` | yes | provider 上の model id。 |
| `invocation_path` | yes | 実行 entrypoint の relative path。 |
| `attempts` | yes | 呼び出し試行回数。 |
| `retry_count` | yes | retry 回数。 |
| `duration_seconds` | yes | role 呼び出しの elapsed time。 |
| `token_usage` | yes | token usage と取得状態。 |
| `api_cost` | yes | API cost と取得状態。 |
| `contribution` | yes | findings reported / accepted / rejected。 |

## 3. 実装チェックリスト

- [x] red test を追加し、schema 未実装で失敗することを確認した。
- [x] `learning/workflow/schemas/model-assignment-cost.schema.json` を追加した。
- [x] schema の meta-schema 検証テストを追加した。
- [x] required field 契約テストを追加した。
- [x] recorded cost と missing cost の混在 payload を受理するテストを追加した。
- [x] `attempts=1` では `retry_count=0` のみ許容するテストを追加した。
- [x] absolute `source_ref` を拒否するテストを追加した。
- [x] D-008 ledger enum に `model_assignment_cost` を追加した。
- [x] post-write verification を実施する。

## 4. Scope Boundary

今回の D-019 では、既存 review-run から `model-assignment-cost` event を自動生成する extractor は追加しない。

理由:

- 既存 `rounds.yaml` から elapsed time / attempts / role assignment は復元できるが、token usage と API cost は provider ごとに未取得のケースがある。
- D-020 cross-repository replication pilot で、複数 repository の deployment smoke、data acquisition run、analysis import に同じ schema を適用できるか確認してから extractor を固定する方が、デプロイ先差分を取り込みやすい。

## 5. Deployability Impact

この対応により、安定デプロイ前の smoke は次を同じ形式で記録できる。

| Check | State |
| --- | --- |
| elapsed time | schema ready |
| retry count | schema ready |
| model assignment | schema ready |
| token usage | schema ready, missing allowed |
| API cost | schema ready, missing allowed |
| role contribution | schema ready |

D-020 で複数 repository に対して smoke / data acquisition / analysis import を実行できた時点で、外部展開に向けた deployability をより強く判定できる。

## 6. Status Snapshot

- `next --json`: `completed`
- current task: D-019 time / cost / model assignment schema implemented and post-write verified
- next task: D-020 cross-repository replication pilot
- last status refresh: 2026-06-09, after post-write verification r1
