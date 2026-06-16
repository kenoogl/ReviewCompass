# workflow-management implementation triad-review target

## 1. Review Purpose

This target is for the implementation triad-review of workflow-management Req 12 / T-014: operation registry / read-only preflight.

The reviewer should verify whether the implementation provides a generic, LLM-independent, read-only preflight foundation that reduces command/path/phase/artifact mistakes without creating artifacts during preflight.

## 2. Source Documents

- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/tasks.md`
- `docs/notes/2026-06-16-workflow-recovery-smell-inventory.md`

## 3. Changed Implementation Artifacts

- `tools/check-workflow-action.py`
  - Adds `operation-preflight --operation-id ... [--json]`.
  - Dispatches to `check_workflow_action.operation_preflight.run_preflight`.
- `tools/check_workflow_action/operation_registry.py`
  - Loads and validates `stages/operation-registry.yaml`.
  - Enforces operation schema, family-required checks, vocabulary references, sequence mode vocabulary, and LLM/provider/model field exclusion.
- `tools/check_workflow_action/operation_preflight.py`
  - Produces a read-only preflight response for registered operations.
  - Validates canonical command/subcommand/options against a local known-invocation registry.
  - Adapts `next --json` into stable `state_refs.next_action` dimensions.
  - Checks deployment planned output boundaries without probing or creating external paths.
- `stages/operation-registry.yaml`
  - Adds initial operation contracts for workflow next, review-run create, triage decide, commit approval chain, session capture, nested issue control, and deployment export.
- `tests/tools/test_operation_registry_preflight.py`
  - Adds TDD coverage for schema requirements, next state dimensions, command option mismatch, review-artifact checks, deployment boundary, and LLM-provider independence.

## 4. Implementation Diff Summary

### 4.1 `tools/check-workflow-action.py`

```diff
+from check_workflow_action.operation_preflight import run_preflight
+
+def cmd_operation_preflight(args):
+  """operation-preflight サブコマンドのエントリポイント（Req 12）"""
+  response = run_preflight(Path.cwd(), args.operation_id)
+  if args.json:
+    print(json.dumps(response, ensure_ascii=False, indent=2))
+  else:
+    print(f"[VERDICT] {response['verdict']}")
+    for reason in response.get("reasons", []):
+      print(f"[REASON] {reason}")
+    print(f"[ACTION] {response.get('next_step')}")
+  if response["verdict"] == "OK":
+    return 0
+  if response["verdict"] == "WARN":
+    return 1
+  return 2
+
+  opf = sub.add_parser(
+    "operation-preflight",
+    help="operation registry に基づく read-only preflight を行う（Req 12）",
+    parents=[common_parser],
+  )
+  opf.add_argument("--operation-id", required=True, help="preflight 対象の operation_id")
+
+  elif args.subcommand == "operation-preflight":
+    sys.exit(cmd_operation_preflight(args))
```

## 5. Key Code Excerpts

### 5.1 Registry schema and family checks

```python
DEFAULT_OPERATION_REGISTRY_PATH = "stages/operation-registry.yaml"

FORBIDDEN_LLM_FIELDS = {
  "llm",
  "provider",
  "model",
  "model_id",
  "proxy_model_id",
}

VALID_KINDS = {
  "irreversible",
  "review_artifact",
  "workflow_state",
  "evidence_capture",
  "deployment_export",
}

VALID_OPERATION_FAMILIES = {
  "review_artifact",
  "workflow_cli",
  "commit_approval_chain",
  "session_record_capture",
  "deployment_export",
  "nested_issue_control",
}

VALID_SEQUENCE_MODES = {
  "parallel_ok",
  "serial_only",
}
```

```python
FAMILY_REQUIRED_CHECKS = {
  "review_artifact": {
    "target_manifest_alignment",
    "bundle_non_empty",
    "criteria_alignment",
    "document-type_alignment",
    "approval_record_alignment",
    "existing_artifact_drift",
    "staged-vs-unstaged_target_selection",
  },
  "workflow_cli": {
    "parser_invocation",
    "workflow_binding",
    "next_active_state_dimensions",
    "scope_consistency",
  },
  "commit_approval_chain": {
    "nonce",
    "target_digest",
    "staged_file_set_digest",
    "staged_content_approval_digest",
    "expiry",
    "consume",
    "invalidated",
    "target",
  },
  "session_record_capture": {
    "session_record_mode",
    "current_session_id",
    "target_session_id",
    "current_session_formal_output_forbidden",
  },
  "deployment_export": {
    "planned_outputs",
    "overwrite_policy",
    "external_output_root",
    "target_app_root",
  },
  "nested_issue_control": {
    "parent_task",
    "discovered_issue",
    "relation",
    "allowed_files",
    "return_condition",
    "nesting_depth",
  },
}
```

```python
def validate_operation(operation):
  reasons = []
  if not isinstance(operation, dict):
    return ["operation は mapping である必要があります"]

  forbidden = _contains_forbidden_field(operation)
  if forbidden:
    reasons.append(f"LLM/provider/model 系 field は registry に含められません: {forbidden}")

  for field in REQUIRED_FIELDS:
    if field not in operation:
      reasons.append(f"operation registry field が欠落しています: {field}")
```

### 5.2 Known invocation and preflight response

```python
KNOWN_INVOCATIONS = {
  "tools/check-workflow-action.py": {
    "next": {"--json", "--log-path"},
    "operation-preflight": {"--json", "--log-path", "--operation-id"},
    "review-wave-summary": {"--json", "--log-path", "--out", "--save"},
    "decision-source-lint": {"--json", "--log-path", "--all", "--verify-pending"},
  },
  "tools/api_providers/run_review.py": {
    None: {
      "--variant",
      "--target",
      "--phase",
      "--criteria",
      "--review-run-dir",
      "--round-id",
      "--config",
      "--prior-finding",
      "--effective-prompt-path",
      "--effective-prompt-sha256",
    },
  },
  "tools/api_providers/review_triage.py": {
    "decide": {
      "--review-run-dir",
      "--finding-id",
      "--final-label",
      "--decision-reason",
      "--decision-actor",
      "--approval-record",
    },
    "assert-apply-fixes-ready": {
      "--review-run-dir",
      "--approval-record",
    },
  },
  "tools/build-deploy-package.py": {
    None: {"--out", "--manifest", "--target-app-root"},
  },
}
```

```python
NEXT_DIMENSION_KEYS = [
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
]
```

```python
def _build_response(operation_id, operation=None, verdict="DEVIATION", reasons=None, next_action=None):
  reasons = list(reasons or [])
  sequence_mode = (operation or {}).get("sequence_mode")
  return {
    "schema_version": "operation-preflight-v1",
    "operation_id": operation_id,
    "verdict": verdict,
    "allowed_verdicts": ALLOWED_VERDICTS,
    "sequence_mode": sequence_mode,
    "allowed_sequence_modes": ALLOWED_SEQUENCE_MODES,
    "state_refs": {
      "next_action": next_action,
      "workflow_state_files": next_action.get("state_files") if isinstance(next_action, dict) else [],
      "git_index": None,
    },
    "required_inputs": list((operation or {}).get("required_inputs") or []),
    "missing_inputs": [],
    "template_available": False,
    "target_identity": list((operation or {}).get("target_identity") or []),
    "worktree_state": {},
    "pending_conflicts": [],
    "integrity_conflicts": [],
    "checks": [{"status": "failed" if reasons else "ok", "reasons": reasons}],
    "planned_outputs": list((operation or {}).get("planned_outputs") or []),
    "canonical_commands": [],
    "next_step": "stop" if verdict == "DEVIATION" else "proceed",
    "reasons": reasons,
  }
```

### 5.3 Read-only deployment boundary check

```python
def _validate_deployment_boundary(operation):
  if operation.get("operation_family") != "deployment_export":
    return []
  reasons = []
  for output in operation.get("planned_outputs") or []:
    path = Path(str(output))
    if path.is_absolute():
      reasons.append(
        "deployment/export の planned_outputs は明示された external output root "
        f"なしに絶対パスを探索できません: {output}"
      )
  return reasons
```

## 6. Initial Registry Coverage

`stages/operation-registry.yaml` currently registers:

- `workflow_next_preflight`
- `review_run_create`
- `triage_decide`
- `commit_approval_chain_preflight`
- `session_record_capture_preflight`
- `nested_issue_preflight`
- `deployment_export_preflight`

Each operation includes:

- `operation_id`
- `kind`
- `operation_family`
- `canonical_invocation`
- `workflow_binding`
- `required_inputs`
- `target_identity`
- `planned_outputs`
- `sequence_mode`
- `worktree_policy`
- `pending_conflict_policy`
- `artifact_policy`
- `family_required_checks`
- `vocabulary_refs`

## 7. Test Evidence

### 7.1 Red test confirmation

Before implementation, the new test file was executed and failed because `operation-preflight` did not exist. This confirmed the tests were red for the intended missing behavior.

### 7.2 Passing verification after implementation

Commands run after implementation:

```text
python3 -m unittest tests.tools.test_operation_registry_preflight -v
```

Result:

```text
Ran 6 tests
OK
```

```text
python3 tools/check-workflow-action.py operation-preflight --operation-id workflow_next_preflight --json
```

Result:

```text
verdict: OK
state_refs.next_action includes current_mainline, required_action, phase, stage,
reopen_scope, impact_review_scope, direct_features, indirect_features,
flag_policy, next_pending_gate, next_drafting_gate, pending_gates,
completed_gates, superseded_gates, state_files.
```

```text
python3 -m unittest tests.tools.test_operation_registry_preflight tests.tools.test_review_wave_summary tests.tools.test_decision_source_lint -v
```

Result:

```text
Ran 20 tests
OK
```

```text
python3 -m unittest tests.tools.test_check_workflow_action -v
```

Result:

```text
Ran 189 tests
OK
```

```text
git diff --check
```

Result:

```text
OK
```

## 8. Review Questions

Please review for:

1. Whether the implementation satisfies Req 12 / T-014 at an implementation level.
2. Whether the preflight is truly read-only and avoids artifact creation before validation.
3. Whether the registry and response schema are generic enough for review-run, triage, commit approval, session capture, nested issue handling, and deployment/export.
4. Whether command/path mistakes are prevented by the known invocation checks, or whether this creates a brittle second parser that can drift from the real parser.
5. Whether `next --json` state dimensions are sufficient for a unique workflow situation.
6. Whether LLM/provider/model independence is preserved.
7. Whether existing workflow CLI behavior is likely to regress.

## 9. Severity Guidance

Use these labels:

- ERROR: behavior is wrong, unsafe, non-read-only, non-generic, LLM/provider-dependent, breaks existing CLI, or fails to prevent the target handback class.
- WARN: behavior is partial, brittle, under-specified, or likely to require follow-up before broad deployment.
- INFO: minor improvement, positive note, or documentation-only observation.
