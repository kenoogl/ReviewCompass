# Post-write Review Target

criteria_id: post_write_verification
phase: post_write_verification
generated_at: 2026-06-19T11:57:06.632111+00:00

## Change Summary

TODO_NEXT_SESSION.md was refreshed to the b06e3e2a handoff and a new workflow-management A-0 reopen classification record was added for task-granularity regeneration. The classification says tasks.md will be regenerated under the new task-granularity discipline, then implementation will create tests and code from tasks.md without creating implementation-drafting.md.

## Review Question

Do these two changed files accurately reflect the user instruction to reopen from the tasks phase, regenerate workflow-management tasks under the new task-granularity discipline, and then implement from tasks.md without overextending the scope beyond workflow-management tasks and implementation?

## Target Files

- TODO_NEXT_SESSION.md sha256=8f7c68666851e8e54e76369abe9adb4e9f6da836ce31987543736f4a2ed07608
- docs/reviews/reopen-classification-2026-06-19-wm-task-granularity-regeneration.md sha256=f932d143642ee3c243ae096b14d560ce0bdd8bf9aea3c51ed52f4efdfe4e31bd

## Scope

- Check whether the changed target files clearly state the intended contract.
- Check whether related instructions are mutually consistent across targets.
- Check whether the documented procedure is actionable before API review, triage, manifest, or commit steps continue.

## Out Of Scope

- Do not request unrelated refactors or style-only rewrites.
- Do not judge files that are not listed in Target Files.
- Do not treat missing implementation work as a document defect unless the target text claims it already exists.

## Finding Policy

- Report must-fix findings for contradictions, missing required gates, or instructions that would allow an unsafe workflow action.
- Report should-fix findings for ambiguity that could cause repeated manual judgment or unnecessary API review loops.
- Return findings: [] when the target files are internally consistent for this review question.

## Sensitive Information Check

- status: passed
- External API review must not proceed if this section reports potential secrets.
