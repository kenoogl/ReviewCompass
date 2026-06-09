---
date: 2026-06-09
candidate_id: D-005
title: finding-to-fix traceability checklist
status: ready
source: docs/notes/2026-06-05-future-development-candidates.md
last_updated: 2026-06-09
---

# D-005 Finding-to-Fix Traceability Checklist

## 0. 位置づけ

このチェックリストは、D-005 `finding-to-fix traceability` を進めるための作業台帳である。

D-005 の目的は、accepted finding がどのテスト、どの変更ファイル、どの commit で解消されたかを追跡できるようにすることである。D-004 の `normalized-finding.schema.json` で定義した `resolution_commit`、`affected_files`、`linked.test_refs` と接続し、review-run report 生成時に finding-to-fix matrix を出す。

## 1. 作業前確認

- [x] `tools/check-workflow-action.py next --json` が `kind: completed` を返すことを確認した。
- [x] D-004 の未コミット変更を保持したまま、D-005 を連続作業として扱う方針を確認した。
- [x] D-005 本文を確認した。
- [x] `tools/api_providers/review_triage.py` の report / ledger 生成経路を確認した。
- [x] `tools/api_providers/tests/test_review_triage.py` の既存 report tests を確認した。

## 2. Trace Contract

accepted finding は、次の条件を満たす triage item と定義する。

- `decision_status: decided`
- `final_label: must-fix` または `final_label: should-fix`
- `finding_id` が空でない

accepted finding がある review-run report では、ledger に `finding_fix_traceability` を要求する。

`finding_fix_traceability[]` の最小 field:

| Field | Required | Purpose |
| --- | --- | --- |
| `finding_id` | yes | triage item との join key。 |
| `resolution_commit` | yes | finding が解消された commit。 |
| `changed_files` | yes | finding 対応で変更されたファイル。 |
| `test_refs` | yes | finding 対応を検証するテスト。 |

D-004 schema との対応:

| D-005 field | D-004 normalized finding field |
| --- | --- |
| `finding_id` | `finding_id` |
| `resolution_commit` | `resolution_commit` |
| `changed_files` | `affected_files` |
| `test_refs` | `linked.test_refs` |

## 3. 実装チェックリスト

- [x] accepted finding に fix trace がない場合、`assert-review-report-ready` が fail-closed する red test を追加した。
- [x] `generate-review-report` が Finding-to-Fix Matrix を出す red test を追加した。
- [x] `assert_review_report_ready` に `finding_fix_traceability` 検査を追加した。
- [x] `build_review_traceability_report` に `## Finding-to-Fix Matrix` を追加した。
- [x] D-005 追加テストを green にした。
- [x] `tools/api_providers/tests/test_review_triage.py` 全体を green にした。
- [x] post-write verification を実施する。
- [ ] commit 前に `next --json` と `git status --short` を確認する。

## 4. Scope Boundary

今回の D-005 では、既存 `triage.yaml` の全 item へ `resolution_commit`、`test_refs`、`changed_files` を直接書き戻す migration は行わない。

理由:

- 既存 review-run には適用済みファイル、commit、テスト証跡が分散しており、一括 migration は推測を含む。
- D-004 で横断分析用 schema を置いたため、D-005 の最初の機械化は report / ledger の join contract として成立する。
- 後続 D-025 で TDD cycle evidence を正本化すると、`test_refs` と red-to-green evidence をより精密に接続できる。

## 5. Status Snapshot

- `next --json`: `completed`
- worktree: D-004 changes pending at D-005 start
- current task: D-005 finding-to-fix traceability implemented
- next task: D-025 TDD cycle evidence
- last status refresh: 2026-06-09, after post-write verification r1 no findings
