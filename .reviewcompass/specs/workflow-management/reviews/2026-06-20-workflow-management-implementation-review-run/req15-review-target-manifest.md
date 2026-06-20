---
target_id: workflow-management-implementation-req15-2026-06-20
phase: implementation.triad-review
---

# Req 15 Review Target Manifest

Review the current contents of the review target files below. This file list is authoritative for the Req 15 implementation review target; the criteria draft is the judgment criteria, not the target file source of truth.

## Source Materials

The following upstream documents are source materials for judging intent transfer. They are not review target files and should not be evaluated as implementation artifacts in this run.

- `.reviewcompass/specs/workflow-management/requirements.md`
- `.reviewcompass/specs/workflow-management/design.md`
- `.reviewcompass/specs/workflow-management/tasks.md`

## Review Target Files

Req 15 schemas and implementation:

- `.reviewcompass/schema/language_task_io.schema.json`
- `.reviewcompass/schema/effective_prompt_manifest.schema.json`
- `tools/check-workflow-action.py`
- `tools/check_workflow_action/effective_prompt_builder.py`
- `tools/check_workflow_action/prompt_audit.py`
- `tools/api_providers/run_role.py`
- `tools/api_providers/run_review.py`

Req 15 focused and compatibility tests:

- `tests/workflow-management/test_language_task_io_schema.py`
- `tests/workflow-management/test_effective_prompt_manifest.py`
- `tests/workflow-management/test_prompt_audit.py`
- `tests/workflow-management/test_prompt_manifest_rounds_recording.py`
- `tools/api_providers/tests/test_run_role.py`
- `tools/api_providers/tests/test_run_review.py`

Verification snapshot:

- `.venv/bin/python3 -m pytest tests/workflow-management/test_language_task_io_schema.py tests/workflow-management/test_effective_prompt_manifest.py tests/workflow-management/test_prompt_audit.py tests/workflow-management/test_prompt_manifest_rounds_recording.py -q`: `9 passed`
- `.venv/bin/python3 -m pytest tools/api_providers/tests/test_run_role.py tools/api_providers/tests/test_run_review.py -q`: `31 passed`
- `.venv/bin/python3 -m pytest tests/workflow-management -q`: `55 passed`
