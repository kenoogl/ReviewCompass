"""T-009 のテスト：レビューモード差分報告と 3 役所見差分報告。"""
import json

import yaml

from diff_reports.mode_diff_writer import ModeDiffWriter
from diff_reports.role_diff_writer import RoleDiffWriter


FINDINGS = [
  {
    "feature": "evaluation",
    "target": "target-1",
    "review_mode": "runtime_mediated",
    "role": "main",
    "severity": "ERROR",
    "final_label": None,
    "counter_status": "not_assessed",
  },
  {
    "feature": "evaluation",
    "target": "target-1",
    "review_mode": "api_mediated",
    "role": "adversarial",
    "severity": "WARN",
    "final_label": None,
    "counter_status": "counter_evidence_raised",
  },
  {
    "feature": "evaluation",
    "target": "target-1",
    "review_mode": "api_mediated",
    "role": "judgment",
    "severity": "ERROR",
    "final_label": "must-fix",
    "counter_status": "no_counter_evidence_after_challenge",
  },
]


def test_diff_report_schema_declares_minimum_fields():
  """diff_report_schema.yaml が mode/role の最低限スキーマを宣言する。"""
  schema = yaml.safe_load(ModeDiffWriter.load_schema().read_text(encoding="utf-8"))
  assert schema["mode_diff_required_fields"] == [
    "feature",
    "review_mode",
    "findings_by_severity",
    "target",
  ]
  assert schema["role_diff_required_fields"] == [
    "feature",
    "role",
    "findings_summary",
    "target",
  ]


def test_mode_diff_writer_outputs_required_4_elements(tmp_path):
  """mode_diff_report.json が 4 要素を含む構造化形式で出力される。"""
  path = ModeDiffWriter().write(tmp_path / "experiments" / "analysis", FINDINGS)
  payload = json.loads(path.read_text(encoding="utf-8"))
  entry = payload["entries"][0]
  assert set(entry) == {"feature", "review_mode", "findings_by_severity", "target"}
  assert payload["entries_by_mode"]["api_mediated"]["findings_by_severity"] == {
    "WARN": 1,
    "ERROR": 1,
  }


def test_role_diff_writer_outputs_required_4_elements(tmp_path):
  """role_diff_report.json が 4 要素を含む構造化形式で出力される。"""
  path = RoleDiffWriter().write(tmp_path / "experiments" / "analysis", FINDINGS)
  payload = json.loads(path.read_text(encoding="utf-8"))
  entry = payload["entries"][0]
  assert set(entry) == {"feature", "role", "findings_summary", "target"}


def test_role_diff_writer_applies_role_specific_summary(tmp_path):
  """敵対役は counter_status、判定役は final_label の集計を含む。"""
  path = RoleDiffWriter().write(tmp_path / "experiments" / "analysis", FINDINGS)
  payload = json.loads(path.read_text(encoding="utf-8"))
  by_role = payload["entries_by_role"]
  assert by_role["adversarial"]["findings_summary"]["by_counter_status"] == {
    "counter_evidence_raised": 1,
  }
  assert by_role["judgment"]["findings_summary"]["by_final_label"] == {
    "must-fix": 1,
  }
