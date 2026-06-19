# Post-write Review Target

criteria_id: normal_output_minimization_contract_clearance
phase: post_write_verification
generated_at: 2026-06-19T02:53:28.248736+00:00

## Change Summary

check-workflow-action の正常系人間可読出力を最小化し、逸脱・警告・非定型処理では詳細を維持する方針を運用文書に反映した。

## Review Question

運用文書の出力契約が、正常系は最小出力、異常系は原因と現在状態を出すという方針と矛盾していないか。

## Target Files

- docs/operations/WORKFLOW_PRECHECK_DETAILS.md sha256=201d0042180346025767d868585b9356bf5b7f9c1f38f2f0e38f2261db566370

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
