---
date: 2026-06-16
gate: stages/tasks.yaml#alignment
feature: workflow-management
reopen: R-0
reopen_topic: operation-registry-preflight-unified-design
decision: existing_sufficient
---

# tasks alignment（整合確認）：operation registry / preflight

reopen R-0 の第3過程、workflow-management tasks フェーズの alignment。Requirement 12 r2、design、tasks triad-review 対処、tasks review-wave 判定、下流 implementation recheck 状態との整合を確認する。

## Requirement 12 r2 との整合

| 要件観点 | tasks での扱い | 整合判定 |
| --- | --- | --- |
| operation registry | T-014 の成果物に `stages/operation-registry.yaml` と registry loader / schema 検査を置いた。 | 整合。 |
| read-only preflight | T-014 の責務と完了条件で Phase 1 を read-only preflight に限定し、runner は Phase 2 として分離した。 | 整合。 |
| common response / verdict | T-014 完了条件とテスト要件に response JSON、`allowed_verdicts`、DEVIATION hard-stop を置いた。 | 整合。 |
| command validation | parser / parser adapter と canonical invocation の照合を完了条件・テスト要件に置いた。 | 整合。 |
| worktree / integrity conflict | worktree conflict と integrity conflict の分離を完了条件・テスト要件に置いた。 | 整合。 |
| review artifact preflight | target / manifest / bundle / criteria / document-type / approval / existing artifact drift / staged-vs-unstaged selection を operation_family 必須 check として明示した。 | 整合。 |
| serial_only approval chain | commit approval chain の順序、nonce、digest、expiry、consume、invalidated、target 検査を完了条件・テスト要件に置いた。 | 整合。 |
| current-session formal record guard | current / target session id と formal output 禁止を完了条件・テスト要件に置いた。 | 整合。 |
| nested issue handling | parent / discovered issue / relation / allowed files / return condition / nesting depth を完了条件・テスト要件に置いた。 | 整合。 |
| deployment / export | 明示入力で与えられた output / external root / target app root だけを read-only に観測する境界を追記した。 | 整合。 |
| scope separation | reopen_scope / impact_review_scope と `next --json` 整合を完了条件に置いた。 | 整合。 |
| LLM 非依存 | LLM / provider / model 系 field 非依存・禁止 field 検査を完了条件・テスト要件に置いた。 | 整合。 |
| next state uniqueness | Requirement 2 所有の `next --json` を参照・照合する側として T-014 に落とし、必須 state dimensions 固定検証を独立テストにした。 | 整合。 |

## design との整合

- design は Requirement 12 を read-only Phase 1 と runner-enabled Phase 2 に分けている。T-014 は Phase 1 のみを扱い、artifact 作成・更新を行わない。
- design の operation contract schema に含まれる `vocabulary_refs` は、T-014 の成果物・完了条件・テスト要件へ反映済み。
- design の operation_family / family_required_checks は、T-014 の初期必須 check として review_artifact、workflow_cli、commit_approval_chain、session_record_capture、deployment_export、nested_issue_control に分けた。
- design の `state_refs.next_action` は、T-014 の `test_operation_preflight_next_state.py` と必須キー固定検証へ落とした。

## triad-review 対処との整合

tasks triad-review は ERROR 2 / WARN 5 / INFO 4 であり、利用者承認済み triage により ERROR 2 件を must-fix、WARN 5 件と `vocabulary_refs` INFO 1 件を should-fix として反映した。

- Req 12 受入 13：T-014 に Requirement 2 所有境界と `next --json` 必須 state dimensions 固定検証を追記した。
- 完了条件 / テスト要件対応：テスト要件を拡張し、state dimensions 固定検証、Req2 所有の `next` 参照、不整合検出を分離した。
- テスト粒度：preflight テストを response / next_state / review_artifacts / approval_chain / session_record / nested_issue / deployment_export に分けた。
- operation_family 割当：初期必須 check を family ごとに明示した。
- deployment / export 外部境界：明示された output / root に限定し、未指定外部探索をしない方針を追記した。
- T-011 境界：T-011 は T-014 の前提ではなく、後段の統合・回帰検証タスクと明記した。

leave-as-is とした INFO は、Phase 1 / Phase 2 分離、LLM 非依存、要件追跡を肯定する所見であり、追加修正は不要と判断した。

## review-wave 判定との整合

`2026-06-16-tasks-operation-registry-preflight-review-wave.md` は no_impact と判定し、他 6 機能への tasks 正本修正不要とした。

T-014 は workflow-management の実装タスクであり、他 feature の tasks 所有権を変更しない。したがって review-wave 判定と整合する。

## 下流 recheck 状態との整合

workflow-management の tasks triad-review / review-wave は完了し、tasks approval は未完了である。implementation は未完了で、Requirement 12 の tasks を受けて TDD 実装へ進む必要がある。

次段の tasks approval は人間承認 gate であり、承認後に implementation フェーズへ進む。

## 判定

- **decision：existing_sufficient**。
- tasks は Requirement 12 r2、design、triad-review 対処、review-wave 判定と整合する。
- 他 feature の tasks 正本を再オープンする必要はない。
- implementation への recheck は維持する。
