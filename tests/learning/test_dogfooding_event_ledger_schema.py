"""D-008 dogfooding event ledger schema の契約テスト。"""
import json
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "learning" / "workflow" / "schemas" / "dogfooding-event-ledger.schema.json"

EVENT_TYPES = [
  "review_run",
  "triage_decision",
  "proxy_decision",
  "workflow_precheck",
  "post_write_verification",
  "reopen",
  "commit_guard",
  "push_guard",
  "finding_fix_traceability",
  "tdd_cycle",
  "side_track_state",
  "model_assignment_cost",
]


def _load_schema():
  return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _valid_payload():
  return {
    "ledger_id": "dogfooding-ledger-2026-06-09",
    "schema_version": 1,
    "project_id": "reviewcompass",
    "events": [
      {
        "event_id": "event-001",
        "event_type": "review_run",
        "occurred_at": "2026-06-09T06:30:00+00:00",
        "source_ref": "docs/notes/review-runs/example/rounds.yaml",
        "payload": {
          "run_id": "example"
        }
      },
      {
        "event_id": "event-002",
        "event_type": "tdd_cycle",
        "occurred_at": "2026-06-09T06:31:00+00:00",
        "source_ref": "learning/workflow/schemas/tdd-cycle.schema.json",
        "payload": {
          "cycle_id": "TDD-2026-06-09-001",
          "linked_finding_ids": ["finding-001"]
        }
      }
    ]
  }


def test_dogfooding_event_ledger_schema_is_valid_json_schema():
  schema = _load_schema()
  Draft202012Validator.check_schema(schema)


def test_dogfooding_event_ledger_event_type_enum_matches_d008_contract():
  schema = _load_schema()
  enum = schema["properties"]["events"]["items"]["properties"]["event_type"]["enum"]
  assert enum == EVENT_TYPES


def test_dogfooding_event_ledger_accepts_multiple_event_types():
  schema = _load_schema()
  Draft202012Validator(schema).validate(_valid_payload())


def test_dogfooding_event_ledger_rejects_unknown_event_type():
  schema = _load_schema()
  payload = _valid_payload()
  payload["events"][0]["event_type"] = "unknown_event"

  try:
    Draft202012Validator(schema).validate(payload)
  except ValidationError:
    return

  raise AssertionError("event_type は D-008 enum のみ許容する")


def test_dogfooding_event_ledger_requires_relative_source_ref():
  schema = _load_schema()
  payload = _valid_payload()
  payload["events"][0]["source_ref"] = "/Users/Daily/Development/ReviewCompass/rounds.yaml"

  try:
    Draft202012Validator(schema).validate(payload)
  except ValidationError:
    return

  raise AssertionError("source_ref は relative path のみ許容する")
