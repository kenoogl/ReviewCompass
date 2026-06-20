---
criteria_id: workflow-management-implementation-req15-structured-effective-prompt-transfer-review-criteria
phase: implementation
status: prompt_quality_reviewed_nonblocking_warnings_addressed
---

# workflow-management implementation req15-structured-effective-prompt-transfer API Review Criteria

## Review Task

Review the target for: Req 15 implementation upstream transfer for structured effective prompt and prompt audit.

Primary judgment question:

Does the target satisfy Req 15 implementation upstream transfer for structured effective prompt and prompt audit, while carrying upstream purpose, responsibility boundaries, acceptance criteria, forbidden actions, unresolved items, and intended transfer without omission, weakening, contradiction, unsupported addition, or drift?

Do not combine multiple independent judgments in this prompt. If another cluster, finding, artifact, or design-policy judgment is needed, create a separate criteria file and run separate prompt-quality review.

## User Review Requirements

- Review purpose: workflow-management implementation triad-review
- Review object: Req 15 implementation artifacts
- Review focus:
  - language task and machine task separation
  - effective prompt manifest and metadata recording
  - prompt audit fail-closed checks
- Scope boundaries:
  - In scope:
    - Req 15 schemas, implementation, compatibility paths, and focused tests
  - Out of scope:
    - Req 14 approval gate state
    - Req 16 proxy triage decision mechanics
- Output requirements:
  - parser-compatible findings
- Prohibited actions:
  - commit
  - push
  - spec.json update
  - phase completion
- Requirement-to-prompt mapping:
  - Review purpose -> Review Task and Required Checks
  - Review focus -> Required Checks
  - Scope boundaries -> Review Target and Out Of Scope
  - Prohibited actions -> Out Of Scope and Finding Policy

## Generic API Review Core

- Keep criteria and target roles distinct.
- Treat the target files as the only review target.
- Treat source materials as background or intent-transfer evidence, not as targets.
- Do not use path-only source materials as model-readable evidence.
- Ask one non-leading primary judgment question.
- Preserve user review requirements without narrowing, broadening, or replacement.
- Exclude credentials, personal identifiers, third-party non-sendable confidential material, and unrelated logs.
- Return parser-compatible findings only.

## Review Target

The authoritative target file set is
`.reviewcompass/specs/workflow-management/reviews/2026-06-20-workflow-management-implementation-review-run/req15-review-target-manifest.md`
and the target files supplied by the review runner. The list below is an orientation
copy only; if it diverges from the manifest or runner target set, treat the manifest
and runner target set as authoritative and report the mismatch.

- `.reviewcompass/schema/language_task_io.schema.json`
- `.reviewcompass/schema/effective_prompt_manifest.schema.json`
- `tools/check-workflow-action.py`
- `tools/check_workflow_action/effective_prompt_builder.py`
- `tools/check_workflow_action/prompt_audit.py`
- `tools/api_providers/run_role.py`
- `tools/api_providers/run_review.py`
- `tests/workflow-management/test_language_task_io_schema.py`
- `tests/workflow-management/test_effective_prompt_manifest.py`
- `tests/workflow-management/test_prompt_audit.py`
- `tests/workflow-management/test_prompt_manifest_rounds_recording.py`
- `tools/api_providers/tests/test_run_role.py`
- `tools/api_providers/tests/test_run_review.py`

Do not treat this criteria file, a wrapper, or an author-written summary as a substitute for the target.

## Source Materials

### workflow-management-req15-upstream-intent

Purpose: Requirement 15 / design / tasks intent for structured effective prompts and prompt audit.
This is a structured summary of the upstream phase chain, paraphrased from
`.reviewcompass/specs/workflow-management/requirements.md`,
`.reviewcompass/specs/workflow-management/design.md`, and
`.reviewcompass/specs/workflow-management/tasks.md`. Use it as intent-transfer
evidence; do not treat it as a replacement for target files.

- purpose: Treat effective prompts as structured language-task specifications while keeping machine tasks in operation contracts, preflight, runners, and guards.
- responsibility_boundaries:
  - Effective prompt structure owns decision_point, preconditions_checked, language_task, postconditions, and on_completion.
  - language_task owns document_kind, input, output_format, and constraints for the LLM's language work.
  - Machine operations such as commit, push, spec.json mutation, review-run execution, approval consume, and state mutation are not embedded as LLM instructions.
  - Prompt audit checks structure, references, anchors, length bounds, manifest/target consistency, language_task/output/postcondition correspondence, and next action compatibility.
  - LLM judge audit is semantic assistance only and must not automate final approval.
- acceptance_criteria:
  - Effective prompt manifest schema validates required sections and source references.
  - generated prompt metadata preserves compatibility with effective_prompt_path and effective_prompt_sha256 in next_action and review-run rounds.
  - prompt audit rejects missing required structure, broken refs, unknown action kind, review target manifest mismatch, machine task leakage, unverified preconditions, and impossible postconditions.
  - prompt audit findings are structured and do not depend on provider or model identity.
  - run_role.py and run_review.py record effective prompt path and sha256 when provided.
- forbidden_actions:
  - Do not summarize away required source material into path-only prompts when the review requires upstream intent transfer.
  - Do not place machine execution procedures in the language_task as if the LLM should perform them manually.
  - Do not delete existing rounds.yaml compatibility fields while adding manifest metadata.
  - Do not let LLM judge audit act as final approval.
- unresolved_or_design_deferred_items:
  - Phase 6 LLM judge audit is later than the mechanical prompt audit and may remain advisory.
  - Full structured prompt generation for all decision points is Phase 4 scope; compatibility Markdown output may remain during transition.
- intended_target_phase_transfer:
  - Implementation should provide language task schema, effective prompt manifest validation, prompt audit logic, and review-run metadata recording.
  - Implementation review should verify schemas, prompt audit tests, and run_role/run_review compatibility listed in req15-review-target-manifest.md against this intent.

### req15-verification-context

Verification snapshots are smoke evidence only. Passing tests are not proof of
correctness and must not suppress findings. Use the target test files themselves
to evaluate whether the boundaries are meaningfully covered.

- `test_language_task_io_schema.py`: covers language task I/O schema shape and separation of language-facing input/output fields.
- `test_effective_prompt_manifest.py`: covers effective prompt manifest required fields and source-reference metadata.
- `test_prompt_audit.py`: covers fail-closed prompt audit cases for missing structure, broken references, machine-task leakage, and next-action compatibility.
- `test_prompt_manifest_rounds_recording.py`: covers review-run metadata compatibility for effective prompt path / sha256 recording.
- `test_run_role.py` and `test_run_review.py`: cover API provider runner compatibility paths that preserve effective prompt metadata.

### direct-boundary-reference-definition

Req 14 and Req 16 are out of scope except when the Req15 target code or schemas
explicitly name their boundary symbols. Examples of direct boundary references:

- prompt audit code or schema fields that explicitly mention approval gates,
  human-only approval, proxy triage, operation contracts, phase transition, or
  irreversible operation authorization
- run_role.py / run_review.py metadata behavior that explicitly passes evidence
  required by Req16 proxy decision or operation-contract checks

Do not review the full Req14 approval gate implementation or full Req16 proxy
triage mechanics.

## Vertical Intent Transfer Customization

Phase chain:

- requirements.md -> design.md -> tasks.md -> implementation

Use upstream materials only for background and transfer checking. Limit target judgment to the current phase artifact.

## Required Checks

1. Check the target against the single judgment item: Req 15 implementation upstream transfer for structured effective prompt and prompt audit.
2. Check that the target satisfies preserved user review requirements.
3. Check that source materials are used only for background or required intent transfer.
4. Check that no finding depends on unstated assumptions or path-only source material.
5. Check that source/digest/prompt length structures are specific enough for later audit:
   - source references are non-empty and traceable to source material or target artifacts
   - digests use explicit sha256-style values where digest binding is claimed
   - prompt length or bound checks identify the measured field, bound source, and failure behavior
   - manifest metadata records path and sha256 without replacing the target content
6. Check that the target does not authorize commit, push, spec.json mutation, phase transition, or gate completion.

## Out Of Scope

- Req 14 approval gate state
- Req 16 proxy triage decision mechanics
- Do not approve or authorize commit, push, spec.json mutation, phase transition, or gate completion.
- Do not judge downstream correctness unless a target omission would force downstream invention.

## Finding Policy

- Use CRITICAL for bypass of human-only approval or irreversible-operation boundaries.
- Use ERROR for missing required behavior, weakened user requirements, or unsupported target behavior.
- Use WARN for meaningful ambiguity, weak traceability, or coverage gaps.
- Use INFO only for minor non-blocking improvements.
- Use precise target locations such as `path`, `path:function`, or `path:section`.
- Return findings: [] only when the target is traceable, correctly scoped, and sufficiently grounded.
