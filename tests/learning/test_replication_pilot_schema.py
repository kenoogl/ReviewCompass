"""D-020 cross-repository replication pilot schema の契約テスト。"""
import json
from pathlib import Path

from jsonschema import Draft202012Validator, ValidationError

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "learning" / "workflow" / "schemas" / "replication-pilot.schema.json"

REQUIRED_FIELDS = [
  "record_type",
  "pilot_id",
  "schema_version",
  "source_ref",
  "repositories",
  "comparison_schema",
  "summary",
]

REQUIRED_REPOSITORY_FIELDS = [
  "repository_id",
  "repository_profile",
  "implementation_tasks",
  "deployment_smoke",
  "data_acquisition_run",
  "analysis_import",
]


def _load_schema():
  return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _repository(repository_id):
  return {
    "repository_id": repository_id,
    "repository_profile": {
      "language": "python",
      "size_class": "small",
      "has_existing_tests": True,
      "has_existing_specs": False
    },
    "implementation_tasks": [
      {
        "task_id": f"{repository_id}-task-001",
        "description": "Add a minimal parser behavior.",
        "review_run_refs": ["docs/notes/review-runs/example/rounds.yaml"],
        "triage_refs": ["docs/notes/review-runs/example/triage.yaml"],
        "fix_refs": ["learning/workflow/examples/finding-fix.yaml"],
        "test_evidence_refs": ["learning/workflow/examples/tdd-cycle.yaml"]
      }
    ],
    "deployment_smoke": {
      "status": "passed",
      "command": "reviewcompass smoke --app-root fixtures/repo-a",
      "evidence_refs": ["docs/notes/review-runs/example/target-manifest.yaml"]
    },
    "data_acquisition_run": {
      "status": "passed",
      "collected_data_areas": [
        "event",
        "finding",
        "finding_fix_traceability",
        "tdd_cycle",
        "model_assignment_cost"
      ],
      "evidence_refs": ["learning/workflow/schemas/dogfooding-event-ledger.schema.json"]
    },
    "analysis_import": {
      "status": "passed",
      "imported_tables": [
        "events",
        "findings",
        "tdd_cycles",
        "model_assignment_costs"
      ],
      "evidence_refs": ["learning/workflow/schemas/model-assignment-cost.schema.json"]
    }
  }


def _valid_payload():
  return {
    "record_type": "replication_pilot",
    "pilot_id": "D020-2026-06-09",
    "schema_version": 1,
    "source_ref": "docs/notes/2026-06-09-d020-cross-repository-replication-checklist.md",
    "repositories": [
      _repository("fixture-repo-a"),
      _repository("fixture-repo-b")
    ],
    "comparison_schema": {
      "data_areas": [
        "event",
        "finding",
        "finding_fix_traceability",
        "tdd_cycle",
        "model_assignment_cost"
      ],
      "schema_refs": [
        "learning/workflow/schemas/dogfooding-event-ledger.schema.json",
        "learning/workflow/schemas/normalized-finding.schema.json",
        "learning/workflow/schemas/tdd-cycle.schema.json",
        "learning/workflow/schemas/model-assignment-cost.schema.json"
      ]
    },
    "summary": {
      "pilot_status": "ready_for_pilot",
      "minimum_repository_count": 2,
      "completed_repository_count": 2,
      "blocking_gap_refs": []
    }
  }


def test_replication_pilot_schema_is_valid_json_schema():
  schema = _load_schema()
  Draft202012Validator.check_schema(schema)


def test_replication_pilot_required_fields_match_d020_contract():
  schema = _load_schema()
  assert schema["required"] == REQUIRED_FIELDS
  repo_schema = schema["properties"]["repositories"]["items"]
  assert repo_schema["required"] == REQUIRED_REPOSITORY_FIELDS


def test_replication_pilot_accepts_two_repository_payload():
  schema = _load_schema()
  Draft202012Validator(schema).validate(_valid_payload())


def test_replication_pilot_requires_at_least_two_repositories():
  schema = _load_schema()
  payload = _valid_payload()
  payload["repositories"] = payload["repositories"][:1]

  try:
    Draft202012Validator(schema).validate(payload)
  except ValidationError:
    return

  raise AssertionError("D-020 pilot は少なくとも 2 repository を要求する")


def test_replication_pilot_requires_all_three_run_results_per_repository():
  schema = _load_schema()
  payload = _valid_payload()
  del payload["repositories"][0]["analysis_import"]

  try:
    Draft202012Validator(schema).validate(payload)
  except ValidationError:
    return

  raise AssertionError("各 repository は deployment / acquisition / import 結果を要求する")


def test_replication_pilot_requires_relative_source_refs():
  schema = _load_schema()
  payload = _valid_payload()
  payload["source_ref"] = "/Users/Daily/Development/ReviewCompass/docs/notes/example.md"

  try:
    Draft202012Validator(schema).validate(payload)
  except ValidationError:
    return

  raise AssertionError("source_ref は relative path のみ許容する")
