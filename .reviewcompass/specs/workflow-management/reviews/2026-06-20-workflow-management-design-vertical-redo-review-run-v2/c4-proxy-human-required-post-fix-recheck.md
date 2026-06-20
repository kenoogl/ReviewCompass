# C4 post-fix recheck: proxy triage human-required predicate

## 対象所見

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-004`
- 指摘: proxy triage decision の human-required predicate が、証跡リストと優先順位の prose にはなっているが、`未解決 approval gate` や `approval_required=true の対象 operation` を機械的にどう判定するか、および `proxy_triage_apply_batch` の formal precondition への接続が弱かった。

## 修正内容

- `.reviewcompass/specs/workflow-management/design.md` の Requirement 16 §3 に `proxy_triage_evaluate_human_required` read-only internal check を追加した。
- predicate の入力を、対象 finding / cluster IDs、finding-to-operation mapping、approval gate record、operation contract、review-wave impact evidence、active reopen / impact review scope と定義した。
- predicate の出力を、`verdict`、`blocks_proxy_apply`、`blocking_reasons[]`、`checked_records[]`、`checked_contracts[]`、`source_refs[]` と定義した。
- `未解決 approval gate` の条件を、未承認、未反映、human-only、binding digest 不一致、`next_action_expectation != proceed`、または必要 record 欠落として定義した。
- `approval_required=true の対象 operation` を、finding-to-operation mapping から operation contract を一意解決し、contract の `approval_required` または branch approval aggregation を読むものとして定義した。
- mapping 欠落、複数候補、contract 参照欠落、contract digest / schema_version drift は `blocks_proxy_apply=true` とした。
- predicate の固定評価順序を 6 段で定義し、human-required 証跡がある場合は triage item や proxy decision の値に関係なく proxy apply を止めると明記した。
- `proxy_triage_apply_batch` の preconditions に、`proxy_triage_evaluate_human_required` が成功し、`blocks_proxy_apply=false` を返していることを追加した。

## 再点検結果

- 指摘されていた prose-only の human-required 優先規則は、read-only internal check と `proxy_triage_apply_batch` precondition に接続された。
- triage item の `decision_status`、`final_label`、`decision_actor_type` は補助確認に限定され、human-required predicate の正本ではないという既存方針と整合している。
- provider / model 名に依存しない判定入力の方針とも矛盾しない。

## 残リスク

- 実装段階では、mapping 欠落、human-only record、approval_required branch、review-wave impact 未解決、active scope 矛盾を fixture 化し、`proxy_triage_apply_batch` が `triage.yaml` を更新しないことを TDD で確認する必要がある。
