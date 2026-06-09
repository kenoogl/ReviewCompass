---
feature: all_features
phase: completed_follow_up
stage: deployable_reconstruction_readiness
date: 2026-06-09
status: ready_with_gaps
candidate_id: D-021
record_type: readiness-report
source_checklist: docs/notes/2026-06-09-d021-deployable-reconstruction-readiness-checklist.md
---

# D-021 Deployable Reconstruction Readiness

## Summary

This report checks whether ReviewCompass is ready to move from self-dogfooding to deployable use in external repositories.

Verdict: `ready_with_gaps`.

Reason: the reconstruction plan requires a deployable command-line tool that can operate against a target application root and preserve app-side / tool-side separation. A minimal external-app-root smoke test now proves that `tools/check-workflow-action.py next --json` can read target-side `.reviewcompass/specs/` outside the ReviewCompass repository when run with the target app root as `cwd`. Remaining gaps are explicit `--app-root` support, broader review-run generation smoke, cost / elapsed-time capture, and normalized finding / fix evidence schemas.

## Scope

In scope:

- deployment readiness for an external target repository
- separation between target app state and ReviewCompass tool assets
- relative-link and placement-independence risks
- ability to collect review-run, triage, decision, fix/test, cost, elapsed-time, and model-assignment evidence in a repeatable shape
- escalation conditions for D-022, D-023, and D-024

Out of scope:

- implementing a deployment fixture in this report
- changing workflow_state or feature `spec.json`
- starting D-004, D-005, D-019, D-020, D-022, D-023, or D-024
- proving cross-repository replication across real external repositories

## Source Policy Summary

The reconstruction plan defines ReviewCompass as a deployable independent artifact rather than a self-application-only system.

| Policy | Evidence | D-021 interpretation |
| --- | --- | --- |
| Extract and rebuild, do not mechanically transplant | `docs/plan/reconstruction-plan-2026-05-21.md` §2.1, §2.2 | Old repository names and self-application language must not become deploy-time assumptions. |
| Deployable design is mandatory | `docs/plan/reconstruction-plan-2026-05-21.md` §2.3, §5 | The first deployment gate is separating app-side state from tool-side code, schema, templates, and commands. |
| Use relative links | `docs/plan/reconstruction-plan-2026-05-21.md` §2.5 | Absolute paths and fixed repository paths are deployment risks unless clearly historical or local-session-only evidence. |
| Target app specs live under `.reviewcompass/specs/` | `docs/plan/reconstruction-plan-2026-05-21.md` §4, §5.23.7 | ReviewCompass self-dogfooding is a first target-app placement, not proof that external placement works. |
| Tool defaults and app overrides are two layers | `docs/plan/reconstruction-plan-2026-05-21.md` §5.18.15 | `reviewcompass.yaml` / API defaults and `<app>/.reviewcompass/config.yaml` need an explicit deployment boundary. |

## Related Candidates

| Candidate | Relationship |
| --- | --- |
| D-020 cross-repository replication | Depends on D-021. D-020 should only select external repos after D-021 proves or explicitly scopes the deployment smoke. |
| D-022 extraction / reconstruction separation audit | Escalate if old repository names, old paths, or self-application assumptions block deployment. |
| D-023 relative-link / placement-independence lint | Escalate if absolute paths, implicit repo-root assumptions, or broken relative links block deployment. |
| D-024 phase-4 backlog整理 | Escalate if scoped-out reconstruction backlog prevents D-021 or D-020 from becoming executable. |

## Deployment Readiness

| Item | Status | Evidence |
| --- | --- | --- |
| App-side / tool-side separation | gap | Plan requires the split, and `.reviewcompass/specs/` is app-side state. Current implementation still mixes repository-local tool code, configs, notes, and app-side state in one repo during self-dogfooding. |
| `.reviewcompass/specs/` as target app state | pass with caveat | Spec state and review records are consistently under `.reviewcompass/specs/<feature>/`. This supports target-app placement, but only inside the ReviewCompass repo so far. |
| Config placement and responsibility | gap | Plan defines tool defaults plus app overrides. Current API settings live in `config/api-settings.yaml`; app-side `.reviewcompass/config.yaml` deployment behavior is not smoke-tested. |
| Templates placement and responsibility | gap | `templates/` exists as tool-side material, but copied app-side template behavior is not tested against an external root. |
| Review-run output placement | pass with caveat | Feature review-runs live under `.reviewcompass/specs/<feature>/reviews/`; post-write and operational review-runs live under `docs/notes/review-runs/`. The split is usable but needs a deployment rule for external apps. |
| CLI target app root | pass with caveat | `tests/tools/test_check_workflow_action.py::NextNavigationTests::test_next_completed_from_external_app_root_fixture` proves `next --json` can run from an external app root when `cwd` is the target root. There is still no explicit `--app-root` argument. |
| Implicit ReviewCompass repo-root dependency | gap | `rg` found many `cwd` / root-relative assumptions in workflow tools. This is acceptable for self-dogfooding, but external deployment needs fixture coverage. |
| Absolute path references | gap | Static scan found 39 files with local absolute-path patterns across docs / templates / tools / state records. Many are historical records, but D-023 should classify reusable artifacts versus historical evidence. |
| Old repository names and self-application terms | gap | Static scan found 16 files with old repository-name patterns and 73 files with self-application / dogfooding terms. Many are legitimate history, but D-022 should classify deployable artifacts separately. |
| Relative-link risk | gap | The plan requires relative links, but no machine lint currently proves link placement-independence across deployable artifacts. |

## Data Acquisition Readiness

| Data area | Status | Evidence |
| --- | --- | --- |
| review-run | pass with gap | `rounds.yaml` records run purpose, timestamp, target files, criteria, model id, provider, role, raw path, parsed path, attempts, and sometimes duration. |
| triage | pass with gap | `triage.yaml` records finding id, source model, severity, final label, decision status, actor, reason, and raw/parsed paths. D-004 should normalize this into a stable finding schema. |
| decision / approval | pass with gap | Proxy decisions and commit approval records exist, but human/proxy approval formats vary by use case. D-006 and D-007 remain useful for auditability. |
| fix / tests | gap | Changed files and test commands are mostly recoverable from commits and session records, not a single stable evidence schema. D-005 and D-025 should handle this. |
| cost | missing | Current representative `rounds.yaml` files do not include API cost. D-019 should add cost capture or explicit missing markers. |
| elapsed time | partial | Some post-write runs record `duration_seconds`; older or larger review-runs often have `duration_seconds: null`. D-019 should normalize elapsed-time capture. |
| model assignment | pass | `rounds.yaml` and `review_summary.md` record role, provider, model, path, and variant-level assignment. |

Representative data checked:

- `.reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/rounds.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/model-result-summary.yaml`
- `.reviewcompass/specs/workflow-management/reviews/2026-06-04-workflow-management-implementation-review-run/triage.yaml`
- `docs/notes/review-runs/postwrite-completion-report-contract-2026-06-09-r3/rounds.yaml`

## Deployment Smoke Gap

D-021 cannot finish as `ready` without broader fixture or external repo smoke, but it now has a minimal app-root smoke for workflow navigation.

Minimum fixture result:

| Check | Result |
| --- | --- |
| Target repo root can be supplied by running from that root | pass |
| Target-side `.reviewcompass/specs/<feature>/` can be discovered | pass |
| ReviewCompass tool repo is not mutated by target feature discovery | pass |
| Synthetic review-run / triage / approval / test evidence can be written | not covered |
| ReviewCompass self-dogfooding `workflow_state` remains unchanged | pass by construction; test writes only under a temp external root |

Smoke command:

```bash
.venv/bin/python3 -m pytest tests/tools/test_check_workflow_action.py::NextNavigationTests::test_next_completed_from_external_app_root_fixture
```

Recommended next action: start D-004. Keep broader review-run / triage / approval / test-evidence smoke as a D-020 prerequisite unless D-004 exposes a schema blocker.

## Escalation Notes

| Escalation | Current decision |
| --- | --- |
| D-022 before D-004 | Do not escalate yet. Old-name and self-application terms exist, but this report has not shown they block deployment. |
| D-023 before D-004 | Do not escalate yet. Absolute-path and `cwd` risks exist, but the next proof should be a smoke fixture; concrete failure would escalate D-023. |
| D-024 before D-004 | Do not escalate yet. No backlog item is currently proven to block D-021 or D-020. |
| D-020 handoff | Hold until broader review-run / triage / approval / test-evidence smoke exists. The minimal app-root fixture is sufficient to proceed to D-004, not to run cross-repository replication. |

## Follow-Up / Handoff

1. Start D-004 normalized finding schema.
2. Pass fix/test traceability gaps to D-005 and TDD evidence gaps to D-025.
3. Pass cost and elapsed-time gaps to D-019.
4. Keep broader review-run / triage / approval / test-evidence smoke as D-020 prerequisite.
5. If a later fixture fails due to app-root or path assumptions, classify the blocker as D-023.
6. If a later fixture exposes old repository assumptions in deployable artifacts, classify the blocker as D-022.

## Completion State

This report completes the D-021 document-audit pass, source-policy summary, and minimal app-root workflow-navigation smoke. The current D-021 state is `ready_with_gaps`; D-004 may proceed, while broader multi-artifact deployment smoke remains a D-020 prerequisite.
