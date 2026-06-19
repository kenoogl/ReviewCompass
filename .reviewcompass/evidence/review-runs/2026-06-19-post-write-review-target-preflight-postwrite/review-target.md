# Post-write Review Target

criteria_id: post_write_review_target_preflight_contract_clearance
phase: post_write_verification
generated_at: 2026-06-19T00:50:08.642667+00:00

## Change Summary

post-write API review 前に review-target を機械生成し、run_review は criteria-file と rendered prompt 証跡を保存するようにした。標準手順と配布 manifest も追従した。

## Review Question

post-write API review の標準手順が、短い criteria ID だけに依存せず、review-target 生成、criteria-file 利用、rendered prompt 保存、機微情報チェックを一貫して要求しているか。

## Target Files

- docs/operations/WORKFLOW_NAVIGATION.md sha256=f467affd2d8d842369a4b9e54fdd5322b1d230b427fca12bfc5c3205916fef73
- docs/operations/DEPLOYMENT.md sha256=4d7230eae5a6bd91ee7b427e99dd786174c6431a1591ed37d9326521f323ac8f
- deploy-manifest.yaml sha256=6500b168b1024b40d8848a1480ea44a9ab6ff8cfc139603a9786d38cf00bfa03
- stages/completed/maintenance-2026-06-19-post-write-review-target-preflight.yaml sha256=f625b5678e2cbe421f7fa7408ab41d5b7b6e1c1091fe88c37a65f38185ad8040

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
