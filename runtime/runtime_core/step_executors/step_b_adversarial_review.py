"""Step B：Adversarial Review（敵対レビュー）実行器（runtime tasks.md T-004）。

Step B は主役結論に同意する場合でも独立した反証の試行を必ず行い、各所見の counter_status を
foundation 3 値正本から必ず設定する。「反証なし」と「反証を試みていない」を曖昧にしない。

対応設計節：design.md §ステップ実行モデル Step B
対応要件：Requirement 1 受入 4、Requirement 4 受入 3、Requirement 6 受入 6
"""
from . import (
  RUNTIME_REVIEW_MODE,
  complete_finding,
  foundation_enum,
  included_steps_for,
  skip_marker,
  write_step_json,
)

STEP_ID = "step_b"
STEP_NAME = "adversarial_review"
SOURCE_ROLE = "adversarial_reviewer"
FILENAME = "step_b_adversarial_review.json"

# foundation finding スキーマの counter_status enum を参照のみで取得（再定義禁止、§判断 6）。
COUNTER_STATUS_VOCAB = foundation_enum("finding.schema.json", "counter_status")


def run(*, run_dir, prompt_identity, llm_boundary, target_artifact, prior_findings, treatment, started_at, closed_at):
  """Step B を実行し steps/step_b_adversarial_review.json を出力する。"""
  if STEP_NAME not in included_steps_for(treatment):
    marker = skip_marker(step_id=STEP_ID, step_name=STEP_NAME, treatment=treatment)
    write_step_json(run_dir, FILENAME, marker)
    return marker

  response = llm_boundary.invoke(
    role=SOURCE_ROLE,
    prompt=prompt_identity,
    target_artifact=target_artifact,
    context={"prior_findings": prior_findings},
  )
  findings = []
  for i, raw in enumerate(response["findings"]):
    counter_status = raw.get("counter_status")
    if counter_status not in COUNTER_STATUS_VOCAB:
      raise ValueError(
        f"Step B の所見には counter_status（foundation 3 値正本 {sorted(COUNTER_STATUS_VOCAB)}）が必須："
        f"{counter_status!r}"
      )
    findings.append(
      complete_finding(
        raw,
        finding_id=f"{STEP_ID}-f{i}",
        step_id=STEP_ID,
        source_role=SOURCE_ROLE,
        counter_status=counter_status,
      )
    )
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
