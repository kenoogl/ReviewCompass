---
criteria_id: workflow-management-implementation-req15-review-2026-06-20-draft
phase: implementation.triad-review
review_target: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-run/req15-review-target-manifest.md
intended_actual_run_dir: .reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-req15-review-run
intended_variant: implementation_review_independent_3way_codex_operator
---

# Req 15 Implementation Review Criteria Draft

## Review Task

Primary judgment question:

Does the Req 15 implementation correctly separate structured language-task judgment from machine execution, while preserving review-run effective prompt metadata compatibility?

## User Review Requirements

This is one item-specific prompt for `workflow-management / implementation / triad-review`.

- Review purpose: defect detection for Req 15 implementation.
- Review object: structured prompt schemas, prompt audit/builder, review-run rounds metadata plumbing, and tests.
- Review focus: language_task schema vocabulary, prompt manifest source/digest coverage, machine task exclusion, on_completion compatibility, prompt manifest recording without deleting existing text prompt metadata.
- Scope boundaries: do not review Req 14 approval gate or Req 16 phase/proxy controls except where the prompt audit directly references those boundaries.
- Prohibited actions: do not authorize commit, push, phase completion, approval, proxy application, or spec.json update.

## Review Target

The authoritative target file list is `req15-review-target-manifest.md`. The actual run must pass that manifest and every file listed there as target files. The inline summary below is for human readability only; if it differs from the manifest, report the mismatch.

Human-readable target summary: language task and effective prompt manifest schemas; effective prompt builder; prompt audit; `prompt-audit` CLI wiring; `run_role.py` / `run_review.py` only for prompt manifest metadata recording; and the four focused T-018 test files.

## Source Materials

Requirement 15 requires:

- `language_task` with `document_kind`, `input`, `output_format`, and `constraints`;
- `input.required_files`, `input.state_refs`, `input.source_refs`;
- `output_format.kind`, `output_format.required_sections`, and `output_format.schema_ref`;
- effective prompt manifest with `decision_point`, `source_artifacts`, `required_disciplines`, `operation_contract`, `expected_output_schema`, `prompt_length`, `preconditions_checked`, `language_task`, `postconditions`, and `on_completion`;
- prompt audit that detects source/digest gaps, machine task leakage, direct state mutation, output schema gaps, prompt length bounds issues, and next-action/on_completion conflict;
- review-run `rounds.yaml` recording of prompt manifest path/sha256 while preserving existing effective prompt path/sha256 fields.

Design intent, paraphrased from `.reviewcompass/specs/workflow-management/design.md` Requirement 15:

- `language_task` describes what the model judges; it must not include git operations, review-run artifact creation, approval consume, side-track mutation, operation execution, or direct workflow/spec mutation;
- `prompt-audit` is read-only and cannot itself authorize completion, commit, push, approval, or state mutation;
- `run_role.py` and `run_review.py` may write review-run artifacts as part of their existing review-run artifact responsibility, but the Req 15 change is limited to adding prompt manifest metadata fields and must not replace text effective prompt metadata.

Tasks intent:

- T-018 required red tests first and implementation without altering those tests;
- text-only effective prompt fields remain P1-compatible during transition;
- manifest field presence should improve auditability without breaking existing review-run consumers.

Verification before review:

- Structured evidence:
  - command: `.venv/bin/python3 -m pytest tests/workflow-management/test_language_task_io_schema.py tests/workflow-management/test_effective_prompt_manifest.py tests/workflow-management/test_prompt_audit.py tests/workflow-management/test_prompt_manifest_rounds_recording.py -q`
  - observed result: `9 passed`
  - scope: language task schema, manifest schema, prompt audit, rounds manifest metadata.
- Related review-run artifact tests:
  - command: `.venv/bin/python3 -m pytest tools/api_providers/tests/test_run_role.py tools/api_providers/tests/test_run_review.py -q`
  - observed result: `31 passed`
  - scope: single-role and multi-role review-run artifact recording.

## Required Checks

1. Check that schema vocabulary is fail-closed for unknown machine-action fields.
2. Check that `prompt_audit.py` rejects direct state mutation, machine execution tasks, and incompatible `on_completion`.
3. Check that read-only `prompt-audit` CLI does not write state or consume approvals.
4. Check that `run_role.py` and `run_review.py` preserve existing effective prompt fields while adding manifest fields.
5. Check that source/digest/prompt length structures require at least `source_artifacts[].path`, `source_artifacts[].sha256`, `operation_contract.operation_id`, `operation_contract.sha256`, `prompt_length.min_chars`, `prompt_length.max_chars`, `prompt_length.source_ref`, and `prompt_length.failure_verdict`.
6. Check that tests include negative coverage for machine-task leakage, unknown fields, missing source digest, prompt bounds, on_completion conflict, and metadata coexistence.

## Out Of Scope

- General quality of all API provider code unrelated to prompt manifest metadata.
- Req 14 approval gate implementation.
- Req 16 proxy triage decision implementation.
- Any phase movement or approval.

## Finding Policy

Return YAML only, without Markdown fences.

Use `CRITICAL` for prompt audit or metadata plumbing that authorizes or implies irreversible actions. Use `ERROR` for schema/audit defects that permit machine execution leakage or lose required metadata. Use `WARN` for meaningful compatibility or coverage gaps. Use `INFO` for minor maintainability or wording issues that do not affect safety or auditability.

Return the parser-compatible YAML shape defined by the review runner. Return `findings: []` only when no actionable implementation issue is found for Req 15.
