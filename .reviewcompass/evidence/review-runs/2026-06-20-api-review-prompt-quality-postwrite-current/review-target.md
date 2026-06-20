# Post-write Review Target

criteria_id: api_review_prompt_quality_postwrite_current
phase: post_write_verification
generated_at: 2026-06-20T14:13:28.799793+00:00

## Change Summary

APIレビュー用プロンプト品質規律・運用文書・規律マップの現在内容に対するpost-write verification

## Review Question

現在の3文書は、APIレビュー用プロンプト品質に関する合意内容を正しく反映し、参照・既存記述・内部論理に矛盾がないか。

## Target Files

- docs/disciplines/discipline_llm_as_judge_prompting.md sha256=2dc7be6e2c21ade683c1736e23d2ce1943a4bc1bcda5b9edabe57ee0e9ccbc33
- docs/operations/API_REVIEW_PROMPT_QUALITY.md sha256=61d209015f56bdeca42127165c91091361cba6b25d38074c819f99499681fda4
- docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml sha256=ca6aa8ef21a672e01268f26a282b0f8fc71329592e4f0b59e2da8e7d24b598e1

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
