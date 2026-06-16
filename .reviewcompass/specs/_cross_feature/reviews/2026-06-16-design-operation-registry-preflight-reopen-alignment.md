---
date: 2026-06-16
gate: stages/design.yaml#alignment
feature: workflow-management
reopen: R-0
reopen_topic: operation-registry-preflight-unified-design
decision: existing_sufficient
---

# design alignment（整合確認）：operation registry / preflight

reopen R-0 の第3過程、workflow-management design フェーズの alignment。Requirement 12 r2、design triad-review r2 の反映、design review-wave 判定、下流 recheck 状態との整合を確認する。

## Requirement 12 r2 との整合

| 要件観点 | design での扱い | 整合判定 |
| --- | --- | --- |
| operation registry | `stages/operation-registry.yaml` を workflow-management 所有の正本 registry とし、operation contract schema を定義した。 | 整合。 |
| command / parser validation | help 文字列ではなく parser / parser adapter と照合する方針を明記した。 | 整合。 |
| preflight response | `verdict`、`allowed_verdicts`、`sequence_mode`、`state_refs.next_action`、conflicts、checks、canonical commands を共通 schema として定義した。 | 整合。 |
| `next --json` 状態一意性 | current mainline、required action、phase / stage、reopen scope、impact review scope、direct / indirect features、flag policy、pending / completed / superseded gates、state files を response に含める設計にした。 | 整合。 |
| worktree / integrity conflict | worktree conflict と integrity conflict を分け、承認 record / manifest / bundle / digest の stale / drift を clean worktree でも検出する設計にした。 | 整合。 |
| review artifact preflight | review target、manifest、bundle、criteria、document-type、approval record、既存 review-run artifact の対象集合一致を作成前に確認する設計にした。 | 整合。 |
| serial_only approval chain | `prepare -> record -> delegate-execution -> guarded commit` を serial_only とし、nonce / digest / expiry / consume / invalidated / target を確認する設計にした。 | 整合。 |
| current-session formal record guard | `session_record_mode`、`current_session_id`、`target_session_id` を response に含め、formal 出力で current と target が同一または不明なら DEVIATION とする設計にした。 | 整合。 |
| nested issue handling | `nested_issue_state` と relation / allowed_files / return_condition / nesting_depth を response に含め、scope drift を DEVIATION とする設計にした。 | 整合。 |
| deployment / export | planned outputs、既存成果物、上書き禁止 policy、外部 root 書き込み、既存 bundle / smoke-run / app file 衝突を作成前に返す設計にした。 | 整合。 |
| LLM 非依存 | operation registry / preflight は provider / model 名を schema に持たず、正本 artifact と機械状態だけで判定する設計にした。 | 整合。 |

## design triad-review r2 対処との整合

design triad-review r2 では ERROR 0、WARN 8、INFO 5 であり、利用者承認済み triage により WARN 8 件を should-fix として反映した。

- active state schema under-typed：`state_refs.next_action` を具体フィールドへ展開した。
- verdict / hard-stop semantics：`allowed_verdicts` と `DEVIATION` の hard-stop 条件を明記した。
- operation family invariants：`operation_family` と `family_required_checks` を追加した。
- cross-source inconsistency：`feature_impact_decisions`、`spec.json`、`pending_gates`、`drafting_completed_gates`、`downstream_impact_decisions`、scope 間の矛盾を DEVIATION とした。
- WARN / DEVIATION 境界：WARN は advisory / read-only で契約上許される場合に限定した。
- current-session guard：current / target session id と formal mode を response に含めた。
- nested issue：parent / discovered issue / relation / allowed files / return condition / nesting depth を response に含めた。

leave-as-is とした INFO / 軽微指摘は、肯定的所見または初期 operation id の拡張可能性に関するものであり、追加設計変更は不要と判断した。

## design review-wave 判定との整合

`2026-06-16-design-operation-registry-preflight-review-wave.md` は no_impact と判定し、他 6 機能への design 正本修正不要とした。

Requirement 12 の設計は workflow-management の操作契約であり、foundation / runtime / evaluation / analysis / self-improvement / conformance-evaluation の設計所有権を変更しない。したがって review-wave 判定と整合する。

## 下流 recheck 状態との整合

workflow-management の design triad-review / review-wave は完了し、design approval は未完了である。tasks / implementation は未完了で、Requirement 12 の設計を受けて TDD 対象へ進む必要がある。

次段の design approval は人間承認 gate であり、承認後に tasks フェーズへ進む。

## 判定

- **decision：existing_sufficient**。
- design は Requirement 12 r2、triad-review r2 対処、review-wave 判定と整合する。
- 他 feature の design 正本を再オープンする必要はない。
- tasks / implementation への recheck は維持する。
