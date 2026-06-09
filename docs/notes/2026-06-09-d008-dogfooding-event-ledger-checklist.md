---
date: 2026-06-09
candidate_id: D-008
title: dogfooding event ledger checklist
status: ready
source: docs/notes/2026-06-05-future-development-candidates.md
last_updated: 2026-06-09
---

# D-008 Dogfooding Event Ledger Checklist

## 0. 位置づけ

このチェックリストは、D-008 `dogfooding event ledger` を進めるための作業台帳である。

D-008 の目的は、ReviewCompass dogfooding 由来の review、triage、guard、post-write、TDD、side track event を、論文用データへ正規化できる ledger schema として固定することである。

## 1. 作業前確認

- [x] `tools/check-workflow-action.py next --json` が `kind: completed` を返すことを確認した。
- [x] D-008 本文を確認した。
- [x] `docs/notes/2026-06-03-dogfooding-deployment-metrics.md` を確認した。
- [x] 既存 `evaluation/metrics/dogfooding_metrics_extractor.py` が最小抽出器であることを確認した。
- [x] D-004 / D-005 / D-025 / D-027 の schema と接続する方針を確認した。

## 2. Event Ledger Contract

`dogfooding-event-ledger.schema.json` は次の root field を持つ。

| Field | Required | Purpose |
| --- | --- | --- |
| `ledger_id` | yes | ledger の安定 ID。 |
| `schema_version` | yes | schema version。 |
| `project_id` | yes | 対象 project。 |
| `events` | yes | event 配列。 |

event item の最小 field:

| Field | Required | Purpose |
| --- | --- | --- |
| `event_id` | yes | event の安定 ID。 |
| `event_type` | yes | event type enum。 |
| `occurred_at` | yes | RFC3339 timestamp。 |
| `source_ref` | yes | relative path の証跡参照。 |
| `payload` | yes | event type ごとの詳細 payload。 |

event type:

- `review_run`
- `triage_decision`
- `proxy_decision`
- `workflow_precheck`
- `post_write_verification`
- `reopen`
- `commit_guard`
- `push_guard`
- `finding_fix_traceability`
- `tdd_cycle`
- `side_track_state`
- `model_assignment_cost`

## 3. 実装チェックリスト

- [x] red test を追加し、schema 未実装で失敗することを確認した。
- [x] `learning/workflow/schemas/dogfooding-event-ledger.schema.json` を追加した。
- [x] schema の meta-schema 検証テストを追加した。
- [x] event type enum 契約テストを追加した。
- [x] 複数 event type payload の受理テストを追加した。
- [x] unknown event type を拒否するテストを追加した。
- [x] absolute `source_ref` を拒否するテストを追加した。
- [x] post-write verification を実施する。

## 4. Scope Boundary

今回の D-008 では、既存 operational record から ledger を自動生成する extractor は追加しない。

理由:

- 既存 `DogfoodingMetricsExtractor` は最小抽出器として残し、D-008 では event ledger の保存 contract を先に固定する。
- 自動生成は D-019 の時間・コスト・モデル割当、D-020 の cross-repository replication と合わせて実装する方が、field の二重設計を避けられる。

## 5. Status Snapshot

- `next --json`: `completed`
- current task: D-008 dogfooding event ledger schema implemented, D-019 event type linked
- next task: D-020 cross-repository replication pilot
- last status refresh: 2026-06-09, after D-019 model assignment cost schema implementation
