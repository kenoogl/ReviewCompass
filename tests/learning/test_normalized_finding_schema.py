"""D-004 normalized finding schema の契約テスト。"""
import json
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "learning" / "workflow" / "schemas" / "normalized-finding.schema.json"

REQUIRED_FIELDS = [
  "finding_id",
  "run_id",
  "source_model",
  "review_role",
  "inspection_criterion",
  "severity",
  "initial_recommendation",
  "final_label",
  "decision_status",
  "decision_actor",
  "observed_at",
  "evidence_refs",
  "affected_files",
  "resolution",
  "false_positive_reversal",
]

SEVERITY_ENUM = ["CRITICAL", "ERROR", "WARN", "INFO"]
FINAL_LABEL_ENUM = ["must-fix", "should-fix", "leave-as-is"]
DECISION_STATUS_ENUM = ["pending", "human_required", "decided", "superseded"]


def _load_schema():
  return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _valid_payload():
  return {
    "finding_id": "NF-2026-06-09-001",
    "run_id": "2026-06-04-workflow-management-implementation-review-run",
    "source_model": "claude-sonnet-4-6",
    "review_role": "primary",
    "inspection_criterion": "implementation-triad-review",
    "severity": "ERROR",
    "initial_recommendation": "must-fix",
    "final_label": "must-fix",
    "decision_status": "decided",
    "decision_actor": {
      "actor_type": "proxy_model",
      "actor_id": "gpt-5.5"
    },
    "observed_at": "2026-06-04T01:29:24.198142+00:00",
    "decided_at": "2026-06-04T01:54:26.988276+00:00",
    "resolved_at": "2026-06-04T12:20:02.364023+00:00",
    "evidence_refs": [
      {
        "label": "raw",
        "path": ".reviewcompass/specs/workflow-management/reviews/run/raw/claude.txt"
      }
    ],
    "affected_files": [
      "tools/check-workflow-action.py"
    ],
    "resolution": {
      "status": "fixed",
      "summary": "raw response preservation gate を追加した。"
    },
    "resolution_commit": "fc30479",
    "linked": {
      "source_raw_path": "raw/claude-sonnet-4-6.round-1.txt",
      "source_parsed_path": "parsed/claude-sonnet-4-6.round-1.yaml",
      "triage_path": ".reviewcompass/specs/workflow-management/reviews/run/triage.yaml"
    },
    "false_positive_reversal": {
      "is_reversal": False,
      "reason": None
    }
  }


def test_normalized_finding_schema_is_valid_json_schema():
  schema = _load_schema()
  Draft202012Validator.check_schema(schema)


def test_normalized_finding_required_fields_match_d004_contract():
  schema = _load_schema()
  assert schema["required"] == REQUIRED_FIELDS


def test_normalized_finding_enums_match_foundation_triage_vocabularies():
  schema = _load_schema()
  assert schema["properties"]["severity"]["enum"] == SEVERITY_ENUM
  assert schema["properties"]["final_label"]["enum"] == FINAL_LABEL_ENUM
  assert schema["properties"]["decision_status"]["enum"] == DECISION_STATUS_ENUM


def test_normalized_finding_accepts_review_run_finding_payload():
  schema = _load_schema()
  Draft202012Validator(schema).validate(_valid_payload())


def test_normalized_finding_rejects_invalid_timestamp():
  schema = _load_schema()
  payload = _valid_payload()
  payload["observed_at"] = "2026-06-04 01:29:24"

  try:
    Draft202012Validator(schema).validate(payload)
  except ValidationError:
    return

  raise AssertionError("observed_at は RFC3339 形式のみ許容する")


def test_normalized_finding_requires_structured_evidence_refs():
  schema = _load_schema()
  payload = _valid_payload()
  payload["evidence_refs"] = ["raw/claude-sonnet-4-6.round-1.txt"]

  try:
    Draft202012Validator(schema).validate(payload)
  except ValidationError:
    return

  raise AssertionError("evidence_refs は label/path を持つ object 配列のみ許容する")
