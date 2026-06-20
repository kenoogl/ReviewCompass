# C6 post-fix recheck: structured prompt length bounds source of truth

## 対象所見

- `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-006`
- 指摘: Requirement 15 の第1層 prompt 検査に「判定点ごとの長さ上下限」があるが、上下限の保存先、設定主体、違反時 verdict が未定義だった。

## 修正内容

- `.reviewcompass/specs/workflow-management/design.md` の structured effective prompt schema に `prompt_length` を追加した。
- `prompt_length` の正本を `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml#decision_points` の `prompt_length_bounds` とし、未設定時は `default_prompt_length_bounds` を使うと定義した。
- `prompt_length_bounds` が `min_chars`、`max_chars`、`failure_verdict` を持ち、`min_chars < max_chars` を満たす必要があることを明記した。
- 長さ基準の設定主体を workflow-management の設計・規律マップ更新手続きに限定し、task 個別の review-run や prompt generator が推測で決めないことを明記した。
- `docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml` に全判定点の既定値 `default_prompt_length_bounds` を追加し、`triad-review` と `approval` には個別の `prompt_length_bounds` を追加した。

## 再点検結果

- 指摘されていた「保存先未定義」は、`WORKFLOW_DISCIPLINE_MAP.yaml` の既定値・個別値により解消した。
- 指摘されていた「誰が設定するか未定義」は、workflow-management の設計・規律マップ更新手続きに限定したことで解消した。
- 指摘されていた「失敗 verdict 未定義」は、`failure_verdict` を bounds の必須項目として扱うことで解消した。
- 既存の `effective_prompt_policy: one_effective_prompt_per_decision_point` とは別フィールドにしたため、判定点カタログの既存意味を壊さない。

## 残リスク

- 実装段階では、`prompt_length_bounds` の schema validation と構造化 prompt への `prompt_length` 投影テストが必要である。
- `default_prompt_length_bounds` の具体値は初期基準であり、実 prompt の分布を見て後続で調整する余地がある。
