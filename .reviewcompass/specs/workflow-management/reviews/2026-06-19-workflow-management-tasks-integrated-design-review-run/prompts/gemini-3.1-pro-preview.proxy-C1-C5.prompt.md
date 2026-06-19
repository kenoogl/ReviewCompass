prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.1-pro-preview

# Task
Review the target document for the requested phase and criteria.

# Phase
tasks_proxy_triage

# Criteria
# Proxy Model Triage Decision Prompt: C1-C5

## Role

You are acting as `proxy_model` for a ReviewCompass tasks triad-review. Your task is to make final triage decisions for finding clusters C1-C5.

This is not an implementation request. Do not edit files. Decide the final triage label and explain the reasoning.

## Review Run

- run_id: `2026-06-19-workflow-management-tasks-integrated-design-review-run`
- phase: `tasks`
- gate: `stages/tasks.yaml#triad-review`
- variant used for review: `implementation_review_independent_3way_codex_operator`
- review target: `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-integrated-design-review-run/review-target.md`
- triage summary: `.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-integrated-design-review-run/raw-review-triage-summary.md`

## Source Raw Responses

Use these raw responses as source evidence:

- primary / gpt-5.4: `raw/gpt-5.4.round-1.txt`
- adversarial / claude-opus-4-8: `raw/claude-opus-4-8.round-1.txt`
- judgment / gemini-3.1-pro-preview: `raw/gemini-3.1-pro-preview.round-1.txt`

The parsed findings and cluster summary are in `raw-review-triage-summary.md`. If a cluster summary overstates, understates, or misgroups the raw findings, adjust the decision and explain why.

## Current Context

The project is in reopen procedure:

- active gate: `stages/tasks.yaml#triad-review`
- state file: `stages/in-progress/reopen-procedure-2026-06-19.yaml`
- classification: R-0 for `workflow-management`
- scope: tasks drafting for approved Requirement 13 through Requirement 16.

Do not decide that the gate or phase is complete. This prompt only asks for triage labels.

## Labels

Use the standard labels:

- `must-fix`: must be addressed before this tasks triad-review can be accepted.
- `should-fix`: should be addressed if practical before moving on; may be batched into the review response.
- `leave-as-is`: no change required; record only.

These labels are operational labels, not closed reasoning choices. You may split or merge clusters if the source evidence supports it, but each final cluster must still receive one of these labels.

## Cluster Proposals from Main Session

### C1: T-017 workflow-state snapshot coverage is underspecified

Source finding ids:

- `2026-06-19-workflow-management-tasks-integrated-design-review-run-gpt-5.4-primary-001`

Draft summary: T-017 mentions snapshot and drift detection, but does not spell out the fixed snapshot payload strongly enough: `spec.json`, `pending_gates`, `drafting_completed_gates`, `completed_gates`, operation contract, staged file set, and worktree digest.

Draft label: `should-fix`

### C2: T-018 prompt manifest compatibility with existing rounds.yaml is unclear

Source finding ids:

- `2026-06-19-workflow-management-tasks-integrated-design-review-run-gpt-5.4-primary-002`
- `2026-06-19-workflow-management-tasks-integrated-design-review-run-claude-opus-4-8-adversarial-001`

Draft summary: T-018 adds structured prompt manifests, but the tasks text does not clearly say how the new manifest path / sha256 coexists with the existing T-004 `effective_prompt_path` / `effective_prompt_sha256` fields in `rounds.yaml`, nor where text-only compatibility ends.

Draft label: `should-fix`

### C3: T-019 consumer impact and scope distinction need concrete inputs

Source finding ids:

- `2026-06-19-workflow-management-tasks-integrated-design-review-run-gpt-5.4-primary-003`
- `2026-06-19-workflow-management-tasks-integrated-design-review-run-claude-opus-4-8-adversarial-002`

Draft summary: T-019 says unreflected consumer impact blocks completion, but does not define the exact required inputs and checks for review-wave summary, carry-forward register, downstream impact decisions, active reopen scope, and impact review scope.

Draft label: `should-fix`

### C4: Traceability rows are correct but too coarse for high-risk Req 14-16 points

Source finding ids:

- `2026-06-19-workflow-management-tasks-integrated-design-review-run-gpt-5.4-primary-004`

Draft summary: Requirement 14 through 16 traceability rows map to T-017 through T-019, but omit several high-risk phrases from the review target: proxy_model / human decision boundary, staged file set / digest checks, and review-wave consumer impact blocking.

Draft label: `should-fix`

### C5: Positive state and scope checks

Source finding ids:

- `2026-06-19-workflow-management-tasks-integrated-design-review-run-gpt-5.4-primary-005`
- `2026-06-19-workflow-management-tasks-integrated-design-review-run-gpt-5.4-primary-006`
- `2026-06-19-workflow-management-tasks-integrated-design-review-run-claude-opus-4-8-adversarial-003`
- `2026-06-19-workflow-management-tasks-integrated-design-review-run-claude-opus-4-8-adversarial-004`
- `2026-06-19-workflow-management-tasks-integrated-design-review-run-claude-opus-4-8-adversarial-005`

Draft summary: The task count, completion criteria, Requirement 13 through 16 traceability presence, XDI-WM-005, T-014 / T-016 responsibility split, `spec.json`, and reopen in-progress state are internally consistent. No edit is needed for these positive findings.

Draft label: `leave-as-is`

## Required Output

Return YAML only:

```yaml
proxy_model_id: gemini-3.1-pro-preview
decisions:
  - cluster_id: C1
    final_label: must-fix | should-fix | leave-as-is
    rationale: <decision rationale>
    rejected_options:
      must-fix: <why rejected, if not selected>
      should-fix: <why rejected, if not selected>
      leave-as-is: <why rejected, if not selected>
    apply_to_finding_ids:
      - <source finding id>
```

If you split or merge clusters, use stable cluster ids such as `C1a` or `C2-C4` and include all affected `apply_to_finding_ids`.


# Output contract
Return YAML only.
The top-level key must be exactly findings.
Do not add wrapper keys such as review, result, metadata, or summary.
Do not wrap the YAML in Markdown code fences.
Do not write prose before or after the YAML.

Each finding must include these keys:
- severity
- target_location
- description
- rationale

Use only these severity values:
- CRITICAL
- ERROR
- WARN
- INFO

If there are no findings, return exactly:

findings: []

Valid shape example:

findings:
  - severity: WARN
    target_location: "path or section"
    description: "Plain finding summary"
    rationale: "Why this matters"

# Prior findings
なし

# Target path
.reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-tasks-integrated-design-review-run/raw-review-triage-summary.md

# Target document
# Tasks Triad Review Raw Triage Summary

run_id: `2026-06-19-workflow-management-tasks-integrated-design-review-run`
variant: `implementation_review_independent_3way_codex_operator`
gate: `stages/tasks.yaml#triad-review`

## Role Assignments

| role | path | provider | model |
| --- | --- | --- | --- |
| primary | api | openai-api | gpt-5.4 |
| adversarial | api | anthropic-api | claude-opus-4-8 |
| judgment | api | gemini-api | gemini-3.1-pro-preview |

## Model Results

| model | parse | raw findings | severity | raw |
| --- | --- | ---: | --- | --- |
| gpt-5.4 | parsed | 6 | WARN:4, INFO:2 | `raw/gpt-5.4.round-1.txt` |
| claude-opus-4-8 | parsed | 5 | WARN:2, INFO:3 | `raw/claude-opus-4-8.round-1.txt` |
| gemini-3.1-pro-preview | parsed | 0 | - | `raw/gemini-3.1-pro-preview.round-1.txt` |

## Same-root Clusters and Draft Triage

### C1: T-017 workflow-state snapshot coverage is underspecified

- Source findings:
  - `2026-06-19-workflow-management-tasks-integrated-design-review-run-gpt-5.4-primary-001`
- Draft label: `should-fix`
- Summary: T-017 mentions snapshot and drift detection, but does not spell out the fixed snapshot payload strongly enough: `spec.json`, `pending_gates`, `drafting_completed_gates`, `completed_gates`, operation contract, staged file set, and worktree digest.
- Suggested action: Add explicit T-017 completion and test coverage for snapshot payload fields and drift comparisons.

### C2: T-018 prompt manifest compatibility with existing rounds.yaml is unclear

- Source findings:
  - `2026-06-19-workflow-management-tasks-integrated-design-review-run-gpt-5.4-primary-002`
  - `2026-06-19-workflow-management-tasks-integrated-design-review-run-claude-opus-4-8-adversarial-001`
- Draft label: `should-fix`
- Summary: T-018 adds structured prompt manifests, but the tasks text does not clearly say how the new manifest path / sha256 coexists with the existing T-004 `effective_prompt_path` / `effective_prompt_sha256` fields in `rounds.yaml`, nor where text-only compatibility ends.
- Suggested action: Clarify that structured manifest fields extend, rather than replace silently, existing T-004 recording and add migration / fail-closed tests for manifest-only, text-only, and mixed states.

### C3: T-019 consumer impact and scope distinction need concrete inputs

- Source findings:
  - `2026-06-19-workflow-management-tasks-integrated-design-review-run-gpt-5.4-primary-003`
  - `2026-06-19-workflow-management-tasks-integrated-design-review-run-claude-opus-4-8-adversarial-002`
- Draft label: `should-fix`
- Summary: T-019 says unreflected consumer impact blocks completion, but does not define the exact required inputs and checks for review-wave summary, carry-forward register, downstream impact decisions, active reopen scope, and impact review scope.
- Suggested action: Add explicit T-019 completion / test requirements for those input files and for preventing `spec.json.reopened` history from being treated as the active reopen scope.

### C4: Traceability rows are correct but too coarse for high-risk Req 14-16 points

- Source findings:
  - `2026-06-19-workflow-management-tasks-integrated-design-review-run-gpt-5.4-primary-004`
- Draft label: `should-fix`
- Summary: Requirement 14 through 16 traceability rows map to T-017 through T-019, but omit several high-risk phrases from the review target: proxy_model / human decision boundary, staged file set / digest checks, and review-wave consumer impact blocking.
- Suggested action: Split or enrich the affected traceability rows so these high-risk points are directly visible without rereading the full task sections.

### C5: Positive state and scope checks

- Source findings:
  - `2026-06-19-workflow-management-tasks-integrated-design-review-run-gpt-5.4-primary-005`
  - `2026-06-19-workflow-management-tasks-integrated-design-review-run-gpt-5.4-primary-006`
  - `2026-06-19-workflow-management-tasks-integrated-design-review-run-claude-opus-4-8-adversarial-003`
  - `2026-06-19-workflow-management-tasks-integrated-design-review-run-claude-opus-4-8-adversarial-004`
  - `2026-06-19-workflow-management-tasks-integrated-design-review-run-claude-opus-4-8-adversarial-005`
- Draft label: `leave-as-is`
- Summary: The task count, completion criteria, Requirement 13 through 16 traceability presence, XDI-WM-005, T-014 / T-016 responsibility split, `spec.json`, and reopen in-progress state are internally consistent. No edit is needed for these positive findings.

## Must-fix Candidate Summary

No `must-fix` candidates were found in this review run.

## Should-fix Candidate Summary

- C1: clarify T-017 workflow-state snapshot payload and drift checks.
- C2: clarify T-018 structured prompt manifest compatibility with T-004 `rounds.yaml` fields.
- C3: clarify T-019 consumer impact inputs and active reopen scope / impact review scope distinction.
- C4: enrich Requirement 14 through 16 traceability rows for high-risk points.

## Stop Point

Per `docs/operations/SESSION_WORKFLOW_GUIDE.md#3.3-a-2`, stop here before proxy_model judgment, edits, spec.json updates, or phase movement.

