# Post-write Review Target

criteria_id: workflow_management_tasks_review_wave_postwrite
phase: post_write_verification
generated_at: 2026-06-19T07:35:30.883649+00:00

## Change Summary

workflow-management tasks review-wave の cross-feature impact 判定を作成し、他 feature の tasks 正本変更不要と判定した。

## Review Question

追加した tasks review-wave 本文と機械サマリが、workflow-management tasks triad-review 後の横断影響判定として十分であり、他 feature の tasks 正本変更不要という結論に重大な抜けや矛盾がないか確認してください。

## Target Files

- .reviewcompass/specs/_cross_feature/reviews/2026-06-19-tasks-integrated-design-review-wave.md sha256=200a283ee2d8a5e6b74fbb0f44ca0ad46dbaa09a658295d17757b26f0f1c7769
- .reviewcompass/specs/_cross_feature/reviews/2026-06-19-tasks-integrated-design-review-wave-summary.md sha256=ad5a08ebf4d6529f45c510aac83bad85ef26d75ef01b766eb6597b6dc957482c

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
