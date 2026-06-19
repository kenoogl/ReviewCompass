# Post-write Review Target

criteria_id: tasks_alignment_and_commit_approval_docs_postwrite
phase: post_write_verification
generated_at: 2026-06-19T08:01:03.354822+00:00

## Change Summary

tasks alignment 証跡と、commit 承認文を LLM が生成できる抜け道を塞ぐ運用文書修正を追加した。

## Review Question

追加された tasks alignment 証跡、および commit 承認文を TTY 対話入力・直近利用者発話由来に限定する文書修正に、重大な抜け、矛盾、または既存規律との不整合がないか確認してください。

## Target Files

- .reviewcompass/specs/_cross_feature/reviews/2026-06-19-tasks-integrated-design-reopen-alignment.md sha256=45be81678dd4bba0d1de05bbbd80aea8bd88c362afcd50ab9cc450656d8ef105
- docs/operations/COMMIT_OPERATION_CARD.md sha256=074a487360c7c4ed16be6a769658e918e269fd8766c75df6a005b3ff86d97c8d
- docs/operations/WORKFLOW_NAVIGATION_FOR_CLAUDE.md sha256=76b64b34f80cf06919c3f91da6e7f5e9d46a6ea447465943345fcdaf1a50e5d0
- docs/operations/WORKFLOW_NAVIGATION_FOR_CODEX.md sha256=1ad72c7a8a57c11bdc8ceeb0c1357d5c75c34a769a123f16829af7a509687dca
- docs/operations/WORKFLOW_PRECHECK.md sha256=93a2f50f205408638cf11ed2f332f41a6e295600903e10a6c27ca8e9adb321c1
- docs/operations/WORKFLOW_PRECHECK_DETAILS.md sha256=b9d88150269cc65ff344dd9b1adef6c0d23ddcb696067c960702a35af4162f2e

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
