# C1 Post-Fix Recheck

## Scope

- Target artifact: `.reviewcompass/specs/workflow-management/design.md`
- Prior blocking decision: `C1` was judged `must-fix`, `blocking`, and `design_level`.
- Fix policy decision: `local_fix_with_modifications`
- Recheck date: 2026-06-20

## Recheck Result

Result: C1 design-level response is addressed by the current `design.md` edits.

The fix remains local to Requirement 12, Requirement 13, and XDI-WM-004 / XDI-WM-005. A broader rewrite is not required by the proxy_model fix-policy decision.

## Evidence

The recheck confirmed that `design.md` now states:

- Requirement 12 is an operation registry / preflight layer, not the operation contract authority.
- `stages/operation-registry.yaml` owns registry-specific metadata and preflight binding only.
- `stages/operation-contracts.yaml` is the physical source of truth for operation contract fields and semantics.
- `.reviewcompass/schema/required_action.schema.json` owns the allowed `required_action` token vocabulary.
- Registry-side `planned_outputs` are references, projections, or binding hints, not an output contract authority.
- Registry / preflight read operation contracts and state evidence only; they do not redefine contract fields, update contracts, execute operations, consume approvals, create workflow state, create review-run artifacts, mutate artifacts, or independently select an action.
- Registry / contract drift, missing contract references, duplicate contract-authority fields, and unbound `required_action` mappings fail closed for executable operation binding.
- `next --json` remains the single action selector; registry / preflight may validate and bind to it but must not select actions independently.
- XDI-WM-004 no longer assigns operation contract authority to the registry.
- XDI-WM-005 now places branch / internal step / max effect / approval aggregation semantics in the operation contract, with registry limited to references, projections, and binding.

## Additional Residual Check

The recheck found one residual pre-existing sentence in the lightweight precheck section that said vocabulary and output contract authority came from operation docs and `tools/check-workflow-action.py`. It was rewritten so those docs/scripts own only the lightweight precheck execution entry, display format, and argument contract. The canonical `required_action`, operation contract fields, and effect / approval / phase / output semantics now point to the schema and operation contract authorities.

## Verification Commands

```text
rg -n "語彙と出力契約の正本|実装に合わせる方向|operation contract schema（Req 12|operation contract 層|registry 上で表す|operation-registry.yaml.*operation contract schema|docs/operations/WORKFLOW_PRECHECK.*正本|tools/check-workflow-action.py.*正本|preflight implementation.*define|script.*canonical" .reviewcompass/specs/workflow-management/design.md

rg -n "required_action.*正本|operation contract の物理正本|contract field を再定義しない|registry / preflight は contract|next --json の別正本|preflight 側が pending gate|operation registry / preflight binding schema|出力 contract の二重正本|安全に束縛済み" .reviewcompass/specs/workflow-management/design.md

.venv/bin/python3 -m pytest tools/api_providers/tests -q
```

## Verification Outcome

- `tools/api_providers/tests`: 152 passed.
- Negative-pattern search no longer finds the C1-invalid formulations:
  - Requirement 12 as operation contract schema located in `stages/operation-registry.yaml`
  - Composite operation branch / approval aggregation represented on the registry
  - Operation docs or check scripts as canonical authority for `required_action`, operation contract fields, effect / approval / phase, or output contract semantics
- Positive-pattern search finds the required replacement boundaries in Requirement 12, Requirement 13, and XDI-WM-004 / XDI-WM-005.

## Remaining Limits

This recheck addresses C1 only. It does not decide C2-C7, does not authorize `spec.json` mutation, does not complete the design gate, and does not authorize commit, push, phase transition, or reopen finalization.
