# workflow-management design triad-review summary：commit execution delegation formal CLI

## Review Run

- Run: `2026-06-16-workflow-management-design-commit-execution-delegation-review-run`
- Variant: `implementation_review_independent_3way`
- Phase: `design`
- Gate: `stages/design.yaml#triad-review`
- Target: `.reviewcompass/specs/workflow-management/reviews/2026-06-16-workflow-management-design-commit-execution-delegation-review-run/review-target.md`
- Criteria: `workflow_management_commit_execution_delegation_design_reopen_triad_review`

## Role Assignments

| role | provider | model | raw |
| --- | --- | --- | --- |
| primary | anthropic-api | claude-sonnet-4-6 | `raw/claude-sonnet-4-6.round-1.txt` |
| adversarial | openai-api | gpt-5.5 | `raw/gpt-5.5.round-1.txt` |
| judgment | gemini-api | gemini-3.1-pro-preview | `raw/gemini-3.1-pro-preview.round-1.txt` |

## Model Result Summary

| model | findings | severity |
| --- | ---: | --- |
| claude-sonnet-4-6 | 11 | ERROR 3, WARN 5, INFO 3 |
| gpt-5.5 | 4 | ERROR 1, WARN 3 |
| gemini-3.1-pro-preview | 3 | WARN 2, INFO 1 |

## Same-Root Clusters And Proposed Triage

### C1: delegation record separation and staged-content binding are ambiguous

- Sources: primary-001, adversarial-001, judgment-003
- Proposed label: `must-fix`
- Summary: The design appends `execution_delegation` to `commit-approval.json`. Claude flags this as conflating staged-content approval and execution delegation; Gemini says co-location can satisfy the requirement if the parent staged-content record is explicitly the binding object. The design must choose and state the binding model clearly. Two viable options:
  - Option A: store delegation in a separate co-located file, e.g. `commit-execution-delegation.json`, referenced by nonce/target digest.
  - Option B: keep a separate field in `commit-approval.json`, but explicitly state that the staged-content approval object is immutable except for controlled delegation/consume fields, and that delegation inherits staged file binding from the parent record plus revalidation.

### C2: invalidation, malformed records, duplicate delegation, and atomic writes are under-specified

- Sources: primary-002, primary-003, adversarial-002, adversarial-003, judgment-002
- Proposed label: `must-fix`
- Summary: The design says replacement requires `invalidate` + new `prepare`, but does not define whether invalidation affects only delegation or the entire challenge/approval cycle. It also does not explicitly fail closed for malformed commit approval JSON, malformed staged-content approval records, malformed delegation objects, duplicate unexpired delegation, partial writes, concurrent writes, or externally mutated approval records. Atomic write and revalidation immediately before write are needed.

### C3: commit-gate revalidation and expiry race need explicit rules

- Sources: primary-006, primary-007
- Proposed label: `must-fix`
- Summary: The design should state that expiry and all binding conditions are checked immediately before writing the delegation record and again at commit-gate evaluation. Presence of `execution_delegation` is not enough; nonce, target digest, staged file set/content, expiry, consumed/invalidated state, and allowed instruction must be revalidated.

### C4: stdin and normalization edge cases need deterministic rules

- Sources: primary-004, primary-005, primary-008, judgment-001
- Proposed label: `should-fix`
- Summary: The design forbids newlines but does not distinguish trailing POSIX newline from internal newline, CR, or CRLF. It strips one trailing Japanese period but does not state that remaining punctuation rejects. It lowercases ASCII but does not state whether full-width Latin variants are normalized or rejected. These are not conceptual blockers, but should be settled before TDD.

### C5: attestation / guarantee vocabulary and schema enforcement need tightening

- Sources: primary-009, primary-010, adversarial-004
- Proposed label: `should-fix`
- Summary: The design names `attestation_type` and `guarantee_scope`, but does not fully define controlled values or consumer interpretation. It also bans LLM/provider/model fields, but should say this is enforced by strict schema/no extra properties, not a loose key check.

### C6: source-document cross-reference check

- Sources: primary-011
- Proposed label: `leave-as-is`
- Summary: The review target listed the in-progress reopen YAML as a source. The design itself need not reference procedure-level constraints from that file. Alignment already checks classification/reopen state; this is a sign-off checklist item, not a design text defect.

## Stop Point

This is the user-visible triage gate. Do not ask proxy_model, edit design/tasks/implementation, update spec.json, or move the phase until the triage decisions are approved by the user or proxy_model under an approved proxy-mode request.

## User Decision And Resolution

- Approval source: 2026-06-16 利用者発言「案A」
- Decision: C1 は Option A（`commit-execution-delegation.json` への別ファイル化）で解消する。C2〜C3 は `must-fix`、C4〜C5 は `should-fix`、C6 は `leave-as-is` として裁定する。
- Resolution: `.reviewcompass/specs/workflow-management/design.md` の §2.2 を更新し、staged 内容承認 record と commit 実行代行承認 record を分離した。delegation record は `.reviewcompass/runtime/approvals/commit-execution-delegation.json` に保存し、nonce、target digest、staged file set digest、staged content approval digest で staged 内容へ明示的に束縛する。
- Additional resolution: invalidation 範囲、形式不正・重複 record の fail-closed、保存直前再検証、atomic write、commit gate 再検証、stdin payload の末尾 LF 1 個だけの許容、CR/CRLF/内部改行拒否、全角 Latin 拒否、strict schema、`attestation_type` / `guarantee_scope` の controlled vocabulary を設計へ反映した。
