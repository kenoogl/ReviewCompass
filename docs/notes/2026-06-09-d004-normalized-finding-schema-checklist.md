---
date: 2026-06-09
candidate_id: D-004
title: normalized finding schema checklist
status: ready
source: docs/notes/2026-06-05-future-development-candidates.md
last_updated: 2026-06-09
---

# D-004 Normalized Finding Schema Checklist

## 0. 位置づけ

このチェックリストは、D-004 `normalized finding schema` を進めるための作業台帳である。

D-004 の目的は、Markdown review と API review-run の findings を同じ分析軸で比較できるようにすることである。通常 workflow の未完了処理ではなく、completed 後の追加改善として扱う。

## 1. 作業前確認

- [x] `tools/check-workflow-action.py next --json` が `kind: completed` を返すことを確認した。
- [x] 作業ツリーが clean であることを確認した。
- [x] D-004 本文を確認した。
- [x] 既存 `learning/workflow/schemas/` の schema を確認した。
- [x] 代表 `triage.yaml` を確認した。

## 2. Schema Comparison Table

| Field | D-004 normalized finding | Existing overlap | Decision |
| --- | --- | --- | --- |
| `finding_id` | required string, 横断分析内で一意 | `triage.yaml.items[].finding_id`, `runtime/schemas/finding.schema.json` | 既存 ID を保持し、正規化データ側では一意性の管理単位として扱う。 |
| `run_id` | required string | `triage.yaml.run_id`, `items[].run_id` | review-run 由来を復元するため required。 |
| `source_model` | required string | `triage.yaml.items[].source_model` | 既存 triage field を継承する。 |
| `review_role` | required enum | `source_role` がある review-run とない review-run が混在 | `primary/adversarial/judgment/integration/post_write/unknown` に正規化する。 |
| `inspection_criterion` | required string | `rounds.yaml` / run 名 / review target に分散 | D-004 固有 field として残す。 |
| `severity` | required enum | `severity_normalized`, foundation `finding.severity` | foundation の `CRITICAL/ERROR/WARN/INFO` を採用する。 |
| `initial_recommendation` | required enum | raw/parsed finding の recommendation 相当、ない場合あり | 初期推薦と最終判断を分けるため D-004 固有 field として残す。 |
| `final_label` | required enum | `triage.yaml.items[].final_label`, foundation `necessity_judgment.final_label` | `must-fix/should-fix/leave-as-is` を採用する。 |
| `decision_status` | required enum | `triage.yaml.items[].decision_status` | `pending/human_required/decided/superseded` に正規化する。 |
| `decision_actor` | required object | `decision_actor`, `decision_actor_type` | `actor_type` と `actor_id` を分け、human/proxy_model/agent/unknown を許容する。 |
| `observed_at` | required RFC3339 timestamp | run generated time, raw file time, parsed time に分散 | finding 観測時刻として required。取得不能な場合は変換処理側で run 時刻を使う。 |
| `decided_at` | optional RFC3339/null | `decision_at` | 決定済みの場合に保持する。 |
| `resolved_at` | optional RFC3339/null | 既存 triage には不足 | D-005 / D-025 と接続するため保持する。 |
| `evidence_refs` | required object array | carry-forward register の `evidence_refs`, triage raw/parsed paths | label/path を必須にし、文字列配列を禁止する。 |
| `affected_files` | required relative path array | `applied_files`, `target_location` | 修正対象と影響範囲を比較するため required。 |
| `resolution` | required object | carry-forward register の `resolution`, triage の `applied_files` | `status` と `summary` を分けて D-005 に渡す。 |
| `resolution_commit` | optional commit hash/null | commit 証跡に分散 | D-005 で機械連携するまで optional。 |
| `linked` | optional object | raw/parsed/triage/approval/test refs に分散 | 参照解決先を集約する任意 object。 |
| `false_positive_reversal` | required object | 既存 triage には明示 field なし | false positive の後日反転を分析するため D-004 固有 field として required。 |

## 3. 既存 Schema との責務境界

| Existing schema / artifact | Role | D-004 boundary |
| --- | --- | --- |
| `proposal.schema.json` | discipline 改善 proposal の保存形式 | finding 判定結果そのものは扱わない。D-004 は proposal の根拠に渡せる finding 単位を定義する。 |
| `metrics.schema.json` | workflow metrics 集計値の保存形式 | D-004 は metrics の入力データ。集計済み数値は扱わない。 |
| `carry-forward-register.schema.json` | unresolved / deferred item の持ち越し台帳 | `evidence_refs` と `resolution` の考え方は近いが、D-004 は review-run finding の正規化が責務。 |
| `rollback.schema.json` | proposal rollback 記録 | D-004 の `resolution` は finding 解消状態であり、discipline rollback 操作は扱わない。 |
| `triage.yaml` | review-run ごとの判定記録 | D-004 は複数形式の triage / Markdown finding を横断分析用 payload に変換した後の schema。 |

## 4. 実装チェックリスト

- [x] red test を追加し、schema 未実装で失敗することを確認する。
- [x] `learning/workflow/schemas/normalized-finding.schema.json` を追加する。
- [x] schema の meta-schema 検証テストを追加する。
- [x] required field 契約テストを追加する。
- [x] enum 契約テストを追加する。
- [x] RFC3339 timestamp 契約テストを追加する。
- [x] structured `evidence_refs` 契約テストを追加する。
- [x] post-write verification を実施する。
- [x] commit 前に `next --json` と `git status --short` を確認する。

## 5. Status Snapshot

- `next --json`: `completed`
- worktree: clean at task start
- current task: D-004 normalized finding schema implemented; post-write verification completed
- next task: D-005 finding-to-fix traceability
- last status refresh: 2026-06-09, after post-write verification manifest generation
