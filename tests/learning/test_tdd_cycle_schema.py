"""D-025 TDD cycle evidence schema の契約テスト。"""
import json
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "learning" / "workflow" / "schemas" / "tdd-cycle.schema.json"

REQUIRED_FIELDS = [
  "event_type",
  "cycle_id",
  "linked_finding_ids",
  "test_first_commit",
  "implementation_commit",
  "failing_test_command",
  "failing_test_result",
  "green_test_command",
  "green_test_result",
  "changed_files",
]


def _load_schema():
  return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _valid_payload():
  return {
    "event_type": "tdd_cycle",
    "cycle_id": "TDD-2026-06-09-001",
    "linked_finding_ids": ["finding-001"],
    "test_first_commit": "fc30479",
    "implementation_commit": "fc30480",
    "failing_test_command": ".venv/bin/python3 -m pytest tests/tools/test_example.py",
    "failing_test_result": {
      "status": "failed",
      "exit_code": 1,
      "summary": "1 failed"
    },
    "green_test_command": ".venv/bin/python3 -m pytest tests/tools/test_example.py",
    "green_test_result": {
      "status": "passed",
      "exit_code": 0,
      "summary": "1 passed"
    },
    "changed_files": [
      "tools/check-workflow-action.py",
      "tests/tools/test_example.py"
    ]
  }


def test_tdd_cycle_schema_is_valid_json_schema():
  schema = _load_schema()
  Draft202012Validator.check_schema(schema)


def test_tdd_cycle_required_fields_match_d025_contract():
  schema = _load_schema()
  assert schema["required"] == REQUIRED_FIELDS


def test_tdd_cycle_accepts_red_to_green_payload():
  schema = _load_schema()
  Draft202012Validator(schema).validate(_valid_payload())


def test_tdd_cycle_requires_failed_red_result():
  schema = _load_schema()
  payload = _valid_payload()
  payload["failing_test_result"]["status"] = "passed"

  try:
    Draft202012Validator(schema).validate(payload)
  except ValidationError:
    return

  raise AssertionError("failing_test_result.status は failed のみ許容する")


def test_tdd_cycle_requires_passed_green_result():
  schema = _load_schema()
  payload = _valid_payload()
  payload["green_test_result"]["exit_code"] = 1

  try:
    Draft202012Validator(schema).validate(payload)
  except ValidationError:
    return

  raise AssertionError("green_test_result.exit_code は 0 のみ許容する")


def test_tdd_cycle_requires_linked_finding_ids():
  schema = _load_schema()
  payload = _valid_payload()
  payload["linked_finding_ids"] = []

  try:
    Draft202012Validator(schema).validate(payload)
  except ValidationError:
    return

  raise AssertionError("linked_finding_ids は 1 件以上を要求する")
