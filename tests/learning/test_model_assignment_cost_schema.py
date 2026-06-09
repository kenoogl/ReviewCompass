"""D-019 time / cost / model assignment schema の契約テスト。"""
import json
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "learning" / "workflow" / "schemas" / "model-assignment-cost.schema.json"

REQUIRED_FIELDS = [
  "event_type",
  "run_id",
  "schema_version",
  "source_ref",
  "role_assignments",
  "summary",
]


def _load_schema():
  return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _valid_payload():
  return {
    "event_type": "model_assignment_cost",
    "run_id": "postwrite-example-2026-06-09-r1",
    "schema_version": 1,
    "source_ref": "docs/notes/review-runs/postwrite-example-2026-06-09-r1/rounds.yaml",
    "role_assignments": [
      {
        "role": "primary",
        "provider": "openai-api",
        "model_id": "gpt-5.4",
        "invocation_path": "tools/api_providers/run_role.py",
        "attempts": 2,
        "retry_count": 1,
        "duration_seconds": 18.25,
        "token_usage": {
          "prompt_tokens": 1200,
          "completion_tokens": 500,
          "total_tokens": 1700,
          "source": "provider_reported"
        },
        "api_cost": {
          "amount": 0.042,
          "currency": "USD",
          "source": "estimated"
        },
        "contribution": {
          "findings_reported": 3,
          "findings_accepted": 1,
          "findings_rejected": 2
        }
      },
      {
        "role": "judgment",
        "provider": "google",
        "model_id": "gemini-3.5-flash",
        "invocation_path": "tools/api_providers/run_role.py",
        "attempts": 1,
        "retry_count": 0,
        "duration_seconds": 9.1,
        "token_usage": {
          "prompt_tokens": None,
          "completion_tokens": None,
          "total_tokens": None,
          "source": "missing"
        },
        "api_cost": {
          "amount": None,
          "currency": "USD",
          "source": "missing"
        },
        "contribution": {
          "findings_reported": 0,
          "findings_accepted": 0,
          "findings_rejected": 0
        }
      }
    ],
    "summary": {
      "total_duration_seconds": 27.35,
      "total_retry_count": 1,
      "total_api_cost": 0.042,
      "cost_completeness": "partial",
      "token_completeness": "partial"
    }
  }


def test_model_assignment_cost_schema_is_valid_json_schema():
  schema = _load_schema()
  Draft202012Validator.check_schema(schema)


def test_model_assignment_cost_required_fields_match_d019_contract():
  schema = _load_schema()
  assert schema["required"] == REQUIRED_FIELDS


def test_model_assignment_cost_accepts_recorded_and_missing_cost_data():
  schema = _load_schema()
  Draft202012Validator(schema).validate(_valid_payload())


def test_model_assignment_cost_requires_retry_count_to_match_attempts():
  schema = _load_schema()
  payload = _valid_payload()
  payload["role_assignments"][0]["attempts"] = 1
  payload["role_assignments"][0]["retry_count"] = 1

  try:
    Draft202012Validator(schema).validate(payload)
  except ValidationError:
    return

  raise AssertionError("attempts=1 の role assignment は retry_count=1 を許容しない")


def test_model_assignment_cost_requires_relative_source_ref():
  schema = _load_schema()
  payload = _valid_payload()
  payload["source_ref"] = "/Users/Daily/Development/ReviewCompass/docs/notes/review-runs/example/rounds.yaml"

  try:
    Draft202012Validator(schema).validate(payload)
  except ValidationError:
    return

  raise AssertionError("source_ref は relative path のみ許容する")
