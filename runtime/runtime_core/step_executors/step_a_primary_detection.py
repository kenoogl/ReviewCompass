"""Step A：Primary Detection（主役検出）実行器（runtime tasks.md T-004）。

対応設計節：design.md §ステップ実行モデル Step A
対応要件：Requirement 1 受入 1〜3、Requirement 4 受入 1〜2、Requirement 6 受入 6
"""
from . import (
  RUNTIME_REVIEW_MODE,
  complete_finding,
  included_steps_for,
  skip_marker,
  write_step_json,
)

STEP_ID = "step_a"
STEP_NAME = "primary_detection"
SOURCE_ROLE = "primary_reviewer"
FILENAME = "step_a_primary_detection.json"


def run(*, run_dir, prompt_identity, llm_boundary, target_artifact, treatment, started_at, closed_at):
  """Step A を実行し steps/step_a_primary_detection.json を出力する。"""
  if STEP_NAME not in included_steps_for(treatment):
    marker = skip_marker(step_id=STEP_ID, step_name=STEP_NAME, treatment=treatment)
    write_step_json(run_dir, FILENAME, marker)
    return marker

  response = llm_boundary.invoke(
    role=SOURCE_ROLE, prompt=prompt_identity, target_artifact=target_artifact
  )
  findings = [
    complete_finding(
      raw,
      finding_id=f"{STEP_ID}-f{i}",
      step_id=STEP_ID,
      source_role=SOURCE_ROLE,
      counter_status="not_assessed",  # Step A では反証未評価
    )
    for i, raw in enumerate(response["findings"])
  ]
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
    "findings": findings,
  }
  write_step_json(run_dir, FILENAME, output)
  return output
