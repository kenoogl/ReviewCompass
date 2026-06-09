"""D-027 side track state schema の契約テスト。"""
import json
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "learning" / "workflow" / "schemas" / "side-track-state.schema.json"

REQUIRED_FIELDS = [
  "active_track",
  "track_kind",
  "reason",
  "target_files",
  "manifest_status",
  "policy_violations",
  "return_to",
  "required_action",
]


def _load_schema():
  return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _valid_payload():
  return {
    "active_track": "post_write_verification",
    "track_kind": "side_track",
    "reason": "post_write_target_dirty",
    "target_files": [
      "docs/notes/example.md"
    ],
    "manifest_status": "pending",
    "policy_violations": [],
    "return_to": {
      "outer_node": "completed_follow_up",
      "inner_node": "next_candidate_selection"
    },
    "required_action": "run_post_write_verification"
  }


def test_side_track_state_schema_is_valid_json_schema():
  schema = _load_schema()
  Draft202012Validator.check_schema(schema)


def test_side_track_state_required_fields_match_d027_contract():
  schema = _load_schema()
  assert schema["required"] == REQUIRED_FIELDS


def test_side_track_state_accepts_post_write_side_track_payload():
  schema = _load_schema()
  Draft202012Validator(schema).validate(_valid_payload())


def test_side_track_state_rejects_absolute_target_file():
  schema = _load_schema()
  payload = _valid_payload()
  payload["target_files"] = ["/Users/Daily/Development/ReviewCompass/docs/notes/example.md"]

  try:
    Draft202012Validator(schema).validate(payload)
  except ValidationError:
    return

  raise AssertionError("target_files は relative path のみ許容する")


def test_side_track_state_requires_return_to_outer_node():
  schema = _load_schema()
  payload = _valid_payload()
  payload["return_to"].pop("outer_node")

  try:
    Draft202012Validator(schema).validate(payload)
  except ValidationError:
    return

  raise AssertionError("return_to.outer_node は必須")


def test_side_track_state_allows_policy_violation_details():
  schema = _load_schema()
  payload = _valid_payload()
  payload["manifest_status"] = "policy_violation"
  payload["policy_violations"] = [
    {
      "path": "tools/api_providers/review_triage.py",
      "violation_type": "forbidden_change_during_post_write",
      "required_action": "complete_post_write_verification_before_tool_changes"
    }
  ]

  Draft202012Validator(schema).validate(payload)
