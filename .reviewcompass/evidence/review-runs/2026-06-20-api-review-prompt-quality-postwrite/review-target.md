# Post-write Review Target

criteria_id: api_review_prompt_quality_post_write
phase: post_write_verification
generated_at: 2026-06-20T00:00:00+09:00

## Change Summary

API review 用プロンプト品質の規律と運用接続を追加・更新した。主な対象は、一般的な API review の基本観点、上流成果物との接続を踏まえたレビュー要件、プロンプト自体をレビューする仕組み、任意場面で使えるプロンプトレビュー要件の明示である。

## Review Question

変更した文書が、API review 用プロンプト品質の判断を、一般的な API review 観点と上流成果物との接続確認の両方に基づいて行えるようにしているか。特に、prompt quality review の役割、判断項目の分離、利用者が任意場面で要件を渡せること、既存 workflow discipline map との接続に矛盾や不足がないかを確認すること。

## Target Files

- docs/disciplines/discipline_llm_as_judge_prompting.md sha256=2dc7be6e2c21ade683c1736e23d2ce1943a4bc1bcda5b9edabe57ee0e9ccbc33
- docs/operations/API_REVIEW_PROMPT_QUALITY.md sha256=3d3082fac238479ed3a2a90e5132d5e1de9c154d71f4f2e4a7c72c33e2204572
- docs/operations/WORKFLOW_DISCIPLINE_MAP.yaml sha256=a1b591cc04a0a6f8791d47151d179216e4876a4898bcf2c014f440c5c1334853

## Scope

- Check whether the changed target files clearly state the intended prompt-quality review contract.
- Check whether the prompt-quality review can handle arbitrary user-provided review requirements without assuming a single fixed problem.
- Check whether general API review criteria and upstream-to-current-phase connection checks are both represented.
- Check whether the discipline map points to the necessary prompt-quality material at the appropriate decision points.

## Out Of Scope

- Do not review code, templates, or files outside Target Files.
- Do not request unrelated refactors or style-only rewrites.
- Do not judge implementation readiness of tools unless a target file claims the implementation already exists.

## Finding Policy

- Report must-fix findings for contradictions, missing required review inputs, missing upstream-connection checks, or instructions that would allow unsafe or under-specified API review prompts.
- Report should-fix findings for ambiguity likely to cause repeated manual judgment, prompt overloading, weak role separation, or unclear handoff between main / adversarial / judgment roles.
- Return findings: [] when the target files are internally consistent for this review question.

## Sensitive Information Check

- status: passed
- External API review must not proceed if this section reports potential secrets.
