"""operation registry / read-only preflight の TDD テスト（Req 12 / T-014）。

実装前の赤テストとして、registry schema、operation family、next state dimensions、
read-only 性、外部探索境界を固定する。
"""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "check-workflow-action.py"


FEATURES = [
  "foundation",
  "runtime",
  "evaluation",
  "analysis",
  "workflow-management",
  "self-improvement",
  "conformance-evaluation",
]


def run(args, cwd):
  return subprocess.run(
    ["python3", str(SCRIPT)] + list(args),
    cwd=str(cwd),
    capture_output=True,
    text=True,
    timeout=30,
  )


def write_feature_dependency(cwd):
  path = Path(cwd) / "stages" / "feature-dependency.yaml"
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(
      {"feature_order": FEATURES, "features": {f: {"depends_on": []} for f in FEATURES}},
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )


def write_specs(cwd):
  five = {
    "drafting": True,
    "triad-review": True,
    "review-wave": True,
    "alignment": True,
    "approval": True,
  }
  for feature in FEATURES:
    spec = {
      "feature_name": feature,
      "workflow_state": {
        "intent": {"drafting": True, "review": True, "approval": True},
        "feature-partitioning": {"candidate-proposal": True, "approval": True},
        "requirements": dict(five),
        "design": dict(five),
        "tasks": dict(five),
        "implementation": {
          "drafting": feature != "workflow-management",
          "triad-review": feature != "workflow-management",
          "review-wave": feature != "workflow-management",
          "alignment": feature != "workflow-management",
          "approval": feature != "workflow-management",
        },
      },
      "reopened": {},
      "recheck": {
        "upstream_change_pending": feature == "workflow-management",
        "impacted_downstream_phases": ["implementation"] if feature == "workflow-management" else [],
      },
    }
    path = Path(cwd) / ".reviewcompass" / "specs" / feature / "spec.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")


def write_reopen_state(cwd):
  path = Path(cwd) / "stages" / "in-progress" / "reopen-procedure-2026-06-16.yaml"
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump(
      {
        "process_id": "reopen-procedure",
        "feature": "workflow-management",
        "classification": "R-0",
        "scope_separation": {
          "reopen_scope": ["workflow-management"],
          "impact_review_scope": FEATURES,
          "flag_policy": {
            "reopen_existing_feature": "false に戻す",
            "indirect_check_only": "維持する",
          },
        },
        "feature_impact_decisions": [
          {
            "feature": f,
            "decision": "reopen_existing_feature" if f == "workflow-management" else "indirect_check_only",
            "impact_basis": "contract_ownership" if f == "workflow-management" else "consumer_or_derivative_only",
            "rationale": "test",
            "evidence": ["docs/reviews/test.md"],
          }
          for f in FEATURES
        ],
        "drafting_completed_gates": ["stages/implementation.yaml#drafting"],
        "pending_gates": [
          "stages/implementation.yaml#triad-review",
          "stages/implementation.yaml#review-wave",
          "stages/implementation.yaml#alignment",
          "stages/implementation.yaml#approval",
        ],
        "completed_gates": [
          "stages/requirements.yaml#approval",
          "stages/design.yaml#approval",
          "stages/tasks.yaml#approval",
        ],
        "downstream_impact_decisions": [
          {
            "gate": "stages/tasks.yaml#approval",
            "feature_scope": ",".join(FEATURES),
            "decision": "approved",
            "rationale": "test",
            "evidence": ["test"],
          }
        ],
      },
      allow_unicode=True,
      sort_keys=False,
    ),
    encoding="utf-8",
  )


def write_registry(cwd, operations):
  path = Path(cwd) / "stages" / "operation-registry.yaml"
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_text(
    yaml.safe_dump({"schema_version": "operation-registry-v1", "operations": operations}, allow_unicode=True, sort_keys=False),
    encoding="utf-8",
  )
  return path


def review_artifact_checks(*extra):
  return [
    "target_manifest_alignment",
    "bundle_non_empty",
    "criteria_alignment",
    "document-type_alignment",
    "approval_record_alignment",
    "existing_artifact_drift",
    "staged-vs-unstaged_target_selection",
    *extra,
  ]


def base_operation(**overrides):
  operation = {
    "operation_id": "workflow_next_preflight",
    "kind": "workflow_state",
    "operation_family": "workflow_cli",
    "canonical_invocation": {
      "entrypoint": "tools/check-workflow-action.py",
      "subcommand": "next",
      "options": ["--json"],
      "positional_args": [],
      "execution_context": "repo_root",
    },
    "workflow_binding": {
      "phase": "implementation",
      "stage": "triad-review",
      "gate": "stages/implementation.yaml#triad-review",
      "next_action_kind": "reopen_in_progress",
    },
    "required_inputs": ["stages/in-progress/reopen-procedure-2026-06-16.yaml"],
    "target_identity": ["workflow-management", "implementation"],
    "planned_outputs": [],
    "sequence_mode": "parallel_ok",
    "worktree_policy": "allow_dirty_read_only",
    "pending_conflict_policy": "allow_matching_reopen_only",
    "artifact_policy": "read_only",
    "family_required_checks": [
      "parser_invocation",
      "workflow_binding",
      "next_active_state_dimensions",
      "scope_consistency",
    ],
    "vocabulary_refs": ["verdict", "sequence_mode"],
  }
  operation.update(overrides)
  return operation


def review_artifact_operation(**overrides):
  operation = base_operation(
    operation_id="review_run_create",
    kind="review_artifact",
    operation_family="review_artifact",
    workflow_binding={"phase": None, "stage": None, "gate": None, "next_action_kind": None},
    canonical_invocation={
      "entrypoint": "tools/api_providers/run_review.py",
      "subcommand": None,
      "options": ["--target", "--phase", "--criteria", "--review-run-dir"],
      "positional_args": [],
      "execution_context": "repo_root",
    },
    required_inputs=["target-manifest.yaml"],
    target_identity=["target_side=unstaged", "target_files=docs/target.md"],
    planned_outputs=[".reviewcompass/specs/workflow-management/reviews/new-run"],
    sequence_mode="parallel_ok",
    worktree_policy="require_explicit_target_side",
    pending_conflict_policy="no_pending_review_artifact",
    artifact_policy="create_new_only",
    family_required_checks=review_artifact_checks(),
    vocabulary_refs=["verdict", "sequence_mode", "target_side"],
  )
  operation.update(overrides)
  return operation


def workflow_mixing_operation(**overrides):
  operation = base_operation(
    operation_id="workflow_mixing_preflight",
    kind="workflow_state",
    operation_family="workflow_cli",
    workflow_binding={
      "phase": "implementation",
      "stage": "triad-review",
      "gate": "stages/implementation.yaml#triad-review",
      "next_action_kind": "reopen_in_progress",
    },
    required_inputs=[
      "stages/in-progress/reopen-procedure-2026-06-16.yaml",
      "allowed_files=docs/allowed.md",
      "pending_unit=reopen-procedure",
    ],
    target_identity=["allowed_files=docs/allowed.md"],
    planned_outputs=[],
    sequence_mode="serial_only",
    worktree_policy="allow_matching_dirty_scope",
    pending_conflict_policy="stop_on_mixed_workflow_scope",
    artifact_policy="read_only",
    family_required_checks=[
      "parser_invocation",
      "workflow_binding",
      "next_active_state_dimensions",
      "scope_consistency",
      "workflow_mixing_preflight",
    ],
    vocabulary_refs=["verdict", "allowed_files", "pending_conflicts"],
  )
  operation.update(overrides)
  return operation


class OperationRegistryPreflightTests(unittest.TestCase):
  def setUp(self):
    self.tmp = Path(tempfile.mkdtemp())
    write_feature_dependency(self.tmp)
    write_specs(self.tmp)
    write_reopen_state(self.tmp)
    (self.tmp / "target-manifest.yaml").write_text(
      yaml.safe_dump({"target_files": ["docs/target.md"]}, allow_unicode=True, sort_keys=False),
      encoding="utf-8",
    )

  def tearDown(self):
    shutil.rmtree(self.tmp, ignore_errors=True)

  def test_registry_schema_requires_vocabulary_refs_and_family_checks(self):
    operation = base_operation()
    operation.pop("vocabulary_refs")
    write_registry(self.tmp, [operation])

    result = run(["operation-preflight", "--operation-id", "workflow_next_preflight", "--json"], self.tmp)

    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("vocabulary_refs", "\n".join(data["reasons"]))

  def test_workflow_preflight_includes_next_state_dimensions(self):
    write_registry(self.tmp, [base_operation()])

    result = run(["operation-preflight", "--operation-id", "workflow_next_preflight", "--json"], self.tmp)

    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    next_action = data["state_refs"]["next_action"]
    for key in [
      "current_mainline",
      "required_action",
      "phase",
      "stage",
      "reopen_scope",
      "impact_review_scope",
      "direct_features",
      "indirect_features",
      "flag_policy",
      "next_pending_gate",
      "next_drafting_gate",
      "pending_gates",
      "completed_gates",
      "superseded_gates",
      "state_files",
    ]:
      self.assertIn(key, next_action)
    self.assertEqual(next_action["phase"], "implementation")
    self.assertEqual(next_action["stage"], "triad-review")
    self.assertEqual(next_action["reopen_scope"], ["workflow-management"])
    self.assertIn("foundation", next_action["impact_review_scope"])

  def test_unknown_option_is_deviation_before_artifact_creation(self):
    operation = base_operation(
      canonical_invocation={
        "entrypoint": "tools/check-workflow-action.py",
        "subcommand": "next",
        "options": ["--json", "--file"],
        "positional_args": [],
        "execution_context": "repo_root",
      }
    )
    write_registry(self.tmp, [operation])

    result = run(["operation-preflight", "--operation-id", "workflow_next_preflight", "--json"], self.tmp)

    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("--file", "\n".join(data["reasons"]))

  def test_review_artifact_family_requires_criteria_document_type_and_target_selection(self):
    operation = base_operation(
      operation_id="review_run_create",
      kind="review_artifact",
      operation_family="review_artifact",
      family_required_checks=["target_manifest_alignment", "bundle_non_empty"],
      canonical_invocation={
        "entrypoint": "tools/api_providers/run_review.py",
        "subcommand": None,
        "options": ["--target", "--phase", "--criteria", "--review-run-dir"],
        "positional_args": [],
        "execution_context": "repo_root",
      },
    )
    write_registry(self.tmp, [operation])

    result = run(["operation-preflight", "--operation-id", "review_run_create", "--json"], self.tmp)

    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    reasons = "\n".join(data["reasons"])
    self.assertIn("criteria", reasons)
    self.assertIn("document-type", reasons)
    self.assertIn("staged-vs-unstaged", reasons)

  def test_existing_review_run_output_path_is_deviation_before_creation(self):
    existing = self.tmp / ".reviewcompass/specs/workflow-management/reviews/existing-run"
    existing.mkdir(parents=True)
    operation = review_artifact_operation(
      planned_outputs=[".reviewcompass/specs/workflow-management/reviews/existing-run"],
      family_required_checks=review_artifact_checks("output_path_collision"),
    )
    write_registry(self.tmp, [operation])

    result = run(["operation-preflight", "--operation-id", "review_run_create", "--json"], self.tmp)

    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    reasons = "\n".join(data["reasons"])
    self.assertIn(".reviewcompass/specs/workflow-management/reviews/existing-run", reasons)
    self.assertIn("already exists", reasons)

  def test_existing_manifest_bundle_or_approval_record_path_is_deviation_before_creation(self):
    paths = [
      ".reviewcompass/runtime/post-write/manifest.yaml",
      ".reviewcompass/runtime/review-bundles/bundle.md",
      ".reviewcompass/runtime/approvals/commit-approval.json",
    ]
    for path in paths:
      target = self.tmp / path
      target.parent.mkdir(parents=True, exist_ok=True)
      target.write_text("existing\n", encoding="utf-8")
    operation = review_artifact_operation(
      planned_outputs=paths,
      family_required_checks=review_artifact_checks("output_path_collision"),
    )
    write_registry(self.tmp, [operation])

    result = run(["operation-preflight", "--operation-id", "review_run_create", "--json"], self.tmp)

    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    reasons = "\n".join(data["reasons"])
    for path in paths:
      self.assertIn(path, reasons)
    self.assertIn("already exists", reasons)

  def test_empty_bundle_target_set_is_deviation(self):
    operation = review_artifact_operation(
      target_identity=["target_side=staged"],
      planned_outputs=[".reviewcompass/runtime/review-bundles/bundle.md"],
      family_required_checks=review_artifact_checks(),
    )
    write_registry(self.tmp, [operation])

    result = run(["operation-preflight", "--operation-id", "review_run_create", "--json"], self.tmp)

    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("empty", "\n".join(data["reasons"]).lower())

  def test_wrong_side_bundle_target_set_is_deviation(self):
    subprocess.run(["git", "init"], cwd=str(self.tmp), capture_output=True, text=True, check=True)
    changed = self.tmp / "docs/target.md"
    changed.parent.mkdir(parents=True, exist_ok=True)
    changed.write_text("unstaged change\n", encoding="utf-8")
    operation = review_artifact_operation(
      target_identity=["target_side=staged", "target_files=docs/target.md"],
      planned_outputs=[".reviewcompass/runtime/review-bundles/bundle.md"],
      family_required_checks=review_artifact_checks(),
    )
    write_registry(self.tmp, [operation])

    result = run(["operation-preflight", "--operation-id", "review_run_create", "--json"], self.tmp)

    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    reasons = "\n".join(data["reasons"]).lower()
    self.assertIn("staged", reasons)
    self.assertIn("docs/target.md", reasons)

  def test_related_artifact_target_sets_must_match(self):
    artifact_targets = {
      ".reviewcompass/runtime/approvals/review-approval.yaml": ["docs/target.md"],
      ".reviewcompass/specs/workflow-management/reviews/run/raw.yaml": ["docs/target.md"],
      ".reviewcompass/specs/workflow-management/reviews/run/triage.yaml": ["docs/other.md"],
      ".reviewcompass/runtime/post-write/manifest.yaml": ["docs/target.md"],
    }
    for path, targets in artifact_targets.items():
      target = self.tmp / path
      target.parent.mkdir(parents=True, exist_ok=True)
      target.write_text(
        yaml.safe_dump({"target_files": targets}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
      )
    operation = review_artifact_operation(
      required_inputs=[
        "target-manifest.yaml",
        "approval_record=.reviewcompass/runtime/approvals/review-approval.yaml",
        "raw_response=.reviewcompass/specs/workflow-management/reviews/run/raw.yaml",
        "triage=.reviewcompass/specs/workflow-management/reviews/run/triage.yaml",
        "manifest=.reviewcompass/runtime/post-write/manifest.yaml",
      ],
      family_required_checks=review_artifact_checks("related_artifact_target_set_consistency"),
    )
    write_registry(self.tmp, [operation])

    result = run(["operation-preflight", "--operation-id", "review_run_create", "--json"], self.tmp)

    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    reasons = "\n".join(data["reasons"])
    self.assertIn("target set", reasons)
    self.assertIn("docs/other.md", reasons)

  def test_deployment_export_does_not_probe_unregistered_external_roots(self):
    outside = self.tmp.parent / "unregistered-external-output"
    operation = base_operation(
      operation_id="deployment_export",
      kind="deployment_export",
      operation_family="deployment_export",
      planned_outputs=[str(outside / "bundle.tar.gz")],
      family_required_checks=[
        "planned_outputs",
        "overwrite_policy",
        "external_output_root",
        "target_app_root",
      ],
    )
    write_registry(self.tmp, [operation])

    result = run(["operation-preflight", "--operation-id", "deployment_export", "--json"], self.tmp)

    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("external", "\n".join(data["reasons"]).lower())
    self.assertFalse(outside.exists())

  def test_response_rejects_llm_provider_model_fields(self):
    operation = base_operation(model="gpt-5.4")
    write_registry(self.tmp, [operation])

    result = run(["operation-preflight", "--operation-id", "workflow_next_preflight", "--json"], self.tmp)

    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("model", "\n".join(data["reasons"]))

  def test_parser_help_option_is_accepted_without_static_known_invocation(self):
    operation = base_operation(
      operation_id="deployment_export",
      kind="deployment_export",
      operation_family="deployment_export",
      canonical_invocation={
        "entrypoint": "tools/build-deploy-package.py",
        "subcommand": None,
        "options": ["--manifest", "--out", "--verify"],
        "positional_args": [],
        "execution_context": "repo_root",
      },
      workflow_binding={"phase": None, "stage": None, "gate": None, "next_action_kind": None},
      required_inputs=["planned_outputs", "overwrite_policy", "external_output_root", "target_app_root"],
      planned_outputs=["dist/reviewcompass-bundle"],
      family_required_checks=[
        "planned_outputs",
        "overwrite_policy",
        "external_output_root",
        "target_app_root",
      ],
    )
    write_registry(self.tmp, [operation])

    result = run(["operation-preflight", "--operation-id", "deployment_export", "--json"], self.tmp)

    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")

  def test_family_required_checks_are_reported_individually(self):
    write_registry(self.tmp, [base_operation()])

    result = run(["operation-preflight", "--operation-id", "workflow_next_preflight", "--json"], self.tmp)

    self.assertEqual(result.returncode, 0, result.stderr)
    data = json.loads(result.stdout)
    checks = {check["name"]: check["status"] for check in data["checks"]}
    self.assertEqual(checks["parser_invocation"], "ok")
    self.assertEqual(checks["workflow_binding"], "ok")
    self.assertEqual(checks["next_active_state_dimensions"], "ok")
    self.assertEqual(checks["scope_consistency"], "ok")

  def test_unknown_declared_family_check_fails_closed(self):
    operation = base_operation(
      family_required_checks=[
        "parser_invocation",
        "workflow_binding",
        "next_active_state_dimensions",
        "scope_consistency",
        "future_unimplemented_check",
      ],
    )
    write_registry(self.tmp, [operation])

    result = run(["operation-preflight", "--operation-id", "workflow_next_preflight", "--json"], self.tmp)

    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("future_unimplemented_check", "\n".join(data["reasons"]))
    checks = {check["name"]: check["status"] for check in data["checks"]}
    self.assertEqual(checks["future_unimplemented_check"], "not_implemented")

  def test_deployment_export_rejects_relative_traversal_without_creating_path(self):
    outside = self.tmp.parent / "outside-bundle"
    operation = base_operation(
      operation_id="deployment_export",
      kind="deployment_export",
      operation_family="deployment_export",
      workflow_binding={"phase": None, "stage": None, "gate": None, "next_action_kind": None},
      required_inputs=["planned_outputs", "overwrite_policy", "external_output_root", "target_app_root"],
      planned_outputs=["../outside-bundle/reviewcompass.tar.gz"],
      family_required_checks=[
        "planned_outputs",
        "overwrite_policy",
        "external_output_root",
        "target_app_root",
      ],
    )
    write_registry(self.tmp, [operation])

    result = run(["operation-preflight", "--operation-id", "deployment_export", "--json"], self.tmp)

    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("traversal", "\n".join(data["reasons"]).lower())
    self.assertFalse(outside.exists())

  def test_json_response_includes_exit_code_contract(self):
    operation = base_operation()
    operation.pop("vocabulary_refs")
    write_registry(self.tmp, [operation])

    result = run(["operation-preflight", "--operation-id", "workflow_next_preflight", "--json"], self.tmp)

    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["exit_code_contract"]["OK"], 0)
    self.assertEqual(data["exit_code_contract"]["WARN"], 1)
    self.assertEqual(data["exit_code_contract"]["DEVIATION"], 2)

  def test_missing_required_input_file_is_deviation_and_reported(self):
    operation = base_operation(
      required_inputs=[
        "stages/in-progress/reopen-procedure-2026-06-16.yaml",
        "docs/reviews/missing-required-input.md",
      ],
    )
    write_registry(self.tmp, [operation])

    result = run(["operation-preflight", "--operation-id", "workflow_next_preflight", "--json"], self.tmp)

    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertIn("docs/reviews/missing-required-input.md", data["missing_inputs"])
    self.assertIn("必須入力", "\n".join(data["reasons"]))

  def test_session_record_formal_current_session_is_deviation(self):
    operation = base_operation(
      operation_id="session_record_capture_preflight",
      kind="evidence_capture",
      operation_family="session_record_capture",
      workflow_binding={"phase": None, "stage": None, "gate": None, "next_action_kind": None},
      required_inputs=[
        "session_record_mode=formal",
        "current_session_id=codex-current",
        "target_session_id=codex-current",
      ],
      target_identity=["codex-current"],
      planned_outputs=[],
      sequence_mode="serial_only",
      worktree_policy="allow_dirty_read_only",
      pending_conflict_policy="allow_matching_capture",
      artifact_policy="read_only",
      family_required_checks=[
        "session_record_mode",
        "current_session_id",
        "target_session_id",
        "current_session_formal_output_forbidden",
      ],
      vocabulary_refs=["session_record_mode"],
    )
    write_registry(self.tmp, [operation])

    result = run(["operation-preflight", "--operation-id", "session_record_capture_preflight", "--json"], self.tmp)

    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(data["state_refs"]["current_session_id"], "codex-current")
    self.assertEqual(data["state_refs"]["target_session_id"], "codex-current")
    self.assertEqual(data["state_refs"]["session_record_mode"], "formal")
    self.assertIn("current session", "\n".join(data["reasons"]))

  def _prepare_dirty_git_scope(self, changed_files):
    subprocess.run(["git", "init"], cwd=str(self.tmp), capture_output=True, text=True, check=True)
    for rel_path in ["docs/allowed.md", "docs/outside.md"]:
      path = self.tmp / rel_path
      path.parent.mkdir(parents=True, exist_ok=True)
      path.write_text("base\n", encoding="utf-8")
    subprocess.run(
      ["git", "add", "docs/allowed.md", "docs/outside.md"],
      cwd=str(self.tmp),
      capture_output=True,
      text=True,
      check=True,
    )
    for rel_path in changed_files:
      (self.tmp / rel_path).write_text("changed\n", encoding="utf-8")

  def test_workflow_mixing_preflight_reports_files_outside_allowed_scope(self):
    self._prepare_dirty_git_scope(["docs/allowed.md", "docs/outside.md"])
    write_registry(self.tmp, [workflow_mixing_operation()])

    result = run(["operation-preflight", "--operation-id", "workflow_mixing_preflight", "--json"], self.tmp)

    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "DEVIATION")
    self.assertEqual(data["worktree_state"]["allowed_files"], ["docs/allowed.md"])
    self.assertEqual(data["worktree_state"]["changed_files"], ["docs/allowed.md", "docs/outside.md"])
    self.assertEqual(data["worktree_state"]["out_of_scope_changed_files"], ["docs/outside.md"])
    self.assertIn("docs/outside.md", "\n".join(data["reasons"]))

  def test_workflow_mixing_preflight_returns_conflict_resolution_choices(self):
    self._prepare_dirty_git_scope(["docs/allowed.md", "docs/outside.md"])
    write_registry(self.tmp, [workflow_mixing_operation()])

    result = run(["operation-preflight", "--operation-id", "workflow_mixing_preflight", "--json"], self.tmp)

    self.assertEqual(result.returncode, 2)
    data = json.loads(result.stdout)
    conflict = data["pending_conflicts"][0]
    self.assertEqual(conflict["kind"], "workflow_mixing")
    self.assertEqual(conflict["pending_unit"], "reopen-procedure")
    self.assertEqual(
      [
        "complete_pending",
        "use_separate_worktree",
        "park_as_blocker_or_side_track",
      ],
      conflict["resolution_choices"],
    )

  def test_workflow_mixing_preflight_accepts_matching_dirty_scope(self):
    self._prepare_dirty_git_scope(["docs/allowed.md"])
    write_registry(self.tmp, [workflow_mixing_operation()])

    result = run(["operation-preflight", "--operation-id", "workflow_mixing_preflight", "--json"], self.tmp)

    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(result.stdout)
    self.assertEqual(data["verdict"], "OK")
    self.assertEqual(data["worktree_state"]["allowed_files"], ["docs/allowed.md"])
    self.assertEqual(data["worktree_state"]["changed_files"], ["docs/allowed.md"])
    self.assertEqual(data["worktree_state"]["out_of_scope_changed_files"], [])
    self.assertEqual(data["pending_conflicts"], [])


if __name__ == "__main__":
  unittest.main()
