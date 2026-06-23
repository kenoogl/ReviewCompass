# Task Quality Review Criteria: Guidance Relocation Inventory

## Review Task
Review whether the backlog TODO and runtime checklist for `todo-2026-06-23-guidance-relocation-inventory` are safe to use as the execution checklist after `task-quality-check audit` returned `OK` with a WARN:

- `red test items appear after implementation items: GRC-RT-1`

The review should decide whether this warning is a blocking task-quality issue, and identify any missing checklist or TODO quality defects that would make execution unsafe.

## User Review Requirements
- WARN from task-quality-check should be reviewed by API, not bypassed by local judgment.
- Review the generated review materials and judge whether the TODO/checklist may proceed.
- Do not authorize commit, push, file moves, or completion of the work.

## Review Target
The target file is `.reviewcompass/evidence/review-materials/2026-06-23-guidance-relocation-inventory-task-quality/review-materials.yaml`.

It contains:
- The backlog TODO full text.
- The runtime checklist full text.
- The task-quality audit result.
- Main preanalysis generated from the audit.
- Review questions and decision boundaries.

## Required Checks
1. Determine whether the WARN about `GRC-RT-1` appearing after implementation items is a blocking issue for this specific inventory-only TODO.
2. Check whether the checklist preserves the source plan slice `GRC-1` and does not broaden scope into file moves, deletion, or consumer reference updates.
3. Check whether each checklist item is concrete enough to execute and verify.
4. Check whether the red-test / acceptance item is sufficient for an inventory/classification-only task.
5. Check whether the checklist can proceed as-is, should be reordered, or needs additional items before execution.

## Out Of Scope
- Do not classify the actual `docs/operations` or `docs/disciplines` files.
- Do not propose file moves, path deletions, or consumer reference updates.
- Do not judge post-write verification, commit readiness, or push readiness.
- Do not treat the generated main preanalysis as authoritative; use it only as a hypothesis.

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
