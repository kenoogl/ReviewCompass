# Post-write Review Target

criteria_id: workflow_management_tasks_alignment_postwrite
phase: post_write_verification
generated_at: 2026-06-19T08:00:18.968093+00:00

## Change Summary

workflow-management tasks alignment の整合確認証跡を追加した。

## Review Question

追加した tasks alignment 証跡が、requirements Requirement 13〜16、design、tasks T-016〜T-019、triad-review 対処、review-wave 判定、workflow_state / reopen 記録の整合確認として十分であり、重大な抜けや矛盾がないか確認してください。

## Target Files

- .reviewcompass/specs/_cross_feature/reviews/2026-06-19-tasks-integrated-design-reopen-alignment.md sha256=45be81678dd4bba0d1de05bbbd80aea8bd88c362afcd50ab9cc450656d8ef105

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
