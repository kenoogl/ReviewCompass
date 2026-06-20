---
target_id: workflow-management-implementation-req16-2026-06-20
phase: implementation.triad-review
---

# Req 16 Review Target Manifest

Review the current contents of the review target files below. This file list is authoritative for the Req 16 implementation review target; the criteria draft is the judgment criteria, not the target file source of truth.

## Source Materials

The following upstream documents are source materials for judging intent transfer. They are not review target files and should not be evaluated as implementation artifacts in this run.

- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/tasks.md`

## Review Target Files

Req 16 schemas and implementation:

- `.reviewcompass/schema/implementation_phase.schema.json`
- `.reviewcompass/schema/proxy_triage_decision.schema.json`
- `.reviewcompass/schema/operation_contract.schema.json`
- `.reviewcompass/schema/required_action.schema.json`
- `tools/check-workflow-action.py`
- `tools/check_workflow_action/implementation_phases.py`
- `tools/check_workflow_action/operation_contracts.py`
- `tools/check_workflow_action/operation_list.py`
- `tools/check_workflow_action/operation_registry.py`
- `tools/check_workflow_action/proxy_triage_decisions.py`

Req 16 focused and operation-contract tests:

- `tests/workflow-management/test_implementation_phase_plan.py`
- `tests/workflow-management/test_operation_list_read_only.py`
- `tests/workflow-management/test_proxy_triage_decision_machine.py`
- `tests/workflow-management/test_review_wave_consumer_impact.py`
- `tests/workflow-management/test_implementation_phase_cli.py`
- `tests/workflow-management/test_operation_contract_cli.py`
- `tests/workflow-management/test_operation_contract_schema.py`
- `tests/workflow-management/test_required_action_contract_mapping.py`

Verification snapshot:

- `.venv/bin/python3 -m pytest tests/workflow-management/test_implementation_phase_plan.py tests/workflow-management/test_operation_list_read_only.py tests/workflow-management/test_proxy_triage_decision_machine.py tests/workflow-management/test_review_wave_consumer_impact.py tests/workflow-management/test_implementation_phase_cli.py -q`: `13 passed`
- `.venv/bin/python3 -m pytest tests/workflow-management/test_operation_contract_cli.py tests/workflow-management/test_operation_contract_schema.py tests/workflow-management/test_required_action_contract_mapping.py -q`: `12 passed`
- `.venv/bin/python3 tools/check-workflow-action.py implementation-phase-check --feature workflow-management --json`: `verdict=OK`
- `.venv/bin/python3 tools/check-workflow-action.py operation-list --json`: `verdict=OK`, `operation_mode=read_only`
- `.venv/bin/python3 -m pytest tests/workflow-management -q`: `55 passed`
