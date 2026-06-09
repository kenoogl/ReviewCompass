---
date: 2026-06-09
candidate_id: D-025
title: TDD cycle evidence checklist
status: ready
source: docs/notes/2026-06-05-future-development-candidates.md
last_updated: 2026-06-09
---

# D-025 TDD Cycle Evidence Checklist

## 0. 位置づけ

このチェックリストは、D-025 `TDD cycle evidence` を進めるための作業台帳である。

D-025 の目的は、レビュー指摘が failing test に変換され、implementation で green になったことを論文用データとして追跡できるようにすることである。D-004 の normalized finding、D-005 の finding-to-fix traceability、後続 D-008 の dogfooding event ledger と接続する。

## 1. 作業前確認

- [x] `tools/check-workflow-action.py next --json` が `kind: completed` を返すことを確認した。
- [x] D-025 本文を確認した。
- [x] `learning/workflow/schemas/` の既存 schema 配置方針を確認した。
- [x] D-004 / D-005 の schema / report contract との接続を確認した。

## 2. TDD Cycle Contract

`tdd_cycle` event は、次の情報を最小契約として持つ。

| Field | Required | Purpose |
| --- | --- | --- |
| `event_type` | yes | `tdd_cycle` 固定。 |
| `cycle_id` | yes | TDD cycle の安定 ID。 |
| `linked_finding_ids` | yes | review finding との join key。1 件以上。 |
| `test_first_commit` | yes | red test を追加した commit。未コミット作業中は `null` を許容する。 |
| `implementation_commit` | yes | green にした implementation commit。未コミット作業中は `null` を許容する。 |
| `failing_test_command` | yes | red を確認した command。 |
| `failing_test_result` | yes | `status: failed`、`exit_code >= 1`。 |
| `green_test_command` | yes | green を確認した command。 |
| `green_test_result` | yes | `status: passed`、`exit_code: 0`。 |
| `changed_files` | yes | TDD cycle で変更した実装 / テスト file。 |

## 3. 接続先

| Neighbor | Link |
| --- | --- |
| D-004 normalized finding | `linked_finding_ids` が normalized finding の `finding_id` と対応する。 |
| D-005 finding-to-fix traceability | `linked_finding_ids`、`changed_files`、commit field が matrix の入力になる。 |
| D-008 dogfooding event ledger | `event_type: tdd_cycle` を event ledger の event type として取り込む。 |
| D-019 cost / time / model assignment | command 実行と cycle 単位の所要時間・コスト記録に接続する。 |

## 4. 実装チェックリスト

- [x] red test を追加し、schema 未実装で失敗することを確認した。
- [x] `learning/workflow/schemas/tdd-cycle.schema.json` を追加した。
- [x] schema の meta-schema 検証テストを追加した。
- [x] required field 契約テストを追加した。
- [x] red-to-green payload の受理テストを追加した。
- [x] red result が `failed` 以外なら拒否するテストを追加した。
- [x] green result が `passed` / `exit_code: 0` 以外なら拒否するテストを追加した。
- [x] `linked_finding_ids` が空なら拒否するテストを追加した。
- [x] post-write verification を実施する。

## 5. Scope Boundary

今回の D-025 では、既存 commit 履歴から TDD cycle event を自動抽出する処理は追加しない。

理由:

- 既存履歴には red test 実行結果、green test 実行結果、finding id の対応が一貫形式で保存されていない。
- D-025 の最初の安定化対象は、後続 D-008 が取り込める event schema の正本化である。
- 抽出器と集計指標は D-008 / D-019 で扱う。

## 6. Status Snapshot

- `next --json`: `completed`
- current task: D-025 TDD cycle evidence schema implemented
- next task: D-027 side track state model
- last status refresh: 2026-06-09, after post-write verification r1 no findings
