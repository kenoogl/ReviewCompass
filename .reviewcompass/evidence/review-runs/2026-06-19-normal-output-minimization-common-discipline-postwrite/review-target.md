# Post-write Review Target

criteria_id: normal_output_minimization_common_discipline_postwrite
phase: post_write_verification
generated_at: 2026-06-19T03:25:14.429042+00:00

## Change Summary

正常系出力最小化の共通規律を追加し、disciplines README に active 必読として登録した。

## Review Question

正常系出力最小化の規律本文と disciplines README の登録内容が矛盾なく、異常系と --json の情報量維持も明確か。

## Target Files

- docs/disciplines/README.md sha256=28362c70f48b90c3d4da03866e69d24b0ebf6e3ed9675a4125c57b85d56cf436
- docs/disciplines/discipline_normal_output_minimization.md sha256=e74d3098d84c52e50f0e6602a426754b52ecdbe16ffa1f6a3fcdaf6a6d71e8a6

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
