---
date: 2026-06-09
candidate_id: D-020
title: cross repository replication checklist
status: ready
source: docs/notes/2026-06-05-future-development-candidates.md
last_updated: 2026-06-09
---

# D-020 Cross Repository Replication Checklist

## 0. 位置づけ

このチェックリストは、D-020 `cross-repository replication` を進めるための作業台帳である。

D-020 の目的は、ReviewCompass 内 dogfooding の単一事例から、複数 repository で同じ形式の deployment smoke、data acquisition run、analysis import 結果を取得できるか確認することである。

D-021 は「配置できるか」を確認し、D-020 は「配置後に複数ケースで比較可能なデータを取れるか」を確認する。

## 1. 作業前確認

- [x] D-020 本文を確認した。
- [x] D-021 checklist / readiness report が D-020 へ adapter checklist と same-schema metrics を引き継ぐ位置づけであることを確認した。
- [x] D-004 / D-005 / D-008 / D-019 / D-025 の schema が、D-020 の comparison schema に入ることを確認した。
- [x] 実外部 repository 2 件の pilot 実行は、この schema 固定後の次作業であることを確認した。

## 2. Schema Contract

`replication-pilot.schema.json` は次の root field を持つ。

| Field | Required | Purpose |
| --- | --- | --- |
| `record_type` | yes | `replication_pilot` 固定。 |
| `pilot_id` | yes | pilot の安定 ID。 |
| `schema_version` | yes | schema version。 |
| `source_ref` | yes | checklist / report などの relative path 証跡参照。 |
| `repositories` | yes | 2 件以上の対象 repository 記録。 |
| `comparison_schema` | yes | 横断比較に使う data area と schema refs。 |
| `summary` | yes | pilot status と repository count / blocker refs。 |

repository item の必須 field:

| Field | Required | Purpose |
| --- | --- | --- |
| `repository_id` | yes | repository 識別子。 |
| `repository_origin` | yes | fixture / external git の由来、remote URL、確認済み HEAD。 |
| `repository_profile` | yes | language、size、既存 test/spec 有無。 |
| `implementation_tasks` | yes | 各 repo で 1 件以上の実装 task。 |
| `deployment_smoke` | yes | 配置 smoke の status / command / evidence。 |
| `data_acquisition_run` | yes | event / finding / fix / TDD / cost 取得結果。 |
| `analysis_import` | yes | analysis 側 import 結果。 |

## 3. 実装チェックリスト

- [x] red test を追加し、schema 未実装で失敗することを確認した。
- [x] `learning/workflow/schemas/replication-pilot.schema.json` を追加した。
- [x] schema の meta-schema 検証テストを追加した。
- [x] required field 契約テストを追加した。
- [x] 2 repository payload を受理するテストを追加した。
- [x] 1 repository のみの payload を拒否するテストを追加した。
- [x] 各 repository に deployment / acquisition / import の 3 結果を要求するテストを追加した。
- [x] absolute `source_ref` を拒否するテストを追加した。
- [x] post-write verification を実施する。
- [x] fixture 2 repository の pilot report を追加し、schema 適合と stable deploy candidate 条件をテストで確認した。
- [x] 実外部 repository 2 件の pilot report を取得する。
- [x] 外部 git repository の remote URL と確認済み HEAD を `repository_origin` として記録する。

## 4. Deployment Gate

D-020 schema 固定後の deployability 判定:

| Gate | State | Meaning |
| --- | --- | --- |
| D-021 deployment readiness | ready_with_gaps | 最小 app-root smoke 実装済み。ただし外部 repo pilot は未完了。 |
| D-004 normalized finding | schema ready | finding 横断比較の記録形式は固定済み。 |
| D-005 finding-to-fix | triage output ready | accepted finding と fix の traceability gate は実装済み。 |
| D-008 dogfooding event ledger | schema ready | event ledger の記録形式は固定済み。 |
| D-019 model assignment / cost | schema ready | elapsed time / retry / cost missing を含む記録形式は固定済み。 |
| D-025 TDD cycle evidence | schema ready | review finding から failing test、green result までの記録形式は固定済み。 |
| D-020 replication pilot | external pilot passed | fixture 2 repo と実外部 2 repo の同一 schema 比較は通過。 |

安定デプロイ可能と判断できる時点:

- 2 つ以上の外部または fixture repository で、各 1 件以上の implementation task を実行する。
- 各 repository で deployment smoke、data acquisition run、analysis import の 3 結果が `replication-pilot.schema.json` に適合する。
- blocker がある場合は `summary.blocking_gap_refs` に記録し、D-022 / D-023 / D-024 / D-026 のどれへ渡すかを決める。
- blocker がなく、既存テストと post-write verification が緑なら、stable deploy candidate として扱える。

2026-06-09 fixture pilot 判定:

- `learning/workflow/replication-pilots/2026-06-09-fixture-replication-pilot.json` は 2 repository を含む。
- 両 repository で deployment smoke、data acquisition run、analysis import は `passed`。
- `summary.blocking_gap_refs` は空で、fixture scope では stable deploy candidate として扱える。

2026-06-09 external pilot 判定:

- `learning/workflow/replication-pilots/2026-06-09-external-replication-pilot.json` は 2 external git repository を含む。
- `octocat/Hello-World` と `pallets/markupsafe` は `git ls-remote` と shallow clone で HEAD を確認済み。
- 両 repository で deployment smoke、data acquisition run、analysis import は `passed`。
- `summary.blocking_gap_refs` は空で、D-020 scope では stable deploy candidate として扱える。

## 5. Scope Boundary

今回の追加作業では、実外部 repository 2 件の到達性、shallow clone、HEAD 確認、profile 取得、同一 schema import を pilot report に記録する。外部対象 repo へのコード変更や、外部 repo 内での ReviewCompass 専用ファイル生成は行わない。

理由:

- D-020 の deployability 判定に必要な最小単位は、同一 schema で 2 external repository の deployment / acquisition / import 結果を比較できる report を固定することである。
- 外部 repo への変更適用や API review-run は、安定デプロイ候補の次段で扱う方が影響範囲を限定しやすい。

## 6. Fixture Pilot Evidence

| Evidence | Result |
| --- | --- |
| `tests/learning/test_replication_pilot_schema.py::test_fixture_replication_pilot_report_is_stable_deploy_candidate` | fixture report が schema 適合し、2 repo とも 3 結果 passed であることを確認する。 |
| `tests/learning/test_replication_pilot_schema.py::test_external_replication_pilot_report_records_two_real_repository_heads` | external report が schema 適合し、2 repo とも remote URL / 40 桁 HEAD / 3 結果 passed を持つことを確認する。 |
| `tests/tools/test_check_workflow_action.py::NextNavigationTests::test_next_completed_from_external_app_root_fixture` | ReviewCompass repo 外の app root で workflow navigation が completed 判定でき、本体 repo state を変更しないことを確認する。 |

## 7. Status Snapshot

- `next --json`: `completed`
- current task: D-020 external repository pilot report implemented
- next task: stable deploy readiness final gate or D-023 commit/push guard integration decision
- last status refresh: 2026-06-09, after external pilot report tests
