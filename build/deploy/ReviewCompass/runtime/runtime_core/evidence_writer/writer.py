"""evidence writer（証拠書き出し器）（runtime tasks.md T-008）。

生段証拠（steps/*.json）と決定証拠（decisions/*.json）から review_case.json へ投影する。
review_case.json を唯一の横断正本とし、foundation の review_case スキーマに準拠させる。
投影規約は projection_rules.yaml（7 項目）が正本。

対応設計節：design.md §証拠出力モデル §生証拠と派生証拠の分離
対応要件：Requirement 4 受入 1〜5
"""
import json
from pathlib import Path

import yaml

# 投影で読む段ファイルの順序（決定的出力のため固定）。
_STEP_FILES = [
  "step_a_primary_detection.json",
  "step_b_adversarial_review.json",
  "step_c_judgment.json",
  "step_d_integration.json",
]


class EvidenceWriter:
  """run ディレクトリの生段証拠・決定証拠を review_case.json へ投影する。"""

  def __init__(self, run_dir, projection_rules_path=None):
    self.run_dir = Path(run_dir)
    self.projection_rules_path = (
      Path(projection_rules_path)
      if projection_rules_path
      else Path(__file__).resolve().parent / "projection_rules.yaml"
    )

  def _load_json(self, relpath):
    path = self.run_dir / relpath
    if not path.is_file():
      return None
    return json.loads(path.read_text(encoding="utf-8"))

  def project_to_review_case(self):
    """投影規約 7 項目を機械適用し review_case.json を組み立てて書き出す。"""
    manifest = yaml.safe_load((self.run_dir / "run_manifest.yaml").read_text(encoding="utf-8"))

    step_records = []
    findings = []
    integration_summary = ""
    for filename in _STEP_FILES:
      step = self._load_json(f"steps/{filename}")
      if step is None:
        continue
      # 投影 1・2：step_outcome → step_status、段別識別子
      step_records.append({
        "step_id": step.get("step_id"),
        "step_name": step.get("step_name"),
        "step_status": step.get("step_outcome"),
        "step_prompt_artifact_id": step.get("prompt_id"),
        "step_started_at": step.get("step_started_at"),
        "step_closed_at": step.get("step_closed_at"),
      })
      # 投影 3：findings 収集
      for finding in step.get("findings", []):
        findings.append(dict(finding))
      # 投影 7：integration_summary
      if "integration_summary" in step:
        integration_summary = step["integration_summary"]

    # 投影 4：decision_units の finding_refs から各所見へ decision_unit_id を逆引き
    decision_units = self._load_json("decisions/decision_units.json") or {"decision_units": []}
    finding_to_unit = {}
    for unit in decision_units.get("decision_units", []):
      for finding_ref in unit.get("finding_refs", []):
        finding_to_unit[finding_ref] = unit["decision_unit_id"]
    for finding in findings:
      if finding["finding_id"] in finding_to_unit:
        finding["decision_unit_id"] = finding_to_unit[finding["finding_id"]]

    # 投影 5・6：検証成果物への参照（無ければ空配列、欠落を捏造しない）
    validator_result_refs = []
    if (self.run_dir / "validation" / "validator_result.json").is_file():
      validator_result_refs = ["validation/validator_result.json"]
    invalidation_marker_refs = []
    if (self.run_dir / "validation" / "invalidation_markers.json").is_file():
      invalidation_marker_refs = ["validation/invalidation_markers.json"]

    review_case = {
      "run_id": manifest["run_id"],
      "target_id": manifest["target_id"],
      "run_metadata_ref": "run_manifest.yaml",
      "step_records": step_records,
      "findings": findings,
      "validator_result_refs": validator_result_refs,
      "invalidation_marker_refs": invalidation_marker_refs,
      "integration_summary": integration_summary,
    }
    # A-006：実行終了後の確定メタデータ（run_status／validator_status／evidence_class）が
    # run_manifest にあれば横断正本にも反映する（design.md §実行終了境界 手順 3）。
    for key in ("run_status", "validator_status", "evidence_class"):
      if key in manifest:
        review_case[key] = manifest[key]
    path = self.run_dir / "review_case.json"
    path.write_text(json.dumps(review_case, ensure_ascii=False, indent=2), encoding="utf-8")
    return review_case
