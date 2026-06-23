# Task Quality Review Criteria: Reduce manual assembly in plan to TODO bridge

## Review Task
Review whether the backlog TODO and runtime checklist for `todo-2026-06-23-plan-todo-bridge-manual-assembly` / `checklist-todo-2026-06-23-plan-todo-bridge-manual-assembly` are safe to use as the execution checklist after `task-quality-check audit` returned `OK`.

Task-quality warnings:

- `red test items appear after implementation items: PTB-RT-1, PTB-RT-2`

The review should decide whether any warning is a blocking task-quality issue, and identify missing checklist or TODO quality defects that would make execution unsafe.

## Prompt Construction Basis
- This criteria document is mechanically generated from task-quality review materials.
- The prompt follows the established three-review practice: material review, independent questions, explicit scope, sensitive-information check, and YAML result contract.
- Treat main preanalysis in the materials as a hypothesis to inspect, not as an answer to copy.

## User Review Requirements
- WARN from task-quality-check should be reviewed by API, not bypassed by local judgment.
- Review the generated review materials and judge whether the TODO/checklist may proceed.
- Do not authorize commit, push, file moves, or completion of the work.

## Review Target
The target file is `.reviewcompass/evidence/review-materials/2026-06-23-plan-todo-bridge-manual-assembly-task-quality/review-materials.yaml`.

It contains:
- The backlog TODO full text.
- The runtime checklist full text.
- The task-quality audit result.
- Main preanalysis generated from the audit.
- Review questions and decision boundaries.

## Required Checks
1. Are checklist items concrete, non-overlapping, and sized for execution? Expected output: Find missing granularity risks with item IDs and evidence.
2. Is the checklist order suitable for TDD and review-before-implementation flow? Expected output: Find ordering risks without treating warnings as automatic failure.
3. Does the checklist preserve the source TODO intent and stated scope? Expected output: Find weakened, omitted, or broadened upstream intent.
4. Do red test items cover the task quality risks before implementation work? Expected output: Find missing or under-specified red test coverage.

Also check whether the checklist can proceed as-is, should be reordered, or needs additional items before execution.

## Out Of Scope
- Do not perform the TODO work itself.
- Do not propose file moves, path deletions, or consumer reference updates unless the TODO explicitly scopes them.
- Do not judge post-write verification, commit readiness, or push readiness.
- Do not treat generated main preanalysis as authoritative.

## Finding Policy
Return findings only for substantive task-quality risks.

Use these severities:
- `ERROR`: Execution should not proceed until fixed.
- `WARN`: Execution may proceed only after explicit acceptance or minor correction.
- `INFO`: Non-blocking observation.

If there are no substantive findings, return an empty findings list and state that the checklist may proceed.

## Output Contract
Respond as YAML with this shape:

```yaml
findings:
  - id: TQ-001
    severity: ERROR|WARN|INFO
    summary: short summary
    evidence: specific item IDs or source text
    recommendation: concrete next action
decision:
  may_proceed: true|false
  reason: concise reason
  required_changes:
    - change, if any
```
