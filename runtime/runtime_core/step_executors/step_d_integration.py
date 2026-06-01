"""Step D：Integration（統合）実行器（runtime tasks.md T-005）。

前段（Step A／B、treatment に応じ Step C）の出力から、追加の言語モデル呼び出しなしで
決定単位と統合成果物を機械的に生成する。本実行器は言語モデル呼び出しを一切含まない
（design.md §判断 4、統合手順 6 ステップ）。

対応設計節：design.md §ステップ実行モデル Step D Integration
対応要件：Requirement 1 受入 1〜3・7、Requirement 4 受入 2〜5、Requirement 5 受入 1
"""
import json
from pathlib import Path

from . import RUNTIME_REVIEW_MODE, foundation_enum, included_steps_for

STEP_ID = "step_d"
STEP_NAME = "integration"
FILENAME = "step_d_integration.json"

# final_label → proposed_action の写像（runtime 所有の機械規則、統合手順 ステップ 4）。
# キー集合は foundation final_label 正本と一致することを起動時に検証する（再定義しない）。
FINAL_LABEL_TO_ACTION = {
  "must-fix": "fix_required",
  "should-fix": "fix_recommended",
  "leave-as-is": "no_action",
}
_FOUNDATION_FINAL_LABELS = foundation_enum("necessity_judgment.schema.json", "final_label")
assert set(FINAL_LABEL_TO_ACTION) == _FOUNDATION_FINAL_LABELS, (
  "final_label 写像が foundation 正本と不一致（再定義になっている）"
)

# 強度順（強い順）。決定単位に複数判定がある場合の代表措置選択に使う。
_LABEL_STRENGTH_ORDER = ["must-fix", "should-fix", "leave-as-is"]

# 判定がない決定単位の既定推奨措置（統合手順 ステップ 4「ない場合は規定の既定規則」）。
DEFAULT_PROPOSED_ACTION = "human_review_required"


def _findings_of(step_output):
  if step_output and step_output.get("step_outcome") == "executed":
    return step_output.get("findings", [])
  return []


def _judgments_of(step_c_output):
  if step_c_output and step_c_output.get("step_outcome") == "executed":
    return step_c_output.get("judgments", [])
  return []


def _strongest_action(labels):
  present = [label for label in labels if label]
  if not present:
    return DEFAULT_PROPOSED_ACTION
  for label in _LABEL_STRENGTH_ORDER:
    if label in present:
      return FINAL_LABEL_TO_ACTION[label]
  return DEFAULT_PROPOSED_ACTION


def _readiness(treatment, outputs_by_step):
  """必須段出力の充足のみで実行終了準備を機械判定する（統合手順 ステップ 5）。"""
  for step_name in included_steps_for(treatment):
    if step_name == STEP_NAME:
      continue
    out = outputs_by_step.get(step_name)
    if out is None or out.get("step_outcome") == "failed":
      return False
  return True


def run(*, run_dir, step_a_output, step_b_output, step_c_output, treatment, started_at, closed_at):
  """Step D を実行し step_d_integration.json と decisions/decision_units.json を出力する。"""
  # ステップ 1：所見収集（source_role を保持したまま統合集合にする）
  findings = _findings_of(step_a_output) + _findings_of(step_b_output)

  # ステップ 2：Step C を含む場合のみ判定を所見に紐づける（非実行時はスキップ）
  judgments = _judgments_of(step_c_output)
  judgment_id_of = {idx: f"judgment-{idx}" for idx in range(len(judgments))}
  finding_to_judgment = {}
  for idx, judgment in enumerate(judgments):
    for finding_ref in judgment.get("finding_refs", []):
      finding_to_judgment[finding_ref] = idx

  # ステップ 3：所見を決定単位に集約（集約キー＝requirement_link または対象領域、新推論なし）
  groups = {}
  group_order = []
  for finding in findings:
    fid = finding["finding_id"]
    j_idx = finding_to_judgment.get(fid)
    if j_idx is not None:
      group_key = ("req", judgments[j_idx].get("requirement_link"))
    else:
      source_refs = finding.get("source_refs") or []
      group_key = ("area", source_refs[0] if source_refs else fid)
    if group_key not in groups:
      groups[group_key] = {"finding_refs": [], "judgment_idxs": []}
      group_order.append(group_key)
    groups[group_key]["finding_refs"].append(fid)
    if j_idx is not None and j_idx not in groups[group_key]["judgment_idxs"]:
      groups[group_key]["judgment_idxs"].append(j_idx)

  # ステップ 4：各決定単位の推奨措置を決める
  decision_units = []
  for i, group_key in enumerate(group_order):
    group = groups[group_key]
    labels = [judgments[ji].get("final_label") for ji in group["judgment_idxs"]]
    decision_units.append({
      "decision_unit_id": f"du-{i + 1:03d}",
      "finding_refs": list(group["finding_refs"]),
      "judgment_refs": [judgment_id_of[ji] for ji in group["judgment_idxs"]],
      "proposed_action": _strongest_action(labels),
      "human_decision": None,            # 人間決定は未確定（T-007 で確定）
      "human_decision_timestamp": None,
      "human_decision_note": "",
    })

  # ステップ 5：実行終了準備判定
  run_close_ready = _readiness(treatment, {
    "primary_detection": step_a_output,
    "adversarial_review": step_b_output,
    "judgment": step_c_output,
  })

  # ステップ 6：integration_summary 生成と書き出し（人間決定は未確定のまま）
  integration_summary = (
    f"統合レビュー記録：treatment={treatment}、所見 {len(findings)} 件、"
    f"決定単位 {len(decision_units)} 件、判定 {len(judgments)} 件、"
    f"run_close_ready={run_close_ready}"
  )
  output = {
    "step_id": STEP_ID,
    "step_name": STEP_NAME,
    "step_outcome": "executed",
    "review_mode": RUNTIME_REVIEW_MODE,
    "step_started_at": started_at,
    "step_closed_at": closed_at,
    "findings_count": len(findings),
    "decision_unit_count": len(decision_units),
    "decision_units": decision_units,
    "integration_summary": integration_summary,
    "run_close_ready": run_close_ready,
  }

  steps_path = Path(run_dir) / "steps" / FILENAME
  steps_path.parent.mkdir(parents=True, exist_ok=True)
  steps_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

  decisions_path = Path(run_dir) / "decisions" / "decision_units.json"
  decisions_path.parent.mkdir(parents=True, exist_ok=True)
  decisions_path.write_text(
    json.dumps({"decision_units": decision_units}, ensure_ascii=False, indent=2),
    encoding="utf-8",
  )
  return output
