# Post-write Review Target

criteria_id: requirements_vertical_review_scope_post_write
phase: post_write_verification
generated_at: 2026-06-19T13:17:48.951278+00:00

## Change Summary

requirements triad-review の縦方向監査で、審査対象を requirements.md に限定し、design.md/tasks.md を参照資料として扱う規律と機械参照マップを追加した

## Review Question

今回の変更は、requirements review の review target/source materials/out of scope を明確にし、上流判断材料から requirements.md への意図伝達を検査する規律として十分か。design.md/tasks.md を誤って審査対象に含める余地、既存 design/tasks/implementation review 規律への退行、または workflow discipline map との不整合がないかを確認してください。

## Target Files

- docs/operations/SESSION_WORKFLOW_GUIDE.md sha256=dc879a5cc1565096854be2b8ae2120c79593fc0ee4c936b054f9fbf3ccdec246
- docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml sha256=6c6985ecc0741f138365e8c0a0a665ee4efda49d667946c05a197161205a2364

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
