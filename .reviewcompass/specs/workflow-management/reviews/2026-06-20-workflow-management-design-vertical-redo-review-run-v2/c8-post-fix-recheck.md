# C8 post-fix recheck: registry schema contract-field prohibition

## 対象所見

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-008`
- 指摘: registry / preflight read-only 境界について、`effect_kind`、`approval_required`、`phase_boundary` などの contract authority field を registry が持ってはならないことが、runtime integrity check としては書かれているが、registry schema の構造制約として明示されていなかった。

## 修正内容

- `.reviewcompass/specs/workflow-management/design.md` の Requirement 12 §1 に、registry schema が operation contract field を構造的に受け付けないことを追記した。
- `stages/operation-registry.yaml` の各 operation entry で禁止するキーとして、`effect_kind`、`approval_required`、`phase_boundary`、`preconditions`、`postconditions`、`side_effects`、`approval_aggregation`、`branching`、`max_effect_kind`、出力・副作用 contract field を列挙した。
- registry が許す contract 接続フィールドを、最低限 `operation_contract_ref`、`contract_digest`、`contract_schema_version` に限定すると明記した。
- 禁止キーが存在する場合は、preflight の runtime integrity check 以前に schema validation error とし、`DEVIATION` として扱うと明記した。
- `planned_outputs`、`sequence_mode`、`required_inputs`、`target_identity` は preflight binding hint として保持できるが、contract 正本と矛盾した場合は registry 側を優先せず fail-closed にすると明記した。

## 再点検結果

- 指摘されていた「runtime guard と schema-level prohibition の区別が曖昧」は、Requirement 12 §1 の schema 制約として明記したことで解消した。
- Requirement 13 §3 の「registry は contract field を再定義しない」という既存方針と整合している。
- registry / preflight は contract を読むだけで、contract field の正本を保持しないという境界が、設計から tasks / implementation へ継承可能になった。

## 残リスク

- 実装段階では、`.reviewcompass/schema/operation_registry.schema.json` または同等の schema に禁止キーの `not` / `unevaluatedProperties` 検査を追加する必要がある。
- 既存の `stages/operation-registry.yaml` に禁止キーが混入していないことを、Phase 1 の schema validation fixture で確認する必要がある。
