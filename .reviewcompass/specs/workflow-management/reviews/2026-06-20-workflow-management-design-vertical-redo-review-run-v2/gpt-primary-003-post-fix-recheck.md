# GPT primary 003 post-fix recheck: approval decision record digest binding

## 対象所見

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-003`
- 指摘: approval decision record の `target_artifact_digest` と `staged_file_set_digest` が独立 nullable に見え、対象 operation に応じて少なくとも一方または両方を必須にする規則が弱かった。actor / timestamp / source との束縛も明示不足だった。

## 修正内容

- `.reviewcompass/specs/workflow-management/design.md` の Requirement 14 §1 の schema 例に、`target_artifact_digest` / `staged_file_set_digest` の `binding_kind` 別必須条件をコメントとして追加した。
- `source_digest` を judgment record の必須フィールドに追加し、判断根拠 source text または source artifact の digest を保持することを定義した。
- `approval_required=true`、human-only override set、phase / gate completion、commit、push、`spec.json` 更新、reopen finalize の対象 record では `binding_kind=none` を禁止すると明記した。
- `binding_kind` ごとの条件付き必須表を追加し、両 digest を独立 optional として扱ってはならないことを明記した。
- `decided_by`、`decided_at`、`source_ref`、`source_digest`、target operation、required_action、binding digest の欠落は形式不正であり、承認 record として扱わないことを明記した。

## 再点検結果

- 指摘された「digest が任意で弱い record になり得る」問題は、`binding_kind` 別の条件付き必須で解消した。
- actor / timestamp / source / target operation / required_action / digest の束縛が、承認 record の最低条件として読めるようになった。
- 既存の `decision_scope` と `binding_kind` derivation 方針、および C9 の traceability 補強と整合している。

## 残リスク

- 実装段階では、approval gate record schema に `binding_kind` 別 required / forbidden 条件、`binding_kind=none` の対象制限、`source_digest` の形式検査を追加する必要がある。
