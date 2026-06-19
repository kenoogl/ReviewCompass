# Post-write Review Target

criteria_id: post_write_manifest_final_seal_contract_clearance
phase: post_write_verification
generated_at: 2026-06-19T01:08:37.577516+00:00

## Change Summary

post-write manifest を commit 直前の最終封印として扱い、review-run 対象外の post-write 未コミット変更が残る場合は write-manifest を fail-closed するようにした。

## Review Question

manifest 作成手順と完了記録が、manifest を途中記録ではなく最終封印として扱い、対象外 post-write 変更を残したまま manifest を作らない contract と矛盾していないか。

## Target Files

- docs/operations/WORKFLOW_NAVIGATION.md sha256=4f01dd574b9fb57b5de84f322cd719e87484fa2f05ae20228c5c2f0e904a0531
- stages/completed/maintenance-2026-06-19-post-write-manifest-final-seal.yaml sha256=03ae3b4683fa7d5c0d7e78166a0d045467bdc2ab66a8e4df7f9c1f283f725184

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
