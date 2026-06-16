---
review_target: workflow-management tasks reopen R-0 operation-registry-preflight
phase: tasks
feature: workflow-management
date: 2026-06-16
source_documents:
  - .reviewcompass/specs/workflow-management/requirements.md
  - .reviewcompass/specs/workflow-management/design.md
  - .reviewcompass/specs/workflow-management/tasks.md
  - stages/in-progress/reopen-procedure-2026-06-16.yaml
---

# Review Target：workflow-management tasks / operation registry preflight

## レビュー目的

workflow-management tasks.md に追加した T-014（operation registry / read-only preflight）が、Requirement 12 と design.md §Requirement 12 設計モデルを TDD 実装可能な粒度へ落とせているかを確認する。

特に次を確認する。

- Requirement 12 受入 1〜13 が tasks の成果物・完了条件・テスト要件へ追跡されているか。
- T-014 が read-only preflight（Phase 1）に閉じ、runner-enabled operation（Phase 2）と混ざっていないか。
- 既存 T-004 / T-006 / T-007 / T-008 / T-011 / T-012 / T-013 との責務境界が妥当か。
- review artifact / approval / bundle / command validation / current-session guard / nested issue / deployment export / next state uniqueness の手戻り原因が、TDD テスト要件へ落ちているか。
- LLM / provider / model 非依存がタスク上でも維持されているか。

## Requirements 抜粋：Requirement 12

```text
Requirement 12：operation registry / preflight

目的：保守担当者が、review-run、post-write verification、triage、reopen、commit approval、session-record、deployment / export などの操作を、記憶・前例・短縮名ではなく、機械可読な operation contract に基づいて開始できるようにする。操作開始前に、正本コマンド、入力、成果物、順序、pending 衝突、worktree 状態、上書き policy を read-only に検査し、作ってから直す手戻りを減らす。

主な受入：
1. operation registry と workflow binding。
2. 成果物を作らない read-only preflight。
3. 共通 response と OK / WARN / DEVIATION。
4. parser / parser adapter に基づく command validation。
5. worktree conflict と integrity conflict の分離。
6. review artifact / bundle / approval 作成前検査。
7. serial_only approval chain。
8. current-session formal record guard。
9. nested issue handling。
10. deployment / export preflight。
11. reopen_scope と impact_review_scope の分離。
12. LLM / provider / model 非依存。
13. Requirement 2 所有の next --json 状態一意性拡張。
```

## Design 抜粋：Req 12 設計要点

```text
Requirement 12 は、作業開始前に「正本コマンド・入力・成果物・順序・衝突・停止条件」を同じ形式で確認するための operation contract 層である。本節は read-only preflight を先に確定し、runner による実行代行は後段へ分離する。

operation contract は operation_id、kind、operation_family、canonical_invocation、workflow_binding、required_inputs、target_identity、planned_outputs、sequence_mode、worktree_policy、pending_conflict_policy、artifact_policy、family_required_checks、vocabulary_refs を持つ。

preflight response は schema_version、operation_id、verdict、allowed_verdicts、sequence_mode、allowed_sequence_modes、state_refs、required_inputs、missing_inputs、template_available、target_identity、worktree_state、pending_conflicts、integrity_conflicts、checks、planned_outputs、canonical_commands、next_step を持つ。

workflow state に依存する operation は state_refs.next_action に next --json から読んだ active state dimensions を含める。少なくとも current mainline、required_action、phase、stage、reopen_scope、impact_review_scope、direct / indirect features、flag policy、next_pending_gate、next_drafting_gate、pending_gates、completed_gates、superseded gate の有無、参照 state files を含める。

DEVIATION は対象 operation の開始を拒否する hard-stop であり、operation policy や人向け表示の都合で WARN に下げてはならない。

Phase 1 は read-only registry / preflight。成果物を作らず、operation 可否と衝突を返す。Phase 2 は runner-enabled operation。Phase 1 の preflight が OK または明示許可された WARN の場合のみ、実際の artifact 作成・更新を行う。
```

## Tasks 変更抜粋

```text
workflow-management 全体で 14 タスク。T-014 は 2026-06-16 reopen R-0 operation registry / preflight で追加。

T-014：operation registry / read-only preflight（Req 12、reopen R-0 2026-06-16）

対応設計節：design.md §Requirement 12 設計モデル §1〜§13、§XDI-WM-004
対応要件：Requirement 12 受入 1〜13

責務：
stages/operation-registry.yaml と read-only preflight を追加し、review-run、post-write verification、triage、reopen、commit approval chain、session-record、deployment / export などの操作を、記憶・前例・短縮名ではなく operation contract から開始できるようにする。Phase 1 は成果物を作らない preflight のみとし、review-run directory、manifest、approval record、session record、commit、deployment / export output を作成・更新しない。実際に artifact を作る runner は Phase 2 として分離する。

前提タスク：
T-002、T-003、T-004、T-006、T-007、T-008、T-012、T-013

成果物：
- stages/operation-registry.yaml
- tools/check_workflow_action/operation_registry.py
- tools/check_workflow_action/operation_preflight.py
- tools/check-workflow-action.py operation-preflight --operation-id <id> --json
- tests/workflow-management/test_operation_registry.py
- tests/workflow-management/test_operation_preflight.py
```

## T-014 完了条件

```text
1. registry が operation_id、kind、operation_family、canonical invocation、workflow binding、required inputs、target identity、planned outputs、sequence mode、各 policy、family required checks を機械検査できる。
2. preflight response が schema_version、operation_id、verdict、allowed_verdicts、sequence_mode、allowed_sequence_modes、state_refs、required_inputs、missing_inputs、template_available、target_identity、worktree_state、pending_conflicts、integrity_conflicts、checks、planned_outputs、canonical_commands、next_step を返す。
3. workflow state に依存する operation では、next --json の active state dimensions を state_refs.next_action に返す。
4. command validation は help 文字列ではなく parser / parser adapter と registry の canonical_invocation を照合する。
5. worktree conflict と integrity conflict を分ける。
6. review artifact 系 operation は target / manifest / bundle / criteria / document-type / approval record / existing review-run artifact の対象集合一致、approval.yaml の finding id / final_label、bundle 非空、staged / unstaged 対象選択、上書き・stale・drift を作成前に検査できる。
7. serial_only operation は approval chain の順序、nonce、digest、expiry、consume、invalidated、target を検査する。
8. current-session formal record guard は current と target が同一または不明なら DEVIATION にする。
9. nested issue handling は記録なしの scope drift を DEVIATION にする。
10. deployment / export preflight は planned outputs、既存成果物、上書き禁止 policy、外部 app root、既存 bundle / smoke-run / app file 衝突を作成前に返す。
11. reopen_scope と impact_review_scope を区別し、next --json と整合させる。
12. 判定は LLM、provider、model 名に依存しない。
13. read-only preflight は正本 artifact を作らず、runner-enabled operation は本タスクの範囲外として明示されている。
```

## T-014 テスト要件

```text
TDD：先に失敗テストを書く。

1. registry schema 正常系と必須 field 欠落・未知 kind・未知 operation_family・family_required_checks 欠落の fail-closed。
2. parser / parser adapter との invocation 照合正常系・存在しない subcommand / option / entrypoint / alias の DEVIATION。
3. preflight response JSON のキー名・型固定、allowed_verdicts と verdict 整合、DEVIATION hard-stop の WARN downgrading 拒否。
4. next --json active state dimensions の取り込みと feature_impact_decisions / spec.json / pending_gates / drafting_completed_gates / downstream_impact_decisions 不整合の検出。
5. worktree conflict と integrity conflict の分離。
6. review artifact preflight の target / manifest / bundle / approval.yaml / existing artifact drift 検査。
7. serial_only approval chain の順序外・期限切れ・消費済み・invalidated・digest 不一致検査。
8. current-session formal record guard。
9. nested issue scope drift。
10. deployment / export planned output / overwrite policy / external root 衝突。
11. read-only 不変性。
12. LLM/provider/model 系 field 非依存・禁止 field 検査。
```

## 要件追跡と XDI

```text
Requirement 12 受入 1〜13 はすべて T-014 に追跡されている。

XDI-WM-004 は T-014 の実装・検証範囲で保持する。対象は operation registry / preflight、正本 invocation、parser / parser adapter 照合、worktree / pending / integrity conflict、review artifact / bundle / approval 作成前検査、serial_only approval chain、current-session formal record guard、nested issue handling、deployment / export preflight、reopen scope / impact review scope、next --json 状態一意性、LLM／provider／model 非依存である。
```

## Review Criteria

次の観点で ERROR / WARN / INFO を返す。

- ERROR：Requirement 12 の必須受入がタスクから抜けている、Phase 1 / Phase 2 が混在している、TDD で検証不能、または既存タスクとの責務衝突により実装不能。
- WARN：受入はあるが粒度・成果物・前提タスク・テスト要件が曖昧で、implementation で手戻りが起きやすい。
- INFO：肯定的所見、軽微な改善、または今後の実装で注意すべき点。
