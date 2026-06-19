# Post-write Review Target

criteria_id: implementation_approval_stop_point_post_write
phase: post_write_verification
generated_at: 2026-06-19T09:59:33.594745+00:00

## Change Summary

implementation phase approval stop point, action prompt discipline, review artifacts, workflow state, and reopen state

## Review Question

Do the implementation approval stop point records and action-prompt discipline accurately show implementation is approved and now waiting for commit, without claiming reopen finalization, push, or post-commit state?

## Target Files

- .reviewcompass/specs/workflow-management/implementation-drafting.md sha256=77368e12d30d51add6d97d56e9511bf5c73777e052cf6c49b8ab0ac9868ab7fb
- .reviewcompass/specs/workflow-management/spec.json sha256=aa2c6bd799b88ae500ba6cbf9b9886533396e91b76c0a454a638c5ea46ca85ea
- stages/in-progress/reopen-procedure-2026-06-19.yaml sha256=77cdfbc13a53c81972b0b6cf0959fd254b794c325da53cc9f7074e83876079fa
- AGENTS.md sha256=f8f9293f0c4c28aed4020440312c5319a67415b40afa77abd13432e426e9812f
- docs/operations/SESSION_WORKFLOW_GUIDE.md sha256=822c0f97a8f3bc9e33c837d0bb9d1b29080f888b301aa22dc6c1199f22f0d9d3
- tests/tools/test_workflow_management_implementation_drafting.py sha256=43e09202508abe10521df05aa8b768b9baeb6f0140924a51ee6cd808230da87b
- .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-approval.md sha256=42466787634de2e0dae164f5cd483259a1d7b8eee147e8c41d441aab53660f38
- .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-reopen-alignment.md sha256=c3e79e23f91f69fc5daabbb62537a7992fe0ea30a5537d2a3157af18cecb880e
- .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-review-wave-summary.md sha256=f63b62e178aefc18041bc507f11863ccc930e106e7f37493377e8d1ca2a97624
- .reviewcompass/specs/_cross_feature/reviews/2026-06-19-implementation-integrated-design-review-wave.md sha256=317dc6523771b2ce3410cf19afb330fc60be2815d9b1dbee7371ecc83d393233
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/prompts/claude-sonnet-4-6.round-1.prompt.md sha256=3dfb47ba32dbb0411fe103f208d677691b2e049a14c011a109b22473a5dfcc40
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/prompts/gemini-3.1-pro-preview.proxy-C1-C7.prompt.md sha256=359cdfdf22092a4ac24c17eb24ea08b2cab5a3f0ffe8dbad2870f3298f5f79fd
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/prompts/gemini-3.1-pro-preview.round-1.prompt.md sha256=03d96b175f44db391d5a790e6ea2fa0e1484efa25271dab41f7c6a0a9f98339f
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/prompts/gpt-5.4.round-1.prompt.md sha256=71b1aa97226a3fca0b58957b87e25d4e491ed867febd6754d12de81e31e67794
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/proxy-decision-prompts/C1-C7.prompt.md sha256=cf828a6bbb8ef63f2fa0eb326a7bd86815c12768483b8ee83afeeff5a433b0d5
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/proxy-decision-summary.md sha256=6209707d4c7c6433bc4346c37a4126ec9e38f638c4bc5e29d6b156ec2cae1989
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/raw-review-triage-summary.md sha256=0338464d2288943cdd4954236417c8d3bccded34d557241ab565e1e1feec4af1
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/review-response.md sha256=6fdaa5960a8c4b55f0db46b399f0982b6c9e0f12fd48f7bdabce6b15e38d3833
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/review-target.md sha256=b6b1ebd2c46782a4e5953951e629e5be345133d120ce6bfdd140cf1071d0f92b
- .reviewcompass/specs/workflow-management/reviews/2026-06-19-workflow-management-implementation-integrated-design-review-run/review_summary.md sha256=9086b1781001098fa5564be379b770428dd90afb994cb30e51eb82068e80831a

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
