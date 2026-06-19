prompt_id: gemini_review
provider: gemini-api
model_id: gemini-3.5-flash

# Task
Review the target document for the requested phase and criteria.

# Phase
post_write_verification

# Criteria
run_id: 2026-06-19-remove-implementation-drafting-artifacts-postwrite-r2
phase: post_write_verification
criteria_id: remove_implementation_drafting_artifacts_and_deleted_staged_guard
criteria_file: .reviewcompass/evidence/review-runs/2026-06-19-remove-implementation-drafting-artifacts-postwrite-r2/review-target.md
criteria_file_sha256: d5b21672c39bcc0a4e6f55fba05982a615d710e638a81474e3f9136c58b00cfb
target_files:
- path: .reviewcompass/README.md
  sha256: 9533a51f23816d865ef9cefd1956b28f83db164ab3aef1a3be8dd3803c7fe3a9
- path: .reviewcompass/specs/workflow-management/tasks.md
  sha256: 715add2dd0ed1a2373eef50ea8c545ebe5620576c1c8f88b095fa9f806d1ddd1
- path: docs/notes/2026-06-12-document-placement-target-design.md
  sha256: a451a6a4200777988c20d49c16cb1ded0acbc038306086c83b3c39d57cf6ea81
- path: docs/operations/SESSION_WORKFLOW_GUIDE.md
  sha256: 522f67fa99b07d98b6a89e4dc088d4d8aca235ef5b5f4a498196a25011504c81
- path: tools/check-workflow-action.py
  sha256: 9b8e3b56301a7ec48f86fcdacdcca50c70b0d725f556b9afc5bcf652da707807
sensitive_information_check:
  status: passed
  checked_at: '2026-06-19T11:44:31.240487+00:00'
recommended_run_review_args:
  criteria_file: .reviewcompass/evidence/review-runs/2026-06-19-remove-implementation-drafting-artifacts-postwrite-r2/review-target.md
  phase: post_write_verification


# Output contract
Return YAML only.
The top-level key must be exactly findings.
Do not add wrapper keys such as review, result, metadata, or summary.
Do not wrap the YAML in Markdown code fences.
Do not write prose before or after the YAML.

Each finding must include these keys:
- severity
- target_location
- description
- rationale

Use only these severity values:
- CRITICAL
- ERROR
- WARN
- INFO

If there are no findings, return exactly:

findings: []

Valid shape example:

findings:
  - severity: WARN
    target_location: "path or section"
    description: "Plain finding summary"
    rationale: "Why this matters"

# Prior findings
なし

# Target path
.reviewcompass/evidence/review-runs/2026-06-19-remove-implementation-drafting-artifacts-postwrite-r2/review-target.md

# Target document
# Post-write Review Target

criteria_id: remove_implementation_drafting_artifacts_and_deleted_staged_guard
phase: post_write_verification
generated_at: 2026-06-19T11:44:31.240487+00:00

## Change Summary

implementation-drafting.md を正式成果物から外し、tasks.md の粒度規律に寄せる。削除済み staged Markdown を commit guard の post-write/lint で DELETED として扱い、削除コミットを誤遮断しないようにする。

## Review Question

変更後、implementation-drafting.md を成果物として残す誘導がなく、tasks.md の粒度規律で実装準備が担保され、削除済み staged Markdown の commit guard 処理にも矛盾や安全上の抜けがないか確認してください。

## Target Files

- .reviewcompass/README.md sha256=9533a51f23816d865ef9cefd1956b28f83db164ab3aef1a3be8dd3803c7fe3a9
- .reviewcompass/specs/workflow-management/tasks.md sha256=715add2dd0ed1a2373eef50ea8c545ebe5620576c1c8f88b095fa9f806d1ddd1
- docs/notes/2026-06-12-document-placement-target-design.md sha256=a451a6a4200777988c20d49c16cb1ded0acbc038306086c83b3c39d57cf6ea81
- docs/operations/SESSION_WORKFLOW_GUIDE.md sha256=522f67fa99b07d98b6a89e4dc088d4d8aca235ef5b5f4a498196a25011504c81
- tools/check-workflow-action.py sha256=9b8e3b56301a7ec48f86fcdacdcca50c70b0d725f556b9afc5bcf652da707807

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

