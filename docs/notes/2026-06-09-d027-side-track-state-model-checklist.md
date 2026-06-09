---
date: 2026-06-09
candidate_id: D-027
title: side track state model checklist
status: ready
source: docs/notes/2026-06-05-future-development-candidates.md
last_updated: 2026-06-09
---

# D-027 Side Track State Model Checklist

## 0. 位置づけ

このチェックリストは、D-027 `side track / BTW Track state model` を進めるための作業台帳である。

D-027 の目的は、post-write verification、sandbox 試行、maintenance などの例外作業を、通常 workflow へ復帰可能な状態として機械判定・可視化できるようにすることである。D-026 Navigator WebUI の前提として、UI ではなく Core 側 snapshot の contract を先に固定する。

## 1. 作業前確認

- [x] `tools/check-workflow-action.py next --json` が `kind: completed` を返すことを確認した。
- [x] D-027 本文を確認した。
- [x] `docs/notes/2026-06-05-workflow-navigator-webui-plan.md` の Side Track / Git Tree 節を確認した。
- [x] 既存 post-write verification と maintenance side track の記述を確認した。

## 2. Side Track Contract

side track state は次の field を最小契約として持つ。

| Field | Required | Purpose |
| --- | --- | --- |
| `active_track` | yes | side track の安定 ID。 |
| `track_kind` | yes | `main_track` / `side_track` / `inner_workflow`。 |
| `reason` | yes | side track が発生した理由。 |
| `target_files` | yes | side track が扱う relative path 群。 |
| `manifest_status` | yes | post-write / audit などの coverage 状態。 |
| `policy_violations` | yes | 禁止変更や逸脱の詳細。空配列可。 |
| `return_to` | yes | 通常 workflow へ戻る outer / inner node。 |
| `required_action` | yes | 復帰に必要な次 action。 |

## 3. 実装チェックリスト

- [x] red test を追加し、schema 未実装で失敗することを確認した。
- [x] `learning/workflow/schemas/side-track-state.schema.json` を追加した。
- [x] schema の meta-schema 検証テストを追加した。
- [x] required field 契約テストを追加した。
- [x] post-write side track payload の受理テストを追加した。
- [x] absolute target path を拒否するテストを追加した。
- [x] `return_to.outer_node` を必須にするテストを追加した。
- [x] policy violation details を許容するテストを追加した。
- [x] post-write verification を実施する。

## 4. Scope Boundary

今回の D-027 では、`tools/check-workflow-action.py next --json` の出力に `active_track` を追加する変更は行わない。

理由:

- 既存 `next --json` はすでに `post_write_verification`、`post_write_policy_violation`、`maintenance_in_progress` を機械判定できる。
- 今回は D-026 / D-008 が参照できる side track state contract を先に固定する。
- `next --json` への統合は、D-026 Navigator snapshot export または D-008 event ledger 実装時に行う。

## 5. Status Snapshot

- `next --json`: `completed`
- current task: D-027 side track state model schema implemented
- next task: D-008 dogfooding event ledger
- last status refresh: 2026-06-09, after post-write verification r1 should-fix reflection
