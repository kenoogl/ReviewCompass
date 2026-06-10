"""Step C：Judgment（判定）実行器（runtime tasks.md T-004）。

判定役が主役・敵対役の所見を読み、最終ラベル（foundation 3 値正本）と推奨措置を決める。

対応設計節：design.md §ステップ実行モデル Step C
対応要件：Requirement 1 受入 1〜3、Requirement 4 受入 1
"""
from . import (
  RUNTIME_REVIEW_MODE,
  foundation_enum,
  included_steps_for,
  skip_marker,
  write_failure,
  write_step_json,
)

STEP_ID = "step_c"
STEP_NAME = "judgment"
SOURCE_ROLE = "judgment_reviewer"
FILENAME = "step_c_judgment.json"

# foundation necessity_judgment スキーマの final_label enum を参照のみで取得（再定義禁止）。
FINAL_LABEL_VOCAB = foundation_enum("necessity_judgment.schema.json", "final_label")


def run(*, run_dir, prompt_identity, llm_boundary, prior_findings, treatment, started_at, closed_at):
  """Step C を実行し steps/step_c_judgment.json を出力する。"""
  if STEP_NAME not in included_steps_for(treatment):
    marker = skip_marker(step_id=STEP_ID, step_name=STEP_NAME, treatment=treatment)
    write_step_json(run_dir, FILENAME, marker)
    return marker

  try:
    response = llm_boundary.invoke(
      role=SOURCE_ROLE,
      prompt=prompt_identity,
      context={"prior_findings": prior_findings},
    )
  except Exception as error:
    return write_failure(run_dir, filename=FILENAME, step_id=STEP_ID,
                         step_name=STEP_NAME, source_role=SOURCE_ROLE, error=error)
  judgments = []
  for raw in response["judgments"]:
    final_label = raw.get("final_label")
    if final_label not in FINAL_LABEL_VOCAB:
      raise ValueError(
        f"Step C の判定 final_label は foundation 3 値正本 {sorted(FINAL_LABEL_VOCAB)} から："
        f"{final_label!r}"
      )
    judgments.append(dict(raw))
  output = {
    "step_id": STEP_ID,
    "step_name": STEP_NAME,
    "step_outcome": "executed",
    "review_mode": RUNTIME_REVIEW_MODE,
    "prompt_artifact_path": prompt_identity["prompt_artifact_path"],
    "prompt_id": prompt_identity["prompt_id"],
    "prompt_version": prompt_identity["prompt_version"],
    "role": prompt_identity["role"],
    "step_started_at": started_at,
    "step_closed_at": closed_at,
    "judgments": judgments,
  }
  write_step_json(run_dir, FILENAME, output)
  return output
