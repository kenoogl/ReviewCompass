---
criteria_id: proxy-decision-c1-fix-policy-prompt-quality-review
phase: prompt-quality
review_target: proxy-decision-c1-fix-policy-prompt.md
---

# C1 Fix Policy Proxy Prompt Quality Review Criteria

Review the target prompt draft itself. Do not judge the eventual `design.md` fix yet.

Question:

Is the draft prompt suitable for asking `proxy_model` to judge the C1 fix policy, given the prior C1 `must-fix / blocking` decision and the current workflow constraints?

## Required Checks

The prompt draft must:

1. Preserve the user request to use proxy mode for C1 response policy instead of main-session unilateral approval.
2. Keep the judgment limited to C1 fix policy, not C2-C7.
3. Include enough prior C1 decision material and relevant design excerpts for the proxy model to judge without guessing.
4. Ask a non-leading question that permits confirming, modifying, rejecting, or replacing the main session's Policy A.
5. Avoid forcing a closed A/B/C choice.
6. Distinguish prior proxy decision, current design material, main-session proposed policy, judgment question, and out-of-scope operations.
7. Avoid authorizing direct file edits, `spec.json` updates, gate completion, phase transition, commit, push, human-only approval substitution, reopen finalization, or irreversible operations.
8. Use a parser-friendly YAML output contract.
9. Avoid credentials, tokens, passwords, nonces, personal identifiers, third-party confidential material, and unrelated full logs.
10. Keep the source material to the minimum needed for this single judgment.

## Finding Policy

- Report `CRITICAL` if the prompt authorizes or implies authorization of irreversible operations, gate completion, human-only approvals, or direct edits.
- Report `ERROR` if the prompt asks the wrong question, combines independent judgments, omits material needed to judge C1 fix policy, or forces a closed choice.
- Report `WARN` if the prompt is usable but has avoidable ambiguity, weak source/target separation, output contract weakness, or mildly leading wording.
- Report `INFO` for minor wording or ergonomics issues.
- Return `findings: []` only if the prompt is safe to use for the intended proxy_model judgment.

## Output Contract

Return YAML only with top-level key `findings`.

If there are no findings, return exactly:

```yaml
findings: []
```

Each finding must include:

```yaml
severity: CRITICAL | ERROR | WARN | INFO
target_location: string
description: string
rationale: string
```
