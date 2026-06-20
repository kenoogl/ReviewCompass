# C3 Post-Fix Recheck

## Scope

- Target artifact: `.reviewcompass/specs/workflow-management/design.md`
- Cluster: C3
- Source findings:
  - `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-003`
  - `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-gpt-5.4-primary-004`
  - `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-003`
  - `2026-06-20-workflow-management-design-vertical-redo-review-run-v2-claude-sonnet-4-6-adversarial-004`
- Recheck date: 2026-06-20

## Issue Summary

C3 said approval records were too weakly bound, and that the proxy / human boundary remained contradictory or under-specified. The key problems were:

- Approval records allowed `target_artifact_digest` and `staged_file_set_digest` to both be nullable without an operation-type rule.
- The approval stage example still allowed `proxy_model`, contradicting the human-only rule for phase approval.
- `decision_scope` was named but not mechanically derived per operation / required_action.
- Proxy triage application was not strongly connected to operation contract preconditions.

## Applied Design Response

`design.md` now states:

- Phase / gate approval stages are `human` only.
- The approval stage example no longer allows `proxy_model`.
- `explicit_human_approval_recorded` is satisfied only by a human-only approval record.
- proxy_model can support triad-review repair-policy / finding triage decisions, but it cannot authorize human-only approval, commit, push, `spec.json` update, phase / gate completion, reopen finalize, or approval-required irreversible operation execution.
- proxy decision artifacts use `decided_by: proxy_model` and `proxy-decision-bundle-*`, not `approved_by: proxy_model` or `approval-proxy-*`.
- Approval gate records include:
  - `decision_scope`
  - `binding_kind`
  - `target_artifact_digest`
  - `staged_file_set_digest`
- `decision_scope` is derived from operation contract fields and the human-only override set, not chosen freely by the record writer.
- `binding_kind` is derived from the operation contract; required digest fields must be present and current.
- `proxy_triage_apply_batch` has explicit preconditions tying proxy application to coverage validation, approval gate records, operation contract fields, and review-wave / downstream impact evidence.

## Verification

The following local checks were run:

```text
rg -n 'human または proxy_model|本人または proxy_model|利用者または proxy_model|proxy_allowed_condition|approval 段の proxy_model|proxy_model.*承認|承認.*proxy_model|approved_by: proxy_model|approval-proxy|actor=human または proxy_model|actor が `proxy_model`|人または proxy_model' .reviewcompass/specs/workflow-management/design.md

rg -n 'decision_scope|binding_kind|human-only override|proxy_triage_apply_batch|human-required predicate|explicit_human_approval_recorded|proxy-decision-bundle|decided_by: proxy_model' .reviewcompass/specs/workflow-management/design.md

.venv/bin/python3 -m pytest tools/api_providers/tests -q
```

Outcome:

- Search no longer finds stale proxy-as-approval permission wording.
- Remaining proxy-related matches are explicit negative boundaries or proxy decision evidence fields.
- Positive-boundary search confirms `decision_scope`, `binding_kind`, human-only override, and `proxy_triage_apply_batch` preconditions are present.
- `tools/api_providers/tests`: 152 passed.

## Result

C3 is addressed by the current `design.md` edits.

## Remaining Limits

This recheck addresses C3 only. It does not decide C4-C7, does not authorize `spec.json` mutation, does not complete the design gate, and does not authorize commit, push, phase transition, or reopen finalization.
