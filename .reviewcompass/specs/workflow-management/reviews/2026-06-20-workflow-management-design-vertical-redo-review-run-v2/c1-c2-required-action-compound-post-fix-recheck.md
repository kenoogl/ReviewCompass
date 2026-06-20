# C1/C2 post-fix recheck: required_action coverage and compound operation branches

## 対象所見

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-001`
- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-002`

## 指摘内容

- 001: 19 個の `required_action` が、effect_kind、approval_required、phase_boundary、sequence、actor、branching、preconditions / postconditions へ個別対応していなかった。
- 002: `run_maintenance` と `run_workflow_stage` について、branch 条件、内部 step、max side effect、approval aggregation が具体化されていなかった。

## 修正内容

- Requirement 13 §3 の 19 語彙対応表に続けて、全 `required_action` の precondition / postcondition baseline IDs を追加した。
- `stages/operation-contracts.yaml` はこの基線を弱めず、各 ID を machine-checkable な check と `source_ref` に展開すると明記した。
- `branching.branches[]` の最低構造として、`branch_id`、`condition`、`internal_steps[]`、`max_effect_kind`、`approval_aggregation`、`human_only_override_applies`、`precondition_ids[]`、`postcondition_ids[]` を定義した。
- `internal_steps[]` の各 step が `step_id`、`effect_kind`、`approval_required`、`phase_boundary`、`source_ref` を持つことを定義した。
- `run_maintenance` の各 branch について、内部 step ごとの `effect_kind`、`approval_required`、`phase_boundary` 基線を追加した。
- `run_workflow_stage` の各 branch について、内部 step ごとの `effect_kind`、`approval_required`、`phase_boundary` 基線を追加した。

## 再点検結果

- 19 語彙は、既存の effect / approval / phase / sequence / actor / branch 表に加えて、pre/postcondition baseline まで設計上たどれるようになった。
- `run_maintenance` と `run_workflow_stage` は、代表値だけではなく branch と step の基線が示され、tasks / implementation が内部 step を推測で発明する余地が減った。
- branch 詳細は operation contract 正本である `stages/operation-contracts.yaml` に展開される前提であり、registry 側に複製しないという C8 の境界とも整合している。

## 残リスク

- 実装段階では、19 語彙の contract coverage fixture、pre/postcondition ID coverage fixture、branch step field coverage fixture を追加する必要がある。
- 外部 API 実行 step の承認要否は、外部送信承認 contract と接続して具体化する必要がある。
